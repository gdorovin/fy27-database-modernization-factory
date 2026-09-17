// Composition only. This file creates no resources of its own, so the modules stay
// independently reviewable and independently replaceable.
//
// Preview with `az deployment group what-if`. Nothing in this repository applies it.

targetScope = 'resourceGroup'

@description('Workload identifier used in resource names. Lowercase, 3-16 characters.')
@minLength(3)
@maxLength(16)
param workloadName string

@description('Environment identifier. Defaults to a non-production value deliberately.')
@allowed(['dev', 'test', 'stage', 'prod'])
param environmentName string = 'dev'

@description('Azure region. Required: there is no correct default for a data residency constraint.')
param location string

@description('Which target to deploy. One workload, one target, chosen from evidence.')
@allowed(['sql-database', 'sql-managed-instance', 'postgresql-flexible'])
param targetKind string

@description('Resource id of the data subnet. For sql-database it holds the private endpoint; for sql-managed-instance and postgresql-flexible it must be delegated to the service, because those targets are injected into the virtual network rather than reached through a private endpoint.')
param privateEndpointSubnetId string

@description('Resource id of the private DNS zone for the target service. sql-database needs privatelink.database.windows.net; postgresql-flexible needs a zone ending in .private.postgres.database.azure.com linked to the virtual network. One zone never serves both, which is why the parameter file must be edited per target.')
param privateDnsZoneId string

@description('Resource id of the Log Analytics workspace receiving diagnostics.')
param logAnalyticsWorkspaceId string

@description('Entra ID object id of the administrator group. No password parameter exists.')
param administratorGroupObjectId string

@description('Administrator group display name, recorded on the resource.')
param administratorGroupName string

@description('Backup retention in days. Conservative default; raise it, do not lower it silently.')
@minValue(7)
@maxValue(35)
param backupRetentionDays int = 14

@description('Zone redundancy. Costs more and survives a zone failure.')
param zoneRedundant bool = false

@description('Backup storage redundancy for the SQL targets. Decided separately from zone redundancy; Geo is the platform default and keeps geo-restore available.')
@allowed(['Local', 'Zone', 'Geo', 'GeoZone'])
param backupStorageRedundancy string = 'Geo'

@description('Geo-redundant backup for the PostgreSQL target. Immutable after creation.')
@allowed(['Enabled', 'Disabled'])
param geoRedundantBackup string = 'Enabled'

@description('Tags applied to every resource. Include an owner; an unowned resource has no incident response.')
param tags object = {
  workload: workloadName
  environment: environmentName
  managedBy: 'fy27-database-modernization-factory'
  deploymentMode: 'reference-only'
}

var namePrefix = toLower('${workloadName}-${environmentName}')

module sqlDatabase 'modules/sql-database.bicep' = if (targetKind == 'sql-database') {
  name: 'deploy-sql-database'
  params: {
    namePrefix: namePrefix
    location: location
    tags: tags
    administratorGroupObjectId: administratorGroupObjectId
    administratorGroupName: administratorGroupName
    privateEndpointSubnetId: privateEndpointSubnetId
    privateDnsZoneId: privateDnsZoneId
    logAnalyticsWorkspaceId: logAnalyticsWorkspaceId
    backupRetentionDays: backupRetentionDays
    zoneRedundant: zoneRedundant
    backupStorageRedundancy: backupStorageRedundancy
  }
}

module sqlManagedInstance 'modules/sql-managed-instance.bicep' = if (targetKind == 'sql-managed-instance') {
  name: 'deploy-sql-managed-instance'
  params: {
    namePrefix: namePrefix
    location: location
    tags: tags
    administratorGroupObjectId: administratorGroupObjectId
    administratorGroupName: administratorGroupName
    subnetId: privateEndpointSubnetId
    logAnalyticsWorkspaceId: logAnalyticsWorkspaceId
    backupRetentionDays: backupRetentionDays
    zoneRedundant: zoneRedundant
    backupStorageRedundancy: backupStorageRedundancy
  }
}

module postgresqlFlexible 'modules/postgresql-flexible.bicep' = if (targetKind == 'postgresql-flexible') {
  name: 'deploy-postgresql-flexible'
  params: {
    namePrefix: namePrefix
    location: location
    tags: tags
    administratorGroupObjectId: administratorGroupObjectId
    administratorGroupName: administratorGroupName
    delegatedSubnetId: privateEndpointSubnetId
    privateDnsZoneId: privateDnsZoneId
    logAnalyticsWorkspaceId: logAnalyticsWorkspaceId
    backupRetentionDays: backupRetentionDays
    zoneRedundant: zoneRedundant
    geoRedundantBackup: geoRedundantBackup
  }
}

@description('The deployed target kind, echoed back so a validation check can assert on it.')
output deployedTargetKind string = targetKind

@description('Name prefix used, so validation can locate the resources it needs to check.')
output namePrefix string = namePrefix
