# Student Risk Prediction System

A full-stack application for predicting academic risk and guiding course planning using Scala/Play Framework backend with Cassandra database and React/TypeScript frontend.

## System Architecture

### Backend Stack
- **Framework**: Play Framework 2.9.4
- **Language**: Scala 2.13.16
- **Database**: Apache Cassandra (External cluster)
- **Authentication**: JWT
- **API**: RESTful JSON API

### Frontend Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **State Management**: Redux Toolkit
- **Charts**: Recharts
- **HTTP Client**: Axios

### Database
- **Cluster**: sunway.hep88.com:9042
- **Keyspace**: subjectplanning
- **Driver**: DataStax Java Driver 4.17.0

## Prerequisites

- **JDK 11 or higher**
- **Scala 2.13.16**
- **sbt 1.9+**
- **Node.js 18+ and npm/yarn**
- **Cassandra Access** (External cluster at sunway.hep88.com:9042)

## Project Structure

```
student-risk-prediction/
├── backend/                    # Scala/Play Framework Backend
│   ├── app/
│   │   ├── controllers/       # API Controllers
│   │   ├── models/            # Data Models
│   │   ├── repositories/      # Database Repositories
│   │   └── services/          # Business Logic Services
│   ├── conf/
│   │   ├── application.conf   # Configuration
│   │   └── routes            # API Routes
│   └── build.sbt             # Build Configuration
│
└── frontend/                  # React/TypeScript Frontend
    ├── src/
    │   ├── components/       # React Components
    │   ├── features/         # Redux Slices
    │   ├── services/         # API Services
    │   ├── App.tsx          # Main App Component
    │   └── main.tsx         # Entry Point
    ├── package.json
    └── vite.config.ts
```

## Backend Setup

### 1. Clone and Navigate to Backend

```bash
cd backend
```

### 2. Configure Cassandra Connection

Edit `conf/application.conf`:

```hocon
cassandra {
  contactPoint = "sunway.hep88.com"
  port = 9042
  keyspace = "subjectplanning"
  datacenter = "datacenter1"
}

jwt {
  secret = "your-secure-secret-key-change-in-production"
  expirationHours = 24
}
```

### 3. Install Dependencies and Run

```bash
# Install dependencies
sbt update

# Run development server
sbt run

# The backend will start on http://localhost:9000
```

### 4. Verify Backend

```bash
curl http://localhost:9000/health
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

The application automatically creates the following tables in Cassandra:

### Students Table
```cql
CREATE TABLE students (
  id UUID PRIMARY KEY,
  student_id TEXT,
  name TEXT,
  email TEXT,
  password_hash TEXT,
  gpa DOUBLE,
  semester INT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Courses Table
```cql
CREATE TABLE courses (
  id UUID PRIMARY KEY,
  course_code TEXT,
  course_name TEXT,
  credits INT,
  difficulty DOUBLE,
  prerequisites LIST<TEXT>,
  description TEXT,
  created_at TIMESTAMP
);
```

### Enrollments Table
```cql
CREATE TABLE enrollments (
  id UUID PRIMARY KEY,
  student_id UUID,
  course_id UUID,
  semester INT,
  grade TEXT,
  status TEXT,
  attendance_rate DOUBLE,
  enrolled_at TIMESTAMP,
  completed_at TIMESTAMP
);
```

### Risk Predictions Table
```cql
CREATE TABLE risk_predictions (
  id UUID PRIMARY KEY,
  student_id UUID,
  course_id UUID,
  risk_level TEXT,
  confidence DOUBLE,
  factors MAP<TEXT, DOUBLE>,
  recommendations LIST<TEXT>,
  predicted_grade TEXT,
  created_at TIMESTAMP
);
```

## Features

### 1. Authentication
- User registration with student details
- JWT-based authentication
- Secure password hashing with BCrypt

### 2. Dashboard
- Current GPA display
- Completed courses count
- Total credits earned
- Average attendance rate
- Course progress with risk indicators

### 3. Risk Prediction Algorithm
The system calculates risk levels based on:
- **GPA Factor (35%)**: Academic performance
- **Attendance Factor (25%)**: Class attendance rate
- **Prerequisite Factor (20%)**: Completion of required prerequisites
- **Difficulty Factor (20%)**: Course difficulty vs student capability

Risk levels:
- **LOW**: Risk score < 0.35
- **MEDIUM**: Risk score 0.35 - 0.65
- **HIGH**: Risk score > 0.65

### 4. Recommendations
Personalized recommendations based on:
- Risk level assessment
- Individual factor analysis
- Study time allocation
- Prerequisite review suggestions

## API Endpoints

### Authentication
```
POST   /auth/register     - Register new student
POST   /auth/login        - Login
POST   /auth/logout       - Logout
GET    /auth/verify       - Verify token
```

### Student Data
```
GET    /api/students/current           - Get current student stats
GET    /api/students/:id/stats         - Get student statistics
GET    /api/students/:id/progress      - Get course progress
GET    /api/students/:id/risks         - Get risk predictions
```

### Health Check
```
GET    /health            - System health status
```

## Development

### Backend Development

```bash
# Run in development mode with auto-reload
sbt ~run

# Run tests
sbt test

# Create distribution
sbt dist
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

1. Update `application.conf` with production values
2. Set environment variables:
   ```bash
   export CASSANDRA_HOST=your-cassandra-host
   export JWT_SECRET=your-production-secret
   ```
3. Build distribution:
   ```bash
   sbt dist
   ```
4. Deploy the generated zip file

### Frontend

1. Build production bundle:
   ```bash
   npm run build
   ```
2. Deploy the `dist` folder to your web server

## Troubleshooting

### Cassandra Connection Issues
- Verify the external cluster is accessible
- Check firewall rules for port 9042
- Confirm datacenter name matches configuration

### CORS Errors
- Ensure frontend URL is in `allowedOrigins` in `application.conf`
- Verify CORS filter is enabled

### JWT Token Errors
- Check JWT secret is properly configured
- Verify token expiration settings

## Security Considerations

1. **Change JWT Secret**: Use a strong, unique secret in production
2. **HTTPS**: Always use HTTPS in production
3. **Password Hashing**: BCrypt is used with appropriate cost factor
4. **Input Validation**: All API inputs are validated
5. **SQL Injection**: Using parameterized queries with Cassandra driver

## License

MIT License

## Contributors

- Your Name / Team Name

## Support

For issues and questions, please create an issue in the repository.