# 🚀 Aircraft Maintenance Analytics System — Azure Deployment Setup Guide

> **Version:** 1.0  
> **Last Updated:** August 2026  
> **Estimated Time:** 45–60 minutes (first deployment)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites Installation](#2-prerequisites-installation)
3. [Azure Account Setup](#3-azure-account-setup)
4. [Terraform State Storage](#4-terraform-state-storage)
5. [Service Principal for CI/CD](#5-service-principal-for-cicd)
6. [Terraform Configuration](#6-terraform-configuration)
7. [Deploy Azure Infrastructure](#7-deploy-azure-infrastructure)
8. [Build & Push Docker Image](#8-build--push-docker-image)
9. [Deploy Application](#9-deploy-application)
10. [GitHub Actions CI/CD Setup](#10-github-actions-cicd-setup)
11. [Post-Deployment Verification](#11-post-deployment-verification)
12. [Cost Estimates](#12-cost-estimates)
13. [Common Commands Cheat Sheet](#13-common-commands-cheat-sheet)
14. [Troubleshooting](#14-troubleshooting)
15. [Rollback Procedures](#15-rollback-procedures)
16. [Security Best Practices](#16-security-best-practices)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AZURE CLOUD (East US)                        │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                   GitHub Actions CI/CD                         │  │
│  │  Push → Lint → Test → Build Docker → Push ACR → Terraform    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│         │                                            │              │
│         ▼                                            ▼              │
│  ┌─────────────────┐                  ┌────────────────────────┐   │
│  │  Azure Container │                  │  Terraform State       │   │
│  │    Registry      │                  │  (Storage Account)     │   │
│  │   (ACR Basic)    │                  └────────────────────────┘   │
│  └────────┬────────┘                                               │
│           │                                                         │
│           ▼                                                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Azure App Service (Linux Web App)                 │  │
│  │             SKU: B1 (dev) / S1 (production)                   │  │
│  │                                                                │  │
│  │  ┌─────────────┐  ┌───────────┐  ┌────────────────────────┐  │  │
│  │  │  Flask App   │  │ Gunicorn  │  │  System Assigned       │  │  │
│  │  │  (Docker)    │  │ 4 workers │  │  Managed Identity      │  │  │
│  │  └──────┬──────┘  └───────────┘  └────────────────────────┘  │  │
│  └─────────┼─────────────────────────────────────────────────────┘  │
│            │                                                        │
│            ▼                                                        │
│  ┌──────────────────┐  ┌─────────────┐  ┌──────────────────────┐  │
│  │ Azure DB for     │  │ Azure Key   │  │ Application          │  │
│  │ PostgreSQL       │  │ Vault       │  │ Insights             │  │
│  │ (Flexible Server)│  │             │  │                      │  │
│  │ SSL required     │  │ Secrets:    │  │ Monitoring & Logs    │  │
│  └──────────────────┘  │ - DB URL    │  └──────────────────────┘  │
│                        │ - Flask key │                            │
│                        │ - JWT key   │                            │
│                        └─────────────┘                            │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Log Analytics Workspace                           │  │
│  │         (Centralized logging & alerting)                       │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Resources Created

| Resource | Purpose | SKU (Dev) |
|----------|---------|-----------|
| Resource Group | Logical container | — |
| App Service Plan | Compute hosting | B1 Basic |
| Linux Web App | Flask container | — |
| Container Registry | Docker images | Basic |
| PostgreSQL Flexible Server | Database | B_Standard_B1ms |
| Key Vault | Secrets management | Standard |
| Application Insights | Monitoring | Pay-as-you-go |
| Log Analytics | Centralized logs | Pay-as-you-go |

---

## 2. Prerequisites Installation

### 2.1 Azure CLI

**Windows (PowerShell as Administrator):**
```bash
winget install Microsoft.AzureCLI
```

**macOS:**
```bash
brew install azure-cli
```

**Linux (Debian/Ubuntu):**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**Verify installation:**
```bash
az version
```

### 2.2 Terraform

**Windows (PowerShell as Administrator):**
```bash
winget install HashiCorp.Terraform
```

**macOS:**
```bash
brew install terraform
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install terraform
```

**Verify installation:**
```bash
terraform version
```

### 2.3 Docker (Already Installed ✅)

```bash
docker --version
# Expected: Docker version 29.7.2, build a7dcaa6
```

Ensure Docker Desktop is running before proceeding.

---

## 3. Azure Account Setup

### 3.1 Create Azure Account

1. Go to **https://azure.microsoft.com/free**
2. Sign up for a **free account** (includes $200 credit for 30 days)
3. You'll need a credit card for verification (won't be charged)

### 3.2 Login to Azure

```bash
az login
```

This opens a browser window. Log in with your Azure credentials.

### 3.3 Select Subscription

```bash
# List all subscriptions
az account list --output table
```

Output:
```
Name                  ID                                    State    Is Default
--------------------  ------------------------------------  -------  -----------
Pay-As-You-Go         xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  Enabled  True
```

```bash
# Set the subscription to use
az account set --subscription "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### 3.4 Note Down Key Values

```bash
az account show --output json
```

Save these values:
- **Subscription ID** (`id`): `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Tenant ID** (`tenantId`): `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

## 4. Terraform State Storage

Terraform needs a remote place to store its state file. We create an Azure Storage Account for this.

### Step 4.1 — Create Resource Group for State

```bash
az group create \
  --name rg-terraform-state \
  --location eastus \
  --output table
```

Output:
```
Location    Name                 ResourceGroup
----------  -------------------  --------------
eastus      rg-terraform-state   rg-terraform-state
```

### Step 4.2 — Create Storage Account

```bash
az storage account create \
  --name stterraformstateaircraft \
  --resource-group rg-terraform-state \
  --location eastus \
  --sku Standard_LRS \
  --encryption-services blob \
  --output table
```

Output:
```
Location    ResourceGroup      Name                       AccessTier    Kind
----------  -----------------  -------------------------  ----------    ----------
eastus      rg-terraform-state  stterraformstateaircraft  Hot           StorageV2
```

### Step 4.3 — Create Blob Container

```bash
az storage container create \
  --name tfstate \
  --account-name stterraformstateaircraft \
  --output table
```

Output:
```
Created: https://stterraformstateaircraft.blob.core.windows.net/tfstate
```

### Step 4.4 — Verify Storage

```bash
az storage container show \
  --name tfstate \
  --account-name stterraformstateaircraft \
  --output table
```

---

## 5. Service Principal for CI/CD

A service principal gives GitHub Actions permission to deploy to your Azure account.

### Step 5.1 — Create Service Principal

```bash
az ad sp create-for-rbac \
  --name "github-actions-aircraft-maintenance" \
  --role "Contributor" \
  --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID" \
  --sdk-auth
```

Replace `YOUR_SUBSCRIPTION_ID` with the value from Step 3.4.

**Output:**
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

**⚠️ SAVE THIS OUTPUT — you need `clientId`, `clientSecret`, `subscriptionId`, and `tenantId` for GitHub Actions secrets.**

### Step 5.2 — Verify Service Principal

```bash
az ad sp show --id "YOUR_CLIENT_ID" --output table
```

---

## 6. Terraform Configuration

### Step 6.1 — Copy Variables File

```bash
cp infra/terraform.tfvars.example infra/terraform.tfvars
```

### Step 6.2 — Edit terraform.tfvars

Open `infra/terraform.tfvars` and fill in your values:

```hcl
# =============================================================================
# GENERAL
# =============================================================================
project_name = "aircraft-maintenance"
environment  = "development"          # development | staging | production
location     = "eastus"               # Azure region

# =============================================================================
# CONTAINER REGISTRY
# =============================================================================
acr_sku = "Basic"                     # Basic ($5/mo) | Standard ($20/mo)

# =============================================================================
# APP SERVICE
# =============================================================================
app_service_sku      = "B1"           # B1 Basic ($13/mo)
app_service_sku_tier = "Basic"
app_instance_count   = 1              # 1 for Basic, 2+ for production

# =============================================================================
# POSTGRESQL DATABASE
# =============================================================================
postgres_sku_name       = "B_Standard_B1ms"   # Dev: B1ms ($12/mo)
postgres_storage_mb     = 32768               # 32 GB
postgres_version        = "16"
postgres_admin_login    = "psqladmin"
postgres_admin_password = "MyStr0ngP@ssw0rd!"  # CHANGE THIS!
postgres_database_name  = "aircraft_maintenance"

# =============================================================================
# KEY VAULT
# =============================================================================
key_vault_sku = "standard"            # standard | premium

# =============================================================================
# APPLICATION
# =============================================================================
log_level              = "info"        # debug | info | warning | error
docker_image_tag       = "latest"
enable_deployment_slot = false         # true for blue-green deploys
```

**Save the file.**

---

## 7. Deploy Azure Infrastructure

### Step 7.1 — Navigate to Infrastructure Directory

```bash
cd infra
```

### Step 7.2 — Initialize Terraform

```bash
terraform init
```

**Expected output:**
```
Initializing the backend...

Successfully configured the backend "azurerm"! Terraform will automatically
use this backend unless the backend configuration changes.

Initializing provider plugins...
- Finding hashicorp/azurerm versions matching "~> 3.100"...
- Installing hashicorp/azurerm v3.100.0...

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure.
```

### Step 7.3 — Preview What Will Be Created

```bash
terraform plan -out=tfplan
```

**Expected output (summary):**
```
Terraform used the selected providers to generate the following execution plan.
Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # azurerm_resource_group.main will be created
  + resource "azurerm_resource_group" "main" { ... }

  # azurerm_container_registry.main will be created
  + resource "azurerm_container_registry" "main" { ... }

  # azurerm_postgresql_flexible_server.main will be created
  + resource "azurerm_postgresql_flexible_server" "main" { ... }

  ... (more resources)

Plan: 14 to add, 0 to change, 0 to destroy.
```

**Review the plan carefully.** Type `yes` if prompted.

### Step 7.4 — Create All Azure Resources

```bash
terraform apply tfplan
```

This takes **5-10 minutes**. You'll see resources being created one by one.

**Expected output:**
```
azurerm_resource_group.main: Creating...
azurerm_resource_group.main: Creation complete after 3s [id=/subscriptions/.../rg-aircraft-maintenance-dev]
azurerm_container_registry.main: Creating...
azurerm_container_registry.main: Creation complete after 30s
...

Apply complete! Resources: 14 added, 0 changed, 0 destroyed.

Outputs:

app_service_url     = "https://app-aircraft-maintenance-dev.azurewebsites.net"
acr_login_server    = "acraircraftmaintenancedev.azurecr.io"
acr_name            = "acraircraftmaintenancedev"
app_service_name    = "app-aircraft-maintenance-dev"
resource_group_name = "rg-aircraft-maintenance-dev"
```

### Step 7.5 — Save These Values

Run this command to see all outputs:

```bash
terraform output
```

**Write down these values:**

| Output | Value |
|--------|-------|
| App Service URL | `https://app-aircraft-maintenance-dev.azurewebsites.net` |
| ACR Login Server | `acraircraftmaintenancedev.azurecr.io` |
| ACR Name | `acraircraftmaintenancedev` |
| App Service Name | `app-aircraft-maintenance-dev` |
| Resource Group | `rg-aircraft-maintenance-dev` |

### Step 7.6 — Return to Project Root

```bash
cd ..
```

---

## 8. Build & Push Docker Image

### Step 8.1 — Login to Azure Container Registry

```bash
az acr login --name acraircraftmaintenancedev
```

**Expected output:**
```
Login Succeeded
```

### Step 8.2 — Build Docker Image

```bash
docker build -t acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest ./app
```

**Expected output:**
```
Step 1/18 : FROM python:3.11-slim AS builder
 ---> a1b2c3d4e5f6
Step 2/18 : WORKDIR /build
 ---> Running in 1234567890ab
...
Successfully built abc123def456
Successfully tagged acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest
```

### Step 8.3 — Push Image to ACR

```bash
docker push acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest
```

**Expected output:**
```
The push refers to repository [acraircraftmaintenancedev.azurecr.io/aircraft-maintenance]
abc123def456: Pushing  54.2MB/89.1MB
abc123def456: Pushed
latest: digest: sha256:abc123... size: 1234
```

### Alternative: Build in Azure (Cloud Build)

Instead of building locally, you can build directly in Azure:

```bash
az acr build \
  --registry acraircraftmaintenancedev \
  --image aircraft-maintenance:latest \
  --file app/Dockerfile \
  ./app
```

---

## 9. Deploy Application

### Step 9.1 — Configure App Service to Use Your Docker Image

```bash
az webapp config container set \
  --resource-group rg-aircraft-maintenance-dev \
  --name app-aircraft-maintenance-dev \
  --docker-custom-image-name acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest
```

**Expected output:**
```
{
  "id": "/subscriptions/.../config/web",
  "name": "app-aircraft-maintenance-dev",
  "kind": "app,linux,container",
  "properties": {
    "dockerRegistryUrl": "https://acraircraftmaintenancedev.azurecr.io",
    "dockerImageName": "aircraft-maintenance:latest",
    ...
  }
}
```

### Step 9.2 — Restart the App

```bash
az webapp restart \
  --resource-group rg-aircraft-maintenance-dev \
  --name app-aircraft-maintenance-dev
```

### Step 9.3 — Wait for the App to Start

```bash
echo "Waiting for app to start..."
sleep 30
```

### Step 9.4 — Test Health Endpoint

```bash
curl https://app-aircraft-maintenance-dev.azurewebsites.net/health
```

**Expected output:**
```json
{"status": "healthy", "service": "aircraft-maintenance-api"}
```

### Step 9.5 — Open in Browser

```bash
az webapp browse \
  --resource-group rg-aircraft-maintenance-dev \
  --name app-aircraft-maintenance-dev
```

Or manually open: **https://app-aircraft-maintenance-dev.azurewebsites.net**

**Login credentials:**
- **Username:** `admin`
- **Password:** `admin123`

---

## 10. GitHub Actions CI/CD Setup

### Step 10.1 — Push Code to GitHub

```bash
# Initialize git (if not already)
cd your-project-root
git init
git add .
git commit -m "Initial commit with Azure deployment config"

# Create GitHub repo (if not exists)
gh repo create aircraft-maintenance --public --source=. --push

# Or add remote manually
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 10.2 — Get ACR Password

```bash
az acr credential show \
  --name acraircraftmaintenancedev \
  --query "passwords[0].value" \
  --output tsv
```

### Step 10.3 — Add GitHub Secrets

Go to **GitHub → Your Repo → Settings → Secrets and variables → Actions → New repository secret**

Add these secrets one by one:

| Secret Name | Value |
|-------------|-------|
| `AZURE_CLIENT_ID` | From Step 5.1 output (`clientId`) |
| `AZURE_TENANT_ID` | From Step 3.4 (`tenantId`) |
| `AZURE_SUBSCRIPTION_ID` | From Step 3.4 (`subscriptionId`) |
| `ACR_USERNAME` | `acraircraftmaintenancedev` |
| `ACR_PASSWORD` | From Step 10.2 command output |
| `TF_STORAGE_ACCOUNT` | `stterraformstateaircraft` |

### Step 10.4 — Test CI/CD Pipeline

```bash
git add .
git commit -m "Configure CI/CD pipeline"
git push origin main
```

Go to **GitHub → Actions** tab to see the pipeline running.

### Step 10.5 — Pipeline Flow

```
Push to main → Test → Build Docker → Push to ACR → Terraform Apply → Deploy → Health Check
```

---

## 11. Post-Deployment Verification

### 11.1 — Check All Resources in Azure Portal

```bash
az portal browse --resource-group rg-aircraft-maintenance-dev
```

Verify these resources exist:

- [ ] App Service (`app-aircraft-maintenance-dev`)
- [ ] App Service Plan (`asp-aircraft-maintenance-dev`)
- [ ] Container Registry (`acraircraftmaintenancedev`)
- [ ] PostgreSQL Server (`psql-aircraft-maintenance-dev`)
- [ ] Key Vault (`kv-aircraft-maintenance-dev`)
- [ ] Application Insights (`ai-aircraft-maintenance-dev`)
- [ ] Log Analytics Workspace (`law-aircraft-maintenance-dev`)

### 11.2 — Check Application Logs

```bash
az webapp log tail \
  --resource-group rg-aircraft-maintenance-dev \
  --name app-aircraft-maintenance-dev
```

### 11.3 — Test All Endpoints

```bash
APP_URL="https://app-aircraft-maintenance-dev.azurewebsites.net"

# Health check
curl $APP_URL/health

# Dashboard (redirects to login)
curl -L $APP_URL/

# Aircraft API list (returns JSON)
curl $APP_URL/aircraft/api/list

# Dashboard stats API
curl $APP_URL/api/dashboard/stats
```

### 11.4 — Check Database Connection

```bash
# Connect to PostgreSQL from Azure Cloud Shell
az postgres flexible-server connect \
  --name psql-aircraft-maintenance-dev \
  --admin-user psqladmin \
  --admin-password "MyStr0ngP@ssw0rd!" \
  --database aircraft_maintenance \
  --query "SELECT COUNT(*) FROM aircraft"
```

### 11.5 — Check Key Vault Secrets

```bash
az keyvault secret list \
  --vault-name kv-aircraft-maintenance-dev \
  --output table
```

Expected secrets:
```
Name                 Value
-------------------  -----
database-url         postgresql://...
flask-secret-key     xxxxxxxxxxxxxx
jwt-secret-key       xxxxxxxxxxxxxx
```

---

## 12. Cost Estimates

### Development Environment

| Resource | SKU | Monthly Cost |
|----------|-----|-------------|
| App Service | B1 (1 instance) | ~$13 |
| PostgreSQL | B_Standard_B1ms | ~$12 |
| Container Registry | Basic | ~$5 |
| Key Vault | Standard | ~$0.03 |
| Application Insights | Pay-as-you-go | ~$2 |
| Log Analytics | Pay-as-you-go | ~$5 |
| **Total** | | **~$37/month** |

### Production Environment

| Resource | SKU | Monthly Cost |
|----------|-----|-------------|
| App Service | S1 (2 instances) | ~$70 |
| PostgreSQL | GP_Standard_D2s_v3 | ~$125 |
| Container Registry | Standard | ~$20 |
| Key Vault | Standard | ~$0.03 |
| Application Insights | Pay-as-you-go | ~$10 |
| Log Analytics | Pay-as-you-go | ~$25 |
| **Total** | | **~$250/month** |

### Cost Optimization Tips

1. **Use Basic SKU for dev** — B1 App Service is sufficient for development
2. **Auto-shutdown dev** — Stop App Service when not in use
3. **Right-size PostgreSQL** — Start small, scale up as needed
4. **Use Reserved Instances** — Save 30-50% with 1-year commitment
5. **Monitor costs** — Set up Azure Cost Management alerts

---

## 13. Common Commands Cheat Sheet

```bash
# =============================================================================
# AZURE CLI COMMANDS
# =============================================================================

# Authentication
az login                                        # Login to Azure
az account list --output table                  # List subscriptions
az account set --subscription "<ID>"            # Set subscription
az account show --output json                   # Current account info

# Resource Management
az group list --output table                    # List resource groups
az group create --name <name> --location <loc>  # Create resource group
az group delete --name <name>                   # Delete resource group

# App Service
az webapp list -g <rg> --output table           # List web apps
az webapp restart -g <rg> -n <name>             # Restart app
az webapp stop -g <rg> -n <name>               # Stop app
az webapp start -g <rg> -n <name>              # Start app
az webapp log tail -g <rg> -n <name>           # View logs
az webapp browse -g <rg> -n <name>             # Open in browser

# Container Registry
az acr list --output table                      # List registries
az acr login --name <name>                      # Login to ACR
az acr credential show --name <name>            # Get credentials

# PostgreSQL
az postgres flexible-server list --output table # List servers
az postgres flexible-server show -g <rg> -n <n> # Show server

# Key Vault
az keyvault list --output table                 # List vaults
az keyvault secret list --vault-name <name>     # List secrets


# =============================================================================
# TERRAFORM COMMANDS
# =============================================================================

# Navigation
cd infra                                       # Go to infra directory

# Initialize
terraform init                                 # Initialize providers
terraform init -upgrade                        # Upgrade providers

# Plan & Apply
terraform plan                                 # Preview changes
terraform plan -out=tfplan                     # Save plan to file
terraform plan -out=tfplan -var="env=prod"     # Plan with variables
terraform apply tfplan                         # Apply saved plan
terraform apply -auto-approve                  # Apply without confirmation

# State
terraform state list                           # List all resources
terraform state show <resource>                # Show resource details
terraform output                               # Show outputs
terraform output -json                         # Outputs as JSON

# Destroy (⚠️ DELETES EVERYTHING)
terraform destroy                              # Destroy all resources
terraform destroy -target=<resource>           # Destroy specific resource

# Workspace (for multi-environment)
terraform workspace list                       # List workspaces
terraform workspace new staging                # Create workspace
terraform workspace select staging             # Switch workspace


# =============================================================================
# DOCKER COMMANDS
# =============================================================================

# Build
docker build -t <image>:<tag> <path>           # Build image
docker build --no-cache -t <image>:<tag> <path># Build without cache

# Push
docker push <image>:<tag>                      # Push to registry
docker tag <image> <registry>/<image>:<tag>    # Tag image

# Run
docker run -d -p 5000:5000 <image>            # Run container
docker logs <container_id>                     # View logs
docker stop <container_id>                     # Stop container
docker rm <container_id>                       # Remove container

# Cleanup
docker image prune                             # Remove unused images
docker container prune                         # Remove stopped containers


# =============================================================================
# PROJECT-SPECIFIC COMMANDS
# =============================================================================

# Local Development
python main.py                                 # Run locally

# Production Deployment (full sequence)
az acr login --name acraircraftmaintenancedev
docker build -t acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest ./app
docker push acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest
az webapp restart -g rg-aircraft-maintenance-dev -n app-aircraft-maintenance-dev
```

---

## 14. Troubleshooting

### Problem: `az: command not found`

**Solution:** Azure CLI is not installed. Run the installation command from Phase 2.

### Problem: `terraform: command not found`

**Solution:** Terraform is not installed. Run the installation command from Phase 2.

### Problem: `Error: Subscription not found`

**Solution:**
```bash
# List available subscriptions
az account list --output table

# Set the correct subscription
az account set --subscription "<SUBSCRIPTION_ID>"
```

### Problem: `Error: ACR login failed`

**Solution:**
```bash
# Re-login to ACR
az acr login --name acraircraftmaintenancedev

# Verify ACR exists
az acr list --output table
```

### Problem: `Error: Terraform init failed`

**Solution:**
```bash
# Check if state storage exists
az storage container show \
  --name tfstate \
  --account-name stterraformstateaircraft

# If not, recreate it
az storage container create \
  --name tfstate \
  --account-name stterraformstateaircraft
```

### Problem: `Error: App returns 500 error`

**Solution:**
```bash
# Check app logs
az webapp log tail \
  --resource-group rg-aircraft-maintenance-dev \
  --name app-aircraft-maintenance-dev

# Restart the app
az webapp restart \
  --resource-group rg-aircraft-maintenance-dev \
  --name app-aircraft-maintenance-dev
```

### Problem: `Error: Database connection refused`

**Solution:**
```bash
# Check PostgreSQL firewall rules
az postgres flexible-server firewall list \
  --resource-group rg-aircraft-maintenance-dev \
  --name psql-aircraft-maintenance-dev

# Add your IP (for local testing)
az postgres flexible-server firewall add \
  --resource-group rg-aircraft-maintenance-dev \
  --name psql-aircraft-maintenance-dev \
  --rule-name allow-my-ip \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP
```

### Problem: `Error: 403 Forbidden on ACR`

**Solution:**
```bash
# Check ACR permissions
az acr repository show-permissions \
  --name acraircraftmaintenancedev \
  --repository aircraft-maintenance

# Re-login
az acr login --name acraircraftmaintenancedev
```

### Problem: `Error: Terraform state locked`

**Solution:**
```bash
# List locks
terraform force-unlock LIST

# Force unlock with lock ID
terraform force-unlock <LOCK_ID>
```

### Problem: `Error: App Service can't pull image`

**Solution:**
```bash
# Check managed identity
az webapp identity show \
  --resource-group rg-aircraft-maintenance-dev \
  --name app-aircraft-maintenance-dev

# Verify ACR role assignment
az role assignment list \
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.ContainerRegistry/registries/acraircraftmaintenancedev
```

---

## 15. Rollback Procedures

### 15.1 — Quick Rollback (App Service)

If the new image has issues, rollback to the previous image:

```bash
# List available images
az acr repository show-tags \
  --name acraircraftmaintenancedev \
  --repository aircraft-maintenance

# Rollback to specific tag
az webapp config container set \
  --resource-group rg-aircraft-maintenance-dev \
  --name app-aircraft-maintenance-dev \
  --docker-custom-image-name acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:PREVIOUS_TAG
```

### 15.2 — Stop App Service

If you need to stop the app immediately:

```bash
az webapp stop \
  --resource-group rg-aircraft-maintenance-dev \
  --name app-aircraft-maintenance-dev
```

### 15.3 — Infrastructure Rollback (Terraform)

```bash
cd infra

# Check state history
git log --oneline

# Checkout previous commit
git checkout <previous-commit>

# Plan and apply
terraform plan -out=tfplan
terraform apply tfplan
```

### 15.4 — Complete Destruction (Nuclear Option)

**⚠️ THIS DELETES EVERYTHING — USE WITH CAUTION**

```bash
cd infra
terraform destroy
```

Also delete the resource group:
```bash
az group delete --name rg-aircraft-maintenance-dev --yes --no-wait
```

---

## 16. Security Best Practices

### 16.1 — Secrets Management

1. **Never hardcode secrets** — Use Azure Key Vault
2. **Use managed identity** — No credentials stored in code
3. **Rotate secrets** — Change passwords regularly
4. **Use RBAC** — Key Vault uses role-based access control

### 16.2 — Network Security

1. **Enable HTTPS only** — All traffic encrypted
2. **Use Private Endpoints** — For production databases
3. **Restrict IP ranges** — PostgreSQL firewall rules
4. **Enable DDoS protection** — For production

### 16.3 — Application Security

1. **Non-root container** — Dockerfile runs as `appuser`
2. **SSL required** — PostgreSQL connections use `sslmode=require`
3. **Strong passwords** — Auto-generated secrets
4. **Input validation** — Flask-WTF for form validation
5. **CSRF protection** — Enable for production

### 16.4 — Monitoring

1. **Enable Application Insights** — Track requests, errors, performance
2. **Set up alerts** — High response time, error rate, CPU usage
3. **Centralized logging** — Log Analytics Workspace
4. **Regular audits** — Review access logs

### 16.5 — Backup & Recovery

1. **Enable PostgreSQL backups** — Automated daily backups
2. **Geo-redundant backups** — For production
3. **Terraform state backup** — Stored in Azure Storage
4. **Docker image versioning** — Keep previous versions

---

## Appendix A: File Structure

```
your-project/
├── .env.example                      # Environment variables template
├── .github/
│   └── workflows/
│       └── deploy.yml                # CI/CD pipeline
├── app/
│   ├── Dockerfile                    # Production multi-stage build
│   ├── .dockerignore                 # Docker build exclusions
│   ├── gunicorn.conf.py              # Gunicorn production config
│   ├── app_config.py                 # Updated with PostgreSQL support
│   ├── requirements.txt              # Updated with psycopg2 + Azure SDK
│   ├── __init__.py                   # Flask app factory
│   ├── models.py                     # SQLAlchemy models
│   ├── run.py                        # Alternative entry point
│   ├── routes/                       # URL routes
│   ├── services/                     # Business logic
│   └── utils/                        # Utility functions
├── infra/
│   ├── main.tf                       # Provider + resource group
│   ├── variables.tf                  # All input variables
│   ├── outputs.tf                    # Deployment outputs
│   ├── acr.tf                        # Container Registry
│   ├── postgres.tf                   # PostgreSQL Flexible Server
│   ├── keyvault.tf                   # Key Vault + secrets
│   ├── appservice.tf                 # App Service (container)
│   ├── monitoring.tf                 # App Insights + Log Analytics
│   └── terraform.tfvars.example      # Variable template
├── templates/                        # Jinja2 HTML templates
├── static/                           # Static files
├── data/                             # Sample data
├── DEPLOYMENT.md                     # Deployment architecture guide
├── SETUP_GUIDE.md                    # This guide
├── README.md                         # Project README
├── main.py                           # Application entry point
├── docker-compose.yml                # Local Docker setup
└── import_data.py                    # Data import utility
```

---

## Appendix B: Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Flask environment | `development` | Yes |
| `SECRET_KEY` | Flask secret key | Auto-generated | Yes (prod) |
| `JWT_SECRET_KEY` | JWT secret key | Auto-generated | Yes (prod) |
| `DATABASE_URL` | PostgreSQL connection string | SQLite (local) | Yes (Azure) |
| `WEBSITES_PORT` | App Service port | `5000` | Yes |
| `LOG_LEVEL` | Logging level | `info` | No |
| `AZURE_KEY_VAULT_URL` | Key Vault URL | Empty | No |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | App Insights | Auto-set | No |
| `GUNICORN_WORKERS` | Number of workers | Auto (2*CPU+1) | No |

---

## Appendix C: Azure CLI Reference

```bash
# Complete deployment command sequence
az login
az account set --subscription "<SUB_ID>"
az acr login --name acraircraftmaintenancedev
docker build -t acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest ./app
docker push acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest
az webapp config container set -g rg-aircraft-maintenance-dev -n app-aircraft-maintenance-dev --docker-custom-image-name acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest
az webapp restart -g rg-aircraft-maintenance-dev -n app-aircraft-maintenance-dev
curl https://app-aircraft-maintenance-dev.azurewebsites.net/health
```

---

**End of Setup Guide**
