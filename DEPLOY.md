# Deployment Guide

This project is split across two providers:

| Layer | Provider | What's deployed |
|-------|----------|------------------|
| Frontend (React + Vite) | **Vercel** | Static SPA built from `frontend/` |
| Backend (Django + FastAPI) | **Render** | Two web services + a Postgres database |

The deploy order matters because each side needs the other's URL:

1. Deploy the Render backend first → get the gateway URL.
2. Deploy Vercel with `VITE_API_URL` pointing at the Render gateway → get the Vercel URL.
3. Set `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `FRONTEND_URL` on Render to the Vercel URL.
4. Trigger a Render redeploy so the new origins take effect.

---

## 1. Push the repo

```bash
git push origin master
```

The repo lives at `github.com/yokesh-kumar-M/Online_compiler` and contains
everything (backend, frontend, executor, Dockerfiles, `render.yaml`,
`frontend/vercel.json`).

---

## 2. Deploy the backend on Render (Blueprint)

1. Open https://dashboard.render.com → **New** → **Blueprint**.
2. Connect the GitHub repo `yokesh-kumar-M/Online_compiler`.
3. Render reads `render.yaml` and proposes three resources:
   - `online-compiler-db` — free Postgres
   - `online-compiler-gateway` — Django (Docker)
   - `online-compiler-executor` — FastAPI executor (Docker)
4. Click **Apply**. First build takes 5–10 minutes (the executor image
   downloads JDK / Node / Go).
5. After both services are **Live**, copy the gateway URL — it looks like
   `https://online-compiler-gateway-XXXX.onrender.com`.

Smoke-test the gateway:

```bash
curl https://online-compiler-gateway-XXXX.onrender.com/health/
# -> {"status":"healthy"}

curl https://online-compiler-gateway-XXXX.onrender.com/
# -> {"service":"online-compiler-gateway","status":"ok",...}
```

### Already have services from a previous attempt?

Render Blueprints create **new** services rather than adopting existing ones.
If your old `online-compiler-gateway-fotz` and `online-compiler-executor-cypu`
are still in the dashboard:
- **Either** delete them first, then run the Blueprint above (clean start), or
- Skip the Blueprint, open each existing service, point it at this repo, and
  paste the env vars below by hand.

Manual env vars for the **gateway** service:

```
DJANGO_SECRET_KEY     = <generate, 50+ chars>
DJANGO_DEBUG          = False
DJANGO_ALLOWED_HOSTS  = .onrender.com,localhost
RENDER                = true
DATABASE_URL          = <internal connection string from the Postgres service>
JWT_SECRET_KEY        = <generate, 50+ chars>
EXECUTOR_API_KEY      = <generate, 50+ chars — paste the same value into the executor>
EXECUTOR_SERVICE_URL  = <executor service hostname, e.g. online-compiler-executor-cypu.onrender.com>
CORS_ALLOWED_ORIGINS  = https://your-app.vercel.app           # set after step 3
CSRF_TRUSTED_ORIGINS  = https://your-app.vercel.app           # set after step 3
FRONTEND_URL          = https://your-app.vercel.app           # set after step 3
LOG_LEVEL             = WARNING
```

Manual env vars for the **executor** service:

```
EXECUTOR_API_KEY        = <same value as gateway>
CODE_EXECUTION_TIMEOUT  = 10
MAX_OUTPUT_SIZE         = 10000
LOG_LEVEL               = WARNING
```

Build / runtime settings (manual mode only):
- Both services use **Docker** runtime.
- Gateway: dockerfile `./Dockerfile`, context `.`, health check `/health/`.
- Executor: root dir `services/executor`, dockerfile `./Dockerfile`, context `.`, health check `/health`.

---

## 3. Deploy the frontend on Vercel

1. Open https://vercel.com/new and import `yokesh-kumar-M/Online_compiler`.
2. Configure the project:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite (auto-detected)
   - **Build / Output / Install commands**: auto from `vercel.json`
3. Add an environment variable (Production + Preview):

   ```
   VITE_API_URL = https://online-compiler-gateway-XXXX.onrender.com/api/v1
   ```

   Use the gateway URL from step 2, and **include `/api/v1` at the end**.

4. Click **Deploy**. After ~2 minutes, copy your Vercel URL
   (e.g. `https://online-compiler.vercel.app`).

---

## 4. Wire CORS / CSRF back to Render

On the **gateway** service in Render → **Environment** tab, set:

```
CORS_ALLOWED_ORIGINS = https://online-compiler.vercel.app
CSRF_TRUSTED_ORIGINS = https://online-compiler.vercel.app
FRONTEND_URL         = https://online-compiler.vercel.app
```

Save → Render auto-redeploys. The Django settings already include a regex
that allows any `*.vercel.app` origin, so preview deploys work without extra
configuration.

---

## 5. Verify end-to-end

1. Open the Vercel URL — login / register screen should load.
2. In DevTools → Network, register a new account → the request should hit
   `https://<gateway>.onrender.com/api/v1/auth/register/` with **200** and
   **no CORS error**.
3. Log in, paste a Python snippet, click Run — the executor should respond.
4. Hit `https://<gateway>.onrender.com/api/docs/` for the Swagger UI.

---

## Local development

Backend (Docker Compose, with Postgres + Redis + executor):

```bash
cp .env.example .env
# edit .env
docker-compose up -d --build
```

Frontend (separate terminal):

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
# vite proxies /api/v1 to localhost:8000 via vite.config.js
```

---

## Environment variables reference

| Variable | Where | Description |
|----------|-------|-------------|
| `VITE_API_URL` | Vercel | Full URL of the Render gateway API, including `/api/v1` |
| `DJANGO_SECRET_KEY` | Render gateway | Django secret key |
| `DJANGO_DEBUG` | Render gateway | `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Render gateway | Comma-separated hostnames |
| `DATABASE_URL` | Render gateway | Postgres connection string (auto-wired by Blueprint) |
| `JWT_SECRET_KEY` | Render gateway | JWT signing key |
| `EXECUTOR_SERVICE_URL` | Render gateway | Executor hostname (auto-wired by Blueprint) |
| `EXECUTOR_API_KEY` | Both Render services | Shared API key (auto-wired by Blueprint) |
| `CORS_ALLOWED_ORIGINS` | Render gateway | Comma-separated Vercel origins |
| `CSRF_TRUSTED_ORIGINS` | Render gateway | Comma-separated Vercel origins |
| `FRONTEND_URL` | Render gateway | Vercel URL (shown on root JSON response) |
| `LOG_LEVEL` | Both Render services | `WARNING` recommended for free tier |
| `RENDER` | Render gateway | `true` — enables Render-specific code paths |

---

## Troubleshooting

**Render gateway 502 / "service unavailable" after deploy** — first request
spins the free-tier container up from cold; wait 30–60 seconds and retry.

**Frontend can hit `/health/` but `/api/v1/*` returns CORS error** — the
`CORS_ALLOWED_ORIGINS` env var on the gateway doesn't match your Vercel
origin exactly. Must be the full scheme+host with no trailing slash.

**Executor service errors with `EXECUTOR_SERVICE_URL` unreachable** — confirm
the gateway has `EXECUTOR_SERVICE_URL` set; check Render's Blueprint sync
panel for any failed env-var resolutions between services.

**"Compilation error: gcc: command not found"** — you're hitting an old
executor image. Re-deploy the executor service so it rebuilds with the new
Dockerfile that installs gcc, g++, javac, node, and go.

**Vercel build fails with peer-dep conflict** — `vercel.json` sets
`installCommand` to `npm install --legacy-peer-deps`; make sure you didn't
override "Install Command" in the Vercel dashboard.

**429 / "too many requests" during testing** — the gateway has rate limits
(20/hour anon, 100/hour user). Bump via `RATE_LIMIT_ANONYMOUS` /
`RATE_LIMIT_AUTHENTICATED` env vars.
