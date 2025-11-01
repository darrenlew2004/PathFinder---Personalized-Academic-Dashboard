# Backend Architecture

## Python Backend Structure

```
backend-python/
│
├── 📋 Configuration & Setup
│   ├── .env.example              # Environment variables template
│   ├── .gitignore                # Git ignore patterns
│   ├── requirements.txt          # Python dependencies
│   ├── setup.ps1                 # Setup script
│   └── start.ps1                 # Start script
│
├── 📖 Documentation
│   ├── README.md                 # Main documentation
│   ├── QUICKSTART.md            # Quick start guide
│   ├── MIGRATION.md             # Migration details
│   ├── CONVERSION_SUMMARY.md    # Conversion summary
│   └── ARCHITECTURE.md          # This file
│
└── 📁 app/                       # Main application
    │
    ├── __init__.py              # Package initializer
    ├── main.py                  # FastAPI app & server
    ├── config.py                # Configuration settings
    │
    ├── 📦 models/               # Data Models (Pydantic)
    │   └── __init__.py          # Student, Course, Enrollment, etc.
    │
    ├── 🔧 services/             # Business Logic
    │   ├── __init__.py
    │   ├── cassandra_service.py      # Database connection
    │   ├── jwt_service.py            # JWT authentication
    │   └── risk_prediction_service.py # Risk calculation
    │
    ├── 💾 repositories/         # Data Access Layer
    │   ├── __init__.py
    │   ├── student_repository.py     # Student CRUD
    │   ├── course_repository.py      # Course CRUD
    │   └── enrollment_repository.py  # Enrollment CRUD
    │
    └── 🛣️ routes/               # API Endpoints
        ├── __init__.py
        ├── auth.py                   # /auth/* endpoints
        ├── student_stats.py          # /api/students/* endpoints
        └── health.py                 # /health endpoint
```

## Request Flow

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ HTTP Request
       ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│            (main.py)                │
│  ┌───────────────────────────────┐ │
│  │    CORS Middleware            │ │
│  └────────────┬──────────────────┘ │
│               │                     │
│               ▼                     │
│  ┌───────────────────────────────┐ │
│  │    Route Handlers             │ │
│  │  - auth.py                    │ │
│  │  - student_stats.py           │ │
│  │  - health.py                  │ │
│  └────────────┬──────────────────┘ │
└───────────────┼─────────────────────┘
                │
                ▼
       ┌────────────────┐
       │  JWT Service   │
       │ (Verify Token) │
       └────────┬───────┘
                │
                ▼
    ┌───────────────────────┐
    │    Repositories       │
    │  - StudentRepository  │
    │  - CourseRepository   │
    │  - EnrollmentRepo     │
    └──────────┬────────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Cassandra Service   │
    │  (Database Layer)   │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │   Cassandra DB      │
    │  sunway.hep88.com   │
    │      :9042          │
    └─────────────────────┘
```

## Layer Responsibilities

### 1. Routes Layer (`app/routes/`)
**Purpose**: Handle HTTP requests and responses

- Validate request data
- Call appropriate services/repositories
- Return formatted responses
- Handle authentication
- Manage HTTP status codes

**Example**:
```python
@router.post("/login")
async def login(request: LoginRequest):
    student = student_repository.find_by_email(request.email)
    if student and verify_password(request.password):
        token = jwt_service.generate_token(student.id, student.email)
        return LoginResponse(token=token, student=student)
```

### 2. Services Layer (`app/services/`)
**Purpose**: Business logic and cross-cutting concerns

- **CassandraService**: Database connection management
- **JWTService**: Token generation and validation
- **RiskPredictionService**: Complex risk calculations

**Example**:
```python
def predict_risk(student, course, enrollments):
    gpa_factor = calculate_gpa_factor(student.gpa)
    attendance_factor = calculate_attendance_factor(enrollments)
    # ... complex calculations
    return RiskPrediction(...)
```

### 3. Repositories Layer (`app/repositories/`)
**Purpose**: Data access and CRUD operations

- Abstract database queries
- Map database rows to models
- Handle database errors
- Provide clean data interface

**Example**:
```python
def find_by_email(self, email: str) -> Optional[Student]:
    query = "SELECT * FROM students WHERE email = %s"
    result = self.session.execute(query, (email,))
    return self._map_row_to_student(result.one())
```

### 4. Models Layer (`app/models/`)
**Purpose**: Data structure definitions

- Define data schemas
- Validation rules
- Type hints
- JSON serialization

**Example**:
```python
class Student(BaseModel):
    id: UUID
    email: EmailStr
    gpa: float = Field(ge=0.0, le=4.0)
```

## Data Flow Example: Student Login

```
1. POST /auth/login
   Body: {"email": "...", "password": "..."}
   │
   ▼
2. auth.py → login()
   - Validate request (Pydantic)
   │
   ▼
3. student_repository.find_by_email()
   - Query Cassandra
   │
   ▼
4. cassandra_service.execute()
   - Execute CQL query
   │
   ▼
5. Cassandra Database
   - Return student row
   │
   ▼
6. student_repository._map_row_to_student()
   - Convert to Student model
   │
   ▼
7. student_repository.verify_password()
   - Check bcrypt hash
   │
   ▼
8. jwt_service.generate_token()
   - Create JWT token
   │
   ▼
9. Return LoginResponse
   Response: {"token": "...", "student": {...}}
```

## Database Schema

### Cassandra Tables

```
┌─────────────────────────────────────┐
│          students                   │
├─────────────────────────────────────┤
│ id              UUID (PK)           │
│ student_id      TEXT                │
│ name            TEXT                │
│ email           TEXT                │
│ password_hash   TEXT                │
│ gpa             DOUBLE              │
│ semester        INT                 │
│ created_at      TIMESTAMP           │
│ updated_at      TIMESTAMP           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│          courses                    │
├─────────────────────────────────────┤
│ id              UUID (PK)           │
│ course_code     TEXT                │
│ course_name     TEXT                │
│ credits         INT                 │
│ difficulty      DOUBLE              │
│ prerequisites   LIST<TEXT>          │
│ description     TEXT                │
│ created_at      TIMESTAMP           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│        enrollments                  │
├─────────────────────────────────────┤
│ id              UUID (PK)           │
│ student_id      UUID                │
│ course_id       UUID                │
│ semester        INT                 │
│ grade           TEXT                │
│ status          TEXT                │
│ attendance_rate DOUBLE              │
│ enrolled_at     TIMESTAMP           │
│ completed_at    TIMESTAMP           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      risk_predictions               │
├─────────────────────────────────────┤
│ id              UUID (PK)           │
│ student_id      UUID                │
│ course_id       UUID                │
│ risk_level      TEXT                │
│ confidence      DOUBLE              │
│ factors         MAP<TEXT,DOUBLE>    │
│ recommendations LIST<TEXT>          │
│ predicted_grade TEXT                │
│ created_at      TIMESTAMP           │
└─────────────────────────────────────┘
```

## API Endpoints Map

```
/
├── /auth
│   ├── POST   /login       → auth.login()
│   ├── POST   /logout      → auth.logout()
│   ├── POST   /register    → auth.register()
│   └── GET    /verify      → auth.verify_token()
│
├── /api/students
│   ├── GET    /current           → student_stats.get_current_student()
│   ├── GET    /{id}/stats        → student_stats.get_student_stats()
│   ├── GET    /{id}/progress     → student_stats.get_course_progress()
│   └── GET    /{id}/risks        → student_stats.get_risk_predictions()
│
├── /health     → health.health_check()
│
├── /docs       → Swagger UI (auto-generated)
└── /redoc      → ReDoc (auto-generated)
```

## Configuration Flow

```
.env file
   │
   ▼
Settings class (config.py)
   │
   ├──> Application settings
   ├──> Database connection
   ├──> JWT configuration
   └──> CORS settings
        │
        ▼
   Used by services
   and repositories
```

## Security Flow

```
Client Request
   │
   ▼
[Authorization: Bearer <token>]
   │
   ▼
get_current_user() dependency
   │
   ├─> Extract token from header
   ├─> jwt_service.validate_token()
   ├─> Verify signature
   ├─> Check expiration
   └─> Extract user claims
       │
       ▼
   Route handler receives user info
```

## Deployment Architecture

```
┌──────────────────────────────────┐
│     Production Server            │
│                                  │
│  ┌────────────────────────────┐ │
│  │   Uvicorn (ASGI Server)    │ │
│  │   - Multiple workers       │ │
│  │   - Process management     │ │
│  └─────────────┬──────────────┘ │
│                │                 │
│                ▼                 │
│  ┌────────────────────────────┐ │
│  │   FastAPI Application      │ │
│  └─────────────┬──────────────┘ │
└────────────────┼─────────────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │   Cassandra Cluster    │
    │   sunway.hep88.com     │
    └────────────────────────┘
```

## Development vs Production

### Development
- Hot reload enabled
- Debug mode on
- Single worker
- Detailed logging
- CORS relaxed

### Production
- No reload
- Debug off
- Multiple workers
- Structured logging
- CORS restricted

---

**This architecture ensures**:
- ✅ Separation of concerns
- ✅ Easy testing
- ✅ Maintainability
- ✅ Scalability
- ✅ Security
