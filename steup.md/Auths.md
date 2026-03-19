# Authentication Setup Runbook (Google OAuth + SessionAuth)

This document is a reproducible checklist for enabling and testing Google login with `django-allauth` in this project.

## 1) Prerequisites

- Python environment activated.
- Dependencies installed:
  - `pip install -r requirements.txt`
- Database migrated:
  - `python manage.py migrate`
- Admin user created:
  - `python manage.py createsuperuser`
- Dev server running from `backend/`:
  - `python manage.py runserver`

## 2) Pick One Local Host And Stay Consistent

Use one host everywhere. Recommended for this project:

- Host: `127.0.0.1`
- Port: `8000`
- Base URL: `http://127.0.0.1:8000`

Important: do not mix `localhost` and `127.0.0.1` during setup.

## 3) Configure Django Site (Required)

1. Open admin: `http://127.0.0.1:8000/admin/`
2. Go to **Sites**.
3. Open the record with ID `1`.
4. Set:
   - Domain name: `127.0.0.1:8000`
   - Display name: `Local Dev`
5. Save.

Why: `SITE_ID = 1` is used by allauth to resolve current domain and callback behavior.

## 4) Create Google OAuth Credentials (Google Cloud)

1. Open Google Cloud Console.
2. Create/select project.
3. Configure **OAuth consent screen** (External is fine for local dev).
4. Create **OAuth Client ID** with type **Web application**.
5. Add authorized redirect URI:

`http://127.0.0.1:8000/accounts/google/login/callback/`

6. Save and copy:
   - Client ID
   - Client Secret

## 5) Create SocialApp in Django Admin

1. In admin, open **Social applications**.
2. Add a new app:
   - Provider: `Google`
   - Name: `Google`
   - Client id: `<from Google Cloud>`
   - Secret key: `<from Google Cloud>`
3. In **Chosen sites**, add the Site `127.0.0.1:8000`.
4. Save.

If this is missing, `/accounts/google/login/` will fail with SocialApp errors.

## 6) Start Login Flow

Open:

`http://127.0.0.1:8000/accounts/google/login/`

This route exists because project URLs include `allauth.urls` under `/accounts/`.

## 7) Verify API Authentication Works

After successful Google login (same browser session), open:

`http://127.0.0.1:8000/api/users/me`

Expected: JSON profile payload with username/email and key status.

## 8) Verify Logout

1. Open: `http://127.0.0.1:8000/accounts/logout/`
2. Confirm logout.
3. Re-open `http://127.0.0.1:8000/api/users/me`

Expected: unauthorized/not authenticated response.

## 9) Quick Troubleshooting

- `SocialApp matching query does not exist`
  - Create SocialApp and attach Site.
- `redirect_uri_mismatch`
  - Ensure Google callback URI exactly matches local URI.
- Login works but API seems anonymous
  - Host mismatch (`localhost` vs `127.0.0.1`) causing cookie mismatch.
- Allauth route not found
  - Ensure `path("accounts/", include("allauth.urls"))` exists and server restarted.

## 10) Optional Smoke Test Checklist

- [ ] Can reach `/accounts/google/login/`
- [ ] Google consent screen appears
- [ ] Redirect returns to local app
- [ ] `/api/users/me` returns authenticated user JSON
- [ ] `/accounts/logout/` clears auth for `/api/users/me`
