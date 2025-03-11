terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "example" {
  name     = "terraform-github-rg"
  location = "East US"
  
  tags = {
    environment = "sandbox"
    deployed_by = "github-actions"
  }
}

output "resource_group_id" {
  value = azurerm_resource_group.example.id
}