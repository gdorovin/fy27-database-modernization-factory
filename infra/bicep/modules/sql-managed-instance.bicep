// An instance-scoped SQL target.
//
// Creates: a managed instance in a delegated subnet, with diagnostics.
// Assumes: the subnet is already delegated and routed, and a route table exists. Those are
// landing-zone concerns and are checked before wave entry, not discovered here.
// Deliberately does not: create a SQL administrator login. Authentication is Entra-only.
//
// Note on cost: an instance-scoped target is materially more expensive than a
// database-scoped one. It is the right answer when instance-scoped features are genuinely
// in use, and an expensive mistake when they are not, which is why the comparison in
// `azure-target-recommendation` blocks rather than merely scores.

@description('Lowercase name prefix, already combined with the environment.')
param namePrefix string

param location string
param tags object

param administratorGroupObjectId string
param administratorGroupName string

@description('Resource id of the delegated subnet. The instance lives inside the virtual network.')
param subnetId string

param logAnalyticsWorkspaceId string

@minValue(7)
@maxValue(35)
param backupRetentionDays int

param zoneRedundant bool

@description('Service tier. Sized from measured evidence.')
@allowed(['GP_Gen8IM', 'GP_Gen8IH', 'BC_Gen8IM', 'BC_Gen8IH'])
param skuName string = 'GP_Gen8IM'

@minValue(4)
@maxValue(80)
param vCores int = 4

@minValue(32)
@maxValue(16384)
param storageSizeInGB int = 256

var instanceName = '${namePrefix}-sqlmi'

resource managedInstance 'Microsoft.Sql/managedInstances@2023-08-01-preview' = {
  name: instanceName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: skuName
    tier: startsWith(skuName, 'BC_') ? 'BusinessCritical' : 'GeneralPurpose'
  }
  properties: {
    subnetId: subnetId
    vCores: vCores
    storageSizeInGB: storageSizeInGB
    licenseType: 'LicenseIncluded'
    // SEC-001: reachable only from the virtual network.
    publicDataEndpointEnabled: false
    // SEC-003: transport security is explicit.
    minimalTlsVersion: '1.2'
    // IAM-001: Entra-only. No administratorLogin, no password.
    administrators: {
      administratorType: 'ActiveDirectory'
      principalType: 'Group'
      login: administratorGroupName
      sid: administratorGroupObjectId
      tenantId: tenant().tenantId
      azureADOnlyAuthentication: true
    }
    zoneRedundant: zoneRedundant
    requestedBackupStorageRedundancy: zoneRedundant ? 'Zone' : 'Local'
    backupStorageRedundancy: zoneRedundant ? 'Zone' : 'Local'
  }
}

resource retention 'Microsoft.Sql/managedInstances/backupShortTermRetentionPolicies@2023-08-01-preview' = {
  parent: managedInstance
  name: 'default'
  properties: {
    retentionDays: backupRetentionDays
  }
}

module diagnostics 'diagnostics.bicep' = {
  name: '${namePrefix}-sqlmi-diag'
  params: {
    resourceId: managedInstance.id
    resourceName: instanceName
    logAnalyticsWorkspaceId: logAnalyticsWorkspaceId
  }
}

output instanceName string = managedInstance.name
output principalId string = managedInstance.identity.principalId
