// Diagnostic settings.
//
// The workspace id is required rather than optional. Making it optional would let a
// deployment succeed with no destination for its audit logs, which satisfies OBS-002 on
// paper and fails it in every way that matters.
//
// Delivery is still verified by a validation check: configuring a sink is not evidence
// that anything arrives in it.

@description('Resource receiving the diagnostic setting.')
param resourceId string

@description('Resource name, used only to build a readable setting name.')
param resourceName string

@description('Destination workspace. Required by design.')
param logAnalyticsWorkspaceId string

@description('Retention in days at the destination. Zero means the workspace policy applies.')
@minValue(0)
@maxValue(730)
param retentionDays int = 0

var settingName = 'diag-${replace(resourceName, '/', '-')}'

resource diagnosticSetting 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: settingName
  scope: any(resourceId)
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        categoryGroup: 'audit'
        enabled: true
        retentionPolicy: {
          enabled: retentionDays > 0
          days: retentionDays
        }
      }
      {
        categoryGroup: 'allLogs'
        enabled: true
        retentionPolicy: {
          enabled: retentionDays > 0
          days: retentionDays
        }
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: {
          enabled: retentionDays > 0
          days: retentionDays
        }
      }
    ]
  }
}

output diagnosticSettingName string = diagnosticSetting.name
