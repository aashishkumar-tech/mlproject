# Pre-Push Deployment Checklist

✅ **Complete this checklist before pushing to GitHub**

## 1. Code & Configuration

- [x] `app.py` - Flask application with prediction endpoints
- [x] `requirements.txt` - All dependencies listed
- [x] `Dockerfile` - Container configuration (2 workers, 120s timeout)
- [x] `.dockerignore` - Artifacts folder NOT excluded (models included)
- [x] `docker-compose.yml` - Local development setup
- [x] `.markdownlint.json` - Markdown linting configuration
- [x] `setup.py` - Package configuration

## 2. CI/CD Pipeline

- [x] `.github/workflows/ec2-deploy.yml` - Complete 3-stage pipeline
  - [x] CI job (tests & linting)
  - [x] Build & Push to ECR job
  - [x] Deploy to EC2 job

## 3. Documentation (Deployment-Focused)

- [x] `README.md` - Emphasizes deployment, CI/CD, DevOps aspects
- [x] `AWS-SETUP-GUIDE.md` - Step-by-step AWS deployment guide
- [x] `HLD.md` - High-level architecture with deployment focus
- [x] `TECHNICAL_DOC.md` - Implementation details
- [x] `API_DOCS.md` - API documentation
- [x] `CONTRIBUTING.md` - Contribution guidelines
- [x] `LICENSE` - MIT License

## 4. GitHub Secrets (Must Configure in GitHub)

Before pushing, ensure these secrets are configured in your GitHub repository:
Settings → Secrets and variables → Actions → New repository secret

- [ ] `AWS_ACCESS_KEY_ID` - IAM user access key
- [ ] `AWS_SECRET_ACCESS_KEY` - IAM user secret key
- [ ] `AWS_REGION` - us-east-1
- [ ] `ECR_REGISTRY` - 951897726242.dkr.ecr.us-east-1.amazonaws.com
- [ ] `ECR_REPOSITORY` - mlproject
- [ ] `EC2_HOST` - Your EC2 public IP (e.g., 34.228.159.84)
- [ ] `EC2_USER` - ec2-user
- [ ] `EC2_SSH_KEY` - Full content of .pem file (including BEGIN/END lines)

## 5. AWS Infrastructure (Must Be Running)

- [ ] EC2 instance is running
- [ ] Docker installed on EC2
- [ ] AWS CLI configured on EC2
- [ ] Security Group allows HTTP (80), SSH (22)
- [ ] ECR repository exists
- [ ] IAM user has ECR permissions

## 6. Files to Update Before Push

### README.md

Replace `YOUR_USERNAME` with your GitHub username in:

- Line 8: Badge URL
- Line 116: Clone URL
- And other occurrences

### Badges (Optional but Recommended)

Update these in README.md:

- Deployment badge (will work after first push)
- GitHub stats badges (replace YOUR_USERNAME)

## 7. Local Testing

Before pushing, test locally:

```bash
# Test Flask app
python app.py
# Visit http://localhost:8080

# Test Docker build
docker build -t mlproject:test .
docker run -d -p 80:8080 --name test mlproject:test
# Visit http://localhost
docker stop test && docker rm test
```

## 8. Git Repository

```bash
# Check all files are staged
git status

# Files that SHOULD be committed:
.github/workflows/ec2-deploy.yml
.dockerignore
.markdownlint.json
Dockerfile
docker-compose.yml
README.md
HLD.md
TECHNICAL_DOC.md
API_DOCS.md
AWS-SETUP-GUIDE.md
CONTRIBUTING.md
LICENSE
app.py
requirements.txt
setup.py
src/
templates/
static/
artifacts/  # Important: model files must be included

# Files that should NOT be committed (in .gitignore):
venv/
__pycache__/
*.pyc
logs/*.log
catboost_info/
mlproject.egg-info/
```

## 9. Security Review

- [x] No hardcoded credentials in code
- [x] AWS credentials stored as GitHub Secrets
- [x] SSH key stored as GitHub Secret (note: rotate after sharing in conversation)
- [x] .gitignore prevents committing sensitive files

## 10. Final Push Commands

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "feat: complete MLOps deployment with CI/CD pipeline

- Automated GitHub Actions workflow for EC2 deployment
- Docker containerization with ECR integration
- Comprehensive documentation focused on deployment
- Production-ready configuration (Gunicorn, health checks)
- AWS infrastructure setup guides"

# Push to main (triggers deployment)
git push origin main
```

## 11. Post-Push Verification

After pushing to GitHub:

1. **Check GitHub Actions**:
   - Go to: <https://github.com/aashishkumar-tech/mlproject/actions>
   - Verify all 3 jobs pass (CI → Build → Deploy)
   - Expected time: ~3 minutes

2. **Verify Deployment**:

   ```bash
   # Check application is live
   curl http://YOUR_EC2_IP/
   
   # SSH to EC2 and check container
   ssh -i ~/.ssh/mlproject-key.pem ec2-user@YOUR_EC2_IP
   docker ps
   docker logs mlproject
   ```

3. **Test Application**:
   - Visit: <http://YOUR_EC2_IP/>
   - Test prediction: <http://YOUR_EC2_IP/predictdata>

4. **Update README.md**:
   - Replace placeholder IP with your actual EC2 IP
   - Update badge URLs with your GitHub username
   - Commit and push updates

## 12. Security Post-Deployment

⚠️ **IMPORTANT**: After sharing SSH keys or AWS credentials in any conversation/chat:

```bash
# Rotate EC2 Key Pair
1. Create new key pair in AWS Console
2. Update EC2 instance key pair
3. Download new .pem file
4. Update EC2_SSH_KEY secret in GitHub

# Rotate AWS Credentials
1. Go to IAM Console → Users → github-actions-mlproject
2. Create new access key
3. Update AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY secrets
4. Delete old access key
```

## 13. Troubleshooting

If deployment fails:

1. **Check GitHub Actions logs** for specific error
2. **SSH to EC2** and run: `docker logs mlproject --tail 100`
3. **Common issues**:
   - Worker timeout → Already fixed (120s timeout)
   - Missing models → Artifacts not in .dockerignore ✓
   - SSH auth → Check EC2_SSH_KEY secret format
   - AWS credentials → Verify IAM permissions

## ✅ Ready to Push

Once all items are checked:

```bash
git push origin main
```

Watch the magic happen in GitHub Actions! 🚀

---

**Project Focus**: This is a **DevOps/MLOps portfolio project** showcasing:

- Automated CI/CD pipelines
- Cloud infrastructure deployment (AWS)
- Container orchestration (Docker)
- Production-grade configuration
- Comprehensive documentation

**Perfect for**: DevOps Engineer, MLOps Engineer, Cloud Engineer roles
