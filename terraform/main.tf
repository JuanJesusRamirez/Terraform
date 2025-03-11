terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstateralfr3v2"
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
  name     = "RG_RALFR3"
  location = "East US"
  
  tags = {
    environment = "uat"
    deployed_by = "github-actions"
  }
}

# Create Azure Container Registry
resource "azurerm_container_registry" "acr" {
  name                = "crralfr3v2uat"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  sku                 = "Standard"
  admin_enabled       = true
}

# Create Log Analytics workspace for Container App Environment
resource "azurerm_log_analytics_workspace" "logs" {
  name                = "ralfr3v2-logs"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# Create Container App Environment
resource "azurerm_container_app_environment" "env" {
  name                       = "caeralfr3v2uatv2"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_resource_group.example.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id
}

# Create Container App
resource "azurerm_container_app" "app" {
  name                         = "caralfr3v2uatv2"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.example.name
  revision_mode                = "Single"

  template {
    container {
      name   = "ralfr3-container"
      image  = "${azurerm_container_registry.acr.login_server}/imgralfr3v2uat:latest"
      cpu    = 0.5
      memory = "1Gi"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8501
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server   = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
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