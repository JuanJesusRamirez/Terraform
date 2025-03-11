#!/bin/bash

# Get the subscription ID from environment variable or use the default
SUBSCRIPTION_ID=${TF_VAR_subscription_id:-"960eb1ea-f872-46cb-bdee-af0c8c00607c"}

# Import the existing Container App into Terraform state for production environment
echo "Importing existing Container App into Terraform state..."
terraform import azurerm_container_app.app /subscriptions/${SUBSCRIPTION_ID}/resourceGroups/RG_RALFPRD/providers/Microsoft.App/containerApps/caralfprd
