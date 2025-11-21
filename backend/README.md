# PathFinder - Python Backend (FastAPI)

Python/FastAPI backend for the PathFinder Academic Dashboard, connected to an existing Cassandra database.

## Features

- 🚀 **FastAPI** - Modern, fast Python web framework
- 🔐 **JWT Authentication** - Token-based authentication with student ID
- 📊 **Cassandra Integration** - Connects to existing database
- 📈 **Student Data API** - Student and subject information endpoints
- 🔄 **CORS Enabled** - Ready for frontend integration

## Tech Stack

- **FastAPI** - Web framework
- **Cassandra** - Database (cassandra-driver with gevent for Python 3.13)
- **PyJWT** - JWT token handling
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Gevent** - Event loop for Cassandra driver compatibility

## Quick Start

```powershell
# 1. Setup (creates venv and installs dependencies)
.\setup.ps1

# 2. Configure .env with your Cassandra credentials

# 3. Start the server
.\start.bat
```

API available at: http://localhost:9000/docs

## API Endpoints

### Authentication
- `POST /auth/login` - Login with student ID (int)
- `POST /auth/logout` - Logout
- `POST /auth/refresh` - Refresh JWT token
- `GET /auth/verify` - Verify JWT token

### Students
- `GET /api/students/list?limit=10` - List students
- `GET /api/students/current` - Get current authenticated student (requires JWT)
- `GET /api/students/{id}/subjects?limit=50` - Get student with subjects

### Health
- `GET /health` - Health check

## Configuration

Edit `.env` file:

```env
CASSANDRA_HOST=your-host
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE=subjectplanning
CASSANDRA_USERNAME=your-username
CASSANDRA_PASSWORD=your-password

JWT_SECRET_KEY=your-secret-key
PORT=9000
```

## Database Schema

**Students Table** (23 columns): id, ic, name, programmecode, program, overallcgpa, overallcavg, year, sem, status, graduated, cohort, etc.

**Subjects Table** (11 columns): id, programmecode, subjectcode, subjectname, examyear, exammonth, status, credit, prerequisite, level, etc.

## Notes

- Uses gevent monkey patching for Python 3.13 compatibility
- Read/write permissions only (no CREATE)
- JWT tokens use student ID (int) as identifier
- Query timeouts/limits to prevent slow operations
