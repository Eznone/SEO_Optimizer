# Pre-Deployment Checklist

This checklist covers the essential steps to transition from local development to a production environment.

## 1. Backend (Django)
- [ ] **Security**: Set `DEBUG = False` in your production environment variables.
- [ ] **Secrets**: Generate a new, unique `SECRET_KEY` for production. Never reuse the development key.
- [ ] **Hosts**: Update `ALLOWED_HOSTS` to include your production API domain (e.g., `api.yourdomain.com`).
- [ ] **CSRF**: Update `CSRF_TRUSTED_ORIGINS` to include your production frontend URL (e.g., `https://app.yourdomain.com`).
- [ ] **Redirects**: Set `FRONTEND_URL` in `.env` to ensure `LOGIN_REDIRECT_URL` and `LOGOUT_REDIRECT_URL` point to the live site.
- [ ] **Database**: Configure a production-grade database (e.g., PostgreSQL or Managed MySQL). Update `DATABASES` in `settings.py` or use `DATABASE_URL`.
- [ ] **Migrations**: Run `python manage.py migrate` on the production server.
- [ ] **Static Files**: Setup a strategy for serving static files (e.g., using **WhiteNoise** or an **S3 Bucket**). Run `python manage.py collectstatic`.
- [ ] **Secure Cookies**: Enable production security settings in `settings.py`:
    ```python
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
    ```
- [ ] **Encryption**: Ensure `FIELD_ENCRYPTION_KEY` is securely stored and consistent across deployments.

## 2. Frontend (Next.js)
- [ ] **API URL**: Set `BACKEND_URL` (server-side) and `NEXT_PUBLIC_BACKEND_URL` (client-side) to your production API domain.
- [ ] **Environment Variables**: Ensure all variables from `exmaple.env` are defined in your hosting platform (e.g., Vercel, Netlify).
- [ ] **Build**: Run `npm run build` locally to verify there are no TypeScript or linting errors before pushing.
- [ ] **OAuth**: Update Redirect URIs in the Google/GitHub Developer Consoles to match your production domain:
    *   `https://api.yourdomain.com/accounts/google/login/callback/`
    *   `https://api.yourdomain.com/accounts/github/login/callback/`

## 3. Infrastructure & Background Tasks
- [ ] **Redis**: Provision a production Redis instance for Celery. Update `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`.
- [ ] **Workers**: Configure your production environment to run Celery workers as background processes (e.g., using `systemd`, `supervisor`, or platform-native background workers).
- [ ] **SSL**: Ensure both frontend and backend are served over **HTTPS**.
- [ ] **Proxy**: If using a custom server, configure Nginx or Apache as a reverse proxy.

## 4. Final Verification
- [ ] **Auth Flow**: Verify Login, Logout, and OAuth registration on the production domain.
- [ ] **CSRF**: Confirm that POST requests (like starting a crawl or logging out) succeed without CSRF errors.
- [ ] **Crawling**: Ensure the backend server has the necessary outbound permissions to crawl external websites.
- [ ] **Logs**: Verify that application logs are being captured and are accessible for troubleshooting.
