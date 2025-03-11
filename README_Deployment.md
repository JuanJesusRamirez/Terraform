# 🚀 Project RALF Deployment

## 📌 Prerequisites
Before deploying the application, make sure you have the following resources in **Microsoft Azure**:
1. An active **Azure Subscription**.
2. **Application registration in Microsoft Entra**, configured with:
  - **Client ID**
  - **Client Secret**
  - **Tenant ID**
  - **Redirect URI**
3. **Azure OpenAI Service** with access to **GPT-4o-mini**.
We are very interested in having available quota for the **o3-mini**.
4. **Cosmos DB Account** with:
  - **Endpoint**
  - **Access Key**
  - **Configured database and container**
5. **Blob Storage Account**.
6. **Azure Key Vault** to manage secrets.
7. **Azure Container Registry** to store Docker images.
8. **Azure Container App** to deploy the application.
9. **Azure DevOps** configured with:
  - **Connection to Container Registry**
  - **Connection to Resource Manager**
10. **Azure Databricks** for testing with notebooks and consuming them serverless.
11. **Azure AI Services** for integrating AI capabilities.
We are very interested in having available quota for the **DeepSeek-R1**.
  > The connection to the Resource Manager is made directly by selecting the chosen subscription. However, for the connection with the Container Registry, the registry must be created beforehand.

---

## 📄 Environment Configuration (`.env`)
Create a `.env` file at the root of the project with the following environment variables:

```ini
AZURE_CLIENT_ID=<CLIENT_ID>
AZURE_CLIENT_SECRET=<CLIENT_SECRET>
AZURE_TENANT_ID=<TENANT_ID>
AZ_KEYVAULT_URL=<KEYVAULT_URL>
AZ_OPENAI_KEY_SECRET_NAME=<OPENAI_KEY_SECRET_NAME>
AZ_OPENAI_ENDPOINT=<OPENAI_ENDPOINT>
AZ_COSMOS_ACCOUNT_URL=<COSMOS_ACCOUNT_URL>
AZ_COSMOS_ACCOUNT_KEY_SECRET_NAME=<COSMOS_ACCOUNT_KEY_SECRET_NAME>
AZ_COSMOS_CONTAINER_NAME=<COSMOS_CONTAINER_NAME>
AZ_COSMOS_DATABASE_NAME=<COSMOS_DATABASE_NAME>
AZ_BLOB_CONNECTION_STRING_SECRET_NAME=<BLOB_CONNECTION_STRING_SECRET_NAME>
REDIRECT_URI=<REDIRECT_URI>
BACKEND_API_URL=<BACKEND_API_URL>
```

> **Note:** Never share sensitive credentials in public repositories. It is recommended to use **Azure Key Vault** to manage secrets.

---

## 📌 Azure DevOps Pipeline Configuration
The following **`azure-pipelines.yml`** file defines the build and deployment process of the application:

```yaml
trigger:
- <DEPLOY_BRANCH>

resources:
- repo: self

variables:
  dockerRegistryServiceConnection: '<DOCKER_REGISTRY_SERVICE_CONNECTION>'
  imageRepository: '<IMAGE_REPOSITORY>'
  containerRegistry: '<CONTAINER_REGISTRY>'
  dockerfilePath: '**/Dockerfile'
  tag: '<TAG>'
  vmImageName: '<VM_IMAGE>'

stages:
- stage: Build
  displayName: Build and push stage
  jobs:
  - job: Build
    displayName: Build
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: Docker@2
      displayName: Build and push an image to container registry
      inputs:
        command: buildAndPush
        repository: $(imageRepository)
        dockerfile: $(dockerfilePath)
        containerRegistry: $(dockerRegistryServiceConnection)
        tags: |
          $(tag)

    - task: AzureCLI@2
      displayName: 'Create Azure Container App'
      inputs:
        azureSubscription: '<AZURE_SUBSCRIPTION>'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az containerapp up \
            --name <CONTAINER_APP_NAME> \
            --resource-group <RESOURCE_GROUP> \
            --location <AZURE_REGION> \
            --environment <CONTAINER_APP_ENVIRONMENT> \
            --image $(containerRegistry)/$(imageRepository):$(tag) \
            --target-port <APP_PORT> \
            --ingress <INGRESS_TYPE> \
            --query properties.configuration.ingress.fqdn
```

---

## 🚀 Deployment Steps
1. **Configure credentials** in Azure Key Vault and ensure the `.env` file contains the correct values.
2. **Create the pipeline** in Azure DevOps using the `azure-pipeline-uat.yaml` file as a reference.
3. **Push the code to the repository** in Azure DevOps.
4. **Run the CI/CD pipeline**, which will:
    - Build the Docker image.
    - Push the image to **Azure Container Registry**.
    - Create and deploy the application in **Azure Container Apps**.
5. **Access the application** through the URL generated after deployment.

---

## 📌 Final Notes
- Ensure that **Azure DevOps** has the appropriate permissions to access **Azure Container Registry** and **Azure Resource Manager**.
- You can modify the **pipeline YAML** to adapt it to **production** or **staging** environments.
- For debugging, check the execution logs in **Azure DevOps** and **Azure Container Apps**.

---

Ready! With this README, your team will be able to deploy the RALF project efficiently and automatically. 🚀