# Deploy Scripts

## Prerequisites
- You will need access to the panintelligence dockerhub projects.  Please contact your Business Success Manager
- You will need experience with [docker compose](https://docs.docker.com/compose/)
- You will need a licence

## Instructions

Please run the following commands in cloud shell on azure.

```powershell
mkdir panintelligence
cd panintelligence
```

### Setting Environment Variables

```powershell
RESOURCE-GROUP=panintelligence
LOCATION="UK South"
SERVICE-PLAN=panintelligenceServicePlan
DATABASE-NAME=panintelligence
APP-NAME=panintelligence
PANINTELLIGENCELICENCE=<paste your licence here>
DATABASEUSERNAME=panintelligence
DATBASEPASSWORD=5up3r53cur3P455w0rd!
```

Next we're going to download our sample compose scripts from the panintelligence public github

```powershell
git clone https://github.com/panintelligencedev/azure-containers

cd azure-containers
```

## Create a resource group

```powershell
az group create --name $RESOURCEGROUP --location LOCATION
```

## Create an Azure Service Plan

```powershell
az appservice plan create --name $SERVICEPLAN -- resource-group $RESOURCEGROUP ---sku B3 --is-linux
```
|sku|Cost (Hour)|Cost (Month)|reccomended|
|--|--|--|--|
|P2V2|£0.373|£120|PROD|
|B3|£0.280|£38|DEV|


## Create a Database

This will create a mariadb for the 

```powershell
az mariadb server create --resource-group $RESOURCEGROUP --name $DATABASENAME --location $LOCATION --admin-user $DATABASEUSERNAME --admin-password $DATABASEPASSWORD --sku-name B_Gen5_1 --version 10.3

az mariadb server firewall-rule create --name allAzureIPs --server $DATABASENAME --resource-group $RESOURCEGROUP --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

DATABASEHOST$(az mariadb server list --query "[?name=='test-containers'].fullyQualifiedDomainName" --output tsv)
```

|sku|Cost (Hour)|Cost (Month)|recommended|
|--|--|--|--|
|B_Gen5_1|£0.029|£21|Dev|
|B_Gen5_2|£0.057|£41|Prod|

## Create a Docker Compose App

```powershell
az webapp create --resource-group $RESOURCEGROUP --plan $SERVICEPLAN --name $APPNAME --multicontainer-config-file docker-compose-panintelligence-separates.yml

```

# Cleaning up

When you've finished with your demonstration, You will want to clean up your environment.  

> This will delete everything you've done.
{.warn}

```bash

az mariadb delete --name $DATABASENAME --resource-group $RESOURCEGROUP

az webapp delete --name $APPNAME --resource-group $RESOURCEGROUP 

az appservice plan delete --name $SERVICEPLAN --resource-group $RESOURCEGROUP

```