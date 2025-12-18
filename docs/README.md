# PathFinder Documentation

Welcome to the PathFinder Academic Dashboard documentation. This folder contains all technical documentation, implementation guides, and system specifications.

---

## 📚 Documentation Overview

### System Architecture & Design

#### [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)
Complete system architecture documentation covering:
- System architecture diagrams
- Application startup flow
- User authentication flow
- Subject prediction flow (end-to-end)
- ML model training & deployment
- Data flow architecture
- Component interactions
- Performance optimizations

#### [USE_CASE_DIAGRAM.md](USE_CASE_DIAGRAM.md)
Use case diagrams and descriptions:
- Mermaid and PlantUML diagram syntax
- 10 main use cases with detailed descriptions
- System actors and interactions
- Non-functional requirements
- Technology stack overview

#### [ANSWERS_Architecture.md](ANSWERS_Architecture.md)
Q&A format architecture documentation:
- Design decisions and rationale
- Technology choices explained
- Common architecture questions answered

---

### Machine Learning & Predictions

#### [ML_IMPLEMENTATION.md](ML_IMPLEMENTATION.md) ⭐
**Comprehensive ML implementation guide:**
- Hybrid prediction system overview
- Data preparation process (99,362 records)
- Feature engineering (33 features)
- Random Forest model training
- Model performance (84.47% accuracy)
- Feature importance analysis
- Integration with rule-based system
- API and frontend updates
- Files created and modified

#### [BATCH_OPTIMIZATION.md](BATCH_OPTIMIZATION.md)
Performance optimization documentation:
- Batch inference vs individual predictions
- 2x speedup with batch processing
- Cache implementation strategies
- ML model batch inference
- Performance benchmarks and results

#### [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md)
Algorithm performance metrics:
- Batch processing efficiency
- System response times
- Hybrid prediction architecture
- Accuracy metrics and validation
- Feature importance rankings
- Real-world performance benchmarks

---

### Deployment & Operations

#### [AWS_EC2_DEPLOYMENT.md](AWS_EC2_DEPLOYMENT.md)
Complete AWS deployment guide:
- EC2 instance setup
- Security group configuration
- Backend deployment
- Frontend deployment
- Nginx configuration
- SSL/HTTPS setup
- Environment variables
- Troubleshooting guide

#### [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
Quick deployment checklist:
- Pre-deployment tasks
- AWS console setup
- Code changes needed
- Step-by-step deployment
- Verification steps
- Service management commands

---

## 🚀 Quick Start Guide

### For Developers
1. Start with [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) to understand the architecture
2. Read [ML_IMPLEMENTATION.md](ML_IMPLEMENTATION.md) for ML system details
3. Check [BATCH_OPTIMIZATION.md](BATCH_OPTIMIZATION.md) for performance tips

### For ML Engineers
1. Read [ML_IMPLEMENTATION.md](ML_IMPLEMENTATION.md) for complete ML pipeline
2. Review [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md) for metrics
3. Check [BATCH_OPTIMIZATION.md](BATCH_OPTIMIZATION.md) for optimization techniques

### For DevOps/Deployment
1. Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for quick deployment
2. Refer to [AWS_EC2_DEPLOYMENT.md](AWS_EC2_DEPLOYMENT.md) for detailed steps
3. Use service management commands from checklist

### For Academic/Reporting
1. Start with [USE_CASE_DIAGRAM.md](USE_CASE_DIAGRAM.md) for use cases
2. Reference [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) for architecture
3. Use [ML_IMPLEMENTATION.md](ML_IMPLEMENTATION.md) for ML methodology
4. Include [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md) for metrics

---

## 📊 Key Metrics & Achievements

### Machine Learning
- **Model Accuracy**: 84.47% (Random Forest)
- **ROC-AUC Score**: 0.8746
- **Training Data**: 99,362 student-subject pairs
- **Features**: 23 selected from 33 engineered features
- **Prediction Method**: Hybrid (70% ML + 30% Rule-based)

### Performance
- **Prediction Speed**: < 10ms per prediction
- **Batch Speedup**: 2x faster than individual predictions
- **ML Inference**: < 7ms
- **API Response**: < 100ms (95th percentile)

### System Scale
- **Students**: 4,483+ profiles
- **Subjects**: 246+ unique courses
- **Subject Records**: 99,362+ entries
- **Prerequisite Chains**: 70+ defined relationships

---

## 🔗 Related Resources

### Backend Code
- **Prediction Service**: `backend/app/services/subject_prediction_service.py`
- **ML Service**: `backend/app/services/ml_prediction_service.py`
- **Training Scripts**: `backend/analysis/`
- **Tests**: `backend/tests/`

### Frontend Code
- **Dashboard**: `frontend/src/components/Dashboard.tsx`
- **API Services**: `frontend/services/`
- **Redux State**: `frontend/features/`

### Data & Models
- **Training Data**: `backend/data/ml_training_data.csv`
- **Trained Model**: `backend/models/random_forest_model.pkl`
- **Raw Data**: `backend/data/studentsTable.csv`, `backend/data/subjectsTable.csv`

---

## 📝 Document Updates

When updating documentation:
1. Keep metrics and statistics current
2. Update code references if files are moved
3. Add new features to appropriate sections
4. Update the quick start guides as needed
5. Maintain consistent formatting

---

## 🤝 Contributing

When adding new documentation:
1. Create new .md file in this folder
2. Add entry to this README under appropriate section
3. Link related documents together
4. Update quick start guides if relevant
5. Keep technical depth appropriate for audience

---

*Documentation last updated: December 2025*
*PathFinder Academic Dashboard - A Hybrid ML + Rule-based Academic Planning System*
