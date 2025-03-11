#!/bin/bash

# Set variables
RESOURCE_GROUP_NAME="terraform-state-rg"
STORAGE_ACCOUNT_NAME="tfstateralfv2"
CONTAINER_NAME="tfstate"
LOCATION="eastus"

# Create resource group
echo "Creating resource group $RESOURCE_GROUP_NAME..."
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

# Create storage account
echo "Creating storage account $STORAGE_ACCOUNT_NAME..."
az storage account create --resource-group $RESOURCE_GROUP_NAME --name $STORAGE_ACCOUNT_NAME --sku Standard_LRS --encryption-services blob

# Create blob container
echo "Creating blob container $CONTAINER_NAME..."
az storage container create --name $CONTAINER_NAME --account-name $STORAGE_ACCOUNT_NAME --resource-group $RESOURCE_GROUP_NAME
