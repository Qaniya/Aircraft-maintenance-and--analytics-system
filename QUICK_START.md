# ⚡ Quick Start — Azure Deployment

> Condensed guide. Full details in `SETUP_GUIDE.md` and `DEPLOYMENT.md`.

---

## Install Tools (Windows)

```bash
winget install Microsoft.AzureCLI
winget install HashiCorp.Terraform
```

## Login to Azure

```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

## Create Terraform State Storage

```bash
az group create --name rg-terraform-state --location eastus
az storage account create --name stterraformstateaircraft --resource-group rg-terraform-state --location eastus --sku Standard_LRS --encryption-services blob
az storage container create --name tfstate --account-name stterraformstateaircraft
```

## Create Service Principal

```bash
az ad sp create-for-rbac --name "github-actions-aircraft-maintenance" --role "Contributor" --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID" --sdk-auth
```

## Configure & Deploy

```bash
# Configure
cp infra/terraform.tfvars.example infra/terraform.tfvars
# Edit infra/terraform.tfvars with your values

# Deploy infrastructure
cd infra
terraform init
terraform plan -out=tfplan
terraform apply tfplan
cd ..

# Build & push Docker image
az acr login --name acraircraftmaintenancedev
docker build -t acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest ./app
docker push acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest

# Deploy to App Service
az webapp config container set -g rg-aircraft-maintenance-dev -n app-aircraft-maintenance-dev --docker-custom-image-name acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest
az webapp restart -g rg-aircraft-maintenance-dev -n app-aircraft-maintenance-dev

# Verify
curl https://app-aircraft-maintenance-dev.azurewebsites.net/health
```

## Your App

- **URL:** https://app-aircraft-maintenance-dev.azurewebsites.net
- **Login:** `admin` / `admin123`

## Cleanup

```bash
cd infra && terraform destroy
az group delete --name rg-aircraft-maintenance-dev --yes --no-wait
```
