# Deployment Guide - Online Compiler Enterprise

## Render.com (RECOMMENDED - Full Stack)

Render is the **recommended platform** for this project. It supports all services:

### One-Click Deploy via Blueprint

1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **"New" → "Blueprint"**
4. Connect your GitHub repo: `yokesh-kumar-M/Online_compiler`
5. Render auto-detects `render.yaml` and creates:
   - **PostgreSQL database** (free tier)
   - **Django Gateway** web service (free tier)
   - **FastAPI Executor** Docker service (free tier)
6. All environment variables are auto-configured
7. Click **"Apply"** and wait ~5 minutes

### Manual Deploy on Render

#### Service 1: PostgreSQL Database
1. Dashboard → New → PostgreSQL
2. Name: `online-compiler-db`
3. Plan: Free
4. Copy the **Internal Database URL**

#### Service 2: Django Gateway
1. Dashboard → New → Web Service
2. Connect GitHub repo
3. Settings:
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn online_compiler.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120`
   - **Root Directory**: `online_compiler`
4. Environment Variables:
   ```
   DJANGO_SECRET_KEY    = <click Generate>
   DJANGO_DEBUG         = False
   DJANGO_ALLOWED_HOSTS = .onrender.com
   RENDER               = true
   DATABASE_URL         = <paste Internal Database URL>
   JWT_SECRET_KEY       = <click Generate>
   EXECUTOR_API_KEY     = <click Generate>
   EXECUTOR_SERVICE_URL = <executor service URL from step 3>
   LOG_LEVEL            = WARNING
   CORS_ALLOWED_ORIGINS = https://your-gateway.onrender.com
   CSRF_TRUSTED_ORIGINS = https://your-gateway.onrender.com
   ```

#### Service 3: FastAPI Executor
1. Dashboard → New → Web Service
2. Connect same repo
3. Settings:
   - **Docker** runtime
   - **Dockerfile Path**: `./services/executor/Dockerfile`
   - **Docker Context**: `./services/executor`
   - **Root Directory**: `online_compiler`
4. Environment Variables:
   ```
   EXECUTOR_API_KEY      = <same key as gateway>
   CODE_EXECUTION_TIMEOUT = 10
   MAX_OUTPUT_SIZE        = 10000
   ```

### After Deploy
- **Web App**: `https://your-gateway.onrender.com`
- **API Docs**: `https://your-gateway.onrender.com/api/docs/`
- **Admin**: `https://your-gateway.onrender.com/admin/`
- **Health**: `https://your-gateway.onrender.com/health/`

---

## Vercel (NOT RECOMMENDED for Django)

> **WARNING**: Vercel is a **serverless/frontend** platform. Django has severe
> limitations on Vercel:
> - 10-second function timeout (code execution WILL fail)
> - No persistent file system
> - No background workers (Celery won't work)
> - No managed PostgreSQL/Redis
> - Cold starts on every request

### When to Use Vercel
Only if you have a **separate frontend** (React/Next.js) that calls the
Render-hosted Django API. In that case:
- Deploy frontend on Vercel
- Point API calls to `https://your-gateway.onrender.com/api/`

### If You MUST Deploy Django on Vercel (Demo Only)
1. Install Vercel CLI: `npm i -g vercel`
2. You need an **external PostgreSQL** (e.g., Neon, Supabase)
3. Set environment variables on Vercel dashboard
4. Run: `cd online_compiler && vercel --prod`
5. Note: Code execution will NOT work due to timeout limits

---

## Docker Compose (Self-Hosted / VPS)

```bash
cd online_compiler
cp .env.production .env
# Edit .env with your production values
docker-compose up -d --build
```

Services: PostgreSQL, Redis, Django Gateway, FastAPI Executor,
Celery Worker, Celery Beat, Nginx reverse proxy.

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DJANGO_SECRET_KEY` | Yes | Django secret key (50+ chars) |
| `DJANGO_DEBUG` | Yes | `False` for production |
| `DJANGO_ALLOWED_HOSTS` | Yes | Comma-separated hostnames |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | No | Redis URL (for caching/Celery) |
| `JWT_SECRET_KEY` | Yes | JWT signing key |
| `EXECUTOR_SERVICE_URL` | Yes | FastAPI executor URL |
| `EXECUTOR_API_KEY` | Yes | Shared API key for executor auth |
| `CORS_ALLOWED_ORIGINS` | Yes | Allowed CORS origins |
| `CSRF_TRUSTED_ORIGINS` | Yes | Trusted CSRF origins |
| `RENDER` | Auto | Set by Render.com |
| `RENDER_EXTERNAL_HOSTNAME` | Auto | Set by Render.com |
