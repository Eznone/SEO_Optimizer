# Session Summary: Resolving SQLite NOT NULL Constraints & URL Normalization Conflicts

This document summarizes the investigation into a persistent `NOT NULL constraint failed: sitemaps_page.priority` error encountered during site crawling on Windows with SQLite.

## 1. The Core Issue: The "Phantom" Null Priority
During a deep crawl, the worker crashed with the following error:
`ERROR/MainProcess] Error crawling https://docs.pydantic.dev/2.12/errors/validation_errors/#missing: NOT NULL constraint failed: sitemaps_page.priority`

### What was happening?
*   **The Schema Conflict:** We recently added a `priority` field to the `Page` model with a `default=0.5`. In Django, this default is applied at the application level.
*   **The SQLite Limitation:** When Django generates migrations for SQLite to add a `NOT NULL` column to an existing table, it often handles the "default" by populating existing rows, but it doesn't always successfully create a permanent `DEFAULT` constraint in the SQLite schema itself.
*   **URL Normalization & Fragments:** The `SiteCrawler` strips fragments (like `#missing`) to avoid duplicate crawls. If a page is linked multiple times with different fragments, they all normalize to the same URL.
*   **The Conflict:** The crawler was using `Page.objects.create()`. If a page already existed due to a fragment normalization or a previous link, the `create()` call would trigger a database conflict. In certain race conditions or conflict resolutions within SQLite, the database would complain about the missing `priority` value before Django could apply its Python-side default.

---

## 2. Evolution of the Fix

### Attempt 1: Schema Investigation
**Strategy:** Verify if the database actually has the `NOT NULL` constraint and if rows are missing values.
*   **Tool:** Used `PRAGMA table_info(sitemaps_page)` via a custom script.
*   **Finding:** The column was indeed `NOT NULL`, but it lacked a database-level `DEFAULT` value. A count showed 0 rows with actual NULL values, confirming the error happened during the *insertion* of new/conflicting data.

### Attempt 2: Implementing `get_or_create` (The Final Fix)
**Strategy:** Move from aggressive creation to defensive retrieval.
*   **The Change:** Replaced `Page.objects.create()` with `Page.objects.get_or_create()`.
*   **Why it works:** `get_or_create` allows us to define `defaults`. If the page already exists (e.g., from a link encountered seconds ago with a different fragment), it simply retrieves the existing record instead of crashing the process.
*   **Explicit Defaults:** We explicitly passed `priority: 0.5` in the `defaults` dictionary, ensuring that even if the database-level default is missing, the application-level value is sent during the `INSERT`.

---

## 3. Key Concepts for Future Troubleshooting

### Django Defaults vs. Database Defaults
*   **Django `default`:** Only applied when you instantiate a model in Python. It is **not** a guarantee that the database column itself has a `DEFAULT` value.
*   **Database `DEFAULT`:** A constraint set at the SQL level (e.g., `DEFAULT 0.5`).
*   **Lesson:** If you see `NOT NULL constraint failed` on a field that has a Django `default`, it often means the database is being hit in a way that bypasses Django's standard instantiation (like a failed `create`, a raw SQL query, or a bulk update).

### URL Normalization Side-Effects
Normalizing URLs is essential for SEO (preventing duplicate content in the sitemap), but it creates "collision" points in your database.
*   **Lesson:** Any field marked as `unique` or `unique_together` (like `job` + `url`) must be handled using `get_or_create` or `update_or_create` if there is any chance the same entity will be encountered multiple times in a single process.

### Defensive Calculation
When performing post-crawl analysis (like `calculate_priorities`), always assume the crawl might have been partial or interrupted.
*   **Lesson:** Use the `or` operator for nullable fields (e.g., `(page.depth or 0)`) to prevent `TypeError` when performing math on data collected from a potentially "dirty" crawl.

---

## 4. Summary of Improvements Made
1.  **Hardened `SiteCrawler`:** Switched to `get_or_create` to handle fragment-heavy sites like documentation (e.g., Pydantic docs).
2.  **Explicit Defaults:** Ensured `priority` is always sent during page creation to appease the SQLite `NOT NULL` constraint.
3.  **Defensive Priority Logic:** Updated `calculate_priorities` to handle edge cases where `depth` might be missing or `None`.
4.  **Status Syncing:** Added logic to update the `status_code` of an existing page if a new link discovers a changed status (e.g., a page that was "pending" or redirected is now found as a 404).

## 5. How to fix things yourself next time
1.  **Inspect the Schema directly:** If you suspect a constraint error, use a script to run `PRAGMA table_info(table_name)` (for SQLite) or `DESCRIBE table_name` (for Postgres/MySQL). Don't trust the `models.py` alone.
2.  **Check for "Hidden" Collisions:** If a crawler fails on a specific URL, check if that URL normalizes to something that already exists in your database.
3.  **Use `get_or_create` by default:** When writing crawlers or scrapers, `get_or_create` is almost always safer than `create`.
