# High-Level Design (HLD) - Student Performance Prediction System

## 1. System Overview

The Student Performance Prediction System is a production-grade Machine Learning web application that predicts student math scores based on demographic and academic features. The system follows a modular architecture with clear separation between data processing, model training, prediction, and deployment layers.

### 1.1 System Purpose

- **Primary Goal**: Predict student math scores to help educators identify students who may need additional support
- **Target Users**: Educational institutions, teachers, administrators
- **Key Benefit**: Early intervention and personalized learning strategies

---

## 2. Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────┐              ┌────────────────┐                 │
│  │  Landing Page │              │ Prediction Form│                 │
│  │  (index.html) │──────────────│  (home.html)   │                 │
│  └───────────────┘              └────────────────┘                 │
│         │                                │                           │
└─────────┼────────────────────────────────┼───────────────────────────┘
          │                                │
          ▼                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      WEB APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Flask Application (app.py)                │   │
│  │                                                               │   │
│  │  Routes:                                                      │   │
│  │  • GET  /            → Landing page                          │   │
│  │  • GET  /predictdata → Prediction form                       │   │
│  │  • POST /predictdata → Process prediction                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                     │
└────────────────────────────────┼─────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PREDICTION PIPELINE LAYER                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────┐         ┌──────────────────┐                   │
│  │  CustomData    │────────▶│ PredictPipeline  │                   │
│  │  (Data Model)  │         │                  │                   │
│  └────────────────┘         └──────────────────┘                   │
│         │                            │                               │
│         │ Transform to DataFrame     │ Load Models                  │
│         ▼                            ▼                               │
│  ┌────────────────────────────────────────────┐                    │
│  │      get_data_as_data_frame()              │                    │
│  └────────────────────────────────────────────┘                    │
│                                │                                     │
└────────────────────────────────┼─────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        MODEL LAYER (ARTIFACTS)                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────┐         ┌──────────────────────┐         │
│  │  preprocessor.pkl    │         │     model.pkl         │         │
│  │  (Transformer)       │────────▶│  (Trained ML Model)   │         │
│  └──────────────────────┘         └──────────────────────┘         │
│          │                                  │                        │
│          │ Feature Engineering              │ Prediction             │
│          ▼                                  ▼                        │
│  • One-Hot Encoding                  • Random Forest /              │
│  • Standard Scaling                    Gradient Boosting /          │
│  • Ordinal Encoding                    XGBoost / CatBoost           │
│                                                                       │
└───────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │  Prediction   │
                         │   Result      │
                         └───────────────┘
```

---

## 3. Component Architecture

### 3.1 Training Pipeline

```text
┌────────────────┐      ┌─────────────────────┐      ┌────────────────┐
│ Data Ingestion │─────▶│ Data Transformation │─────▶│ Model Training │
└────────────────┘      └─────────────────────┘      └────────────────┘
        │                        │                             │
        ▼                        ▼                             ▼
  • Load CSV            • Feature Engineering          • Model Selection
  • Train/Test Split    • Encoding (Numerical/         • Hyperparameter
  • Validation            Categorical)                   Tuning
                        • Scaling                       • Evaluation
                        • Save Preprocessor             • Save Best Model
```

### 3.2 Inference Pipeline

```text
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────┐
│ User Input  │─────▶│ CustomData   │─────▶│ Preprocessor│─────▶│  Model   │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────┘
                             │                     │                    │
                             ▼                     ▼                    ▼
                      • Validate Input      • Transform          • Predict
                      • Convert to DF       • Scale/Encode       • Return Score
```

---

## 4. Data Flow

### 4.1 Training Data Flow

```text
1. Raw Data (stud.csv)
   ↓
2. Data Ingestion Component
   ├─→ train.csv (80%)
   ├─→ test.csv (20%)
   └─→ data.csv (full dataset)
   ↓
3. Data Transformation Component
   ├─→ Numerical Pipeline (StandardScaler)
   ├─→ Categorical Pipeline (OneHotEncoder / OrdinalEncoder)
   └─→ preprocessor.pkl
   ↓
4. Model Trainer Component
   ├─→ Train multiple models (RF, GB, XGB, CatBoost)
   ├─→ Evaluate using R² score
   └─→ Save best model → model.pkl
```

### 4.2 Prediction Data Flow

```text
1. User Form Submission
   ├─→ gender
   ├─→ race_ethnicity
   ├─→ parental_level_of_education
   ├─→ lunch
   ├─→ test_preparation_course
   ├─→ reading_score
   └─→ writing_score
   ↓
2. CustomData Class
   ├─→ Validate inputs
   └─→ Convert to pandas DataFrame
   ↓
3. PredictPipeline
   ├─→ Load preprocessor.pkl
   ├─→ Transform features
   ├─→ Load model.pkl
   └─→ Generate prediction
   ↓
4. Return predicted math_score
```

---

## 5. Deployment Architecture

### 5.1 CI/CD Pipeline

```text
┌──────────────────────────────────────────────────────────────────────┐
│                          GITHUB REPOSITORY                            │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ Push to main
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      GITHUB ACTIONS WORKFLOW                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────┐      ┌──────────────────┐      ┌────────────────┐ │
│  │   CI Job    │─────▶│ Build & Push Job │─────▶│   Deploy Job   │ │
│  └─────────────┘      └──────────────────┘      └────────────────┘ │
│        │                       │                         │           │
│        ▼                       ▼                         ▼           │
│  • Run tests           • Build Docker Image      • SSH to EC2       │
│  • Linting             • Tag with SHA            • Pull from ECR    │
│                        • Push to ECR             • Stop old         │
│                                                   • Start new        │
└──────────────────────────────────────────────────────────────────────┘
                                                           │
                                                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                          AWS INFRASTRUCTURE                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    AWS ECR (Container Registry)              │    │
│  │  951897726242.dkr.ecr.us-east-1.amazonaws.com/mlproject     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                │                                      │
│                                ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    AWS EC2 Instance (t2.micro)               │    │
│  │  • Amazon Linux 2023                                         │    │
│  │  • Docker Engine                                             │    │
│  │  • Public IP: 34.228.159.84                                  │    │
│  │  • Security Group: SSH(22), HTTP(80), HTTPS(443)            │    │
│  │                                                               │    │
│  │  ┌────────────────────────────────────────────────────┐     │    │
│  │  │         Docker Container (mlproject)                │     │    │
│  │  │  • Port Mapping: 80:8080                           │     │    │
│  │  │  • Gunicorn (2 workers, 120s timeout)              │     │    │
│  │  │  • Flask Application                                │     │    │
│  │  └────────────────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │  End Users    │
                        │  (HTTP:80)    │
                        └───────────────┘
```

### 5.2 Container Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    Docker Container                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Gunicorn WSGI Server                       │   │
│  │  • 2 worker processes                                │   │
│  │  • 120 second timeout                                │   │
│  │  • Binds to 0.0.0.0:8080                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Flask Application (app.py)                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Application Code                        │   │
│  │  • src/pipeline/predict_pipeline.py                 │   │
│  │  • src/components/                                   │   │
│  │  • artifacts/ (models)                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Base Image: python:3.10-slim                                │
└─────────────────────────────────────────────────────────────┘
        │
        │ Port Mapping
        ▼
    Host Port 80
```

---

## 6. Technology Stack

### 6.1 Machine Learning Stack

| Component            | Technology        | Purpose                          |
| -------------------- | ----------------- | -------------------------------- |
| Programming Language | Python 3.10       | Core development language        |
| ML Framework         | scikit-learn      | Model training and preprocessing |
| Ensemble Models      | XGBoost, CatBoost | Advanced boosting algorithms     |
| Data Processing      | pandas, numpy     | Data manipulation                |
| Model Serialization  | dill              | Saving/loading models            |

### 6.2 Web Stack

| Component   | Technology | Purpose                      |
| ----------- | ---------- | ---------------------------- |
| Web Framework | Flask      | HTTP server and routing      |
| WSGI Server | Gunicorn   | Production-grade app server  |
| Templating  | Jinja2     | HTML template rendering      |
| Forms       | HTML5      | User input collection        |
| Styling     | CSS3       | UI presentation              |

### 6.3 DevOps Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containerization | Docker | Application packaging |
| CI/CD | GitHub Actions | Automated deployment pipeline |
| Container Registry | AWS ECR | Docker image storage |
| Compute | AWS EC2 (t2.micro) | Application hosting |
| Networking | AWS VPC, Security Groups | Network isolation and security |
| Version Control | Git/GitHub | Source code management |

---

## 7. Security Architecture

### 7.1 Network Security

```text
┌────────────────────────────────────────────────────────────┐
│                    Internet (Public)                        │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │   AWS Security Group    │
              │  • Port 22 (SSH)        │
              │  • Port 80 (HTTP)       │
              │  • Port 443 (HTTPS)     │
              └─────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │    EC2 Instance         │
              │  • Private IP           │
              │  • Public IP (Elastic)  │
              └─────────────────────────┘
```

### 7.2 Authentication & Authorization

- **GitHub Secrets**: Encrypted storage for AWS credentials, SSH keys
- **IAM User**: Dedicated user with minimal permissions (ECR only)
- **SSH Key Pair**: RSA key-based authentication for EC2 access
- **Network Isolation**: Security groups restrict inbound traffic

### 7.3 Data Security

- **Model Artifacts**: Stored in container, not exposed via HTTP
- **Logging**: No sensitive data logged
- **Input Validation**: Form validation on client and server side

---

## 8. Scalability Considerations

### 8.1 Current Limitations

- **Single EC2 Instance**: No high availability
- **t2.micro Resources**: 1 vCPU, 1GB RAM
- **Stateful Deployment**: No horizontal scaling

### 8.2 Future Scaling Options

```text
Current Architecture:
┌────────────┐
│   EC2      │ ← Single point of failure
└────────────┘

Scalable Architecture:
                ┌────────────────┐
                │  Load Balancer │
                └────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    ┌───────┐       ┌───────┐       ┌───────┐
    │  EC2  │       │  EC2  │       │  EC2  │
    └───────┘       └───────┘       └───────┘
```

**Recommendations**:

- Use Auto Scaling Groups for EC2
- Add Application Load Balancer
- Implement model caching (Redis)
- Use RDS for storing predictions
- Consider serverless (AWS Lambda + API Gateway)

---

## 9. Monitoring & Observability

### 9.1 Current Monitoring

- **Docker Logs**: `docker logs mlproject`
- **Application Logs**: Stored in `logs/` directory
- **GitHub Actions**: Build and deployment status

### 9.2 Recommended Monitoring

```text
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐      ┌──────────────┐                  │
│  │  CloudWatch    │──────│  Prometheus  │                  │
│  │  • Metrics     │      │  • Scraping  │                  │
│  │  • Alarms      │      └──────────────┘                  │
│  └────────────────┘             │                           │
│                                  ▼                           │
│                      ┌──────────────────┐                   │
│                      │    Grafana       │                   │
│                      │  • Dashboards    │                   │
│                      │  • Alerting      │                   │
│                      └──────────────────┘                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Key Metrics to Track**:

- Request latency
- Prediction success rate
- Model inference time
- CPU/Memory utilization
- Error rates (4xx, 5xx)

---

## 10. Disaster Recovery

### 10.1 Backup Strategy

| Component | Backup Method | Frequency |
|-----------|--------------|-----------|
| Source Code | Git repository | Every commit |
| Docker Images | ECR versioning | Every build (SHA tags) |
| Model Artifacts | S3 backup (future) | After retraining |
| EC2 Instance | AMI snapshots (future) | Weekly |

### 10.2 Recovery Procedures

**Container Failure**:

```bash
docker stop mlproject
docker rm mlproject
docker pull <ECR_REGISTRY>/mlproject:latest
docker run -d -p 80:8080 --name mlproject <ECR_REGISTRY>/mlproject:latest
```

**EC2 Instance Failure**:

1. Launch new EC2 instance
2. Install Docker and AWS CLI
3. Update GitHub Secrets with new EC2_HOST
4. Trigger GitHub Actions workflow

---

## 11. Cost Analysis

### 11.1 Current AWS Costs (Free Tier)

| Service | Usage | Cost |
|---------|-------|------|
| EC2 (t2.micro) | 750 hrs/month | $0.00 (free tier) |
| ECR Storage | < 10GB | $0.00 (free tier) |
| Data Transfer | Minimal | $0.00 (free tier) |
| **Total** | | **$0.00/month** |

### 11.2 Post-Free-Tier Costs

| Service | Usage | Estimated Cost |
|---------|-------|---------------|
| EC2 (t2.micro) | 24/7 | ~$8.50/month |
| ECR Storage | 5GB | ~$0.50/month |
| Data Transfer | 10GB | ~$0.90/month |
| **Total** | | **~$10/month** |

---

## 12. System Constraints

### 12.1 Technical Constraints

- **Memory**: Limited to 1GB RAM (t2.micro)
- **CPU**: Single vCPU, shared
- **Storage**: EBS volume, limited IOPS
- **Network**: Variable latency

### 12.2 Operational Constraints

- **Deployment**: ~3 minutes per deployment
- **Downtime**: Brief interruption during deployments
- **Concurrent Users**: Limited by single instance capacity

### 12.3 Model Constraints

- **Training Data**: Fixed dataset (no real-time learning)
- **Inference Time**: ~5-10 seconds per prediction
- **Model Size**: Must fit in container memory

---

## 13. Future Roadmap

### Phase 1: Immediate Improvements

- [ ] Add HTTPS with SSL certificate
- [ ] Implement health check endpoint
- [ ] Add request logging and analytics
- [ ] Set up CloudWatch monitoring

### Phase 2: Feature Enhancements

- [ ] REST API with FastAPI
- [ ] Model versioning and A/B testing
- [ ] User authentication
- [ ] Prediction history tracking

### Phase 3: Infrastructure Upgrades

- [ ] Multi-AZ deployment
- [ ] Load balancing
- [ ] Database integration (RDS)
- [ ] CDN for static assets (CloudFront)

### Phase 4: ML Pipeline Improvements

- [ ] Automated model retraining
- [ ] Feature store implementation
- [ ] Model monitoring and drift detection
- [ ] Explainability dashboard (SHAP values)

---

## 14. Conclusion

This High-Level Design document outlines a production-ready ML system with:

- ✅ Modular architecture for maintainability
- ✅ Automated CI/CD for rapid deployments
- ✅ Containerized deployment for consistency
- ✅ Scalable design patterns for future growth
- ✅ Security best practices
- ✅ Cost-effective infrastructure (Free Tier)

The system successfully balances simplicity for a portfolio project with professional-grade architecture principles suitable for real-world applications.
