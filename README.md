<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&duration=2800&pause=2000&color=4ADE80&center=true&vCenter=true&width=700&lines=Axithor+Cloud+OS;Deploy+in+Seconds.+Scale+Without+Limits.;Your+Drive.+Your+Sites.+Your+Cloud." alt="Typing SVG" />

<br/>

<a href="https://www.axithor.tech">
  <img src="https://img.shields.io/badge/🌐_axithor.tech-0d1f1a?style=for-the-badge&logoColor=4ade80" />
</a>
&nbsp;
<img src="https://img.shields.io/badge/Status-POC_Complete-4ade80?style=for-the-badge" />
&nbsp;
<img src="https://img.shields.io/badge/License-MIT-818cf8?style=for-the-badge" />
&nbsp;
<img src="https://img.shields.io/badge/Tests-73_Passing-4ade80?style=for-the-badge" />

<br/><br/>

<img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js&logoColor=white" />
<img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black" />
<img src="https://img.shields.io/badge/TailwindCSS-3-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" />
<img src="https://img.shields.io/badge/Google_Drive_API-v3-4285F4?style=flat-square&logo=google-drive&logoColor=white" />
<img src="https://img.shields.io/badge/SQLAlchemy-2.x-cc0000?style=flat-square" />
<img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white" />

<br/><br/>

> **A self-hosted static site deployment platform** — upload a ZIP, connect Google Drive, and your website is live in seconds.
>
> Built by [**Axithor**](https://www.axithor.tech) · *Engineering Business Growth with Intelligence.*

</div>

---

## ⚡ What is Axithor Cloud OS?

**Axithor Cloud OS** is a proof-of-concept cloud platform that lets you deploy static websites using **Google Drive as the storage backbone**. No AWS. No Vercel. No monthly bills. Just your Drive, your sites, your cloud.

```
You upload a ZIP  →  Backend extracts it  →  Files go to your Google Drive
Browser visits URL  →  FastAPI fetches from Drive  →  Asset served with perfect headers
```

This POC demonstrates the full deployment pipeline, a production-grade static asset serving engine, path-level security hardening, intelligent caching, and a polished dashboard — built entirely from scratch by the Axithor team.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🚀 Deploy
- **ZIP Upload** — drag & drop your built site
- **Auto folder creation** in Google Drive per site
- **Redeploy** anytime — clean wipe + re-upload
- **File validation** — only safe extensions allowed
- **50 MB** per file · **500 MB** total per deployment

</td>
<td width="50%">

### 🌐 Serve
- **Streaming delivery** — 64 KB chunks via `StreamingResponse`
- **30+ MIME types** — HTML, CSS, JS, SVG, WOFF2, AVIF and more
- **ETag + 304** — conditional GET, zero bandwidth waste
- **Immutable cache** — fonts & images cached for 1 year
- **`X-Served-By: Axithor-Edge`** on every response

</td>
</tr>
<tr>
<td width="50%">

### 🔒 Security
- **Path traversal blocked** — `../`, `%2e%2e`, `%2f`, `%5c`, null bytes
- **Google OAuth 2.0** — OIDC login + Drive OAuth (separate clients)
- **JWT sessions** — signed tokens, protected API routes
- **Input sanitization** on all file paths before DB lookup

</td>
<td width="50%">

### 🧠 Intelligence
- **Auto token refresh** — Drive tokens refreshed before expiry, zero downtime
- **SPA fallback** — `index.html` returned for unmatched routes
- **Asset Verification** — HEAD-check every deployed file with latency
- **Structured logging** via `structlog` — every request traced

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AXITHOR CLOUD OS                         │
├─────────────────┬───────────────────────────┬───────────────────┤
│   Next.js 15    │      FastAPI Backend       │   Google Drive    │
│   Frontend      │      (Python 3.12)         │   (Storage)       │
│                 │                            │                   │
│  ┌───────────┐  │  ┌──────────────────────┐  │  ┌─────────────┐ │
│  │ Dashboard │──┼─▶│  /api/v1/sites       │  │  │  Drive API  │ │
│  │ Deploy UI │  │  │  /api/v1/deploy      │──┼─▶│  v3         │ │
│  │ Verify Pg │  │  │  /api/v1/storage     │  │  │             │ │
│  └───────────┘  │  │  /serve/{sub}/{path} │  │  │  axithor-   │ │
│                 │  └──────────┬───────────┘  │  │  {subdomain}│ │
│  Auth: JWT ─────┼─────────────┘              │  │  /files...  │ │
│  (HttpOnly)     │  SQLite → Neon PG (prod)   │  └─────────────┘ │
└─────────────────┴────────────────────────────┴───────────────────┘

  Browser ──▶ GET /serve/mysite/images/hero.png
                │
           sanitize_path()  ──[unsafe]──────▶  400 HTML
                │
           resolve_site()   ──[not found]───▶  404 HTML
                │
           resolve_file()   ──[SPA mode]────▶  index.html fallback
                │
           check ETag       ──[match]───────▶  304 Not Modified
                │
           refresh token if expired
                │
           StreamingResponse(stream_drive_file())
                │
           ← Cache-Control + ETag + X-Served-By: Axithor-Edge
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15, React 19, TailwindCSS 3, TypeScript |
| **Backend** | Python 3.12, FastAPI 0.115, SQLAlchemy 2.x, Alembic |
| **Auth** | Google OAuth 2.0 (Authlib 1.7.2), JWT (python-jose) |
| **Storage** | Google Drive API v3 — multipart upload + async streaming |
| **Database** | SQLite (dev) → Neon PostgreSQL (prod) |
| **HTTP Client** | httpx (async, 64 KB streaming chunks) |
| **Logging** | structlog |
| **Testing** | pytest, pytest-asyncio, FastAPI TestClient |
| **Container** | Docker + Docker Compose + Nginx reverse proxy |

---

## 📁 Project Structure

```
axithor-cloud-os/
├── backend/
│   ├── app/
│   │   ├── api/v1/routes/
│   │   │   ├── auth.py          # Google OIDC login + JWT cookies
│   │   │   ├── sites.py         # Site CRUD
│   │   │   ├── deploy.py        # ZIP upload & Drive deployment
│   │   │   ├── storage.py       # Drive OAuth + token management
│   │   │   └── serve.py         # ★ Static asset engine
│   │   ├── services/
│   │   │   ├── asset_resolution_service.py  # path security, cache, streaming
│   │   │   ├── deployment_service.py        # ZIP → Drive pipeline
│   │   │   ├── subdomain_service.py         # subdomain → site → file
│   │   │   ├── google_drive_service.py      # Drive API wrapper
│   │   │   └── google_drive_storage_service.py  # token refresh
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── repositories/        # DB access layer
│   │   ├── schemas/             # Pydantic request/response models
│   │   └── utils/
│   │       └── mime_types.py    # 30+ extension MIME registry
│   ├── alembic/versions/        # 5 migrations (SQLite batch mode)
│   └── tests/
│       ├── conftest.py
│       ├── test_mime_types.py        # 24 tests
│       ├── test_asset_resolution.py  # 22 tests
│       └── test_serve_api.py         # 9 integration tests
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── dashboard/
│       │   │   └── sites/[id]/
│       │   │       ├── page.tsx       # Site detail + deploy
│       │   │       └── verify/        # Asset verification page
│       │   └── auth/                  # Login page
│       ├── components/
│       │   └── SiteForm.tsx           # Create site modal
│       └── lib/
│           └── api.ts                 # Authenticated fetch wrapper
├── nginx/
│   └── nginx.conf                     # Reverse proxy config
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Google Cloud Console project with OAuth 2.0 credentials

### 1. Clone

```bash
git clone https://github.com/jayaprakash2207/AXITHOR-CLOUD-OS-POC.git
cd AXITHOR-CLOUD-OS-POC
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your values
```

```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_DRIVE_REDIRECT_URI=http://localhost:8000/api/v1/storage/google/callback
SECRET_KEY=your_jwt_secret_minimum_32_chars
DATABASE_URL=sqlite:///./axithor.db
FRONTEND_BASE_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / Mac

pip install -e .
python -m alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 5. Run tests

```bash
cd backend
python -m pytest tests/ -v
```

```
tests/test_mime_types.py        24 tests  ✅
tests/test_asset_resolution.py  22 tests  ✅
tests/test_serve_api.py          9 tests  ✅
─────────────────────────────────────────
TOTAL                           73 tests  ✅ All passing
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/auth/google/login` | Initiate Google OIDC login |
| `GET` | `/api/v1/auth/me` | Get current user |
| `GET` | `/api/v1/sites` | List all sites |
| `POST` | `/api/v1/sites` | Create a new site |
| `GET` | `/api/v1/sites/{id}` | Get site details |
| `POST` | `/api/v1/deploy/{site_id}` | Deploy ZIP to site |
| `GET` | `/api/v1/sites/{id}/files` | List deployed files |
| `GET` | `/api/v1/storage/google/login` | Connect Google Drive |
| `GET` | `/api/v1/storage/me` | Drive account info |
| `GET` | `/api/v1/storage/usage` | Drive quota & metadata |
| `GET` | `/serve/{subdomain}/{path}` | **Serve static asset** |

---

## 🛡️ Security Hardening

The `/serve/` endpoint rejects malicious paths before any DB lookup:

```
# All blocked — return 400 Bad Request:
/serve/mysite/../../../etc/passwd     ← directory traversal
/serve/mysite/%2e%2e/secret           ← URL-encoded dot-dot
/serve/mysite/file.html%00.php        ← null byte injection
/serve/mysite/css%2fstyle.css         ← encoded slash smuggling
/serve/mysite/css\style.css           ← Windows path separator
```

---

## 🗺️ Roadmap

- [x] Google OAuth login (OIDC)
- [x] Google Drive integration + token auto-refresh
- [x] ZIP deployment pipeline
- [x] Static asset serving engine with streaming
- [x] ETag / 304 / Cache-Control headers
- [x] Path security hardening (9 attack vectors blocked)
- [x] Asset verification dashboard
- [x] 73 unit + integration tests
- [ ] Wildcard DNS + Nginx (`{subdomain}.axithor.tech`)
- [ ] Custom domain support
- [ ] Multi-user isolation
- [ ] Drive file cleanup on redeploy
- [ ] Rate limiting on serve endpoint
- [ ] PostgreSQL production setup
- [ ] S3 / GCS alternate storage backend
- [ ] Usage analytics per site
- [ ] Webhook-driven auto-redeploy from Drive changes
- [ ] CDN edge layer

---

## 🏢 About Axithor

<div align="center">

**[Axithor](https://www.axithor.tech)** is an AI-powered growth studio.

We build intelligent systems, scalable products, and compounding growth engines for modern businesses that refuse to be ordinary.

*Engineering Business Growth with Intelligence.*

<br/>

<a href="https://www.axithor.tech">
  <img src="https://img.shields.io/badge/🌐_Website-axithor.tech-4ade80?style=for-the-badge" />
</a>

</div>

---

<div align="center">

Built with ❤️ by **Axithor** &nbsp;·&nbsp; © 2026 Axithor Groups &nbsp;·&nbsp;
<img src="https://img.shields.io/badge/Made_in-India_🇮🇳-FF9933?style=flat-square" />

</div>
