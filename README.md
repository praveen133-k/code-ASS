# Issues & Insights Tracker

A production-ready issue tracking system built with **SvelteKit**, **FastAPI**, and **PostgreSQL**. Features role-based access control, real-time updates, and comprehensive issue management.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Common Issues & Solutions

#### Backend Issues
- **Import errors in tests**: Run `python backend/run_tests.py` instead of pytest directly
- **Database connection errors**: Ensure PostgreSQL is running and migrations are applied
- **Missing directories**: Run `python setup.py` to create required directories

#### Frontend Issues
- **TypeScript errors**: Install Node.js types with `npm install @types/node`
- **Build errors**: Clear node_modules and reinstall with `rm -rf node_modules && npm install`
- **Port conflicts**: Change ports in docker-compose.yml or stop conflicting services

### Running with Docker (Recommended)

1. **Clone and start the application:**
```bash
git clone <repository-url>
cd issues-insights-tracker
docker compose up --build
```

### Quick Setup (Alternative)

1. **Run the setup script:**
```bash
python setup.py
```

2. **Start the database:**
```bash
docker-compose up db -d
```

3. **Run migrations:**
```bash
cd backend && alembic upgrade head
```

4. **Start the application:**
```bash
docker-compose up
```

2. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics
- Health Check: http://localhost:8000/health
- Database: localhost:5432
- Redis: localhost:6379

3. **Create your first user:**
- Visit http://localhost:3000
- Click "Sign up" and create an account
- You'll be automatically assigned the REPORTER role

### Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/issues_db"
export SECRET_KEY="your-secret-key-here"

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🏗️ Architecture Overview

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (SvelteKit)   │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

#### Frontend (SvelteKit)
- **Framework**: SvelteKit with SSR enabled
- **Styling**: Tailwind CSS for responsive design
- **Charts**: Chart.js for data visualization
- **Markdown**: Marked.js for issue descriptions
- **Testing**: Playwright for E2E tests

#### Backend (FastAPI)
- **Framework**: FastAPI with automatic OpenAPI docs
- **Database**: SQLAlchemy ORM with PostgreSQL
- **Authentication**: JWT tokens with OAuth2
- **Migrations**: Alembic for database schema management
- **Testing**: pytest with ≥80% coverage target

#### Database (PostgreSQL 15+)
- **Tables**: Users, Issues, DailyStats
- **Features**: ACID compliance, JSON support, full-text search

### Key Features

#### 🔐 Authentication & Authorization
- **Email/Password**: Traditional login with bcrypt hashing
- **Google OAuth**: Social login integration (planned)
- **Role-Based Access Control (RBAC)**:
  - **REPORTER**: Create and view own issues
  - **MAINTAINER**: Triage any issue, update status/tags
  - **ADMIN**: Full CRUD on everything

#### 📋 Issue Management
- **CRUD Operations**: Create, read, update, delete issues
- **Status Workflow**: OPEN → TRIAGED → IN_PROGRESS → DONE
- **Severity Levels**: LOW, MEDIUM, HIGH, CRITICAL
- **File Attachments**: Upload and store files (planned)
- **Markdown Support**: Rich text descriptions

#### 📊 Dashboard & Analytics
- **Real-time Charts**: Open issues by severity (Chart.js)
- **Statistics**: Daily aggregated issue counts
- **Background Jobs**: Automated data aggregation every 30 minutes (Celery)
- **File Upload**: Support for file attachments (local storage)

#### 🔄 Real-time Updates
- **WebSocket/SSE**: Live issue list updates
- **Auto-refresh**: When issues are created or status changes

## 📁 Project Structure

```
issues-insights-tracker/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app and routes
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # Database operations
│   │   ├── deps.py          # Dependencies and auth
│   │   └── database.py      # Database connection
│   ├── alembic/             # Database migrations
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Backend container
├── frontend/
│   ├── src/
│   │   ├── routes/          # SvelteKit pages
│   │   ├── app.html         # HTML template
│   │   └── app.css          # Global styles
│   ├── package.json         # Node dependencies
│   ├── svelte.config.js     # SvelteKit config
│   ├── tailwind.config.js   # Tailwind config
│   └── Dockerfile          # Frontend container
├── docker-compose.yml       # Multi-service orchestration
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

#### Backend
```bash
DATABASE_URL=postgresql+psycopg2://user:pass@host:port/db
SECRET_KEY=your-secret-key-here
```

#### Frontend
```bash
VITE_API_URL=http://localhost:8000  # Backend API URL
```

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR,
    google_id VARCHAR,
    role user_role DEFAULT 'REPORTER'
);
```

#### Issues Table
```sql
CREATE TABLE issues (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    file_path VARCHAR,
    severity issue_severity NOT NULL,
    status issue_status DEFAULT 'OPEN',
    reporter_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### E2E Tests
```bash
cd frontend
npm run test:e2e
```

### Run All Tests
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm run test && npm run test:e2e
```

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Use proper secrets management
2. **Database**: Use managed PostgreSQL service
3. **File Storage**: Use S3-compatible storage for uploads
4. **SSL/TLS**: Configure HTTPS for production
5. **Monitoring**: Add Prometheus metrics and logging
6. **Backup**: Implement database backup strategy

### Docker Production Build
```bash
docker compose -f docker-compose.prod.yml up --build
```

## 📈 Performance & Scalability

### Current Performance
- **Frontend**: SSR-enabled SvelteKit for fast initial loads
- **Backend**: FastAPI with async support
- **Database**: Optimized queries with proper indexing

### Scalability Considerations
- **Horizontal Scaling**: Stateless backend services
- **Database**: Connection pooling and read replicas
- **Caching**: Redis for session storage and caching
- **CDN**: Static asset delivery optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🔍 Trade-offs & Decisions

### Architecture Trade-offs

#### ✅ Chosen: SvelteKit + FastAPI
- **Pros**: 
  - SSR for better SEO and performance
  - Type safety with TypeScript
  - Automatic API documentation
  - Modern developer experience
- **Cons**: 
  - Smaller ecosystem compared to React/Vue
  - Learning curve for SvelteKit

#### ✅ Chosen: PostgreSQL
- **Pros**: 
  - ACID compliance
  - Rich feature set (JSON, full-text search)
  - Excellent performance
  - Strong community support
- **Cons**: 
  - More complex than SQLite
  - Requires separate server setup

#### ✅ Chosen: JWT Authentication
- **Pros**: 
  - Stateless authentication
  - Works well with microservices
  - No server-side session storage
- **Cons**: 
  - Token size overhead
  - Cannot invalidate tokens easily
  - Security considerations with token storage

### Alternative Approaches Considered

#### Authentication
- **Session-based**: Better for single-domain apps, but requires Redis
- **OAuth2 with PKCE**: More secure for mobile apps, but complex setup

#### Database
- **MongoDB**: Better for document-based data, but less ACID compliance
- **SQLite**: Simpler setup, but limited concurrent users

#### Frontend
- **React + Next.js**: Larger ecosystem, but more complex
- **Vue + Nuxt**: Good alternative, but less TypeScript support

### Future Enhancements

#### Planned Features
- [ ] Google OAuth integration
- [ ] File upload with S3
- [ ] Real-time notifications
- [ ] Advanced search and filtering
- [ ] Issue templates
- [ ] Email notifications
- [ ] API rate limiting
- [ ] Audit logging

#### Performance Optimizations
- [ ] Database query optimization
- [ ] Frontend code splitting
- [ ] CDN integration
- [ ] Redis caching layer
- [ ] Background job optimization

## 🆘 Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Clean up containers and volumes
docker compose down -v
docker system prune -a

# Rebuild from scratch
docker compose up --build --force-recreate
```

#### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker compose ps

# View logs
docker compose logs db
```

#### Frontend Build Issues
```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Getting Help
- Check the [Issues](../../issues) page
- Review the API documentation at `/docs`
- Check Docker logs: `docker compose logs`

---

**Built with ❤️ using modern web technologies** 