// Example parameters. Every value here is obviously fake.
//
// Copy this file, substitute real values outside this repository, and run what-if.
// Do not commit a parameter file containing real resource ids.

using './main.bicep'

param workloadName = 'storeops'
param environmentName = 'dev'
param location = 'northeurope'
param targetKind = 'sql-managed-instance'

// Placeholder resource ids. The all-zero subscription id makes it obvious these are not real.
param privateEndpointSubnetId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-placeholder/providers/Microsoft.Network/virtualNetworks/vnet-placeholder/subnets/snet-data'
param privateDnsZoneId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-placeholder/providers/Microsoft.Network/privateDnsZones/privatelink.database.windows.net'
param logAnalyticsWorkspaceId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-placeholder/providers/Microsoft.OperationalInsights/workspaces/law-placeholder'

// Entra ID group, not an individual. Individual administrators leave with the individual.
param administratorGroupObjectId = '00000000-0000-0000-0000-000000000000'
param administratorGroupName = 'grp-placeholder-dba'

param backupRetentionDays = 14
param zoneRedundant = false

param tags = {
  workload: 'storeops'
  environment: 'dev'
  owner: 'REPLACE-ME-owner-role'
  managedBy: 'fy27-database-modernization-factory'
  deploymentMode: 'reference-only'
}
