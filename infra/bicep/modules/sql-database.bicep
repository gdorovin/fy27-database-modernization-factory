// A database-scoped SQL target.
//
// Creates: logical server, database, private endpoint, diagnostics.
// Assumes: the subnet and private DNS zone already exist and are managed elsewhere.
// Deliberately does not: create a SQL administrator login. Authentication is Entra-only,
// so there is no password parameter to leak, rotate, or forget.

@description('Lowercase name prefix, already combined with the environment.')
param namePrefix string

param location string
param tags object

@description('Entra ID group object id for administrators.')
param administratorGroupObjectId string
param administratorGroupName string

param privateEndpointSubnetId string
param privateDnsZoneId string
param logAnalyticsWorkspaceId string

@minValue(7)
@maxValue(35)
param backupRetentionDays int

param zoneRedundant bool

@description('Where automated backups are stored. Independent of zone redundancy on purpose: deriving it from zoneRedundant silently set backups to locally redundant storage and removed geo-restore.')
@allowed(['Local', 'Zone', 'Geo', 'GeoZone'])
param backupStorageRedundancy string = 'Geo'

@description('Whether the logical server may open outbound connections (linked servers, external data sources, elastic queries). Disabled here keeps the reference deployment self-contained; enabling it requires outbound firewall rules and a documented reason.')
@allowed(['Enabled', 'Disabled'])
param restrictOutboundNetworkAccess string = 'Disabled'

@description('Service objective. Sized from measured evidence, never from an estimate.')
param skuName string = 'GP_S_Gen5_2'

@description('Maximum size in bytes. Default is deliberately modest.')
param maxSizeBytes int = 34359738368

var serverName = '${namePrefix}-sql'
var databaseName = '${namePrefix}-db'

resource sqlServer 'Microsoft.Sql/servers@2023-08-01' = {
  name: serverName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    // SEC-001: no public endpoint. Turning this on requires a policy exception with
    // compensating controls, not a parameter change.
    publicNetworkAccess: 'Disabled'
    // SEC-003: transport security is explicit rather than inherited from a default.
    minimalTlsVersion: '1.2'
    // IAM-001: Entra-only. There is no administratorLogin or password property here.
    administrators: {
      administratorType: 'ActiveDirectory'
      principalType: 'Group'
      login: administratorGroupName
      sid: administratorGroupObjectId
      tenantId: tenant().tenantId
      azureADOnlyAuthentication: true
    }
    // NET-001: outbound restriction is a parameter with a stated default, not a silent
    // hardening that breaks linked servers and external data sources on first use.
    restrictOutboundNetworkAccess: restrictOutboundNetworkAccess
  }
}

resource database 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: sqlServer
  name: databaseName
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  properties: {
    maxSizeBytes: maxSizeBytes
    zoneRedundant: zoneRedundant
    // AVL-003: backups are configured here; a restore test is a validation check, because
    // a backup that has never been restored is an assumption.
    requestedBackupStorageRedundancy: backupStorageRedundancy
  }
}

resource shortTermRetention 'Microsoft.Sql/servers/databases/backupShortTermRetentionPolicies@2023-08-01' = {
  parent: database
  name: 'default'
  properties: {
    retentionDays: backupRetentionDays
  }
}

module privateEndpoint 'private-endpoint.bicep' = {
  name: '${namePrefix}-sql-pe'
  params: {
    namePrefix: '${namePrefix}-sql'
    location: location
    tags: tags
    subnetId: privateEndpointSubnetId
    privateDnsZoneId: privateDnsZoneId
    targetResourceId: sqlServer.id
    groupId: 'sqlServer'
  }
}

module diagnostics 'diagnostics.bicep' = {
  name: '${namePrefix}-sql-diag'
  params: {
    resourceId: database.id
    resourceName: '${serverName}/${databaseName}'
    logAnalyticsWorkspaceId: logAnalyticsWorkspaceId
  }
}

output serverName string = sqlServer.name
output databaseName string = database.name
output principalId string = sqlServer.identity.principalId
