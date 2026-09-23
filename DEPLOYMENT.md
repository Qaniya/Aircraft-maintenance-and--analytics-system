# 🚀 Azure Cloud Deployment Strategy

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AZURE CLOUD (East US)                            │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    GitHub Actions CI/CD                            │  │
│  │  Push → Lint → Test → Build Docker → Push to ACR → Terraform     │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                                            │                  │
│         ▼                                            ▼                  │
│  ┌─────────────────┐                    ┌──────────────────────────┐   │
│  │  Azure Container │                    │     Terraform State      │   │
│  │    Registry      │                    │  (Azure Storage Account) │   │
│  │   (ACR Basic)    │                    └──────────────────────────┘   │
│  └────────┬────────┘                                                   │
│           │                                                             │
│           ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Azure App Service (Linux)                     │   │
│  │                   SKU: B1 (dev) / S1 (prod)                     │   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │   │
│  │  │   Flask App   │  │   Gunicorn   │  │  Managed Identity    │  │   │
│  │  │   (Docker)    │  │  (4 workers) │  │  (AcrPull + KV)     │  │   │
│  │  └──────┬───────┘  └──────────────┘  └──────────────────────┘  │   │
│  └─────────┼───────────────────────────────────────────────────────┘   │
│            │                                                            │
│            ▼                                                            │
│  ┌─────────────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Azure DB for       │  │  Azure Key   │  │  Application         │  │
│  │  PostgreSQL         │  │  Vault       │  │  Insights            │  │
│  │  (Flexible Server)  │  │              │  │                      │  │
│  │  SKU: B1ms (dev)    │  │  Secrets:    │  │  Monitoring,         │  │
│  │  32GB storage       │  │  - DB URL    │  │  Logs, Metrics       │  │
│  │  SSL required       │  │  - Flask key │  │                      │  │
│  │                     │  │  - JWT key   │  │                      │  │
│  └─────────────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   Azure Log Analytics Workspace                  │   │
│  │              (Centralized logging & alerting)                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required Tools
| Tool | Version | Purpose |
|------|---------|---------|
| Azure CLI | ≥ 2.50 | Azure resource management |
| Terraform | ≥ 1.5 | Infrastructure as Code |
| Docker | ≥ 24.0 | Container builds |
| GitHub CLI | ≥ 2.35 | (Optional) GitHub secrets setup |

### Required Azure Permissions
- **Contributor** on the target subscription
- **User Access Administrator** (for RBAC role assignments)
- **Owner** on the resource group (if using existing)

---

## IaC Tool: Terraform

### Why Terraform?

| Criteria | Terraform | ARM/Bicep | Pulumi |
|----------|-----------|-----------|--------|
| Multi-cloud | ✅ | ❌ Azure only | ✅ |
| Community modules | ✅ 3000+ | ⚠️ Limited | ⚠️ Growing |
| State management | ✅ Built-in | ❌ | ✅ |
| Learning curve | Medium | High | Medium |
| Azure support | ✅ azurerm 3.x | ✅ Native | ✅ |
| Maturity | ✅ 10+ years | ✅ Stable | ⚠️ 5 years |

### Terraform Module Structure
```
infra/
├── main.tf              # Provider config, resource group
├── variables.tf         # All input variables
├── outputs.tf           # Deployment outputs (URLs, commands)
├── acr.tf               # Azure Container Registry
├── postgres.tf          # PostgreSQL Flexible Server
├── keyvault.tf          # Key Vault + secrets
├── appservice.tf        # App Service Plan + Web App
├── monitoring.tf        # Log Analytics + Application Insights
└── terraform.tfvars.example  # Variable template
```

---

## Step-by-Step Deployment

### Phase 1: Azure Setup (One-time)

```bash
# 1. Login to Azure
az login

# 2. Create Terraform state storage (for remote state)
az group create --name rg-terraform-state --location eastus
az storage account create \
  --name stterraformstateaircraft \
  --resource-group rg-terraform-state \
  --location eastus \
  --sku Standard_LRS \
  --encryption-services blob
az storage container create \
  --name tfstate \
  --account-name stterraformstateaircraft

# 3. Create GitHub Actions service principal
az ad sp create-for-rbac \
  --name "github-actions-aircraft-maintenance" \
  --role "Contributor" \
  --scopes "/subscriptions/<YOUR_SUBSCRIPTION_ID>" \
  --sdk-auth
```

### Phase 2: GitHub Secrets Setup

Add these secrets in GitHub → Settings → Secrets → Actions:

| Secret | Value |
|--------|-------|
| `AZURE_CLIENT_ID` | Service principal client ID |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| `ACR_USERNAME` | ACR admin username (or leave empty for managed identity) |
| `ACR_PASSWORD` | ACR admin password |
| `TF_STORAGE_ACCOUNT` | Terraform state storage account name |

### Phase 3: Deploy Infrastructure

```bash
# 1. Initialize Terraform
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# 2. Plan
terraform init
terraform plan -out=tfplan

# 3. Apply (creates all Azure resources)
terraform apply tfplan

# 4. Note the outputs
terraform output
# → app_service_url: https://app-aircraft-maintenance-dev.azurewebsites.net
# → acr_login_server: acraircraftmaintenancedev.azurecr.io
```

### Phase 4: Build and Push Docker Image

```bash
# Option A: Build locally
cd app
docker build -t acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest .
docker login acraircraftmaintenancedev.azurecr.io
docker push acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest

# Option B: Build in ACR (cloud build)
az acr build \
  --registry acraircraftmaintenancedev \
  --image aircraft-maintenance:latest \
  .
```

### Phase 5: Deploy Application

```bash
# Trigger deployment
az webapp config container set \
  --resource-group rg-aircraft-maintenance-development \
  --name app-aircraft-maintenance-development \
  --docker-custom-image-name acraircraftmaintenancedev.azurecr.io/aircraft-maintenance:latest

# Verify
curl https://app-aircraft-maintenance-dev.azurewebsites.net/health
```

---

## CI/CD Pipeline (GitHub Actions)

### Pipeline Flow
```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Push to  │───▶│  Lint &  │───▶│  Build   │───▶│  Deploy  │───▶│  Smoke   │
│   main    │    │   Test   │    │  Docker  │    │ Terraform│    │   Test   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │  Push to ACR  │
                              └──────────────┘
```

### Environments
| Branch | Environment | Auto-deploy |
|--------|-------------|-------------|
| `main` | development | ✅ Yes |
| `release/*` | staging | Manual trigger |
| `main` (manual) | production | Manual trigger |

### Blue-Green Deployment (Production)
```bash
# Enable deployment slot in terraform.tfvars
enable_deployment_slot = true

# Deploy to staging slot first
az webapp deployment slot swap \
  --resource-group rg-aircraft-maintenance-production \
  --name app-aircraft-maintenance-production \
  --slot staging

# Swap when ready
az webapp deployment slot swap \
  --resource-group rg-aircraft-maintenance-production \
  --name app-aircraft-maintenance-production \
  --slot production
```

---

## Database Migration (SQLite → PostgreSQL)

Your app currently uses SQLite. The deployment automatically handles PostgreSQL:

### What Changed
1. `app_config.py` — Now reads `DATABASE_URL` env var, falls back to SQLite for dev
2. `Dockerfile` — Includes `libpq5` for PostgreSQL driver
3. `requirements.txt` — Added `psycopg2-binary`

### Migration Steps
```bash
# The database tables are created automatically by SQLAlchemy on first run.
# To migrate existing SQLite data:

# 1. Export from SQLite
python -c "
from app import create_app, db
from app.models import *
app = create_app('development')
with app.app_context():
    # Export data
    import json
    data = {}
    for model in [User, Aircraft, Component, MaintenanceRecord, Alert, FailurePrediction, FlightData]:
        data[model.__tablename__] = [r.to_dict() for r in model.query.all()]
    with open('data_export.json', 'w') as f:
        json.dump(data, f)
"

# 2. Import into PostgreSQL (set DATABASE_URL to your Azure DB first)
python -c "
import json
from app import create_app, db
from app.models import *
app = create_app('production')  # Uses DATABASE_URL
with app.app_context():
    db.create_all()
    with open('data_export.json') as f:
        data = json.load(f)
    # ... import logic
"
```

### Flask-Migrate (Recommended for Production)
```bash
pip install flask-migrate

# In your app/__init__.py, add:
from flask_migrate import Migrate
migrate = Migrate(app, db)

# Commands:
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## Cost Estimates

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

---

## Security Best Practices

1. **Secrets in Key Vault** — Never hardcode secrets; use Azure Key Vault
2. **Managed Identity** — App Service uses managed identity for ACR and Key Vault access
3. **SSL/TLS** — PostgreSQL requires `sslmode=require`
4. **Non-root container** — Dockerfile runs as `appuser`
5. **Network isolation** — Use Private Endpoints for production
6. **RBAC** — Key Vault uses RBAC, not access policies
7. **No default secrets** — Production config fails if `SECRET_KEY` not set

---

## Monitoring & Alerting

### Application Insights Tracks
- Request/response times
- Failed requests
- Exception tracking
- Dependency calls (DB, external APIs)
- Custom metrics

### Recommended Alerts
```terraform
# Add to monitoring.tf for production:
resource "azurerm_monitor_metric_alert" "high_response_time" {
  name                = "alert-high-response-time"
  resource_group_name = local.resource_group_name
  scopes              = [azurerm_linux_web_app.main.id]
  description         = "Alert when average response time > 5s"
  severity            = 2

  criteria {
    metric_namespace = "Microsoft.Web/sites"
    metric_name      = "AverageResponseTime"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 5000

    dimension {
      name     = "Instance"
      operator = "Include"
      values   = ["*"]
    }
  }
}
```

---

## Rollback Strategy

### Quick Rollback (App Service)
```bash
# Rollback to previous Docker image
az webapp config container set \
  --resource-group rg-aircraft-maintenance-production \
  --name app-aircraft-maintenance-production \
  --docker-custom-image-name <previous-image-tag>
```

### Infrastructure Rollback (Terraform)
```bash
# List state history
terraform state list

# Rollback infrastructure
git checkout <previous-commit>
cd infra
terraform plan -out=tfplan
terraform apply tfplan
```

---

## File Structure (Post-Implementation)

```
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
│   └── ...                           # (existing app code)
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
├── DEPLOYMENT.md                     # This guide
└── ...                               # (existing project files)
```
