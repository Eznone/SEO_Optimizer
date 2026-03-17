import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import hashlib
from django.db.models import Count
from .models import SitemapJob, Page, Link, AuditIssue, Recommendation
import logging

logger = logging.getLogger(__name__)

class SiteCrawler:
    def __init__(self, job: SitemapJob, max_pages=100):
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
        # Allow same domain and its subdomains (like www)
        target_domain = parsed.netloc
        if target_domain == self.domain:
            return True
        if target_domain.endswith('.' + self.domain) or self.domain.endswith('.' + target_domain):
            return True
        return False

    def should_ignore(self, url):
        """
        Determines if a URL should be ignored based on common asset extensions
        and framework-specific path segments.
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # 1. Check file extensions
        ignored_extensions = (
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', # Images
            '.css', '.js', '.map', # Assets
            '.woff', '.woff2', '.ttf', '.eot', '.otf', # Fonts
            '.mp4', '.webm', '.ogg', '.mp3', '.wav', # Media
            '.pdf', '.zip', '.gz', '.tar', '.dmg', '.exe', # Files
            '.webmanifest', '.json', '.xml' # Metadata/Config
        )
        if path.endswith(ignored_extensions):
            return True

        # 2. Check path segments (Framework noise and common asset folders)
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

    def crawl(self):
        # queue of (url, source_page_model, depth)
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
                
                page, created = Page.objects.get_or_create(
                    job=self.job,
                    url=normalized_url,
                    defaults={
                        'status_code': status_code,
                        'depth': depth,
                        'priority': 0.5
                    }
                )

                if not created:
                    # Update status code if it changed or was None
                    if page.status_code != status_code:
                        page.status_code = status_code
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
                    page.content_hash = hashlib.sha256(text_content.encode('utf-8')).hexdigest()
                    page.save()

                    # Extract links from <a> tags
                    found_urls = set()
                    for a in soup.find_all('a', href=True):
                        found_urls.add((a.get('href'), a.text.strip()[:500], 'nofollow' in a.get('rel', [])))

                    # Next.js / Modern SPA support: Extract hrefs from script data
                    import re
                    script_content = "".join([s.text for s in soup.find_all('script') if s.text])
                    # Pattern for "href":"/path", "pathname":"/path", or "url":"/path"
                    # Handles optional backslashes before quotes common in escaped JSON
                    href_patterns = re.findall(r'\\?"(?:href|pathname|url)\\?":\\?"([^\\"]+)\\?"', script_content)
                    for href in href_patterns:
                        # Clean escaped slashes common in JSON
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
        self.job.save()


class SiteAnalyzer:
    def __init__(self, job: SitemapJob):
        self.job = job

    def analyze(self):
        issues_created = 0

        pages = Page.objects.filter(job=self.job)
        for page in pages:
            incoming_links_count = Link.objects.filter(job=self.job, target_url=page.url).count()
            if incoming_links_count == 0 and page.depth > 0:
                AuditIssue.objects.create(
                    job=self.job,
                    page=page,
                    issue_type='orphan',
                    severity='high',
                    description=f"Page has no internal incoming links."
                )
                issues_created += 1

        broken_pages = Page.objects.filter(job=self.job, status_code__gte=400)
        for page in broken_pages:
            AuditIssue.objects.create(
                job=self.job,
                page=page,
                issue_type='broken_link',
                severity='high',
                description=f"Page returned status {page.status_code}."
            )
            issues_created += 1

        for page in pages:
            if page.canonical_url and page.canonical_url != page.url:
                AuditIssue.objects.create(
                    job=self.job,
                    page=page,
                    issue_type='canonical_conflict',
                    severity='medium',
                    description=f"Canonical URL points to {page.canonical_url} instead of {page.url}."
                )
                issues_created += 1

        for page in pages.filter(is_noindex=True):
            AuditIssue.objects.create(
                job=self.job,
                page=page,
                issue_type='noindex',
                severity='medium',
                description="Page has a meta robots noindex tag."
            )
            issues_created += 1

        duplicates = Page.objects.filter(job=self.job, status_code=200).values('content_hash').annotate(count=Count('id')).filter(count__gt=1)
        for dup in duplicates:
            if not dup['content_hash']: continue
            dup_pages = Page.objects.filter(job=self.job, content_hash=dup['content_hash'])
            for page in dup_pages:
                AuditIssue.objects.create(
                    job=self.job,
                    page=page,
                    issue_type='duplicate_content',
                    severity='medium',
                    description="Page shares identical content with other pages."
                )
                issues_created += 1

        self.job.total_issues_found = issues_created
        self.job.save()

        self.calculate_priorities()
        self._generate_recommendations()

    def calculate_priorities(self):
        """
        Calculates a priority score (0.1 - 1.0) for each page based on:
        1. Depth (closer to root = higher)
        2. Popularity (more internal links = higher)
        """
        pages = Page.objects.filter(job=self.job)
        
        # Signal 1: Popularity (Incoming link count)
        # Find the max number of incoming links for any page to normalize the boost
        max_links = Link.objects.filter(job=self.job).values('target_url').annotate(count=Count('id')).order_by('-count').first()
        max_count = max_links['count'] if max_links else 1

        for page in pages:
            # Base priority starts at 1.0
            priority = 1.0
            
            # Decay by depth: -0.2 per click away from root (capped at 0.8 loss)
            depth_decay = min(0.8, (page.depth or 0) * 0.2)
            priority -= depth_decay
            
            # Boost by popularity: Add up to 0.2 based on normalized link count
            incoming_count = Link.objects.filter(job=self.job, target_url=page.url).count()
            popularity_boost = (incoming_count / max_count) * 0.2
            priority += popularity_boost
            
            # Clamp between 0.1 and 1.0
            page.priority = max(0.1, min(1.0, round(priority, 1)))
            page.save()

    def _generate_recommendations(self):
        issue_counts = AuditIssue.objects.filter(job=self.job).values('issue_type', 'severity').annotate(count=Count('id'))
        
        for ic in issue_counts:
            count = ic['count']
            itype = ic['issue_type']
            
            if itype == 'broken_link' and count > 0:
                Recommendation.objects.create(
                    job=self.job,
                    priority=1,
                    action_required=f"Fix {count} broken internal links.",
                    business_impact="Broken links waste crawl budget and lead to a poor user experience, directly impacting rankings and conversions.",
                    affected_pages_count=count
                )
            elif itype == 'orphan' and count > 0:
                Recommendation.objects.create(
                    job=self.job,
                    priority=1,
                    action_required=f"Link to {count} orphan pages.",
                    business_impact="Orphan pages cannot be found by users navigating the site and receive no internal link equity, severely harming their SEO potential.",
                    affected_pages_count=count
                )
            elif itype == 'duplicate_content' and count > 0:
                Recommendation.objects.create(
                    job=self.job,
                    priority=2,
                    action_required=f"Resolve {count} pages with duplicate content.",
                    business_impact="Duplicate content confuses search engines, dilutes ranking signals, and wastes crawl budget.",
                    affected_pages_count=count
                )
            elif itype == 'noindex' and count > 0:
                Recommendation.objects.create(
                    job=self.job,
                    priority=3,
                    action_required=f"Review {count} pages with noindex tags.",
                    business_impact="Pages with noindex will not appear in search results. Ensure these are intentional.",
                    affected_pages_count=count
                )
            elif itype == 'canonical_conflict' and count > 0:
                Recommendation.objects.create(
                    job=self.job,
                    priority=2,
                    action_required=f"Fix {count} canonical conflicts.",
                    business_impact="Canonical conflicts confuse search engines regarding which version of a page to rank.",
                    affected_pages_count=count
                )

class SitemapGenerator:
    def __init__(self, pages: List[Page], changefreq: str = "weekly"):
        self.pages = pages
        self.changefreq = changefreq
        self.generation_time = datetime.now().strftime('%Y-%m-%d')

    def generate_xml(self) -> bytes:
        urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

        for page in self.pages:
            url_el = ET.SubElement(urlset, "url")
            ET.SubElement(url_el, "loc").text = page.url
            ET.SubElement(url_el, "lastmod").text = self.generation_time
            ET.SubElement(url_el, "changefreq").text = self.changefreq
            ET.SubElement(url_el, "priority").text = str(page.priority)

        return ET.tostring(urlset, encoding='utf-8', method='xml', xml_declaration=True)
