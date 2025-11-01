# Quick Start Guide - Python Backend

## 🚀 Get Started in 3 Steps

### Step 1: Run Setup Script

Open PowerShell in the `backend-python` folder and run:

```powershell
.\setup.ps1
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create a `.env` file from the template

### Step 2: Configure Environment

Edit the `.env` file if needed (the defaults should work):

```env
CASSANDRA_HOST=sunway.hep88.com
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE=subjectplanning
```

**Important**: Change the JWT secret in production!

### Step 3: Start the Server

```powershell
.\start.ps1
```

The server will start at:
- **API**: http://localhost:9000
- **Swagger Docs**: http://localhost:9000/docs

## 📝 What Was Converted?

Your Scala/Play Framework backend has been fully converted to Python/FastAPI:

### ✅ All Features Maintained:
- JWT Authentication
- Student registration and login
- Course enrollment tracking
- Risk prediction algorithms
- Student statistics and analytics
- Same Cassandra database connection

### 🔄 API Endpoints (Identical):
- `POST /auth/login`
- `POST /auth/register`
- `GET /api/students/current`
- `GET /api/students/{id}/stats`
- `GET /api/students/{id}/progress`
- `GET /api/students/{id}/risks`
- `GET /health`

### 📊 Database Connection:
- Uses the **same Cassandra database** (sunway.hep88.com:9042)
- Connects to **same keyspace** (subjectplanning)
- Works with **DataGrip** simultaneously
- No data migration needed!

## 🆚 Python vs Scala Backend

| Feature | Scala/Play | Python/FastAPI |
|---------|-----------|----------------|
| Database | Cassandra ✅ | Cassandra ✅ |
| Auth | JWT ✅ | JWT ✅ |
| API Endpoints | Same ✅ | Same ✅ |
| Risk Prediction | Same Algorithm ✅ | Same Algorithm ✅ |
| Auto Docs | ❌ | Swagger/OpenAPI ✅ |
| Async Support | ✅ | ✅ |
| Type Safety | ✅ | Pydantic ✅ |

## 🔧 Common Commands

### Activate Virtual Environment:
```powershell
.\venv\Scripts\Activate.ps1
```

### Install New Package:
```powershell
pip install package-name
pip freeze > requirements.txt
```

### Run Tests:
```powershell
pytest
```

### Check API Docs:
Open browser to: http://localhost:9000/docs

## 🐛 Troubleshooting

### "Cannot connect to Cassandra"
- Check if Cassandra is running
- Verify host/port in `.env`
- Test connection with DataGrip

### "Port 9000 already in use"
- Stop the Scala backend first, or
- Change `PORT=8000` in `.env`

### "Module not found"
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

## 📚 Next Steps

1. **Test the API**: Visit http://localhost:9000/docs
2. **Update Frontend**: Point your frontend to this backend
3. **Keep Both**: You can run both backends (different ports)

## 💡 Tips

- Both backends can run simultaneously on different ports
- They both connect to the same database
- Switch between them by updating your frontend API URL
- Use `/docs` endpoint to test API calls interactively

---

**Your Python backend is ready to use! 🎉**
