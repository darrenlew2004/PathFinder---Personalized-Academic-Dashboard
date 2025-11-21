# PathFinder - Python Backend (FastAPI)

This is the Python/FastAPI backend for the PathFinder Academic Dashboard, converted from the original Scala/Play Framework implementation.

## Features

- 🚀 **FastAPI** - Modern, fast Python web framework
- 🔐 **JWT Authentication** - Secure token-based authentication
- 📊 **Cassandra Database** - Connect to your existing Cassandra database
- 🎯 **Risk Prediction** - ML-based academic risk assessment
- 📈 **Student Analytics** - Comprehensive student performance tracking
- 🔄 **CORS Enabled** - Ready for frontend integration

## Tech Stack

- **FastAPI** - Web framework
- **Cassandra** - Database (cassandra-driver)
- **PyJWT** - JWT token handling
- **Bcrypt** - Password hashing
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## Project Structure

```
backend-python/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── models/
│   │   └── __init__.py      # Pydantic models (Student, Course, etc.)
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── student_repository.py
│   │   ├── course_repository.py
│   │   └── enrollment_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cassandra_service.py
│   │   ├── jwt_service.py
│   │   └── risk_prediction_service.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── student_stats.py # Student statistics endpoints
│       └── health.py        # Health check endpoint
├── .env.example             # Environment variables template
├── .gitignore
├── requirements.txt         # Python dependencies
└── README.md
```

## Installation

### Prerequisites

- Python 3.9 or higher
- Access to Cassandra database (sunway.hep88.com:9042)
- pip (Python package manager)

### Setup Steps

1. **Navigate to the Python backend directory:**
   ```powershell
   cd backend-python
   ```

2. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Create `.env` file from template:**
   ```powershell
   copy .env.example .env
   ```

6. **Edit `.env` file with your configuration:**
   - Update `CASSANDRA_HOST`, `CASSANDRA_PORT` if needed
   - Set `JWT_SECRET_KEY` to a secure random string
   - Configure `CASSANDRA_USERNAME` and `CASSANDRA_PASSWORD` if using auth

## Configuration

Edit the `.env` file:

```env
# Application
APP_NAME=PathFinder Academic Dashboard
DEBUG=True
HOST=0.0.0.0
PORT=9000

# CORS - Update with your frontend URL
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Cassandra Database
CASSANDRA_HOST=sunway.hep88.com
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE=subjectplanning
CASSANDRA_DATACENTER=datacenter1
CASSANDRA_USERNAME=
CASSANDRA_PASSWORD=

# JWT - CHANGE THIS IN PRODUCTION!
JWT_SECRET_KEY=your-256-bit-secret-change-this-in-production-make-it-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

## Running the Application

### Development Mode (with auto-reload):

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

Or simply:

```powershell
python app/main.py
```

### Production Mode:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 9000 --workers 4
```

The API will be available at:
- **API**: http://localhost:9000
- **Swagger Docs**: http://localhost:9000/docs
- **ReDoc**: http://localhost:9000/redoc

## API Endpoints

### Authentication

- `POST /auth/login` - Login with email and password
- `POST /auth/logout` - Logout (client-side token removal)
- `POST /auth/register` - Register a new student
- `GET /auth/verify` - Verify JWT token

### Student Statistics

- `GET /api/students/current` - Get current authenticated student
- `GET /api/students/{id}/stats` - Get student statistics
- `GET /api/students/{id}/progress` - Get course progress
- `GET /api/students/{id}/risks` - Get risk predictions

### Health Check

- `GET /health` - Health check endpoint

## Database Schema

The application automatically creates the following Cassandra tables on startup:

- `students` - Student information and credentials
- `courses` - Course catalog
- `enrollments` - Student course enrollments
- `risk_predictions` - Risk prediction data

## Connecting to DataGrip/Cassandra

This Python backend connects to the **same Cassandra database** you're viewing in DataGrip:

1. **Host**: sunway.hep88.com
2. **Port**: 9042
3. **Keyspace**: subjectplanning

Both DataGrip and the Python app read/write to the same database.

## Development

### Running Tests (Optional):

```powershell
pytest
```

### Code Formatting:

```powershell
pip install black
black app/
```

### Type Checking:

```powershell
pip install mypy
mypy app/
```

## Differences from Scala Backend

### Similarities:
✅ Same API endpoints and routes
✅ Same Cassandra database connection
✅ Same JWT authentication mechanism
✅ Same risk prediction algorithm
✅ Same business logic

### Improvements:
- ✨ Automatic OpenAPI/Swagger documentation
- ✨ Type hints with Pydantic validation
- ✨ Simpler async/await syntax
- ✨ Easier dependency management with pip
- ✨ More readable Python syntax

## Troubleshooting

### Cassandra Connection Issues:

```
Error: Failed to connect to Cassandra
```

**Solution**: Check that:
- Cassandra is running and accessible
- Host and port are correct in `.env`
- Firewall allows connection to port 9042
- Credentials are correct (if using authentication)

### Module Not Found:

```
ModuleNotFoundError: No module named 'app'
```

**Solution**: Make sure you're running from the `backend-python` directory and virtual environment is activated.

### Port Already in Use:

```
Error: [Errno 10048] Only one usage of each socket address
```

**Solution**: Either stop the Scala backend or change the port in `.env`:
```env
PORT=8000
```

## Migration from Scala Backend

To switch from Scala to Python backend:

1. **Stop the Scala backend** (if running)
2. **Start the Python backend** (this one)
3. **Update frontend API URL** (if needed)
4. **Both use the same database** - no data migration needed!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the PathFinder Academic Dashboard.

## Support

For issues or questions:
- Check the `/docs` endpoint for API documentation
- Review logs for error messages
- Ensure Cassandra connectivity

---

**Made with ❤️ using FastAPI and Python**
