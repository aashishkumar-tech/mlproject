# 🚀 Azure Quick Push Guide

## Before You Push - Replace These

1. **In README.md** - Find and replace:
   - `YOUR_USERNAME` → Your GitHub username (multiple places)
   - Update deployment section to mention Azure
   - Add your Azure VM IP if you want to showcase it

2. **In GitHub** - Configure 9 Secrets (Settings → Secrets → Actions):

   ```text
   AZURE_CREDENTIALS
   AZURE_SUBSCRIPTION_ID
   ACR_LOGIN_SERVER
   ACR_NAME
   ACR_USERNAME
   ACR_PASSWORD
   VM_HOST
   VM_USER
   VM_SSH_KEY
   ```

## Push Commands

```bash
cd "C:\Users\Aashish kumar\Videos\mlproject"

git add .

git commit -m "feat: Azure deployment with CI/CD"

git push origin main
```

## After Push

1. Watch: <https://github.com/YOUR_USERNAME/mlproject/actions>
2. Test: http://YOUR_AZURE_VM_IP/
3. ⭐ Star your own repo to show confidence!

---

## Quick Checklist

- [ ] Created Service Principal (Step 1)
- [ ] Created Resource Group `mlproject-rg`
- [ ] Created ACR `mlprojectacr`
- [ ] Created Azure VM `mlproject-vm`
- [ ] Installed Docker on VM
- [ ] Configured ACR access on VM
- [ ] Added all 9 GitHub Secrets
- [ ] Created `.github/workflows/azure-deploy.yml`
- [ ] Pushed to GitHub
- [ ] Verified deployment works

---

**✅ Your project showcases**:

- Automated CI/CD (GitHub Actions)
- Docker containerization
- Azure cloud deployment (Azure VM, ACR)
- Production-ready configuration
- Professional documentation

**Perfect for DevOps/MLOps/Cloud Engineer roles!** ☁️🎯

---

## Cost-Saving Tips

- **Stop VM when not needed**: Azure Portal → VM → Stop (saves ~$0.04/hour)
- **Set auto-shutdown**: VM → Auto-shutdown → Schedule for 11 PM daily
- **Use B1s for testing**: ~$8/month vs B2s ~$30/month
- **Delete old ACR images**: Keep only latest 5 tags
- **Monitor costs**: Azure Portal → Cost Management + Billing

---

## Troubleshooting Quick Fixes

### Pipeline fails at "Deploy to Azure VM"

```bash
# SSH into VM manually and check Docker
ssh -i ~/.ssh/mlproject-vm_key.pem azureuser@YOUR_VM_IP
docker ps
docker logs mlproject
```

### Can't access website

```bash
# Check Azure Network Security Group
# Azure Portal → VM → Networking → Check port 80 is open
```

### ACR authentication fails

```bash
# Re-login to ACR from VM
docker login mlprojectacr.azurecr.io
# Use username and password from ACR Access Keys
```

---

## Useful Azure CLI Commands

```bash
# View your VM status
az vm list --resource-group mlproject-rg --output table

# Stop VM (save money)
az vm stop --resource-group mlproject-rg --name mlproject-vm

# Start VM
az vm start --resource-group mlproject-rg --name mlproject-vm

# View ACR repositories
az acr repository list --name mlprojectacr --output table

# View ACR tags for an image
az acr repository show-tags --name mlprojectacr --repository mlproject --output table

# Clean up old ACR images (keep latest 5)
az acr repository show-tags --name mlprojectacr --repository mlproject \
  --orderby time_desc --output tsv | tail -n +6 | \
  xargs -I {} az acr repository delete --name mlprojectacr --image mlproject:{} --yes
```
