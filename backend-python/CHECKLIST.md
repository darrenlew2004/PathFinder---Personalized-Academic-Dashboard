# 🎯 Getting Started Checklist

Follow these steps to get your Python backend up and running!

## ☑️ Pre-Installation Checklist

- [ ] Python 3.9 or higher installed
  ```powershell
  python --version
  ```
  
- [ ] Access to Cassandra database (sunway.hep88.com:9042)

- [ ] PowerShell available (default on Windows)

## 🚀 Installation Steps

### Step 1: Navigate to Backend Directory
```powershell
cd c:\Github\PathFinder---Personalized-Academic-Dashboard\backend-python
```
- [ ] Navigated to backend-python folder

### Step 2: Run Setup Script
```powershell
.\setup.ps1
```

This will:
- [ ] Create Python virtual environment
- [ ] Install all dependencies
- [ ] Create `.env` file from template

### Step 3: Configure Environment (Optional)
```powershell
notepad .env
```

Default settings should work, but you can customize:
- [ ] Reviewed `.env` file
- [ ] Updated JWT_SECRET_KEY (recommended for production)
- [ ] Verified CASSANDRA_HOST and PORT
- [ ] Set CASSANDRA_USERNAME/PASSWORD (if needed)

### Step 4: Start the Server
```powershell
.\start.ps1
```

- [ ] Server started successfully
- [ ] No connection errors
- [ ] Seeing startup logs

## ✅ Verification Steps

### 1. Check Server Health
Open browser to: http://localhost:9000/health

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-01T...",
  "service": "PathFinder Academic Dashboard API",
  "version": "1.0.0"
}
```

- [ ] Health endpoint returns 200 OK
- [ ] JSON response received

### 2. Check API Documentation
Open browser to: http://localhost:9000/docs

- [ ] Swagger UI loads
- [ ] See all API endpoints listed
- [ ] Can expand endpoint details

### 3. Test Authentication (Optional)

In Swagger UI at `/docs`:

1. **Register a test student**
   - Click `POST /auth/register`
   - Click "Try it out"
   - Fill in test data:
     ```json
     {
       "student_id": "TEST001",
       "name": "Test Student",
       "email": "test@example.com",
       "password": "password123",
       "gpa": 3.5,
       "semester": 1
     }
     ```
   - Click "Execute"
   - [ ] Returns 201 Created

2. **Login with test student**
   - Click `POST /auth/login`
   - Fill in credentials:
     ```json
     {
       "email": "test@example.com",
       "password": "password123"
     }
     ```
   - Click "Execute"
   - [ ] Returns JWT token
   - [ ] Copy the token

3. **Verify token**
   - Click `GET /auth/verify`
   - Click "Try it out"
   - Add header: `Authorization: Bearer <your-token>`
   - Click "Execute"
   - [ ] Returns valid: true

### 4. Check Database Connection

In DataGrip or Cassandra client:

```sql
SELECT * FROM subjectplanning.students;
```

- [ ] Can see the test student you created
- [ ] Data matches what you entered

## 🔧 Troubleshooting

### Issue: "Python not found"
**Solution**: Install Python 3.9+ from python.org

- [ ] Resolved

### Issue: "Cannot connect to Cassandra"
**Solutions**:
1. Check Cassandra is running
2. Verify host/port in `.env`
3. Test connection in DataGrip
4. Check firewall settings

- [ ] Resolved

### Issue: "Port 9000 already in use"
**Solutions**:
1. Stop Scala backend, or
2. Change port in `.env`:
   ```
   PORT=8000
   ```

- [ ] Resolved

### Issue: "Module not found"
**Solution**: Activate virtual environment and reinstall
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- [ ] Resolved

## 📱 Frontend Integration

### Update Frontend API URL

If your frontend is in `frontend/` folder:

1. Find API configuration file (usually `src/services/api.ts`)

2. Update base URL:
   ```typescript
   const API_BASE_URL = 'http://localhost:9000';
   ```

- [ ] Frontend API URL updated
- [ ] Frontend can connect to Python backend

### Test Frontend Integration

1. Start Python backend
2. Start frontend (usually `npm run dev`)
3. Try to login
4. Check network tab in browser

- [ ] Frontend sends requests to Python backend
- [ ] Receives proper responses
- [ ] Authentication works

## 🎓 Learning Resources

### Explore the API
- [ ] Visited http://localhost:9000/docs
- [ ] Tried different endpoints
- [ ] Tested with sample data

### Read Documentation
- [ ] Read README.md
- [ ] Reviewed QUICKSTART.md
- [ ] Checked ARCHITECTURE.md

### Optional Learning
- [ ] FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/
- [ ] Pydantic Docs: https://docs.pydantic.dev/
- [ ] Cassandra Python Driver: https://docs.datastax.com/

## 🎉 Success Criteria

You're all set when:

- [x] Python backend starts without errors
- [x] `/health` endpoint returns healthy status
- [x] `/docs` shows interactive API documentation
- [x] Can register and login a test user
- [x] Cassandra database connection works
- [x] Frontend can communicate with backend (if applicable)

## 📊 Performance Check

Run a few API calls and verify:

- [ ] Login: < 500ms response time
- [ ] Student stats: < 1s response time
- [ ] Risk predictions: < 2s response time
- [ ] No memory leaks during operation

## 🔐 Security Check (Production)

Before deploying to production:

- [ ] Change JWT_SECRET_KEY to strong random value
- [ ] Update ALLOWED_ORIGINS to actual frontend URL
- [ ] Set DEBUG=False
- [ ] Review Cassandra credentials
- [ ] Enable HTTPS
- [ ] Set up rate limiting
- [ ] Configure proper logging

## 🚀 Deployment Checklist (Optional)

When ready for production:

- [ ] Update environment variables
- [ ] Set up process manager (systemd, supervisor)
- [ ] Configure reverse proxy (nginx, Apache)
- [ ] Set up SSL certificates
- [ ] Configure monitoring
- [ ] Set up backup strategy
- [ ] Test failover scenarios

## 📞 Get Help

If stuck:

1. **Check logs**: Look at console output for errors
2. **Review docs**: README.md has detailed info
3. **Test database**: Use DataGrip to verify connection
4. **Check config**: Ensure `.env` has correct values
5. **Restart**: Try `.\start.ps1` again

## ✨ Next Steps

After everything works:

1. **Explore Features**
   - [ ] Try all API endpoints
   - [ ] Test risk predictions
   - [ ] Review student statistics

2. **Customize**
   - [ ] Adjust risk prediction weights
   - [ ] Add custom endpoints
   - [ ] Extend models

3. **Integrate**
   - [ ] Connect frontend
   - [ ] Test full workflow
   - [ ] Deploy to production

---

## 📝 Notes

- Both Scala and Python backends can run simultaneously
- They share the same database
- Switch between them by changing frontend API URL
- Python backend is fully compatible with existing data

---

**Congratulations! Your Python backend is ready! 🎊**

Need help? Check the documentation files or the `/docs` endpoint!
