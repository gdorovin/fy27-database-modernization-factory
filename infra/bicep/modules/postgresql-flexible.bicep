// A managed PostgreSQL target.
//
// Creates: a flexible server with private access, Entra authentication, and diagnostics.
// Assumes: the subnet is delegated and the private DNS zone exists.
// Deliberately does not: install extensions. Extension availability is verified per
// extension and per server version during assessment, and the outcome is a validation
// check rather than a template default. Enabling one here would let an unverified
// dependency into the deployment silently.

@description('Lowercase name prefix, already combined with the environment.')
param namePrefix string

param location string
param tags object

param administratorGroupObjectId string
param administratorGroupName string

param privateEndpointSubnetId string
param privateDnsZoneId string
param logAnalyticsWorkspaceId string

@minValue(7)
@maxValue(35)
param backupRetentionDays int

param zoneRedundant bool

@description('Major version. Chosen from the assessed source version and its upgrade path.')
@allowed(['14', '15', '16'])
param postgresVersion string = '16'

@description('Compute tier. Sized from measured evidence.')
param skuName string = 'Standard_D2ds_v5'

@allowed(['Burstable', 'GeneralPurpose', 'MemoryOptimized'])
param skuTier string = 'GeneralPurpose'

@minValue(32)
param storageSizeGB int = 128

var serverName = '${namePrefix}-pg'

resource flexibleServer 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: serverName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: skuName
    tier: skuTier
  }
  properties: {
    version: postgresVersion
    // IAM-001: Entra authentication only. There is no administratorLoginPassword here,
    // which is the point: a parameter that does not exist cannot be committed by mistake.
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Disabled'
      tenantId: tenant().tenantId
    }
    storage: {
      storageSizeGB: storageSizeGB
      autoGrow: 'Enabled'
    }
    backup: {
      backupRetentionDays: backupRetentionDays
      geoRedundantBackup: zoneRedundant ? 'Enabled' : 'Disabled'
    }
    highAvailability: {
      // AVL-002: configuring this is not the same as testing it. A controlled failover is
      // a blocking validation check.
      mode: zoneRedundant ? 'ZoneRedundant' : 'Disabled'
    }
    network: {
      // SEC-001 and NET-001: private access only.
      publicNetworkAccess: 'Disabled'
      delegatedSubnetResourceId: privateEndpointSubnetId
      privateDnsZoneArmResourceId: privateDnsZoneId
    }
  }
}

resource entraAdministrator 'Microsoft.DBforPostgreSQL/flexibleServers/administrators@2024-08-01' = {
  parent: flexibleServer
  name: administratorGroupObjectId
  properties: {
    principalType: 'Group'
    principalName: administratorGroupName
    tenantId: tenant().tenantId
  }
}

module diagnostics 'diagnostics.bicep' = {
  name: '${namePrefix}-pg-diag'
  params: {
    resourceId: flexibleServer.id
    resourceName: serverName
    logAnalyticsWorkspaceId: logAnalyticsWorkspaceId
  }
}

output serverName string = flexibleServer.name
output principalId string = flexibleServer.identity.principalId
