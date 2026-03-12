import httpx
import time
import re
import ssl
from bs4 import BeautifulSoup


def _get_ssl_context():
    return ssl.create_default_context()


def perform_seo_analysis(url: str, target_keywords: list[str] = None):
    start_time = time.perf_counter()

    print(f"--- Starting Analysis for: {url} ---")

    try:
        response = httpx.get(url, follow_redirects=True, timeout=10.0, verify=_get_ssl_context())
        html_content = response.text

    except Exception as e:
        return {"status": "Error", "message": str(e)}

    end_time = time.perf_counter()
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 1. Basic SEO Extraction
    title = soup.title.string if soup.title else ""
    h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
    
    # DEBUG: See what metadata was found
    print(f"[DEBUG] Title Found: '{title}'")
    print(f"[DEBUG] H1 Tags Found: {len(h1_tags)}")

    # 2. Keyword Analysis
    keyword_results = {}
    if target_keywords:
        # Get all visible text on the page for density check
        page_text = soup.get_text(separator=' ', strip=True).lower()
        
        for kw in target_keywords:
            kw_lower = kw.lower()
            # Count occurrences using regex for word boundaries
            matches = re.findall(rf'\b{re.escape(kw_lower)}\b', page_text)
            count = len(matches)
            
            # DEBUG: Log the specific keyword hits
            print(f"[DEBUG] Keyword '{kw}': Found {count} matches.")
            
            keyword_results[kw] = {
                "count": count,
                "in_title": kw_lower in title.lower(),
                "in_h1": any(kw_lower in h.lower() for h in h1_tags),
                "density_score": round((count / len(page_text.split())) * 100, 2) if page_text.split() else 0
            }

    print(f"--- Analysis Complete ({round(end_time - start_time, 2)}s) ---")
    return {
        "url": url,
        "title": title,
        "load_time_seconds": round(end_time - start_time, 3),
        "keyword_analysis": keyword_results,
        "status": "Success"
    }

# Example Usage to test:
# results = perform_seo_analysis("https://www.example.com", ["example", "domain"])
# print(results)