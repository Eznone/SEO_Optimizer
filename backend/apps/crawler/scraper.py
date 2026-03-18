from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import hashlib
import json
import logging
from .models import CrawlJob, CrawledPage, Link

logger = logging.getLogger(__name__)

class SiteCrawler:
    def __init__(self, job: CrawlJob, max_pages=100):
        self.job = job
        self.base_url = job.target_url
        self.domain = urlparse(self.base_url).netloc
        self.max_pages = max_pages
        self.visited_urls = set()
        self.pages_crawled = 0

    def normalize_url(self, url):
        parsed = urlparse(url)
        return parsed._replace(fragment='').geturl()

    def is_internal(self, url):
        parsed = urlparse(url)
        target_domain = parsed.netloc
        if target_domain == self.domain:
            return True
        if target_domain.endswith('.' + self.domain) or self.domain.endswith('.' + target_domain):
            return True
        return False

    def should_ignore(self, url):
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        ignored_extensions = (
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
            '.css', '.js', '.map',
            '.woff', '.woff2', '.ttf', '.eot', '.otf',
            '.mp4', '.webm', '.ogg', '.mp3', '.wav',
            '.pdf', '.zip', '.gz', '.tar', '.dmg', '.exe',
            '.webmanifest', '.json', '.xml'
        )
        if path.endswith(ignored_extensions):
            return True

        ignored_segments = (
            '/_next/', '/static/', '/favicons/', '/assets/', 
            '/chunks/', '/wp-content/', '/wp-includes/', 
            '/node_modules/', '/vendor/', '/bower_components/',
            'data:', 'javascript:'
        )
        for segment in ignored_segments:
            if segment in path or url.startswith(segment):
                return True
                
        return False

    def extract_json_ld(self, soup):
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        payloads = []
        for script in json_ld_scripts:
            if script.string:
                try:
                    data = json.loads(script.string)
                    payloads.append(data)
                except json.JSONDecodeError:
                    continue
        return payloads if payloads else None

    def crawl(self):
        queue = [(self.base_url, None, 0)]
        
        while queue and self.pages_crawled < self.max_pages:
            url, source_page, depth = queue.pop(0)
            normalized_url = self.normalize_url(url)
            
            if self.should_ignore(normalized_url):
                continue

            if normalized_url in self.visited_urls:
                if source_page:
                    Link.objects.create(
                        job=self.job,
                        source_page=source_page,
                        target_url=normalized_url,
                        is_dofollow=True,
                    )
                continue
                
            self.visited_urls.add(normalized_url)
            
            try:
                logger.info(f"Crawling {normalized_url}")
                response = requests.get(normalized_url, timeout=10.0, allow_redirects=False)
                status_code = response.status_code
                
                page, created = CrawledPage.objects.get_or_create(
                    job=self.job,
                    url=normalized_url,
                    defaults={
                        'status_code': status_code,
                        'depth': depth,
                        'priority': 0.5,
                        'metadata_headers': dict(response.headers)
                    }
                )

                if not created:
                    if page.status_code != status_code:
                        page.status_code = status_code
                        page.metadata_headers = dict(response.headers)
                        page.save()

                if source_page:
                    Link.objects.create(
                        job=self.job,
                        source_page=source_page,
                        target_url=normalized_url,
                        is_broken=(status_code >= 400)
                    )

                self.pages_crawled += 1

                if 300 <= status_code < 400:
                    target_url = response.headers.get('Location')
                    if target_url:
                        target_url = urljoin(normalized_url, target_url)
                        queue.append((target_url, page, depth + 1))
                    continue

                is_html = 'text/html' in response.headers.get('Content-Type', '')
                if status_code == 200 and is_html:
                    page.raw_html = response.text
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    title_tag = soup.find('title')
                    page.title = title_tag.text.strip()[:500] if title_tag else None

                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    page.meta_description = meta_desc.get('content', '').strip() if meta_desc else None

                    h1_tag = soup.find('h1')
                    page.h1 = h1_tag.text.strip()[:500] if h1_tag else None

                    canonical_tag = soup.find('link', rel='canonical')
                    page.canonical_url = canonical_tag.get('href', '').strip()[:2000] if canonical_tag else None

                    robots_tag = soup.find('meta', attrs={'name': 'robots'})
                    if robots_tag:
                        robots_content = robots_tag.get('content', '').lower()
                        if 'noindex' in robots_content:
                            page.is_noindex = True

                    text_content = soup.get_text(separator=' ', strip=True)
                    page.extracted_text = text_content
                    page.content_hash = hashlib.sha256(text_content.encode('utf-8')).hexdigest()
                    
                    page.json_ld_payload = self.extract_json_ld(soup)
                    
                    page.save()

                    found_urls = set()
                    for a in soup.find_all('a', href=True):
                        found_urls.add((a.get('href'), a.text.strip()[:500], 'nofollow' in a.get('rel', [])))

                    import re
                    script_content = "".join([s.text for s in soup.find_all('script') if s.text])
                    href_patterns = re.findall(r'\\?"(?:href|pathname|url)\\?":\\?"([^\\"]+)\\?"', script_content)
                    for href in href_patterns:
                        clean_href = href.replace('\\/', '/')
                        found_urls.add((clean_href, "", False))

                    for href, link_text, is_nofollow in found_urls:
                        full_url = urljoin(normalized_url, href)
                        
                        if self.should_ignore(full_url):
                            continue
                            
                        if self.is_internal(full_url):
                            queue.append((full_url, page, depth + 1))
                        else:
                            Link.objects.create(
                                job=self.job,
                                source_page=page,
                                target_url=full_url,
                                anchor_text=link_text,
                                is_dofollow=not is_nofollow
                            )

            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                if source_page:
                    Link.objects.create(
                        job=self.job,
                        source_page=source_page,
                        target_url=normalized_url,
                        is_broken=True
                    )

        self.job.total_pages_crawled = self.pages_crawled
        self.job.status = 'completed'
        from django.utils import timezone
        self.job.completed_at = timezone.now()
        self.job.save()
