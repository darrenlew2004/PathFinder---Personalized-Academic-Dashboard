# PathFinder - Personalized Academic Dashboard

> **An intelligent academic planning system that predicts student success using hybrid Machine Learning and rule-based algorithms**

PathFinder is a full-stack web application that helps university students make informed decisions about course selection by predicting their probability of success in each subject. Built with a hybrid AI approach combining Random Forest ML (84.5% accuracy) with domain-expert prerequisite analysis, PathFinder provides transparent, actionable recommendations to optimize academic paths.

## 🎯 Key Features

- **🤖 Hybrid AI Predictions** - Combines Machine Learning (Random Forest, 84.5% accuracy) with rule-based prerequisite analysis for transparent, accurate predictions
- **📊 Real-Time Success Probability** - Get instant predictions with confidence scores and risk assessments (Low/Medium/High/Very High)
- **🔍 Explainable AI** - View top contributing factors and see exactly why the model makes each prediction
- **📈 Performance Analytics** - Track GPA trends, cohort comparisons, and subject difficulty metrics
- **🎓 Academic Planning** - Smart course recommendations based on prerequisites, performance history, and predicted success rates
- **⚡ High Performance** - Sub-10ms predictions with 2x speedup through batch processing optimization
- **🔐 Secure Authentication** - JWT-based authentication protecting student data

## 💡 What Makes PathFinder Unique?

### Hybrid Prediction System
Unlike pure ML or pure rule-based systems, PathFinder uses a **weighted ensemble approach**:
- **70% Machine Learning**: Random Forest model trained on 99,362 student-subject records
- **30% Rule-Based**: Expert-defined prerequisite chains with weighted relationships
- **Result**: Best of both worlds - ML accuracy with transparent reasoning

### Academic Impact
- Trained on **4,483 students** across **246 unique courses**
- **23 engineered features** including GPA, prerequisite performance, cohort statistics
- **84.47% test accuracy** with 0.8746 ROC-AUC score
- Helps identify at-risk students early with actionable recommendations

### Production-Ready Performance
- **< 10ms** per prediction (real-time experience)
- **< 7ms** ML model inference
- Batch processing achieves **2x speedup** over individual predictions
- Scales to handle **1,000+ predictions per second**

## 🏗️ System Architecture

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

## 📁 Project Structure

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
│   ├── run.py                 #         # Python/FastAPI Backend
│   ├── app/
│   │   ├── services/
│   │   │   ├── subject_prediction_service.py  # Hybrid prediction engine
│   │   │   ├── ml_prediction_service.py       # Random Forest ML model
│   │   │   └── student_analytics_service.py   # Analytics engine
│   │   ├── routes/                            # RESTful API endpoints
│   │   ├── catalog/                           # BCS program definitions
│   │   └── repositories/                      # Database access layer
│   ├── analysis/
│   │   ├── prepare_ml_data_from_cassandra.py  # Feature engineering
│ # Prerequisites

- **Python 3.13+**
- **Node.js 18+ and npm**
- **Cassandra Database Access** (or use CSV fallback mode)

### Backend Setup

**1. Navigate to Backend**

```bash
cd backend
```

**2. Install Dependencies**              # Main dashboard with predictions
│   │   ├── Login.tsx                    # Authentication UI
│   │   └── Header.tsx                   # Navigation
│   ├── services/                        # API integration
│   ├── features/                        # Redux state management
│   └── main.tsx                         # Application entry point
**3. Configure Environment**

Create/edit `.env` file in `backend/` directoryd                        # Documentation index
│   ├── ML_IMPLEMENTATION.md             # ML system deep dive
│   ├── SYSTEM_OVERVIEW.md               # Architecture diagrams
│   ├── USE_CASE_DIAGRAM.md              # Use cases and requirements
│   ├── PERFORMANCE_REPORT.md            # Metrics and benchmarks
│   ├── BATCH_OPTIMIZATION.md            # Performance optimization
│   ├── AWS_EC2_DEPLOYMENT.md            # Deployment guide
│   └── DEPLOYMENT_CHECKLIST.md          # Quick deployment steps
│
└── deployment/                          # Production deployment configs
```

## 📚 Documentation

All technical documentation is available in the [`docs/`](docs/) folder:

- **[ML Implementation Guide](docs/ML_IMPLEMENTATION.md)** - Complete ML pipeline, feature engineering, and training process
- **[System Overview](docs/SYSTEM_OVERVIEW.md)** - Architecture diagrams and component interactions
- **[Performance Report](docs/PERFORMANCE_REPORT.md)** - Benchmarks, metrics, and accuracy analysis
- **[Use Case Diagrams](docs/USE_CASE_DIAGRAM.md)** - Functional and non-functional requirements
- **[Deployment Guide](docs/AWS_EC2_DEPLOYMENT.md)** - Step-by-step production deployment

## 🚀 Quick Start
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
**4. Run Backend**

```bash
# Using start script (recommended)
.\start.ps1

# Or directly
python run.py
```

Backend will start on **http://localhost:9000**

**5. Verify Backend**
- Health Check: http://localhost:9000/health
- API Documentation: http://localhost:9000/docs (Swagger UI)

### Frontend Setup

**1. Navigate to Frontend**health
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
**3. Configure Environment**

Create `.env` file in `frontend/` directory
### 3. Configure Environment

Create `.env` file:

```env
VITE_API_URL=http://localhost:9000
```

### 4. Run Development Server

```bash
**4. Run Development Server**

```bash
npm run dev
```

Frontend will start on **http://localhost:5173**

---

## 🔬 Machine Learning Details

### 🔐rerequisite Features (7)**:
- Weighted prerequisite GPA, missing prerequisites
- Min/max prerequisite grades, completion rate

**Subject Cohort Features (4)**:
- Historical pass rate, average score/GPA
- Total students who took the subject

**Categorical Features (5)**:
- Programme code, gender, subject code, cohort, financial aid status

### Model Performance

| Metric | Value |
|--------|-------|
| **Test Accuracy** | 84.47% |
| **ROC-AUC Score** | 0.8746 |
| **Precision (Pass)** | 94% |
| **Recall (Pass)** | 88% |
| **Recall (Fail)** | 66% |

**Top 5 Feature Importance**:
1. Current GPA (16.2%)
2. Subject Pass Rate (11.7%)
3. Subject Average GPA (10.5%)
4. Student Fail Rate (10.5%)
5. C👤 ohort Year (7.5%)

### Hybrid Prediction Formula

```
Final Prediction = (0.7 × ML_Probability) + (0.3 × Rule_Based_Probability)
```📈 

This weighted ensemble provides:
- **High accuracy** from ML model
- **🤖 AI Predictions (Hybrid ML + Rule-Based)ity** from rule-based analysis
- **Robustness** with fallback to rules if ML unavailable

For complete ML implementation details, see [ML_IMPLEMENTATION.md](docs/ML_IMPLEMENTATION.md)

---
🎓 
## 🎓 Use Cases

### For Students
- **Course Selection**: Get predictions before enrolling in a subject
- **Risk Assessment**: Understand difficulty level and success probability
- **Academic Planning**: See which electives match your strengths
- **🏥 Performance Tracking**: Monitor GPA trends and progress

### For Academic Advisors
- **Early Intervention**: Identify at-risk students proactively
- **Course Recommendations**: Data-driven guidance for student planning
**Full API documentation**: http://localhost:9000/docs (Swagger UI)

---

## 🧪 Testing

Comprehensive test suite available in `backend/tests/`:

```bash
cd backend/tests

# Run all tests
python test_all.py

# Or run individual tests
python test_hybrid_predictions.py      # Test ML predictions
python test_batch_performance.py       # Test performance optimizations
python test_api_performance.py         # Test API endpoints
python test_academic_planner.py        # Test academic planning
```

For detailed testing documentation, see [backend/tests/README.md](backend/tests/README.md)

---

## 💻
### For Administrators
- **Curriculum Analysis**: Understand subject difficulty patterns
- **Success Metrics**: Track pass rates and student outcomes
- **Enrollment Planning**: Predict demand for courses
- **Performance Monitoring**: System-wide academic health dashboard
---

## 🚢 Production Deployment

### Quick Deployment (AWS EC2)

See [Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md) for step-by-step guide.

```bash
# 1. Clone repository on EC2
git clone https://github.com/YOUR_USERNAME/PathFinder---Personalized-Academic-Dashboard.git

# 2. Run deployment script
cd PathFinder---Personalized-Academic-Dashboard
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

For detailed deployment instructions, see [AWS EC2 Deployment Guide](docs/AWS_EC2_DEPLOYMENT.md)

---

## 🔴 Cassandra Connection Issues
- Verify cluster is accessible from your network
- Check `.env` credentials and connection settings
- Confirm datacenter name matches your cluster
- **Fallback**: System can use CSV files if Cassandra unavailable

### 🐍 Python 3.13 Compatibility
- Ensure `run.py` applies gevent monkey patching before imports
- asyncore module was removed in Python 3.13; gevent provides compatibility

### 🔑 JWT Token Errors
- Check `JWT_SECRET_KEY` in `.env`
- Verify token expiration settings
- Frontend must send Authorization header: `Bearer <token>`

### 🌐 CORS Errors
- Frontend proxy is configured in `vite.config.ts`
- Backend CORS is enabled in `main.py`
- Check `ALLOWED_ORIGINS` in backend `.env`

### 🤖 ML Model Not Loading
- Ensure model files exist in `backend/models/`:
  - `random_forest_model.pkl`
  - `label_encoders.pkl`
  - `model_metadata.json`
- If missing, train the model:
  ```bash
  cd backend/analysis
  python prepare_ml_data_from_cassandra.py
  python train_random_forest.py
  ```

---

## 🏆 Project Achievements

- ✅ **84.47% ML Accuracy** with Random Forest classifier
- ✅ **99,362 Training Records** across 4,483 students
- ✅ **Sub-10ms Predictions** with batch optimization
- ✅ **70+ Prerequisite Chains** manually defined by domain experts
- ✅ **Hybrid AI System** combining ML + rule-based approaches
- ✅ **Production-Ready** with comprehensive testing and documentation
- ✅ **Full-Stack Implementation** from data engineering to deployment

---

## 👥 Contributing

This project was developed as an academic research project. If you'd like to contribute or use this for educational purposes:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact & Support

For questions or support regarding this project:
- 📖 Check the [Documentation](docs/README.md)
- 🐛 Report issues on GitHub Issues
- 📚 Read the [ML Implementation Guide](docs/ML_IMPLEMENTATION.md)

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with scikit-learn for Machine Learning capabilities
- FastAPI for high-performance backend framework
- React and Material-UI for modern frontend experience
- Apache Cassandra for scalable data storage
- Sunway University for providing the academic dataset

---

**PathFinder** - Empowering students with AI-driven academic planning 🎓✨

## 📖 Database Schema

### Students Table (Cassandra)
- Student ID, demographics, programme details
- Overall CGPA, Year 1 CGPA
- Cohort, graduation status
- 23 columns total

### Subjects Table (Cassandra)
- Student-subject records
- Grades, percentages, exam details
- Subject codes, prerequisites
- 11 columns total

**Total Records**: 99,362+ student-subject pairs across 4,483 students

---

## 🤔
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