# Deploy Scripts

## Prerequisites
- You will need access to the panintelligence dockerhub projects.  Please contact your Business Success Manager
- You will need experience with [docker compose](https://docs.docker.com/compose/)
- You will need a licence
- The [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)

## Instructions

Please run the following commands in cloud shell (bash) on azure.

```bash
mkdir panintelligence
cd panintelligence
```

### Setting Environment Variables

```bash
RESOURCEGROUP=panintelligence
STORAGEACCOUNT=panintelligence1
STORAGESHARENAME=themes
THEMESSTORAGENAME=themes
LOCATION="uksouth"
SERVICEPLAN=panintelligenceServicePlan
DATABASENAME=<unique_database_name>
APPNAME=<unique_app_name>
DATABASEUSERNAME=panintelligence
DATABASEPASSWORD=5up3r53cur3P455w0rd!
DOCKERURL=https://docker.io
DOCKERUSER=<Your docker username>
DOCKERPASSWORD=<Your docker password>
PANINTELLIGENCELICENCE=<paste your licence here>
```

Next we're going to download our sample compose scripts from the panintelligence public github

```bash
git clone https://github.com/Panintelligence/azure-containers.git

cd azure-containers

```

## Create a resource group

```bash
az group create --name $RESOURCEGROUP --location $LOCATION

```

## Create a Storage account

```bash
az storage account create --resource-group $RESOURCEGROUP --name $STORAGEACCOUNT --location $LOCATION
STORAGEKEY=$(az storage account keys list --resource-group $RESOURCEGROUP --account-name $STORAGEACCOUNT --query "[0].value" --output tsv)
```

## Create a share volume

```bash
az storage share create --name $STORAGESHARENAME --account-name $STORAGEACCOUNT --account-key $STORAGEKEY
```

## Create an Azure Service Plan

```bash
az appservice plan create --name $SERVICEPLAN --resource-group $RESOURCEGROUP --sku B3 --is-linux

```
|sku|Cost (Hour)|Cost (Month)|reccomended|
|--|--|--|--|
|P2V2|£0.373|£120|PROD|
|B3|£0.280|£38|DEV|


## Create a Database

This will create a mariadb for the 

```bash
az mariadb server create --resource-group $RESOURCEGROUP --name $DATABASENAME --location $LOCATION --admin-user $DATABASEUSERNAME --admin-password $DATABASEPASSWORD --sku-name B_Gen5_1 --version 10.3

az mariadb server firewall-rule create --name allAzureIPs --server $DATABASENAME --resource-group $RESOURCEGROUP --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

az mariadb server update --resource-group $RESOURCEGROUP --name $DATABASENAME --ssl-enforcement Disabled

DATABASEHOST=$(az mariadb server list --query "[?name=='$DATABASENAME'].fullyQualifiedDomainName" --output tsv)

az mariadb server configuration set --resource-group $RESOURCEGROUP --server $DATABASENAME --name lower_case_table_names --value 1
az mariadb server configuration set --resource-group $RESOURCEGROUP --server $DATABASENAME --name sql_mode --value ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_AUTO_VALUE_ON_ZERO,NO_ENGINE_SUBSTITUTION,STRICT_TRANS_TABLES
az mariadb server configuration set --resource-group $RESOURCEGROUP --server $DATABASENAME --name log_bin_trust_function_creators --value ON
```

|sku|Cost (Hour)|Cost (Month)|recommended|
|--|--|--|--|
|B_Gen5_1|£0.029|£21|Dev|
|B_Gen5_2|£0.057|£41|Prod|

## Create a Docker Compose App

```bash

python3 compose_build.py --host $DATABASEHOST --username $DATABASEUSERNAME --password $DATABASEPASSWORD --licence "$PANINTELLIGENCELICENCE"

az webapp create --resource-group $RESOURCEGROUP --plan $SERVICEPLAN --name $APPNAME --multicontainer-config-type COMPOSE --multicontainer-config-file docker-compose-panintelligence-separates.yml --docker-registry-server-user $DOCKERUSER --docker-registry-server-password $DOCKERPASSWORD

az webapp config appsettings set --name $APPNAME --resource-group $RESOURCEGROUP --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=true
az webapp config appsettings set --name $APPNAME --resource-group $RESOURCEGROUP --settings WEBSITES_CONTAINER_START_TIME_LIMIT=300
az webapp config container set --docker-registry-server-url $DOCKERURL --docker-registry-server-password $DOCKERPASSWORD --docker-registry-server-user $DOCKERUSER --name $APPNAME --resource-group $RESOURCEGROUP
az webapp config storage-account add --resource-group $RESOURCEGROUP --name $APPNAME --storage-type AzureFiles --share-name $STORAGESHARENAME --account-name $STORAGEACCOUNT --access-key $STORAGEKEY --custom-id "themes" --mount-path "/themes"
az webapp config storage-account add --resource-group $RESOURCEGROUP --name $APPNAME --storage-type AzureFiles --share-name $STORAGESHARENAME --account-name $STORAGEACCOUNT --access-key $STORAGEKEY --custom-id "keys" --mount-path "/keys"
```

Finally we're going to increase the logging level of the web application.

```bash
az webapp log config --docker-container-logging filesystem --name $APPNAME --resource-group $RESOURCEGROUP
```

# Cleaning up

When you've finished with your demonstration, You will want to clean up your environment.  

> This will delete everything you've done.
{.warn}

```bash

az mariadb server delete --name $DATABASENAME --resource-group $RESOURCEGROUP

az webapp delete --name $APPNAME --resource-group $RESOURCEGROUP 

az appservice plan delete --name $SERVICEPLAN --resource-group $RESOURCEGROUP

az group delete --name $RESOURCEGROUP

```
