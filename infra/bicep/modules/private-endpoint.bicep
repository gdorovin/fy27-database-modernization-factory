// Private connectivity, with DNS integration in the same module.
//
// The two belong together. A private endpoint without a DNS zone group resolves to the
// public address, which looks correct in a diagram and fails at cutover — and that failure
// is the single most common cutover-night surprise.

@description('Lowercase name prefix for the endpoint.')
param namePrefix string

param location string
param tags object

@description('Subnet hosting the endpoint.')
param subnetId string

@description('Private DNS zone matching the target service.')
param privateDnsZoneId string

@description('Resource the endpoint points at.')
param targetResourceId string

@description('Service group, for example sqlServer or postgresqlServer.')
param groupId string

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: '${namePrefix}-pe'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${namePrefix}-plsc'
        properties: {
          privateLinkServiceId: targetResourceId
          groupIds: [groupId]
        }
      }
    ]
  }
}

// NET-002: without this, name resolution silently returns the public address.
resource dnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: privateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'config'
        properties: {
          privateDnsZoneId: privateDnsZoneId
        }
      }
    ]
  }
}

output privateEndpointId string = privateEndpoint.id
output privateEndpointName string = privateEndpoint.name
