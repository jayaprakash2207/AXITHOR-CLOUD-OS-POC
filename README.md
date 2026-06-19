<!-- TOP WAVE BANNER -->
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1f1a,50:0a3d2e,100:4ade80&height=200&section=header&text=AXITHOR%20CLOUD%20OS&fontSize=52&fontColor=4ade80&fontAlignY=38&animation=fadeIn&desc=Deploy%20in%20Seconds.%20Scale%20Without%20Limits.&descSize=18&descAlignY=60&descFontColor=ffffff80" />

<div align="center">

<!-- ANIMATED TYPING -->
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=22&duration=3000&pause=1500&color=4ADE80&center=true&vCenter=true&multiline=false&width=600&lines=🚀+Upload+a+ZIP+→+Your+site+goes+live;☁️+Google+Drive+is+your+storage+backend;🔒+Zero+config.+Zero+AWS.+Zero+bills.;⚡+Built+by+Axithor+—+axithor.tech" alt="Typing SVG" />

<br/><br/>

<!-- STATUS BADGES -->
[![Status](https://img.shields.io/badge/🟢_Status-POC_Complete-4ade80?style=for-the-badge)](https://github.com/jayaprakash2207/AXITHOR-CLOUD-OS-POC)
[![Tests](https://img.shields.io/badge/✅_Tests-73_Passing-4ade80?style=for-the-badge)](https://github.com/jayaprakash2207/AXITHOR-CLOUD-OS-POC)
[![License](https://img.shields.io/badge/📄_License-MIT-818cf8?style=for-the-badge)](LICENSE)
[![Made In](https://img.shields.io/badge/🇮🇳_Made_in-India-FF9933?style=for-the-badge)](https://www.axithor.tech)

<br/>

<!-- WEBSITE BADGE -->
<a href="https://www.axithor.tech">
<img src="https://img.shields.io/badge/🌐_www.axithor.tech-Visit_Us-4ade80?style=for-the-badge&labelColor=0d1f1a" />
</a>

<br/><br/>

<!-- TECH STACK ICONS -->
<img src="https://skillicons.dev/icons?i=python,fastapi,nextjs,react,ts,tailwind,docker,nginx,postgres,git&theme=dark&perline=10" />

</div>

<br/>

---

## <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=2000&pause=99999&color=4ADE80&vCenter=true&width=280&lines=⚡+What+is+Axithor+Cloud+OS?" alt="" />

<div align="center">

> **A self-hosted static site deployment platform where Google Drive is your cloud.**
> Upload a ZIP. Connect your Drive. Your website is live — instantly.

</div>

```
📦 ZIP Upload  →  🔍 Validate  →  ☁️ Google Drive  →  🌐 Live Site
     │                  │                 │                   │
  Extract files    Check extensions   Upload files      Serve assets
  Strip root dir   50MB per file      Per-site folder   with perfect
  Compute SHA256   500MB total        Streaming API     HTTP headers
```

<br/>

---

## ✨ Features

<div align="center">
<table>
<tr>
<td align="center" width="25%">

<img width="60" src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=40&duration=99999&pause=99999&color=4ADE80&center=true&vCenter=true&width=60&height=60&lines=🚀" />

**Deploy**

ZIP upload → Drive in seconds<br/>
Auto Drive folder per site<br/>
Redeploy anytime (clean wipe)<br/>
50MB/file · 500MB total

</td>
<td align="center" width="25%">

<img width="60" src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=40&duration=99999&pause=99999&color=818cf8&center=true&vCenter=true&width=60&height=60&lines=🌐" />

**Serve**

64 KB streaming chunks<br/>
30+ MIME types supported<br/>
ETag + 304 (zero bandwidth)<br/>
Immutable cache for assets

</td>
<td align="center" width="25%">

<img width="60" src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=40&duration=99999&pause=99999&color=f472b6&center=true&vCenter=true&width=60&height=60&lines=🔒" />

**Security**

Path traversal blocked<br/>
Null byte injection blocked<br/>
Encoded attack vectors blocked<br/>
JWT-protected API routes

</td>
<td align="center" width="25%">

<img width="60" src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=40&duration=99999&pause=99999&color=fb923c&center=true&vCenter=true&width=60&height=60&lines=🧠" />

**Intelligence**

Auto token refresh before expiry<br/>
SPA fallback (index.html)<br/>
Per-asset verification page<br/>
Structured logging (structlog)

</td>
</tr>
</table>
</div>

<br/>

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          AXITHOR CLOUD OS                                │
│                                                                          │
│   ┌─────────────────┐       ┌──────────────────────┐    ┌────────────┐  │
│   │   Next.js 15    │       │   FastAPI Backend     │    │  Google    │  │
│   │   + React 19    │◄─────►│   Python 3.12        │◄──►│   Drive   │  │
│   │   + Tailwind    │  JWT  │   SQLAlchemy 2.x      │    │   API v3  │  │
│   └─────────────────┘       └──────────┬───────────┘    └────────────┘  │
│                                        │                                 │
│   Routes handled:                      │  DB: SQLite (dev)               │
│   ├── /dashboard          ◄────────────┤      Neon PG (prod)             │
│   ├── /dashboard/sites    ◄────────────┤                                 │
│   └── /dashboard/verify   ◄────────────┘                                 │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                  ASSET SERVING PIPELINE                         │   │
│   │                                                                 │   │
│   │  GET /serve/{subdomain}/{path}                                  │   │
│   │       │                                                         │   │
│   │  [1] sanitize_path()   ──bad──► 400 HTML (styled error page)   │   │
│   │       │                                                         │   │
│   │  [2] resolve_site()    ──miss──► 404 HTML                      │   │
│   │       │                                                         │   │
│   │  [3] resolve_file()    ──miss──► index.html (SPA fallback)     │   │
│   │       │                                                         │   │
│   │  [4] check ETag        ──hit───► 304 Not Modified (no body)    │   │
│   │       │                                                         │   │
│   │  [5] refresh token if expired (proactive, zero-downtime)        │   │
│   │       │                                                         │   │
│   │  [6] StreamingResponse(stream_drive_file(), 64KB chunks)        │   │
│   │       │                                                         │   │
│   │       └──► Cache-Control + ETag + Vary + X-Served-By: Axithor  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

<br/>

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|:---:|:---|:---|
| 🖥️ **Frontend** | Next.js 15 · React 19 · TypeScript · TailwindCSS | Dashboard, deploy UI, asset verification |
| ⚙️ **Backend** | Python 3.12 · FastAPI · SQLAlchemy 2.x · Alembic | API, deployment engine, asset server |
| 🔐 **Auth** | Google OAuth 2.0 (Authlib) · JWT (python-jose) | OIDC login + Drive access (separate clients) |
| ☁️ **Storage** | Google Drive API v3 | Multipart upload · async streaming · 64KB chunks |
| 🗄️ **Database** | SQLite (dev) → Neon PostgreSQL (prod) | Sites, files, deployments, storage accounts |
| 🌐 **HTTP** | httpx (async) | Drive streaming, token refresh |
| 📦 **Container** | Docker · Docker Compose · Nginx | Reverse proxy, local orchestration |
| 🧪 **Testing** | pytest · pytest-asyncio · FastAPI TestClient | 73 tests across 3 suites |

</div>

<br/>

---

## 📁 Project Structure

```
AXITHOR-CLOUD-OS-POC/
│
├── 🐍 backend/
│   ├── app/
│   │   ├── api/v1/routes/
│   │   │   ├── auth.py           ← Google OIDC login + JWT cookies
│   │   │   ├── sites.py          ← Site CRUD (create, list, detail)
│   │   │   ├── deploy.py         ← ZIP upload → Drive pipeline
│   │   │   ├── storage.py        ← Drive OAuth + token lifecycle
│   │   │   └── serve.py          ← ⭐ Static asset engine (Module 4.5)
│   │   │
│   │   ├── services/
│   │   │   ├── asset_resolution_service.py  ← path security, cache, ETag
│   │   │   ├── deployment_service.py        ← ZIP → validate → Drive
│   │   │   ├── subdomain_service.py         ← subdomain → site → file
│   │   │   ├── google_drive_service.py      ← Drive API wrapper
│   │   │   └── google_drive_storage_service.py  ← token refresh
│   │   │
│   │   ├── models/               ← SQLAlchemy ORM (User, Site, WebsiteFile…)
│   │   ├── repositories/         ← DB access layer
│   │   ├── schemas/              ← Pydantic request/response models
│   │   └── utils/mime_types.py   ← 30+ extension MIME registry
│   │
│   ├── alembic/versions/         ← 5 migrations (SQLite batch mode)
│   └── tests/
│       ├── test_mime_types.py         ← 24 tests
│       ├── test_asset_resolution.py   ← 22 tests (security + headers)
│       └── test_serve_api.py          ← 9 integration tests
│
├── ⚛️ frontend/src/
│   ├── app/
│   │   ├── dashboard/            ← Main dashboard + site list
│   │   │   └── sites/[id]/
│   │   │       ├── page.tsx      ← Site detail + ZIP deploy
│   │   │       └── verify/       ← ⭐ Asset verification dashboard
│   │   └── login/                ← Google sign-in page
│   ├── components/SiteForm.tsx   ← Create site modal (auto-slug)
│   └── lib/api.ts                ← JWT-aware fetch wrapper
│
├── 🐋 nginx/nginx.conf           ← Reverse proxy config
├── docker-compose.yml
└── README.md
```

<br/>

---

## 🚀 Quick Start

### Prerequisites

- Python **3.12+**
- Node.js **18+**
- [Google Cloud Console](https://console.cloud.google.com) — OAuth 2.0 credentials (Web Application)

<br/>

### 1️⃣ Clone

```bash
git clone https://github.com/jayaprakash2207/AXITHOR-CLOUD-OS-POC.git
cd AXITHOR-CLOUD-OS-POC
```

### 2️⃣ Environment

```bash
cp .env.example .env
```

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_DRIVE_REDIRECT_URI=http://localhost:8000/api/v1/storage/google/callback
SECRET_KEY=your_32_char_minimum_secret_key_here
DATABASE_URL=sqlite:///./axithor.db
FRONTEND_BASE_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

### 3️⃣ Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -e .
python -m alembic upgrade head
uvicorn app.main:app --reload --port 8000
# ✅ API  →  http://localhost:8000
# ✅ Docs →  http://localhost:8000/docs
```

### 4️⃣ Frontend

```bash
cd frontend
npm install
npm run dev
# ✅ Dashboard → http://localhost:3000
```

### 5️⃣ Test Suite

```bash
cd backend
python -m pytest tests/ -v
```

```
tests/test_mime_types.py        ████████████████████  24/24  ✅
tests/test_asset_resolution.py  ████████████████████  22/22  ✅
tests/test_serve_api.py         ████████████████████   9/9   ✅
─────────────────────────────────────────────────────────────
TOTAL                                                 73/73  ✅ All passing
```

<br/>

---

## 🔌 API Reference

<div align="center">

| Method | Endpoint | Auth | Description |
|:---:|:---|:---:|:---|
| `GET` | `/api/v1/auth/google/login` | ❌ | Initiate Google OIDC sign-in |
| `GET` | `/api/v1/auth/me` | ✅ | Current user profile |
| `GET` | `/api/v1/sites` | ✅ | List all sites |
| `POST` | `/api/v1/sites` | ✅ | Create a new site |
| `GET` | `/api/v1/sites/{id}` | ✅ | Site details |
| `POST` | `/api/v1/deploy/{site_id}` | ✅ | **Deploy ZIP to site** |
| `GET` | `/api/v1/sites/{id}/files` | ✅ | List deployed files |
| `GET` | `/api/v1/storage/google/login` | ✅ | Connect Google Drive |
| `GET` | `/api/v1/storage/me` | ✅ | Drive account info |
| `GET` | `/api/v1/storage/usage` | ✅ | Quota + Drive metadata |
| `GET` | `/serve/{subdomain}/{path}` | ❌ | **⭐ Serve static asset** |

</div>

<br/>

---

## 🛡️ Security Hardening

The `/serve/` endpoint sanitizes **every** request before touching the database:

<div align="center">

| Attack Vector | Example | Result |
|:---|:---|:---:|
| Directory traversal | `/serve/site/../../../etc/passwd` | `400` |
| URL-encoded dot-dot | `/serve/site/%2e%2e/secret` | `400` |
| Null byte injection | `/serve/site/file.html%00.php` | `400` |
| Encoded slash | `/serve/site/css%2fstyle.css` | `400` |
| Windows separator | `/serve/site/css\style.css` | `400` |
| Encoded backslash | `/serve/site/css%5cstyle.css` | `400` |
| Unknown subdomain | `/serve/doesnotexist/` | `404` |
| No storage connected | *(Drive disconnected)* | `503` |

</div>

All error responses return **styled dark-mode HTML pages** — never raw JSON errors in the browser.

<br/>

---

## 🗺️ Roadmap

<div align="center">

```
DONE ████████████████████████████████████████ v0.1 POC
NEXT ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ v1.0 Production
```

</div>

**✅ Completed — POC**
- [x] Google OAuth 2.0 login (OIDC) + JWT session management
- [x] Google Drive OAuth — separate client, no OIDC conflicts
- [x] ZIP deployment pipeline with file validation
- [x] Static asset serving engine — streaming, MIME, ETag, Cache-Control
- [x] Path security hardening — 8 attack vectors blocked
- [x] Proactive token refresh — zero-downtime after 1-hour expiry
- [x] Asset verification dashboard with per-file HEAD checks + latency
- [x] Styled HTML error pages (400, 404, 500, 503)
- [x] 73 unit + integration tests — all passing
- [x] Docker + Nginx setup

**🔲 Planned — v1.0 Production**
- [ ] Wildcard DNS + Nginx → `{subdomain}.axithor.tech`
- [ ] Custom domain support with SSL
- [ ] Multi-user isolation (per-user Drive token + site scoping)
- [ ] Drive file cleanup on redeploy
- [ ] Rate limiting on `/serve/` endpoint
- [ ] PostgreSQL production setup (Neon)
- [ ] S3 / GCS alternate storage backend
- [ ] Usage analytics per site
- [ ] Webhook auto-redeploy from Drive file changes
- [ ] CDN edge layer for global distribution

<br/>

---

## 🏢 About Axithor

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=16&duration=3000&pause=1000&color=4ADE80&center=true&vCenter=true&width=540&lines=Engineering+Business+Growth+with+Intelligence;AI+%7C+Automation+%7C+Web+Dev+%7C+Consulting;50%2B+Projects+·+3×+Avg+ROI+·+98%25+Satisfaction" />

<br/>

**[Axithor](https://www.axithor.tech)** is an AI-powered growth studio — we build intelligent systems, scalable products, and compounding growth engines for modern businesses that refuse to be ordinary.

<br/>

| | Service | Description |
|:---:|:---|:---|
| 🤖 | **AI & Automation** | Intelligent systems embedded into your operations |
| 💻 | **Web & App Dev** | Production-grade products, MVPs to enterprise |
| 📈 | **Digital Marketing** | AI-optimised campaigns for maximum ROI |
| 🎯 | **Business Consulting** | Strategy from operators who've scaled companies |

<br/>

[![Website](https://img.shields.io/badge/🌐_Website-axithor.tech-4ade80?style=for-the-badge&labelColor=0d1f1a)](https://www.axithor.tech)
[![GitHub](https://img.shields.io/badge/GitHub-AXITHOR--CLOUD--OS--POC-181717?style=for-the-badge&logo=github)](https://github.com/jayaprakash2207/AXITHOR-CLOUD-OS-POC)

</div>

<br/>

---

<div align="center">
<sub>Built with ❤️ by <strong>Axithor</strong> &nbsp;·&nbsp; © 2026 Axithor Groups &nbsp;·&nbsp; <img src="https://img.shields.io/badge/Made_in-India_🇮🇳-FF9933?style=flat-square" /></sub>
</div>

<!-- BOTTOM WAVE -->
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:4ade80,50:0a3d2e,100:0d1f1a&height=120&section=footer" />
