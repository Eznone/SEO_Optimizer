# Session Summary: Building a Robust SEO Audit & Recommendation Engine

This document details the transformation of the `sitemaps` application from a basic XML generator into a deep-site diagnostic tool. It covers the architectural decisions, the "why" behind the changes, and a guide for implementing similar systems in the future.

## 1. The Objective: Moving Beyond "Just a File"

The original product generated a single-page XML sitemap with static metadata. To provide real value, the system needed to move toward **Depth and Diagnosis**:

- **Depth:** Crawling the entire site (BFS) instead of just the home page.
- **Diagnosis:** Identifying _why_ a site is underperforming (broken links, orphans, duplicates).
- **Actionability:** Providing prioritized recommendations with business impact, not just a list of URLs.

## 2. The New Architecture: Relational Auditing

Instead of keeping crawl data in memory, we moved to a **Robust Relational Model**. This allows for complex querying (e.g., "find all pages with no incoming links") and historical tracking.

### Data Models

- **`SitemapJob`**: The parent entity tracking status, totals, and the final file.
- **`Page`**: Stores real metadata (`title`, `description`, `h1`, `canonical_url`, `is_noindex`) and a `content_hash` for duplicate detection.
- **`Link`**: Maps the relationship between pages. This is critical for detecting **Orphan Pages** and **Broken Internal Links**.
- **`AuditIssue`**: Atomic SEO failures (e.g., "404 detected", "Canonical mismatch").
- **`Recommendation`**: High-level, prioritized advice mapped to business risks (e.g., "Wasted crawl budget").

## 3. The Implementation Logic

### A. The Deep Crawler (`SiteCrawler`)

We implemented a **Breadth-First Search (BFS)** crawler.

1. **Queue Management:** Start with the base URL. Add discovered internal links to a queue.
2. **Normalization:** Strip fragments (`#section`) to avoid crawling the same page multiple times.
3. **Metadata Extraction:** Use `BeautifulSoup` to parse tags that search engines care about.
4. **Content Hashing:** Use `hashlib.sha256` on the page text to identify near-identical content clusters.

### B. The Analysis Engine (`SiteAnalyzer`)

Analysis happens _after_ the crawl is complete. This "post-processing" phase allows us to look at the site as a whole:

- **Orphan Detection:** Query for `Page` objects that have zero entries in the `Link` table as a `target_url`.
- **Broken Link Mapping:** Identify links pointing to non-200 status codes.
- **Conflict Resolution:** Compare the requested `url` against the `canonical_url` tag.

### C. The Recommendation Logic

Issues are aggregated into recommendations. This is where we translate technical data into **Business Value**:

- _Technical:_ 50 broken links.
- _Recommendation:_ "Fix 50 broken links to stop wasting crawl budget and improve user retention."

## 4. How to do it yourself (The "Recipe")

When building a diagnostic engine, follow these steps:

1. **Define the "Healthy" State:** What does a perfect page look like? (200 OK, unique title, self-referential canonical, etc.).
2. **Capture the "Current" State:** Build a crawler that saves _everything_ it sees to a database. Don't try to analyze while crawling; just collect.
3. **Run Comparative Queries:**
   - Find everything in the "Current" state that doesn't match the "Healthy" state.
   - Use SQL/Django ORM `Count` and `Exclude` to find structural gaps (like orphans).
4. **Prioritize by Severity:** Map every issue type to a severity (High/Medium/Low).
   - _High:_ Broken links, 5xx errors.
   - _Medium:_ Missing descriptions, duplicate content.
5. **Clean Output:** Ensure your final artifact (the Sitemap XML) only contains the "Healthy" pages discovered during the crawl.

## 5. Key Lessons Learned

- **Async vs. Relational:** While async crawling is fast, saving to a relational DB ensures data integrity and allows for powerful post-crawl analysis that memory-only crawlers can't easily do.
- **Normalizing is Safety:** Always normalize URLs. Without it, `site.com/` and `site.com/index.html` might be treated as different pages, leading to infinite loops or bloated reports.
- **Fail Gracefully:** Use `try/except` blocks inside your crawler loop so that one timeout or 404 doesn't crash the entire multi-page crawl.
