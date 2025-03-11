# Terraform

This project uses Terraform to deploy a containerized application to Azure Container Apps.

## Infrastructure Components
- Azure Resource Group
- Azure Container Registry (ACR)
- Azure Container App Environment
- Azure Container App

## CI/CD Pipeline
The GitHub Actions workflow handles:
1. Provisioning infrastructure using Terraform
2. Building the Docker image
3. Pushing the image to Azure Container Registry
4. Deploying the application to Azure Container App

## Prerequisites
- Azure subscription
- GitHub repository with secrets configured:
  - AZURE_CREDENTIALS: Azure service principal credentials

## Local Development
```bash
# Initialize Terraform
cd terraform
terraform init

# Plan the deployment
terraform plan

# Apply the changes
terraform apply
```

## Importing Existing Resources
If you encounter the error that resources already exist in Azure but are not in the Terraform state:

```bash
# Navigate to the terraform directory
cd terraform

# Import the existing Container App
terraform import azurerm_container_app.app /subscriptions/{subscription_id}/resourceGroups/RG_RALFV2/providers/Microsoft.App/containerApps/caralfuatv2

# Then run apply to update the state
terraform apply
```

The CI/CD workflow is configured to automatically detect and import existing resources before applying changes.

## Application
The application consists of a FastAPI backend and a Streamlit frontend, both containerized using Docker.