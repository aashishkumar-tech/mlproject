# API Documentation

## Overview

The Student Performance Prediction System provides a web-based interface for predicting student math scores. This document describes the available endpoints, request/response formats, and usage examples.

**Base URL**: `http://34.228.159.84` (Production)  
**Local URL**: `http://localhost:8080` (Development)

---

## Endpoints

### 1. Landing Page

**Endpoint**: `GET /`

**Description**: Returns the application landing page with project overview and navigation.

**Request**:

```http
GET / HTTP/1.1
Host: 34.228.159.84
```

**Response**:
- **Status Code**: 200 OK
- **Content-Type**: text/html
- **Body**: HTML page with project introduction and "Get Started" button

**Example**:

```bash
curl http://34.228.159.84/
```

---

### 2. Prediction Form (GET)

**Endpoint**: `GET /predictdata`

**Description**: Returns the prediction form page with input fields for student information.

**Request**:

```http
GET /predictdata HTTP/1.1
Host: 34.228.159.84
```

**Response**:
- **Status Code**: 200 OK
- **Content-Type**: text/html
- **Body**: HTML form with 7 input fields

**Form Fields**:
| Field Name | Type | Values | Required |
|------------|------|--------|----------|
| gender | select | male, female | Yes |
| ethnicity | select | group A, B, C, D, E | Yes |
| parental_level_of_education | select | 6 education levels | Yes |
| lunch | select | standard, free/reduced | Yes |
| test_preparation_course | select | none, completed | Yes |
| reading_score | number | 0-100 | Yes |
| writing_score | number | 0-100 | Yes |

**Example**:

```bash
curl http://34.228.159.84/predictdata
```

---

### 3. Make Prediction (POST)

**Endpoint**: `POST /predictdata`

**Description**: Accepts student information and returns predicted math score.

**Request**:

```http
POST /predictdata HTTP/1.1
Host: 34.228.159.84
Content-Type: application/x-www-form-urlencoded

gender=male&ethnicity=group+A&parental_level_of_education=bachelor%27s+degree&lunch=standard&test_preparation_course=completed&reading_score=72&writing_score=74
```

**Request Parameters**:

| Parameter | Type | Description | Example | Constraints |
|-----------|------|-------------|---------|-------------|
| gender | string | Student's gender | "male" | Required: male or female |
| ethnicity | string | Race/ethnicity group | "group A" | Required: group A/B/C/D/E |
| parental_level_of_education | string | Parent's education level | "bachelor's degree" | Required: see options below |
| lunch | string | Lunch type | "standard" | Required: standard or free/reduced |
| test_preparation_course | string | Test prep status | "completed" | Required: none or completed |
| reading_score | float | Reading test score | 72.0 | Required: 0-100 |
| writing_score | float | Writing test score | 74.0 | Required: 0-100 |

**Parental Education Options**:
- "some high school"
- "high school"
- "some college"
- "associate's degree"
- "bachelor's degree"
- "master's degree"

**Response**:
- **Status Code**: 200 OK
- **Content-Type**: text/html
- **Body**: HTML page with form and prediction result

**Success Response Example**:

```html
<div class="result">
    <h2>Predicted Math Score: 75.32</h2>
</div>
```

**Example using curl**:

```bash
curl -X POST http://34.228.159.84/predictdata \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "gender=male" \
  -d "ethnicity=group A" \
  -d "parental_level_of_education=bachelor's degree" \
  -d "lunch=standard" \
  -d "test_preparation_course=completed" \
  -d "reading_score=72" \
  -d "writing_score=74"
```

**Example using Python requests**:

```python
import requests

url = "http://34.228.159.84/predictdata"

data = {
    "gender": "male",
    "ethnicity": "group A",
    "parental_level_of_education": "bachelor's degree",
    "lunch": "standard",
    "test_preparation_course": "completed",
    "reading_score": 72,
    "writing_score": 74
}

response = requests.post(url, data=data)
print(response.text)  # HTML with prediction
```

**Example using JavaScript fetch**:

```javascript
const formData = new URLSearchParams({
    gender: 'male',
    ethnicity: 'group A',
    parental_level_of_education: "bachelor's degree",
    lunch: 'standard',
    test_preparation_course: 'completed',
    reading_score: 72,
    writing_score: 74
});

fetch('http://34.228.159.84/predictdata', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData
})
.then(response => response.text())
.then(html => console.log(html));
```

---

## Error Responses

### 400 Bad Request

**Scenario**: Missing required field or invalid value

**Response**:

```http
HTTP/1.1 400 Bad Request
Content-Type: text/html

<error message displayed in form>
```

**Example**: Missing reading_score parameter

---

### 500 Internal Server Error

**Scenario**: Server-side error (model loading failed, prediction error)

**Response**:

```http
HTTP/1.1 500 Internal Server Error
Content-Type: text/html

Internal Server Error
```

**Possible Causes**:
- Model file not found
- Invalid input data format
- Model inference timeout
- Memory issues

**Debugging**:

```bash
# Check Docker logs
docker logs mlproject --tail 100
```

---

## Data Model

### Input Data Schema

```python
{
    "gender": str,                          # "male" | "female"
    "race_ethnicity": str,                  # "group A" | "group B" | "group C" | "group D" | "group E"
    "parental_level_of_education": str,     # Education level string
    "lunch": str,                           # "standard" | "free/reduced"
    "test_preparation_course": str,         # "none" | "completed"
    "reading_score": float,                 # 0.0 to 100.0
    "writing_score": float                  # 0.0 to 100.0
}
```

### Output Data Schema

```python
{
    "predicted_math_score": float  # 0.0 to 100.0
}
```

---

## Usage Examples

### Example 1: High-Performing Student

**Input**:

```json
{
    "gender": "female",
    "ethnicity": "group E",
    "parental_level_of_education": "master's degree",
    "lunch": "standard",
    "test_preparation_course": "completed",
    "reading_score": 95,
    "writing_score": 93
}
```

**Expected Output**: ~92-98 (high score)

---

### Example 2: Student Needing Support

**Input**:

```json
{
    "gender": "male",
    "ethnicity": "group A",
    "parental_level_of_education": "some high school",
    "lunch": "free/reduced",
    "test_preparation_course": "none",
    "reading_score": 45,
    "writing_score": 48
}
```

**Expected Output**: ~40-50 (lower score indicating need for support)

---

### Example 3: Average Student

**Input**:

```json
{
    "gender": "female",
    "ethnicity": "group C",
    "parental_level_of_education": "some college",
    "lunch": "standard",
    "test_preparation_course": "none",
    "reading_score": 70,
    "writing_score": 68
}
```

**Expected Output**: ~65-72 (average score)

---

## Rate Limiting

Currently, there is **no rate limiting** implemented. 

**Recommended limits for production**:
- 100 requests per minute per IP
- 1000 requests per hour per IP

**Future implementation** (using Flask-Limiter):

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per minute"]
)

@app.route('/predictdata', methods=['POST'])
@limiter.limit("10 per minute")
def predict_datapoint():
    # ... prediction logic
```

---

## Performance Metrics

### Response Times

| Endpoint | Average Response Time | 95th Percentile |
|----------|----------------------|-----------------|
| GET / | ~50ms | ~100ms |
| GET /predictdata | ~50ms | ~100ms |
| POST /predictdata | ~5-10s | ~15s |

**Note**: First prediction after container start may take 10-15 seconds due to model loading.

### Concurrent Requests

Current configuration supports:
- **Max concurrent requests**: ~4 (2 Gunicorn workers × 2 threads)
- **Queue capacity**: Limited by Gunicorn backlog (default 2048)

---

## Health Check

**Endpoint**: `GET /` (can be used for health checks)

**Health Check Script**:

```bash
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://34.228.159.84/)
if [ $response -eq 200 ]; then
    echo "Service is healthy"
    exit 0
else
    echo "Service is unhealthy (HTTP $response)"
    exit 1
fi
```

**Docker Health Check** (add to Dockerfile):

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/ || exit 1
```

---

## Authentication

Currently, **no authentication** is required.

**Future implementation recommendations**:
- API key-based authentication for programmatic access
- OAuth2 for user authentication
- JWT tokens for session management

---

## Versioning

**Current Version**: v1.0.0

**Future API Versioning**:

```
/api/v1/predict    # Version 1
/api/v2/predict    # Version 2 with breaking changes
```

---

## CORS Policy

**Current Policy**: No CORS headers set (same-origin only)

**Enable CORS** (for cross-origin requests):

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/predictdata": {"origins": "*"}})
```

---

## Logging

All API requests are logged with the following information:
- Timestamp
- Request method and path
- Response status code
- Processing time

**Log Format**:

```
[2026-02-01 15:11:38] POST /predictdata - 200 OK - 8.52s
```

**Access Logs** (Gunicorn):

```bash
docker logs mlproject 2>&1 | grep "POST /predictdata"
```

---

## Future API Enhancements

### Planned Features

1. **REST API with JSON responses**

   ```python
   @app.route('/api/v1/predict', methods=['POST'])
   def api_predict():
       data = request.get_json()
       # ... prediction logic
       return jsonify({
           'predicted_math_score': float(result),
           'confidence': 0.85,
           'model_version': '1.0.0'
       })
   ```

2. **Batch predictions**

   ```python
   @app.route('/api/v1/predict/batch', methods=['POST'])
   def batch_predict():
       students = request.get_json()['students']
       results = []
       for student in students:
           # ... predict for each
           results.append(prediction)
       return jsonify({'predictions': results})
   ```

3. **Model explainability**

   ```python
   @app.route('/api/v1/explain', methods=['POST'])
   def explain_prediction():
       # ... SHAP values or feature importance
       return jsonify({
           'prediction': 75.0,
           'feature_importance': {
               'reading_score': 0.35,
               'writing_score': 0.30,
               'parental_education': 0.20,
               # ...
           }
       })
   ```

4. **Prediction history**

   ```python
   @app.route('/api/v1/predictions/history', methods=['GET'])
   def get_history():
       # ... retrieve from database
       return jsonify({'predictions': [...]})
   ```

---

## Testing the API

### Manual Testing with Postman

1. **Import Collection**:

   ```json
   {
     "info": {
       "name": "Student Performance API",
       "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
     },
     "item": [
       {
         "name": "Make Prediction",
         "request": {
           "method": "POST",
           "header": [
             {
               "key": "Content-Type",
               "value": "application/x-www-form-urlencoded"
             }
           ],
           "body": {
             "mode": "urlencoded",
             "urlencoded": [
               {"key": "gender", "value": "male"},
               {"key": "ethnicity", "value": "group A"},
               {"key": "parental_level_of_education", "value": "bachelor's degree"},
               {"key": "lunch", "value": "standard"},
               {"key": "test_preparation_course", "value": "completed"},
               {"key": "reading_score", "value": "72"},
               {"key": "writing_score", "value": "74"}
             ]
           },
           "url": {
             "raw": "http://34.228.159.84/predictdata",
             "protocol": "http",
             "host": ["34", "228", "159", "84"],
             "path": ["predictdata"]
           }
         }
       }
     ]
   }
   ```

### Automated Testing with pytest

```python
# tests/test_api.py
import requests
import pytest

BASE_URL = "http://34.228.159.84"

def test_landing_page():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "Student Performance" in response.text

def test_prediction_form():
    response = requests.get(f"{BASE_URL}/predictdata")
    assert response.status_code == 200
    assert "gender" in response.text

def test_make_prediction():
    data = {
        "gender": "male",
        "ethnicity": "group A",
        "parental_level_of_education": "bachelor's degree",
        "lunch": "standard",
        "test_preparation_course": "completed",
        "reading_score": 72,
        "writing_score": 74
    }
    response = requests.post(f"{BASE_URL}/predictdata", data=data)
    assert response.status_code == 200
    assert "Predicted Math Score" in response.text

def test_invalid_input():
    data = {
        "gender": "invalid",
        # ... missing required fields
    }
    response = requests.post(f"{BASE_URL}/predictdata", data=data)
    assert response.status_code in [400, 500]
```

---

## Support

For API-related questions or issues:
- **GitHub Issues**: https://github.com/YOUR_USERNAME/mlproject/issues
- **Documentation**: See [TECHNICAL_DOC.md](TECHNICAL_DOC.md)
- **Email**: [YOUR_EMAIL]

---

**Last Updated**: February 1, 2026  
**API Version**: 1.0.0
