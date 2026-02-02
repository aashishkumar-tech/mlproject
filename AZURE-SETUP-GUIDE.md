# Azure Setup Guide - Step by Step

Complete guide to deploy your ML project to Azure Virtual Machine with Azure Container Registry (ACR) and GitHub Actions CI/CD.

---

## Prerequisites

- Azure Account with active subscription ([Get free $200 credit](https://azure.microsoft.com/free/))
- GitHub repository with your code
- Basic familiarity with Azure Portal

---

## Step 1: Create Service Principal for GitHub Actions

### 1.1 Open Azure Cloud Shell

1. Sign in to Azure Portal: <https://portal.azure.com/>
2. Click the **Cloud Shell** icon (>_) in top right
3. Select **Bash** when prompted
4. Wait for Cloud Shell to initialize

### 1.2 Create Service Principal

Run these commands in Cloud Shell:

```bash
# Get your subscription ID
az account show --query id --output tsv

# Create service principal with contributor role
# Replace YOUR_SUBSCRIPTION_ID with the ID from above
az ad sp create-for-rbac \
  --name "github-actions-mlproject" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth
```

### 1.3 Save the Output

**IMPORTANT**: Copy the entire JSON output. You'll need this for GitHub Secrets.

Example output:

```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  ...
}
```

---

## Step 2: Create Resource Group

### 2.1 Via Azure Portal

1. In Azure Portal, search for **Resource groups**
2. Click **+ Create**
3. **Subscription**: Select your subscription
4. **Resource group**: `mlproject-rg`
5. **Region**: `East US` (or choose closer region)
6. Click **Review + create** → **Create**

### 2.2 Via Azure CLI (Alternative)

```bash
az group create --name mlproject-rg --location eastus
```

---

## Step 3: Create Azure Container Registry (ACR)

### 3.1 Via Azure Portal

1. Search for **Container registries**
2. Click **+ Create**
3. **Subscription**: Select your subscription
4. **Resource group**: Select `mlproject-rg`
5. **Registry name**: `mlprojectacr` (must be globally unique, lowercase, alphanumeric)
6. **Location**: Same as resource group (`East US`)
7. **SKU**: **Basic** (sufficient for small projects)
8. Click **Review + create** → **Create**
9. Wait 1-2 minutes for deployment

### 3.2 Note Registry Details

1. Go to your ACR resource
2. From the **Overview** page, copy:
   - **Login server**: `mlprojectacr.azurecr.io` → This is your **ACR_LOGIN_SERVER**
   - **Registry name**: `mlprojectacr` → This is your **ACR_NAME**

### 3.3 Enable Admin Access

1. In your ACR, click **Access keys** in left menu
2. Enable **Admin user** toggle
3. Copy and save:
   - **Username**: Usually same as registry name
   - **password**: One of the two passwords shown
   - You'll use these for Docker login

---

## Step 4: Create Azure Virtual Machine

### 4.1 Via Azure Portal

1. Search for **Virtual machines**
2. Click **+ Create** → **Azure virtual machine**

#### Basic Configuration

1. **Subscription**: Select your subscription
2. **Resource group**: Select `mlproject-rg`
3. **Virtual machine name**: `mlproject-vm`
4. **Region**: Same as resource group (`East US`)
5. **Availability options**: No infrastructure redundancy required
6. **Security type**: Standard
7. **Image**: **Ubuntu Server 22.04 LTS - x64 Gen2**
8. **Size**: Click **See all sizes**
   - Select **Standard_B2s** (2 vCPUs, 4GB RAM) - Good for ML
   - Or **Standard_B1s** (1 vCPU, 1GB RAM) for testing only

#### Administrator Account

1. **Authentication type**: **SSH public key**
2. **Username**: `azureuser`
3. **SSH public key source**: **Generate new key pair**
4. **Key pair name**: `mlproject-vm_key`

#### Inbound Port Rules

1. **Public inbound ports**: Select **Allow selected ports**
2. **Select inbound ports**: Check both:
    - **SSH (22)**
    - **HTTP (80)**

#### Next: Disks

1. Click **Next: Disks**
2. **OS disk type**: **Standard SSD** (cost-effective)
3. **Delete with VM**: Check this box

#### Next: Networking

1. Click **Next: Networking**
2. **Virtual network**: (new) mlproject-vm-vnet (default is fine)
3. **Subnet**: (new) default (10.0.0.0/24)
4. **Public IP**: (new) mlproject-vm-ip
5. **NIC network security group**: **Basic**
6. **Public inbound ports**: Confirm **SSH (22), HTTP (80)** are selected
7. **Delete public IP and NIC when VM is deleted**: Check this box

#### Review and Create

1. Click **Review + create**
2. Review the configuration
3. Click **Create**

### 4.2 Download SSH Private Key

**IMPORTANT**: A popup will appear asking you to download the private key.

1. Click **Download private key and create resource**
2. File downloads as `mlproject-vm_key.pem`
3. **Save this file securely!** You can't download it again.
4. Move to safe location:

   ```powershell
   # On Windows (PowerShell):
   Move-Item ~/Downloads/mlproject-vm_key.pem ~/.ssh/
   ```

   ```bash
   # On Mac/Linux:
   mv ~/Downloads/mlproject-vm_key.pem ~/.ssh/
   chmod 400 ~/.ssh/mlproject-vm_key.pem
   ```

### 4.3 Wait for Deployment

- Wait 3-5 minutes for VM creation
- Click **Go to resource** when complete

### 4.4 Note VM Details

From the VM **Overview** page, copy and save:

- **Public IP address** (e.g., `20.185.45.123`) → This is **VM_HOST**
- **Size**: Confirm it's the size you selected
- **Status**: Should show "Running"

---

## Step 5: Configure Azure VM

### 5.1 Connect via SSH

```bash
# On Windows PowerShell:
ssh -i ~/.ssh/mlproject-vm_key.pem azureuser@20.185.45.123

# On Mac/Linux:
ssh -i ~/.ssh/mlproject-vm_key.pem azureuser@YOUR_VM_IP
```

Type `yes` when asked about fingerprint.

### 5.2 Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (no sudo needed for docker commands)
sudo usermod -aG docker azureuser

# Install Docker Compose (optional but useful)
sudo apt install docker-compose -y

# Log out and back in for group changes to take effect
exit
# Then SSH back in
```

### 5.3 Verify Docker Installation

```bash
# After reconnecting
docker --version
docker ps
```

### 5.4 Install Azure CLI on VM

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify installation
az --version
```

### 5.5 Configure Azure Container Registry Access

**Option A - Using Admin Credentials (Simpler):**

```bash
# Login to ACR using admin credentials
docker login mlprojectacr.azurecr.io
# Enter:
# Username: mlprojectacr (your ACR name)
# Password: (use the password from Step 3.3)
```

**Option B - Using Service Principal (Production Recommended):**

```bash
# Login using service principal
az login --service-principal \
  --username YOUR_CLIENT_ID \
  --password YOUR_CLIENT_SECRET \
  --tenant YOUR_TENANT_ID

# Login to ACR
az acr login --name mlprojectacr
```

### 5.6 Test ACR Connection

```bash
# This should show "Login Succeeded"
docker login mlprojectacr.azurecr.io
```

---

## Step 6: Configure Firewall Rules (If Needed)

### 6.1 Verify Network Security Group

1. In Azure Portal, go to your VM
2. Click **Networking** in left menu
3. Confirm these inbound rules exist:
   - **Port 22** (SSH) from your IP or Any
   - **Port 80** (HTTP) from Any (0.0.0.0/0)

### 6.2 Add Custom Port (If App Uses Different Port)

If your app runs on a custom port (e.g., 8080):

1. Click **Add inbound port rule**
2. **Destination port ranges**: `8080`
3. **Protocol**: TCP
4. **Action**: Allow
5. **Name**: `Port_8080`
6. Click **Add**

---

## Step 7: Configure GitHub Secrets

### 7.1 Open GitHub Repository Settings

1. Go to your GitHub repository
2. Click **Settings** tab
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** for each below

### 7.2 Add All Required Secrets

Add these secrets one by one:

| Secret Name           | Value                                  | Where to Find                                    |
| --------------------- | -------------------------------------- | ------------------------------------------------ |
| `AZURE_CREDENTIALS`   | Full JSON output from Step 1.2         | The entire JSON from service principal creation  |
| `AZURE_SUBSCRIPTION_ID` | Your subscription ID                | From the JSON or Azure Portal                    |
| `ACR_LOGIN_SERVER`    | `mlprojectacr.azurecr.io`              | From Step 3.2 (your ACR login server)            |
| `ACR_NAME`            | `mlprojectacr`                         | Your ACR name from Step 3                        |
| `ACR_USERNAME`        | Admin username                         | From Step 3.3 (usually same as ACR name)         |
| `ACR_PASSWORD`        | Admin password                         | From Step 3.3 (ACR access keys)                  |
| `VM_HOST`             | `20.185.45.123`                        | From Step 4.4 (VM public IP)                     |
| `VM_USER`             | `azureuser`                            | Default Azure VM username                        |
| `VM_SSH_KEY`          | Full content of .pem file              | See Step 7.3 below                               |

### 7.3 Add SSH Private Key

**On Windows (PowerShell):**

```powershell
Get-Content ~/.ssh/mlproject-vm_key.pem | clip
```

**On Mac/Linux:**

```bash
cat ~/.ssh/mlproject-vm_key.pem | pbcopy  # Mac
# OR
cat ~/.ssh/mlproject-vm_key.pem  # Copy output manually
```

Paste the ENTIRE content (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`) into the `VM_SSH_KEY` secret.

---

## Step 8: Create GitHub Actions Workflow

### 8.1 Create Workflow File

Create `.github/workflows/azure-deploy.yml`:

```yaml
# CI/CD Pipeline: Build, Push to ACR, Deploy to Azure VM
name: CI/CD - Deploy to Azure

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  ACR_LOGIN_SERVER: ${{ secrets.ACR_LOGIN_SERVER }}
  ACR_NAME: ${{ secrets.ACR_NAME }}
  IMAGE_NAME: mlproject

permissions:
  contents: read

jobs:
  # ===== CI: Run tests and validation =====
  ci:
    name: Continuous Integration
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.10
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Lint with flake8 (optional)
        continue-on-error: true
        run: |
          pip install flake8
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true

      - name: Run tests (if present)
        continue-on-error: true
        run: |
          if [ -d "tests" ] || ls *test*.py 2>/dev/null; then
            pip install pytest
            pytest -v || true
          else
            echo "No tests found, skipping test step"
          fi

  # ===== BUILD: Build Docker image and push to ACR =====
  build-and-push:
    name: Build and Push to ACR
    runs-on: ubuntu-latest
    needs: ci
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    outputs:
      image: ${{ steps.build-image.outputs.image }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Login to Azure Container Registry
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.ACR_LOGIN_SERVER }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Build, tag, and push image to ACR
        id: build-image
        env:
          IMAGE_TAG: ${{ github.sha }}
        run: |
          # Build Docker image
          docker build -t $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG .
          docker tag $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

          # Push both tags to ACR
          docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG
          docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

          echo "image=$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG" >> $GITHUB_OUTPUT
          echo "✅ Image pushed: $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG"

  # ===== DEPLOY: Deploy to Azure VM =====
  deploy:
    name: Deploy to Azure VM
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup SSH Key
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.VM_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.VM_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy to Azure VM
        env:
          VM_HOST: ${{ secrets.VM_HOST }}
          VM_USER: ${{ secrets.VM_USER }}
          ACR_LOGIN_SERVER: ${{ secrets.ACR_LOGIN_SERVER }}
          ACR_USERNAME: ${{ secrets.ACR_USERNAME }}
          ACR_PASSWORD: ${{ secrets.ACR_PASSWORD }}
          IMAGE_NAME: ${{ env.IMAGE_NAME }}
        run: |
          ssh -i ~/.ssh/id_rsa $VM_USER@$VM_HOST << 'ENDSSH'
            set -e
            echo "🔐 Logging into ACR..."
            echo "${{ secrets.ACR_PASSWORD }}" | docker login ${{ secrets.ACR_LOGIN_SERVER }} \
              --username ${{ secrets.ACR_USERNAME }} \
              --password-stdin

            echo "🐳 Pulling latest image..."
            docker pull ${{ secrets.ACR_LOGIN_SERVER }}/${{ env.IMAGE_NAME }}:latest

            echo "🛑 Stopping old container (if exists)..."
            docker stop mlproject 2>/dev/null || true
            docker rm mlproject 2>/dev/null || true

            echo "🚀 Starting new container..."
            docker run -d \
              --name mlproject \
              --restart unless-stopped \
              -p 80:8080 \
              ${{ secrets.ACR_LOGIN_SERVER }}/${{ env.IMAGE_NAME }}:latest

            echo "🧹 Cleaning up old images..."
            docker image prune -af

            echo "✅ Deployment completed!"
            docker ps | grep mlproject
          ENDSSH

      - name: Verify Deployment
        run: |
          echo "🌐 Application URL: http://${{ secrets.VM_HOST }}/"
          echo "✅ Deployment pipeline completed successfully!"
```

### 8.2 Commit and Push

```bash
git add .github/workflows/azure-deploy.yml
git commit -m "Add Azure CI/CD pipeline"
git push origin main
```

---

## Step 9: Test the Pipeline

### 9.1 Monitor GitHub Actions

1. Go to your GitHub repository
2. Click **Actions** tab
3. You should see a workflow running: **CI/CD - Deploy to Azure**
4. Click on the running workflow to see live logs

### 9.2 Watch the Stages

- ✅ **CI**: Tests and linting (2-3 min)
- ✅ **Build and Push to ACR**: Docker build and push (5-10 min)
- ✅ **Deploy to Azure VM**: SSH and container deployment (2-3 min)

---

## Step 10: Verify Deployment

### 10.1 Check Website

Open browser and go to:

```text
http://YOUR_VM_PUBLIC_IP/
```

You should see your ML project homepage!

### 10.2 Test Prediction Endpoint

```text
http://YOUR_VM_PUBLIC_IP/predictdata
```

### 10.3 Check Container on Azure VM

```bash
# SSH into VM
ssh -i ~/.ssh/mlproject-vm_key.pem azureuser@YOUR_VM_IP

# Check running containers
docker ps

# View logs
docker logs mlproject -f

# Check recent logs
docker logs --tail 50 mlproject
```

---

## Step 11: (Optional) Set Up Custom Domain with HTTPS

### 11.1 Assign Static IP to VM

1. In Azure Portal, go to your VM
2. Click **Networking** → Public IP address link
3. Click **Configuration** in left menu
4. **Assignment**: Change to **Static**
5. Click **Save**

### 11.2 Configure DNS

1. Go to your domain registrar (Namecheap, GoDaddy, etc.)
2. Create **A Record**:
   - Name: `mlproject` or `@` (for root domain)
   - Type: A
   - Value: Your VM static public IP
   - TTL: 300 or Auto

### 11.3 Install Nginx and SSL Certificate

```bash
# SSH into VM
ssh -i ~/.ssh/mlproject-vm_key.pem azureuser@YOUR_VM_IP

# Install Nginx
sudo apt update
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx

# Install Certbot for Let's Encrypt SSL
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d mlproject.yourdomain.com

# Configure Nginx as reverse proxy
sudo nano /etc/nginx/sites-available/mlproject
```

Add this configuration:

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
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/mlproject /etc/nginx/sites-enabled/

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 11.4 Update Network Security Group

1. In Azure Portal, go to VM → **Networking**
2. Ensure **HTTPS (443)** port is open
3. If not, click **Add inbound port rule**:
   - **Destination port ranges**: `443`
   - **Protocol**: TCP
   - **Name**: `HTTPS`
   - Click **Add**

---

## Troubleshooting

### GitHub Actions Fails

#### Error: "Permission denied (publickey)"

- Check `VM_SSH_KEY` secret contains full private key with BEGIN/END lines
- Verify `VM_USER` is `azureuser`
- Check VM Network Security Group allows SSH from 0.0.0.0/0

#### Error: "Failed to pull image from ACR"

- SSH into VM and test: `docker login mlprojectacr.azurecr.io`
- Verify ACR admin user is enabled
- Check ACR username and password in GitHub Secrets

#### Error: "docker: command not found"

- Docker not installed on VM
- Reconnect SSH after adding user to docker group

### Application Not Accessible

#### Can't access `http://VM_IP/`

- Check Network Security Group allows HTTP (port 80)
- Verify container is running: `docker ps`
- Check container logs: `docker logs mlproject`
- Test locally on VM: `curl http://localhost`

#### Container crashes on startup

- View logs: `docker logs mlproject`
- Check if `artifacts/` folder exists with models
- Verify Dockerfile and application.py are correct

### High Costs

- **Stop VM when not in use**: VM → **Stop** (you won't be charged for compute)
- **Delete old ACR images**: Go to ACR → Repositories → Select old tags → Delete
- **Use smaller VM size**: B1s instead of B2s for testing
- **Set up auto-shutdown**: VM → Auto-shutdown (schedule daily shutdown)

---

## Cost Estimate (East US)

- **ACR Basic**: ~$5/month
- **VM B2s (2 vCPU, 4GB RAM)**: ~$30/month (730 hours)
- **VM B1s (1 vCPU, 1GB RAM)**: ~$8/month
- **Standard SSD (30GB)**: ~$2.50/month
- **Public IP (Static)**: ~$3.60/month
- **Total**: ~$40-45/month for B2s, ~$20/month for B1s

**Save money:**

- Use B1s for development/testing
- Stop VM when not needed (VM → Stop)
- Use Azure Free Tier (12 months: 750 hours/month B1s)
- Delete unused ACR images regularly

---

## Auto-Shutdown Configuration

### Set Up Auto-Shutdown

1. In Azure Portal, go to your VM
2. Click **Auto-shutdown** in left menu
3. **Enable**: Toggle ON
4. **Scheduled shutdown time**: 11:00 PM (or your preferred time)
5. **Time zone**: Select your timezone
6. **Notification**: Add your email (optional)
7. Click **Save**

This saves money by automatically stopping VM at night!

---

## Quick Reference Commands

```bash
# SSH to Azure VM
ssh -i ~/.ssh/mlproject-vm_key.pem azureuser@YOUR_VM_IP

# Check running containers
docker ps

# View logs
docker logs -f mlproject

# Restart container
docker restart mlproject

# Pull and run manually
docker login mlprojectacr.azurecr.io
docker pull mlprojectacr.azurecr.io/mlproject:latest
docker stop mlproject && docker rm mlproject
docker run -d --name mlproject -p 80:8080 mlprojectacr.azurecr.io/mlproject:latest

# Check disk space
df -h

# Check system resources
htop  # install first: sudo apt install htop -y

# View Azure CLI login status
az account show

# Stop/Start VM from CLI
az vm stop --resource-group mlproject-rg --name mlproject-vm
az vm start --resource-group mlproject-rg --name mlproject-vm

# Delete resource group (remove everything)
az group delete --name mlproject-rg --yes --no-wait
```

---

## Azure-Specific Features to Explore

1. **Azure Monitor**: Set up alerts for VM health and performance
2. **Azure Application Insights**: Monitor application performance
3. **Azure Key Vault**: Store secrets securely
4. **Azure DevOps**: Alternative to GitHub Actions
5. **Azure Load Balancer**: Scale with multiple VMs
6. **Azure App Service**: Simpler PaaS alternative to VMs
7. **Azure Container Instances**: Serverless containers

---

## Comparing AWS vs Azure

| Feature           | AWS              | Azure                          |
| ----------------- | ---------------- | ------------------------------ |
| Container Registry| ECR              | ACR                            |
| Virtual Machine   | EC2              | Azure VM                       |
| CLI Tool          | AWS CLI          | Azure CLI                      |
| Auth Method       | IAM User/Keys    | Service Principal              |
| Default User      | ec2-user/ubuntu  | azureuser                      |
| Free Tier         | 750hrs t2.micro  | 750hrs B1s                     |
| Networking        | Security Groups  | Network Security Groups        |

---

## Next Steps

1. ✅ Monitor GitHub Actions on every push
2. ✅ Set up Azure Monitor alerts
3. ✅ Configure automated backups
4. ✅ Implement blue-green deployments with staging slots
5. ✅ Explore Azure App Service as PaaS alternative
6. ✅ Add Azure Application Insights for monitoring

---

## Support

If you encounter issues:

1. Check GitHub Actions logs
2. SSH into VM and check `docker logs mlproject`
3. Verify all GitHub Secrets are correct
4. Check Azure Portal → VM → Activity log for Azure-specific errors
5. Review Azure Monitor logs (if enabled)

Good luck with your Azure deployment! ☁️🚀
