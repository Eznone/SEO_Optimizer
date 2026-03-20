# Pre-Deployment Checklist

This checklist covers the essential steps to transition from local development to a production environment, with a focus on the **Oracle Cloud (Backend) + Vercel (Frontend)** free tier strategy.

## 1. Backend (Django) - Oracle Cloud Free Tier
Oracle Cloud offers high-performance ARM (Ampere A1) instances with up to 24GB RAM for free, which is perfect for running Django, Celery, Redis, and Postgres together using Docker Compose.

- [ ] **Security**: Set `DEBUG = False` in your production environment variables.
- [ ] **Secrets**: Generate a new, unique `SECRET_KEY` for production. Never reuse the development key.
- [ ] **Hosts**: Update `ALLOWED_HOSTS` to include your Oracle instance's Public IP or domain (e.g., `api.yourdomain.com`).
- [ ] **CSRF**: Update `CSRF_TRUSTED_ORIGINS` to include your **Vercel** production URL (e.g., `https://your-app.vercel.app`).
- [ ] **Redirects**: Set `FRONTEND_URL` in `.env` to point to your live Vercel site.
- [ ] **Database Migration**: Move from SQLite to **PostgreSQL**. Update `DATABASES` in `settings.py` to use environment variables.
- [ ] **Static Files**: Setup a strategy for serving static files. Since you have a VPS (Oracle), you can use **Nginx** or **WhiteNoise** with `python manage.py collectstatic`.
- [ ] **Secure Cookies**: Enable production security settings in `settings.py`:
    ```python
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
    ```
- [ ] **Oracle Security List**: Open the necessary ports in the Oracle Cloud Console (Ingress Rules):
    *   `80` (HTTP) - for Nginx
    *   `443` (HTTPS) - for SSL (using Certbot/Let's Encrypt)
    *   `8000` - (Optional) if exposing Django directly for testing
- [ ] **Oracle OS Firewall**: Run `iptables` or `firewall-cmd` commands on the instance to open the ports at the OS level.
- [ ] **Docker Architecture**: Ensure your Docker images are built for **ARM64** (Oracle ARM instances) or use multi-arch builds.

## 2. Frontend (Next.js) - Vercel
Vercel is the industry standard for Next.js deployment and offers a robust free tier.

- [ ] **API Proxy**: In `next.config.ts`, ensure `BACKEND_URL` is set to your Oracle instance's domain.
- [ ] **Environment Variables**: Add all variables from `exmaple.env` to the **Vercel Dashboard** (Settings -> Environment Variables).
- [ ] **Rewrites**: Verify that `/api/`, `/accounts/`, and `/media/` are correctly proxied to your Oracle backend in `next.config.ts`.
- [ ] **OAuth**: Update Redirect URIs in the Google/GitHub Developer Consoles:
    *   `https://api.yourdomain.com/accounts/google/login/callback/`
    *   `https://api.yourdomain.com/accounts/github/login/callback/`

## 3. Infrastructure & Background Tasks (Oracle VPS)
Running all services on a single high-memory Oracle instance.

- [ ] **Redis**: Run a Redis container on your Oracle instance. Update `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` to point to `redis://localhost:6379/0` (within the Docker network).
- [ ] **Workers**: Run at least one Celery worker and one Celery beat container. Monitor them with a tool like `watchtower` or `portainer` (both can run on Oracle).
- [ ] **SSL (HTTPS)**: Install `certbot` and use Nginx to terminate SSL for your API domain. Vercel handles SSL automatically for the frontend.
- [ ] **Persistence**: Ensure your Docker Compose uses **Volumes** so that your Postgres data and generated media files (sitemaps, LLMS.txt) aren't lost when containers restart.

## 4. Final Verification
- [ ] **Auth Flow**: Verify Login, Logout, and OAuth registration across both domains.
- [ ] **Media Access**: Confirm you can download a generated sitemap from the Vercel frontend (it should proxy through to the Oracle VPS storage).
- [ ] **Worker Health**: Trigger a crawl and verify that the worker on the Oracle instance picks it up and successfully processes it.
- [ ] **Outbound Requests**: Confirm that the Oracle instance can successfully reach external sites (no egress blocking).
