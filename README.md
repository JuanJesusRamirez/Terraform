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

## Application
The application consists of a FastAPI backend and a Streamlit frontend, both containerized using Docker.