// public-ask-the-docs: infrastructure (tech spec section 7, Charter C8.3).
// Resource group rg-aveto-ask (eastus2) only. Exactly C8.3's list, nothing else:
//   one user-assigned identity, one container registry, one Log Analytics workspace
//   (+ table-retention children), one Container Apps environment, one Container App,
//   two role assignments (Key Vault Secrets User on the EXISTING vault, AcrPull on the registry).
// No secret value appears here. The API key is read by the platform from Key Vault by reference.

targetScope = 'resourceGroup'

@description('Azure region. Matches the resource group.')
param location string = 'eastus2'

@description('Create the Container App. False for the first pass (no image exists yet).')
param deployApp bool = false

@description('Image tag in the registry (the short commit). Used only when deployApp is true.')
param imageTag string = 'unset'

@description('Kill switch. on = the service answers nothing and calls no model. Fails closed.')
@allowed(['on', 'off'])
param killSwitch string = 'on'

@description('How the visitor key is derived: rightmost X-Forwarded-For entry, or the peer address.')
@allowed(['xff_last', 'peer'])
param clientKey string = 'xff_last'

@description('Set the 7-day retention on the two platform log tables. Only once the tables exist.')
param configureLogRetention bool = false

@description('Model price, nano-dollars per input token.')
param priceInNanoPerToken int = 3000

@description('Model price, nano-dollars per output token.')
param priceOutNanoPerToken int = 15000

@description('Monthly spend cap in US dollars.')
param monthlyCapUsd int = 10

var identityName = 'id-aveto-ask'
var registryName = 'acravetoaskgp'
var workspaceName = 'log-aveto-ask'
var environmentName = 'cae-aveto-ask'
var appName = 'ca-aveto-ask'
var vaultName = 'kv-aveto-ask-gp'
var secretName = 'anthropic-api-key'
var keyVaultSecretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: registryName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    workspaceCapping: {
      dailyQuotaGb: json('0.5')
    }
  }
}

resource consoleLogsTable 'Microsoft.OperationalInsights/workspaces/tables@2022-10-01' = if (configureLogRetention) {
  parent: workspace
  name: 'ContainerAppConsoleLogs_CL'
  properties: {
    retentionInDays: 7
    totalRetentionInDays: 7
  }
}

resource systemLogsTable 'Microsoft.OperationalInsights/workspaces/tables@2022-10-01' = if (configureLogRetention) {
  parent: workspace
  name: 'ContainerAppSystemLogs_CL'
  properties: {
    retentionInDays: 7
    totalRetentionInDays: 7
  }
}

resource managedEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
        sharedKey: workspace.listKeys().primarySharedKey
      }
    }
  }
}

// The vault already exists (created by the owner, C6.5). Referenced, never created or changed here.
resource vault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: vaultName
}

resource vaultSecretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: vault
  name: guid(vault.id, identity.id, keyVaultSecretsUserRoleId)
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsUserRoleId)
  }
}

resource registryPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: registry
  name: guid(registry.id, identity.id, acrPullRoleId)
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = if (deployApp) {
  name: appName
  location: location
  dependsOn: [
    vaultSecretsUser
    registryPull
  ]
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: managedEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: registry.properties.loginServer
          identity: identity.id
        }
      ]
      secrets: [
        {
          name: secretName
          keyVaultUrl: 'https://${vaultName}${environment().suffixes.keyvaultDns}/secrets/${secretName}'
          identity: identity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'aveto-ask'
          image: '${registry.properties.loginServer}/aveto-ask:${imageTag}'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'ANTHROPIC_API_KEY', secretRef: secretName }
            { name: 'ASK_KILL_SWITCH', value: killSwitch }
            { name: 'ASK_CLIENT_KEY', value: clientKey }
            { name: 'ASK_PRICE_IN_NANO_PER_TOKEN', value: string(priceInNanoPerToken) }
            { name: 'ASK_PRICE_OUT_NANO_PER_TOKEN', value: string(priceOutNanoPerToken) }
            { name: 'ASK_MONTHLY_CAP_USD', value: string(monthlyCapUsd) }
          ]
          probes: [
            {
              type: 'Startup'
              httpGet: {
                path: '/health'
                port: 8000
              }
              periodSeconds: 5
              failureThreshold: 24
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8000
              }
              periodSeconds: 10
            }
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8000
              }
              periodSeconds: 30
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

output registryLoginServer string = registry.properties.loginServer
output appFqdn string = app.?properties.?configuration.?ingress.?fqdn ?? ''
