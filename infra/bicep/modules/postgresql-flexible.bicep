// A managed PostgreSQL target.
//
// Creates: a flexible server with private access, Entra authentication, and diagnostics.
// Assumes: the subnet is delegated to Microsoft.DBforPostgreSQL/flexibleServers and the
// private DNS zone exists. This module uses virtual-network injection, not a private
// endpoint: the server lives *inside* the delegated subnet, and a delegated subnet cannot
// also host private endpoints. The DNS zone must therefore be a
// `*.private.postgres.database.azure.com` zone, not the `privatelink.*` zone a private
// endpoint would use, and it must be linked to the virtual network.
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

@description('Resource id of the subnet delegated to Microsoft.DBforPostgreSQL/flexibleServers. The server is injected into it.')
param delegatedSubnetId string

@description('Resource id of a private DNS zone ending in .private.postgres.database.azure.com, linked to the virtual network.')
param privateDnsZoneId string
param logAnalyticsWorkspaceId string

@minValue(7)
@maxValue(35)
param backupRetentionDays int

param zoneRedundant bool

@description('Geo-redundant backup. Immutable after the server is created, so it is an explicit decision here rather than a side effect of zoneRedundant. Enabled by default; disabling it permanently removes geo-restore for this server.')
@allowed(['Enabled', 'Disabled'])
param geoRedundantBackup string = 'Enabled'

@description('Major version. Chosen from the assessed source version and its upgrade path. 14 reaches community end of life on 2026-11-12 and is offered only as an interim landing for an estate that cannot yet move further.')
@allowed(['14', '15', '16', '17', '18'])
param postgresVersion string = '17'

@description('Compute size. Sized from measured evidence. Must belong to the tier below: Burstable uses Standard_B*, GeneralPurpose Standard_D*ds_v5, MemoryOptimized Standard_E*ds_v5.')
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
      // AVL-003: an explicit, immutable decision. See the parameter description.
      geoRedundantBackup: geoRedundantBackup
    }
    highAvailability: {
      // AVL-002: configuring this is not the same as testing it. A controlled failover is
      // a blocking validation check.
      mode: zoneRedundant ? 'ZoneRedundant' : 'Disabled'
    }
    network: {
      // SEC-001 and NET-001: private access only, by virtual-network injection. Stated
      // explicitly even though injection implies it, so the decision is visible in the
      // template rather than inherited from the networking mode.
      publicNetworkAccess: 'Disabled'
      delegatedSubnetResourceId: delegatedSubnetId
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
