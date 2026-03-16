# 🖥️ Online Compiler Enterprise

An enterprise-grade web-based code compilation and execution platform built with Django, Django REST Framework, FastAPI, and Docker microservices architecture.

## 🚀 Features

### Core Functionality
- **Multi-language Support**: Python, JavaScript, C, C++, Java, Go
- **Real-time Code Execution**: Execute code with instant results via microservice architecture
- **Advanced Code Editor**: Monaco Editor with syntax highlighting, auto-completion, and error detection
- **Code Snippets**: Save, share, fork, and star code snippets
- **OAuth 2.0 Authentication**: GitHub and Google sign-in support
- **JWT Authentication**: Secure token-based API authentication
- **API Documentation**: Interactive Swagger/ReDoc API docs at `/api/docs/`

### Security
- Sandboxed code execution via isolated Docker containers
- Rate limiting (anonymous and authenticated)
- CSRF protection
- CORS configuration
- Resource limits on code execution (CPU, memory, timeout)
- Audit logging for all security events

### Architecture
- **Gateway Service**: Django + DRF (API, auth, snippets)
- **Executor Service**: FastAPI (isolated code execution)
- **PostgreSQL**: Primary database
- **Redis**: Caching, sessions, Celery broker
- **Celery**: Async task processing
- **Nginx**: Reverse proxy with rate limiting

## 🏗️ Project Structure

```
online_compiler/
├── accounts/                # User auth, OAuth, profiles
├── compiler/                # Code execution, API endpoints
├── snippets/                # Code snippets CRUD
├── online_compiler/         # Django project settings
├── services/
│   └── executor/            # FastAPI executor microservice
├── nginx/                   # Nginx reverse proxy config
├── scripts/                 # Deployment scripts
├── templates/               # HTML templates
├── docker-compose.yml       # Multi-container orchestration
├── Dockerfile               # Gateway service image
└── requirements.txt         # Python dependencies
```

## 🔧 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### 1. Clone & Configure

```bash
git clone https://github.com/yokesh-kumar-M/Online_compiler
cd online_compiler

# Copy and edit environment variables
cp .env.example .env
# Edit .env with your production values
```

### 2. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access the Application

| Service          | URL                              |
|------------------|----------------------------------|
| Web Interface    | http://localhost                  |
| API Docs         | http://localhost/api/docs/        |
| Admin Panel      | http://localhost/admin/           |
| Health Check     | http://localhost/health/          |

### Default Admin Credentials
- **Email**: admin@compiler.dev
- **Password**: AdminPass123!@# (change immediately in production)

## 📖 API Endpoints

### Authentication
| Method | Endpoint                          | Description          |
|--------|-----------------------------------|----------------------|
| POST   | `/api/v1/auth/register/`          | Register new account |
| POST   | `/api/v1/auth/login/`             | Login & get JWT      |
| POST   | `/api/v1/auth/logout/`            | Logout & blacklist   |
| POST   | `/api/v1/auth/token/refresh/`     | Refresh JWT token    |
| GET    | `/api/v1/auth/profile/`           | Get user profile     |
| POST   | `/api/v1/auth/change-password/`   | Change password      |
| POST   | `/api/v1/auth/github/callback/`   | GitHub OAuth         |
| POST   | `/api/v1/auth/google/callback/`   | Google OAuth         |

### Code Execution
| Method | Endpoint                          | Description              |
|--------|-----------------------------------|--------------------------|
| POST   | `/api/v1/compiler/execute/`       | Execute code             |
| GET    | `/api/v1/compiler/languages/`     | Supported languages      |
| GET    | `/api/v1/compiler/examples/`      | Code examples            |
| GET    | `/api/v1/compiler/health/`        | Service health status    |

### Snippets
| Method | Endpoint                          | Description              |
|--------|-----------------------------------|--------------------------|
| GET    | `/api/v1/snippets/`               | List snippets            |
| POST   | `/api/v1/snippets/`               | Create snippet           |
| GET    | `/api/v1/snippets/{id}/`          | Get snippet              |
| PUT    | `/api/v1/snippets/{id}/`          | Update snippet           |
| DELETE | `/api/v1/snippets/{id}/`          | Delete snippet           |
| POST   | `/api/v1/snippets/{id}/star/`     | Star/unstar snippet      |
| POST   | `/api/v1/snippets/{id}/fork/`     | Fork snippet             |

## 🔒 Production Deployment

1. Copy `.env.production` to `.env` and update with your values
2. Set `DJANGO_DEBUG=False`
3. Set a strong `DJANGO_SECRET_KEY`
4. Update `DJANGO_ALLOWED_HOSTS` with your domain
5. Configure `CORS_ALLOWED_ORIGINS` with your frontend URL
6. Set up SSL/TLS certificates for HTTPS
7. Run: `docker-compose up -d --build`

## 📝 License

MIT License

## 👤 Author

Made with ❤️ by **Yokesh Kumar**
