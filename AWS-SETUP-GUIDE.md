# AWS Setup Guide - Step by Step

Complete guide to deploy your ML project to AWS EC2 with ECR and GitHub Actions CI/CD.

---

## Prerequisites

- AWS Account with billing enabled
- GitHub repository with your code
- Basic familiarity with AWS Console

---

## Step 1: Create IAM User for GitHub Actions

### 1.1 Open IAM Console

1. Sign in to AWS Console: <https://console.aws.amazon.com/>
2. Search for **IAM** in the top search bar
3. Click **IAM** service

### 1.2 Create New User

1. Click **Users** in left sidebar
2. Click **Create user** button
3. **User name**: `github-actions-mlproject`
4. Click **Next**

### 1.3 Set Permissions

1. Select **Attach policies directly**
2. Search and check these policies:
   - `AmazonEC2ContainerRegistryFullAccess`
3. Click **Next**
4. Click **Create user**

### 1.4 Create Access Keys

1. Click on the user you just created
2. Go to **Security credentials** tab
3. Scroll to **Access keys** section
4. Click **Create access key**
5. Select **Application running outside AWS**
6. Click **Next** → **Create access key**
7. **IMPORTANT**: Copy and save:
   - Access key ID (e.g., `AKIAIOSFODNN7EXAMPLE`)
   - Secret access key (e.g., `wJalrXUtnFEMI/K7MDENG...`)
   - You'll add these to GitHub Secrets later

---

## Step 2: Create ECR Repository

### 2.1 Open ECR Console

1. Search for **ECR** in AWS Console search bar
2. Click **Elastic Container Registry**

### 2.2 Create Repository

1. Click **Get Started** or **Create repository**
2. **Visibility**: Select **Private**
3. **Repository name**: `mlproject`
4. Leave other settings as default
5. Click **Create repository**

### 2.3 Note Repository Details

After creation, you'll see:

- **Repository URI**: `123456789012.dkr.ecr.us-east-1.amazonaws.com/mlproject`
- Copy the part BEFORE `/mlproject` → This is your **ECR_REGISTRY**
  - Example: `123456789012.dkr.ecr.us-east-1.amazonaws.com`
- The repository name is: `mlproject` → This is your **ECR_REPOSITORY**

---

## Step 3: Launch EC2 Instance

### 3.1 Open EC2 Console

1. Search for **EC2** in AWS Console
2. Click **EC2** service

### 3.2 Create Key Pair (if you don't have one)

1. In left sidebar, click **Key Pairs** (under Network & Security)
2. Click **Create key pair**
3. **Name**: `mlproject-key`
4. **Key pair type**: RSA
5. **Private key format**: `.pem`
6. Click **Create key pair**
7. **IMPORTANT**: File downloads automatically - save it securely!
8. Move to safe location:

   ```bash
   # On Windows (PowerShell):
   Move-Item ~/Downloads/mlproject-key.pem ~/.ssh/
   
   # On Mac/Linux:
   mv ~/Downloads/mlproject-key.pem ~/.ssh/
   chmod 400 ~/.ssh/mlproject-key.pem
   ```

### 3.3 Create Security Group

1. In left sidebar, click **Security Groups**
2. Click **Create security group**
3. **Security group name**: `mlproject-sg`
4. **Description**: `Allow SSH and HTTP for ML project`
5. **VPC**: Leave default

6. **Add Inbound rules** (click "Add rule" for each):
   - **Rule 1**:
     - Type: `SSH`
     - Port: `22`
     - Source: `My IP` (for your IP) or `0.0.0.0/0` (anywhere - less secure)
   - **Rule 2**:
     - Type: `HTTP`
     - Port: `80`
     - Source: `0.0.0.0/0` (Anywhere IPv4)
   - **Rule 3** (optional for HTTPS later):
     - Type: `HTTPS`
     - Port: `443`
     - Source: `0.0.0.0/0`

7. Click **Create security group**

### 3.4 Launch Instance

1. Go to **EC2 Dashboard**
2. Click **Launch instance** button

#### Instance Configuration

1. **Name**: `mlproject-server`

2. **Application and OS Images (AMI)**:

   - Select **Amazon Linux 2023 AMI** (free tier eligible)
   - OR **Ubuntu Server 22.04 LTS**

3. **Instance type**:

   - Select **t3.medium** (2 vCPU, 4GB RAM - recommended for ML)
   - Or **t2.medium** if t3 not available
   - Note: t2.micro (free tier) may be too small for ML models

4. **Key pair**:

   - Select the key pair you created: `mlproject-key`

5. **Network settings**:

   - Click **Edit**
   - **Firewall (security groups)**: Select existing security group
   - Choose: `mlproject-sg`

6. **Configure storage**:

   - Change to **20 GB** or **30 GB** (free tier allows up to 30GB)

7. Click **Launch instance**

8. Wait 1-2 minutes for instance to start

### 3.5 Note Instance Details

1. Go to **Instances** in left sidebar
2. Click on your instance
3. Copy and save these from the **Details** tab:

   - **Public IPv4 address** (e.g., `54.123.45.67`) → This is **EC2_HOST**
   - **Public IPv4 DNS** (e.g., `ec2-54-123-45-67.compute-1.amazonaws.com`)

---

## Step 4: Configure EC2 Instance

### 4.1 Connect via SSH

```bash
# On Windows PowerShell:
ssh -i ~/.ssh/mlproject-key.pem ec2-user@54.123.45.67

# On Mac/Linux:
ssh -i ~/.ssh/mlproject-key.pem ec2-user@YOUR_EC2_IP

# If using Ubuntu AMI, use:
ssh -i ~/.ssh/mlproject-key.pem ubuntu@YOUR_EC2_IP
```

Type `yes` when asked about fingerprint.

### 4.2 Install Docker

#### For Amazon Linux 2023

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (no sudo needed)
sudo usermod -aG docker ec2-user

# Log out and back in for group changes
exit
# Then SSH back in
```

#### For Ubuntu

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install docker.io -y

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker ubuntu

# Log out and back in
exit
# Then SSH back in
```

### 4.3 Install AWS CLI

```bash
# Download AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Install unzip if not present
sudo yum install unzip -y  # Amazon Linux
# OR: sudo apt install unzip -y  # Ubuntu

# Unzip and install
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version
docker --version
```

### 4.4 Configure AWS Credentials on EC2

**Option A - IAM Role (Recommended for Production):**

1. In AWS Console → EC2 → Select your instance
2. Actions → Security → Modify IAM role
3. Create new role with `AmazonEC2ContainerRegistryReadOnly`
4. Attach to instance

**Option B - Configure Credentials Manually:**

```bash
aws configure
# Enter:
# - AWS Access Key ID: (use the IAM user key from Step 1)
# - AWS Secret Access Key: (use the secret from Step 1)
# - Default region: us-east-1 (or your region)
# - Default output format: json
```

### 4.5 Test ECR Login

```bash
# Replace with your region and registry
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# You should see: "Login Succeeded"
```

---

## Step 5: Configure GitHub Secrets

### 5.1 Open GitHub Repository Settings

1. Go to your GitHub repository
2. Click **Settings** tab
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** for each below

### 5.2 Add All Required Secrets

Add these secrets one by one:

| Secret Name             | Value                                            | Where to Find                                         |
| ----------------------- | ------------------------------------------------ | ----------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | Your IAM access key                              | From Step 1.4                                         |
| `AWS_SECRET_ACCESS_KEY` | Your IAM secret key                              | From Step 1.4                                         |
| `AWS_REGION`            | `us-east-1`                                      | Your AWS region                                       |
| `ECR_REGISTRY`          | `123456789012.dkr.ecr.us-east-1.amazonaws.com`   | From Step 2.3 (WITHOUT /mlproject)                    |
| `ECR_REPOSITORY`        | `mlproject`                                      | Repository name from Step 2.2                         |
| `EC2_HOST`              | `54.123.45.67`                                   | From Step 3.5 (Public IPv4)                           |
| `EC2_USER`              | `ec2-user`                                       | Use `ec2-user` for Amazon Linux, `ubuntu` for Ubuntu  |
| `EC2_SSH_KEY`           | Full content of .pem file                        | See Step 5.3 below                                    |

### 5.3 Add SSH Private Key

**On Windows (PowerShell):**

```powershell
Get-Content ~/.ssh/mlproject-key.pem | clip
```

**On Mac/Linux:**

```bash
cat ~/.ssh/mlproject-key.pem | pbcopy  # Mac
# OR
cat ~/.ssh/mlproject-key.pem  # Copy output manually
```

Paste the ENTIRE content (including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`) into the `EC2_SSH_KEY` secret.

---

## Step 6: Test the Pipeline

### 6.1 Commit and Push

```bash
# From your project directory
git add .
git commit -m "Add EC2 CI/CD pipeline"
git push origin main
```

### 6.2 Monitor GitHub Actions

1. Go to your GitHub repository
2. Click **Actions** tab
3. You should see a workflow running: **CI/CD - Deploy to EC2**
4. Click on the running workflow to see live logs

### 6.3 Watch the Stages

- ✅ **CI**: Tests and linting (2-3 min)
- ✅ **Build and Push to ECR**: Docker build and push (5-10 min)
- ✅ **Deploy to EC2**: SSH and container deployment (2-3 min)

---

## Step 7: Verify Deployment

### 7.1 Check Website

Open browser and go to:

```text
http://YOUR_EC2_PUBLIC_IP/
```

You should see your ML project homepage!

### 7.2 Test Prediction Endpoint

```text
http://YOUR_EC2_PUBLIC_IP/predictdata
```

### 7.3 Check Container on EC2

```bash
# SSH into EC2
ssh -i ~/.ssh/mlproject-key.pem ec2-user@YOUR_EC2_IP

# Check running containers
docker ps

# View logs
docker logs mlproject -f

# Check recent logs
docker logs --tail 50 mlproject
```

---

## Step 8: (Optional) Set Up Custom Domain

### 8.1 Register Domain (if you don't have one)

- Use Route 53, Namecheap, or GoDaddy

### 8.2 Point Domain to EC2

1. Go to **Route 53** in AWS Console
2. Create hosted zone for your domain
3. Create **A Record**:

   - Name: `mlproject.yourdomain.com`
   - Type: A
   - Value: Your EC2 public IP
   - TTL: 300

### 8.3 Set Up SSL with Let's Encrypt (HTTPS)

```bash
# SSH into EC2
# Install Nginx
sudo yum install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx

# Install Certbot
sudo yum install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d mlproject.yourdomain.com

# Configure Nginx to proxy to Docker container
sudo nano /etc/nginx/conf.d/mlproject.conf
```

Add this config:

```nginx
server {
    listen 80;
    server_name mlproject.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name mlproject.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/mlproject.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mlproject.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

---

## Troubleshooting

### GitHub Actions Fails

#### Error: "Permission denied (publickey)"

- Check `EC2_SSH_KEY` secret contains full private key with BEGIN/END lines
- Verify `EC2_USER` matches your AMI (ec2-user or ubuntu)
- Check Security Group allows SSH from 0.0.0.0/0

#### Error: "Failed to pull image from ECR"

- SSH into EC2 and test: `aws ecr get-login-password | docker login ...`
- Verify IAM role or AWS credentials are configured on EC2
- Check IAM user has ECR permissions

#### Error: "docker: command not found"

- Docker not installed on EC2
- Reconnect SSH after adding user to docker group

### Application Not Accessible

#### Can't access `http://EC2_IP/`

- Check Security Group allows HTTP (port 80) from 0.0.0.0/0
- Verify container is running: `docker ps`
- Check container logs: `docker logs mlproject`
- Test locally on EC2: `curl http://localhost`

#### Container crashes on startup

- View logs: `docker logs mlproject`
- Likely missing artifacts or model files
- Check if `artifacts/` folder exists and has models

### High Costs

- Stop EC2 when not in use (or use auto-scaling)
- Delete old ECR images: ECR Console → Repository → Select old images → Delete
- Use t3.micro instead of t3.medium for testing (though may be slow for ML)

---

## Cost Estimate (us-east-1)

- **ECR**: ~$0.10/GB/month for storage
- **EC2 t3.medium**: ~$30/month (on-demand, 24/7)
- **Data Transfer**: First 100GB/month free, then $0.09/GB
- **Total**: ~$30-35/month for basic setup

**Save money:**

- Use t3.micro (~$7/month) for testing
- Stop instance when not needed
- Use AWS Free Tier (12 months: 750 hrs/month t2.micro + 30GB storage)

---

## Next Steps

1. ✅ Monitor GitHub Actions on every push
2. ✅ Add CloudWatch alarms for EC2 health
3. ✅ Set up automated backups
4. ✅ Implement blue-green deployments
5. ✅ Add load balancer for high availability

---

## Quick Reference Commands

```bash
# SSH to EC2
ssh -i ~/.ssh/mlproject-key.pem ec2-user@YOUR_EC2_IP

# Check running containers
docker ps

# View logs
docker logs -f mlproject

# Restart container
docker restart mlproject

# Pull and run manually
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_REGISTRY
docker pull YOUR_REGISTRY/mlproject:latest
docker stop mlproject && docker rm mlproject
docker run -d --name mlproject -p 80:8080 YOUR_REGISTRY/mlproject:latest

# Check disk space
df -h

# Check system resources
htop  # install first: sudo yum install htop -y
```

---

## Support

If you encounter issues:

1. Check GitHub Actions logs
2. SSH into EC2 and check `docker logs mlproject`
3. Verify all GitHub Secrets are correct
4. Review AWS CloudWatch logs (if enabled)

Good luck with your deployment! 🚀
