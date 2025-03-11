terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  
  backend "azurerm" {
    resource_group_name  = "terraform-state-prd-rg"
    storage_account_name = "tfstateralfprd"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
    # NOTE: Authentication parameters (subscription_id, tenant_id, client_id, client_secret)
    # are provided via the terraform init command in the GitHub Actions workflow
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "example" {
  name     = "RG_RALFPRD"
  location = "East US"
  
  tags = {
    environment = "production"
    deployed_by = "github-actions"
  }
}

# Create Azure Container Registry
resource "azurerm_container_registry" "acr" {
  name                = "crralfprd"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  sku                 = "Standard"
  admin_enabled       = true
}

# Create Log Analytics workspace for Container App Environment
resource "azurerm_log_analytics_workspace" "logs" {
  name                = "ralfprd-logs"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# Create Container App Environment
resource "azurerm_container_app_environment" "env" {
  name                       = "caeralfprd"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_resource_group.example.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id
}

# Create Container App
resource "azurerm_container_app" "app" {
  name                         = "caralfprd"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.example.name
  revision_mode                = "Single"

  template {
    container {
      name   = "ralfprd-container"
      image  = "${azurerm_container_registry.acr.login_server}/imgralfprd:latest"
      cpu    = 2
      memory = "4Gi"
    }
    
    # Add min_replicas setting to allow scaling to zero
    min_replicas = 0
    max_replicas = 10
  }

  ingress {
    external_enabled = true
    target_port      = 8501
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.acr.admin_password
  }

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "registry-password"
  }
}

output "resource_group_id" {
  value = azurerm_resource_group.example.id
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "container_app_url" {
  value = azurerm_container_app.app.latest_revision_fqdn
}
