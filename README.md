# 🏠 PG Finder — Django REST API

Backend for the **PG Finder Platform** — connecting corporate professionals and students with verified PG accommodations across India.

**Stack:** Django 4.2 + DRF + PostgreSQL + Redis + Celery + Django Channels + drf-spectacular (Swagger)

---

## 📋 API Endpoints

| Module | Endpoints |
|--------|-----------|
| **Auth** | `POST /api/auth/register/` · `login/` · `logout/` · `refresh/` · `otp/request/` · `otp/verify/` |
| **Profile** | `GET/PATCH /api/profile/` · `POST /api/profile/change-password/` · `GET/POST /api/profile/kyc/` |
| **Listings** | `GET/POST /api/listings/` · `GET/PATCH/DELETE /api/listings/{id}/` · `POST /api/listings/{id}/photos/` · `PATCH /api/listings/{id}/status/` |
| **Wishlist** | `GET/POST /api/listings/wishlist/` · `DELETE /api/listings/wishlist/{id}/` |
| **Search** | `GET /api/search/?city=&budget_min=&budget_max=&gender_type=&has_wifi=&lat=&lng=&radius_km=&sort=` |
| **Inquiries** | `GET/POST /api/inquiries/` · `GET /api/inquiries/{id}/` · `PATCH /api/inquiries/{id}/status/` |
| **Media** | `POST /api/upload/photo/` → returns S3 presigned URL |
| **Chat** | `GET /api/chat/room/{inquiry_id}/` · WebSocket: `ws://host/ws/chat/{room_id}/` |
| **Notifications** | `GET /api/notifications/` · `POST /api/notifications/mark-all-read/` · `PATCH /api/notifications/{id}/read/` |
| **Subscriptions** | `GET /api/subscriptions/plans/` · `GET /api/subscriptions/my/` · `POST /api/subscriptions/create-order/` · `POST /api/subscriptions/verify-payment/` |
| **Admin** | `GET /api/admin-panel/pending-verifications/` · `PATCH /api/admin-panel/verify-owner/{id}/` · `PATCH /api/admin-panel/listings/{id}/moderate/` · `GET /api/admin-panel/stats/` |

## 📖 API Docs (Swagger)

| URL | Description |
|-----|-------------|
| `/api/docs/` | Swagger UI (interactive) |
| `/api/redoc/` | ReDoc (read-only) |
| `/api/schema/` | Raw OpenAPI 3.0 JSON |
| `/django-admin/` | Django admin panel |

---

## 🚀 Local Development

```bash
# 1. Clone and set up environment
git clone <repo-url>
cd pg_finder
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY

# 3. Run migrations
python manage.py migrate

# 4. Create a superuser
python manage.py createsuperuser

# 5. Start the dev server
python manage.py runserver

# 6. (Optional) Start Celery for async tasks
redis-server &  # or use Docker
celery -A pg_finder worker --loglevel=info

# 7. (Optional) Start Daphne for WebSocket support
daphne -b 0.0.0.0 -p 8000 pg_finder.asgi:application
```

Visit `http://localhost:8000/api/docs/` for Swagger UI.

---

## ☁️ Deploy to Render

### Option A — render.yaml (Infrastructure as Code)
```bash
# Push to GitHub, then in Render dashboard:
# New > Blueprint > Connect your repo
# Render reads render.yaml and creates all services automatically
```

### Option B — Manual setup
1. **Web Service** → Runtime: Python · Build: `./build.sh` · Start: `daphne -b 0.0.0.0 -p $PORT pg_finder.asgi:application`
2. **Worker** → Start: `celery -A pg_finder worker --loglevel=info`
3. **PostgreSQL** → Create a Render managed database, copy `DATABASE_URL`
4. **Redis** → Create a Render Redis instance, copy `REDIS_URL`

### Required Environment Variables (Render Dashboard)
```
SECRET_KEY          → auto-generate or set a 50+ char random string
DEBUG               → False
ALLOWED_HOSTS       → .onrender.com
DATABASE_URL        → from Render PostgreSQL
REDIS_URL           → from Render Redis
CORS_ALLOWED_ORIGINS → https://your-nextjs.vercel.app
```

---

## 🏗️ Project Structure

```
pg_finder/
├── pg_finder/          # Project config (settings, urls, celery, asgi)
├── accounts/           # Custom user model, JWT auth, OTP, KYC
├── listings/           # PG listing CRUD, photos, wishlist
├── search/             # Advanced geo-filter search
├── inquiries/          # Tenant → Owner inquiry flow
├── media/              # S3 presigned URL uploads
├── notifications/      # In-app + email + SMS notifications (Celery)
├── chat/               # WebSocket real-time chat (Django Channels)
├── subscriptions/      # Razorpay subscription plans + billing
├── admin_panel/        # Platform admin endpoints (KYC, moderation, stats)
├── requirements.txt
├── render.yaml         # Render IaC deployment config
├── build.sh            # Render build script
└── .env.example
```

---

## 🔐 Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

Obtain tokens via `POST /api/auth/login/` or `POST /api/auth/register/`.  
Refresh via `POST /api/auth/refresh/` using the `refresh` token.  
OTP login: `POST /api/auth/otp/request/` → `POST /api/auth/otp/verify/`.

---

## 📦 Key Libraries

| Library | Purpose |
|---------|---------|
| `djangorestframework` | REST API framework |
| `djangorestframework-simplejwt` | JWT auth + token blacklisting |
| `drf-spectacular` | Auto Swagger/OpenAPI 3.0 docs |
| `django-filter` | Powerful queryset filtering |
| `django-storages + boto3` | AWS S3 file uploads |
| `celery + redis` | Async email/SMS/push tasks |
| `channels + channels-redis` | WebSocket real-time chat |
| `dj-database-url` | Render PostgreSQL URL parsing |
| `whitenoise` | Static file serving on Render |
| `razorpay` | Subscription billing |
| `daphne` | ASGI server (HTTP + WebSocket) |

---

## 🗺️ Phase Roadmap

| Phase | Timeline | Features |
|-------|----------|---------|
| **Phase 1 MVP** | Months 0–3 | Auth, Listings CRUD, Search, Inquiries, Notifications |
| **Phase 2 Growth** | Months 3–6 | In-app Chat, Trust & Reviews, Smart Alerts |
| **Phase 3 Scale** | Months 6–12 | Subscriptions, Analytics, B2B, PostGIS geo-search |

---

*Built for India's growing migration economy 🇮🇳*
