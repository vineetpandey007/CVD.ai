# code-vuln-detector — Setup & Deployment Guide

What this is: a website that takes a code snippet, runs it through a
pretrained CodeBERT vulnerability-detection checkpoint *and* Bandit/Semgrep
static analysis, and returns a merged report (vulnerable/not, CWE type,
confidence, line-level findings). No model training involved — the
checkpoint is used as-is. No Docker — backend runs as a plain Python
process, frontend is a static build.

## 1. Prerequisites

- Python 3.11+
- Node 20+
- git

## 2. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
```
DUCKDB_PATH=../data/app.duckdb
MODEL_CHECKPOINT=mrm8488/codebert-base-finetuned-detect-insecure-code
ALLOWED_ORIGINS=http://localhost:5173
```

Run it:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The database file is created automatically on first startup (`init_db()`
in `app/db.py`) — nothing to run manually. First request will also be
slow while the model checkpoint downloads from Hugging Face Hub; it's
cached locally after that.

**Do not run this with `--workers > 1`.** DuckDB allows only one
read-write connection to the database file at a time, across OS
processes — multiple uvicorn workers will fight over the file. One
process is the right choice at this project's scale anyway.

## 3. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
```

Edit `.env`:
```
VITE_API_URL=http://localhost:8000
```

```bash
npm run dev
```

## 4. Testing

```bash
# backend
cd backend && pytest

# frontend
cd frontend && npm test
```

Also worth doing manually before every release: run Bandit and Semgrep
against this repo's own code (the `self-scan.yml` CI workflow does this
automatically on every PR too).

## 5. Deployment — two paths

### Path A: Render / Vercel (recommended, matches the 7-day roadmap)

- **Backend → Render**, native Python web service, no Docker:
  - Build command: `pip install -r backend/requirements.txt`
  - Start command: reads `Procfile` at repo root, or set directly:
    `uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir backend`
  - Set the same env vars from step 2 in Render's dashboard
  - Attach a persistent disk for `DUCKDB_PATH` — Render's default
    filesystem is ephemeral and the database file would reset on every
    deploy otherwise
- **Frontend → Vercel**, auto-deploys from the `frontend/` directory,
  set `VITE_API_URL` to the deployed Render backend URL
- **DDoS/edge protection:** add your domain to Cloudflare (free tier),
  DNS-proxy mode, enable the free managed WAF ruleset — this covers what
  a platform-hosted deploy doesn't (see `docs/security-hardening.md`)

### Path B: Self-hosted VPS

- Clone the repo to `/opt/code-vuln-detector`, set up the venv as in
  step 2 inside `backend/.venv`
- Install and enable the systemd unit:
  ```bash
  sudo cp deploy/backend.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable --now backend
  ```
- Install nginx on the host (`apt install nginx` / `dnf install nginx`,
  not a container), use `nginx/nginx.conf` as the site config, build the
  frontend (`npm run build` in `frontend/`) and point nginx's `root` at
  `frontend/dist`
- Get a TLS cert (certbot/Let's Encrypt), uncomment the HTTPS redirect
  and HSTS header in `nginx.conf`
- Cloudflare in front of the VPS's public IP for real DDoS coverage —
  nginx rate limiting alone only stops application-layer abuse, not
  volumetric attacks (see `docs/security-hardening.md` for the full
  reasoning)

## 6. Security checklist before going public

- [ ] `shell=False`, argv-list subprocess calls in `bandit_runner.py` / `semgrep_runner.py`
- [ ] Generated (not user-derived) temp file paths, with guaranteed cleanup
- [ ] Subprocess timeout set
- [ ] `slowapi` rate limiting active on `/api/analyze`
- [ ] Request body size capped (nginx `client_max_body_size` or FastAPI validation)
- [ ] Cloudflare (or equivalent) in front of the public domain
- [ ] Security headers set (CSP, X-Frame-Options, X-Content-Type-Options)
- [ ] `SECURITY.md` disclosure policy published
- [ ] ORM/parameterized queries only for any new DB fields (already the
      pattern in `app/models.py`)
- [ ] `NOTICE.md` credits the model checkpoint's license and source

Full detail on every item: `docs/security-hardening.md`.

## 7. Repo map — where things live

| Concern | Location |
|---|---|
| API routes | `backend/app/routes/` |
| Model loading + inference | `backend/app/inference/` |
| Bandit/Semgrep wrappers | `backend/app/static_analysis/` |
| DuckDB + SQLAlchemy setup | `backend/app/db.py` |
| Scan history model/queries | `backend/app/models.py` |
| CWE name lookup | `backend/app/cwe/cwe_lookup.json` |
| Frontend pages | `frontend/src/pages/` |
| Frontend API client | `frontend/src/api/client.ts` |
| Reverse proxy (self-host only) | `nginx/nginx.conf` |
| systemd unit (self-host only) | `deploy/backend.service` |
| Render deploy target | `Procfile` |
| Sample vulnerable/safe code | `examples/` |
| Architecture, model card, roadmap | `docs/` |

## 8. Known limitations (be upfront about these in your README)

- Single-checkpoint model — accuracy is whatever the public checkpoint
  achieves on its own training distribution (mostly Devign/BigVul, C/C++
  and general-purpose code); it wasn't fine-tuned on your own data
- Single-process backend — a deliberate DuckDB constraint, fine at this
  scale, worth calling out as a scaling limitation rather than an oversight
- No sandboxed code execution — the app only *analyzes* code statically,
  it never runs submitted code, which is why there's no RCE surface today;
  don't add a "run this code" feature without a real sandboxing plan
  (gVisor/Firecracker), it's a different risk class entirely
