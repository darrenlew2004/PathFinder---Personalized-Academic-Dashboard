# PathFinder - Personalized Academic Dashboard

A full-stack application for academic planning and student data management using FastAPI/Python backend with Cassandra database and React/TypeScript frontend.

## System Architecture

### Backend Stack
- **Framework**: FastAPI (Python)
- **Language**: Python 3.13+
- **Database**: Apache Cassandra (External cluster)
- **Authentication**: JWT
- **API**: RESTful JSON API
- **Event Loop**: Gevent (for Cassandra driver compatibility)

### Frontend Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **State Management**: Redux Toolkit
- **HTTP Client**: Axios

### Database
- **Cluster**: sunway.hep88.com:9042
- **Keyspace**: subjectplanning
- **Driver**: Cassandra Driver 3.29.2 with gevent

## Prerequisites

- **Python 3.13+**
- **Node.js 18+ and npm**
- **Cassandra Access** (External cluster at sunway.hep88.com:9042)

## Features

- 🔐 **JWT Authentication** - Secure student login system
- 📊 **Student Analytics** - Cohort analysis, enrollment trends, grade distributions
- 🎯 **Subject Predictions** - AI-powered success predictions based on prerequisites
- 📈 **Performance Tracking** - GPA trends and subject completion analysis
- 🎓 **Program Catalog** - BCS program requirements and variants
- 📱 **Responsive UI** - Material-UI based dashboard with multiple tabs

## Project Structure

```
PathFinder---Personalized-Academic-Dashboard/
├── backend/                    # Python/FastAPI Backend
│   ├── analysis/              # Data Analysis Scripts
│   ├── app/
│   │   ├── catalog/           # Program Catalogs
│   │   ├── routes/            # API Endpoints
│   │   ├── models/            # Pydantic Models
│   │   ├── repositories/      # Database Access Layer
│   │   └── services/          # Business Logic & ML
│   ├── data/                  # CSV Data Files
│   ├── run.py                 # Entry Point
│   └── requirements.txt       # Python Dependencies
│
└── frontend/                  # React/TypeScript Frontend
    ├── src/components/        # React Components
    ├── features/              # Redux Slices
    ├── services/              # API Services
    ├── main.tsx               # Entry Point
    └── package.json
```

## Backend Setup

### 1. Navigate to Backend

```bash
cd backend
```

### 2. Install Dependencies

```bash
# Run setup script (creates venv and installs packages)
.\setup.ps1

# Or manually:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure Environment

Edit `.env` file:

```env
CASSANDRA_HOST=sunway.hep88.com
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE=subjectplanning
CASSANDRA_DATACENTER=datacenter1
CASSANDRA_USERNAME=your-username
CASSANDRA_PASSWORD=your-password

JWT_SECRET_KEY=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

PORT=9000
```

### 4. Run Backend

```powershell
# Using start script (recommended)
.\start.ps1

# Or directly
python run.py

# The backend will start on http://localhost:9000
```

### 5. Verify Backend

```bash
curl http://localhost:9000/health
# Or visit: http://localhost:9000/docs (Swagger UI)
```

## Frontend Setup

### 1. Navigate to Frontend

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
# or
yarn install
```

### 3. Configure Environment

Create `.env` file:

```env
VITE_API_URL=http://localhost:9000
```

### 4. Run Development Server

```bash
npm run dev
# or
yarn dev

# The frontend will start on http://localhost:5173
```

## Database Schema

The application connects to existing Cassandra tables:

### Students Table (23 columns)
- `id` (int) - Primary key
- `ic`, `name` - Student identification
- `programmecode`, `program` - Program information
- `overallcgpa`, `overallcavg` - Academic performance
- `year`, `sem` - Current academic position
- `status`, `graduated`, `cohort` - Student status
- And 11 additional fields for demographics and academic history

### Subjects Table (11 columns)
- `id` (int) - Primary key
- `programmecode`, `subjectcode`, `subjectname` - Subject details
- `examyear`, `exammonth` - Examination period
- `status`, `credit`, `prerequisite`, `level` - Subject properties

## API Endpoints

### Authentication
```
POST   /auth/login         - Login with student ID (returns JWT token)
POST   /auth/refresh       - Refresh JWT token
GET    /auth/verify        - Verify JWT token
```

### Student Data
```
GET    /api/students/current              - Get current student info
GET    /api/students/{id}/stats           - Get student statistics
```

### Analytics
```
GET    /api/analytics/cohort              - Cohort performance analysis
GET    /api/analytics/subject-enrollment  - Subject enrollment trends
GET    /api/analytics/subject-pass-rates  - Subject pass rate analysis
```

### Predictions
```
GET    /api/predictions/students/{id}/subject/{code}  - Predict single subject success
POST   /api/predictions/students/{id}/subjects        - Predict multiple subjects
```

### Program Catalog
```
GET    /api/catalogue/progress/{period}/{variant}     - Get program progress
GET    /api/catalogue/variants                        - List program variants
POST   /api/catalogue/what-if                         - What-if analysis
```

### Health Check
```
GET    /health             - System health status
```

Full API documentation available at: `http://localhost:9000/docs`

## Development

### Backend Development

```powershell
# Run with auto-reload (via start.ps1)
.\start.ps1

# Or manually activate venv and run
.\venv\Scripts\Activate.ps1
python run.py
```

### Frontend Development

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Production Deployment

### Backend

1. Update `.env` with production values
2. Install dependencies in production environment
3. Run with production ASGI server:
   ```bash
   python run.py
   # Or use gunicorn with gevent workers
   ```

### Frontend

1. Build production bundle:
   ```bash
   npm run build
   ```
2. Deploy the `dist` folder to your web server

## Troubleshooting

### Cassandra Connection Issues
- Verify cluster is accessible from your network
- Check `.env` credentials and connection settings
- Confirm datacenter name matches your cluster

### Python 3.13 Compatibility
- Ensure `run.py` applies gevent monkey patching before imports
- asyncore module was removed in Python 3.13; gevent provides compatibility

### JWT Token Errors
- Check JWT_SECRET_KEY in `.env`
- Verify token expiration settings
- Frontend must send Authorization header: `Bearer <token>`

### CORS Errors
- Frontend proxy is configured in `vite.config.ts`
- Backend CORS is enabled in `main.py`

## Testing

Login with any student ID from the database to test the application. Visit `http://localhost:5173` for the frontend and `http://localhost:9000/docs` for API documentation.

## License

MIT License