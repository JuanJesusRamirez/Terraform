#!/bin/bash

# Import the existing Container App into Terraform state for production environment
echo "Importing existing Container App into Terraform state..."
terraform import azurerm_container_app.app /subscriptions/960eb1ea-f872-46cb-bdee-af0c8c00607c/resourceGroups/RG_RALFPRD/providers/Microsoft.App/containerApps/caralfprd
