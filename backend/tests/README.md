# PathFinder Test Suite

This folder contains all test files for the PathFinder Academic Dashboard backend.

## Test Files

### `test_all.py` - Comprehensive Test Suite ⭐
**Run this file to execute all tests at once**

```bash
cd backend/tests
python test_all.py
```

Combines all tests into one comprehensive suite:
- Hybrid Prediction System
- Batch Performance Testing
- API Performance Testing
- Academic Planner Integration

---

### `test_hybrid_predictions.py` - Hybrid ML System Tests
Tests the integrated Random Forest + Rule-based hybrid prediction system.

**What it tests:**
- ML model availability and loading
- Hybrid predictions for sample students
- Prediction method (rule-based, ML, or hybrid)
- Success probabilities and risk levels
- Top contributing factors from ML
- Prerequisite analysis
- Cohort statistics

**Run:**
```bash
python test_hybrid_predictions.py
```

**Sample students tested:**
- Student 9897587 → CSC3206 (AI Course)
- Student 2733926 → NET3106 (Network Security)
- Student 2721492 → CSC2103 (Data Structures)

---

### `test_batch_performance.py` - Performance Optimization Tests
Compares batch inference vs individual predictions to measure performance improvements.

**What it tests:**
- Batch prediction performance
- Individual prediction performance
- Cache effectiveness
- ML model batch vs individual inference
- Speedup calculations

**Run:**
```bash
python test_batch_performance.py
```

**Expected results:**
- ✅ ~2x speedup with batch processing
- ✅ ~2.4x speedup for ML model inference
- ✅ Cache hit improvements

---

### `test_api_performance.py` - API Endpoint Tests
Tests backend API endpoints to identify performance bottlenecks.

**What it tests:**
- Health check endpoint
- List variants endpoint
- Get electives endpoint
- Get all courses endpoint
- Response times and payload sizes

**Run:**
```bash
python test_api_performance.py
```

**Note:** Backend server must be running (`python run.py`)

**Performance benchmarks:**
- 🟢 FAST: < 1.0 second
- 🟡 SLOW: 1.0 - 5.0 seconds
- 🔴 VERY SLOW: > 5.0 seconds

---

### `test_academic_planner.py` - Academic Planning Tests
Tests the complete academic planner workflow with ML predictions.

**What it tests:**
- Loading student data from CSV
- Loading program variants
- Computing student progress
- Finding eligible electives (with prerequisites met)
- Running ML predictions for available courses
- Ranking recommendations by success probability

**Run:**
```bash
# Default student (2733926)
python test_academic_planner.py

# Specific student
python test_academic_planner.py 9897587

# Specific student and variant
python test_academic_planner.py 9897587 202301 normal
```

**Arguments:**
1. Student ID (default: 2733926)
2. Intake (default: 202301)
3. Entry type (default: normal)

---

## Running All Tests

### Quick Run
```bash
cd backend/tests
python test_all.py
```

### Individual Tests
```bash
# Test hybrid predictions
python test_hybrid_predictions.py

# Test batch performance
python test_batch_performance.py

# Test API performance (requires backend running)
python test_api_performance.py

# Test academic planner
python test_academic_planner.py
```

---

## Prerequisites

### Python Dependencies
All required packages should be installed:
```bash
cd backend
pip install -r requirements.txt
```

### Data Requirements
- `backend/data/flattened_students_subjects.csv` or `backend/data/subjectplanning_students.csv`
- `backend/models/random_forest_model.pkl` (for ML tests)
- `backend/models/label_encoders.pkl` (for ML tests)

### Backend Server (for API tests only)
```bash
cd backend
python run.py
```

---

## Test Output

Each test provides detailed output including:
- ✅ Success indicators
- ❌ Error messages with stack traces
- 📊 Statistics and metrics
- ⏱️ Performance timings
- 💡 Recommendations
- 🎯 Prediction results

---

## Troubleshooting

### ML Model Not Available
```
⚠ ML Model is NOT available
```
**Solution:** Train the model first:
```bash
cd backend/analysis
python prepare_ml_data_from_cassandra.py
python train_random_forest.py
```

### Data Not Loaded
```
❌ Data not loaded!
```
**Solution:** Ensure CSV files exist in `backend/data/`

### API Connection Failed
```
❌ Cannot connect to backend
```
**Solution:** Start the backend server:
```bash
cd backend
python run.py
```

---

## Adding New Tests

To add new tests to the suite:

1. Create new test file: `test_yourfeature.py`
2. Add test function: `def test_yourfeature():`
3. Import and call in `test_all.py`:
   ```python
   from test_yourfeature import test_yourfeature
   
   def main():
       # ... existing tests ...
       test_yourfeature()
   ```

---

*Last updated: December 2025*
