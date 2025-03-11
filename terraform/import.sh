#!/bin/bash

# Import the existing Container App into Terraform state
echo "Importing existing Container App into Terraform state..."
terraform import azurerm_container_app.app /subscriptions/960eb1ea-f872-46cb-bdee-af0c8c00607c/resourceGroups/RG_RALFV2/providers/Microsoft.App/containerApps/caralfuatv2
