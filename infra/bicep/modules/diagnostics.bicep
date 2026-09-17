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

@description('Destination workspace. Required by design. Retention is a property of the workspace and its tables, not of this setting: the per-setting retentionPolicy was retired and is deliberately absent.')
param logAnalyticsWorkspaceId string

var settingName = 'diag-${replace(resourceName, '/', '-')}'

resource diagnosticSetting 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: settingName
  scope: any(resourceId)
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        // allLogs is a superset of audit; listing both duplicated every audit record.
        categoryGroup: 'allLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

output diagnosticSettingName string = diagnosticSetting.name
