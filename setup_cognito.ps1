# setup_cognito.ps1 - Windows PowerShell version

$REGION = "us-east-1"
$USERNAME = "fisMcpUser"
$PASSWORD = "fisMcpUser123!"

# Create User Pool
$pool = aws cognito-idp create-user-pool `
  --pool-name "FisMcpPool" `
  --policies '{"PasswordPolicy":{"MinimumLength":8}}' `
  --region $REGION | ConvertFrom-Json
$POOL_ID = $pool.UserPool.Id

# Create App Client (with secret for DevOps Agent Console)
$client = aws cognito-idp create-user-pool-client `
  --user-pool-id $POOL_ID `
  --client-name "FisMcpClient" `
  --generate-secret `
  --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" `
  --allowed-o-auth-flows code `
  --allowed-o-auth-scopes openid `
  --allowed-o-auth-flows-user-pool-client `
  --supported-identity-providers COGNITO `
  --callback-urls "https://api.prod.cp.aidevops.us-east-1.api.aws/v1/register/mcpserver/callback" `
  --region $REGION | ConvertFrom-Json
$CLIENT_ID = $client.UserPoolClient.ClientId
$CLIENT_SECRET = $client.UserPoolClient.ClientSecret

# Create User
aws cognito-idp admin-create-user `
  --user-pool-id $POOL_ID `
  --username $USERNAME `
  --region $REGION `
  --message-action SUPPRESS | Out-Null

# Set Password
aws cognito-idp admin-set-user-password `
  --user-pool-id $POOL_ID `
  --username $USERNAME `
  --password $PASSWORD `
  --region $REGION `
  --permanent | Out-Null

# Get Bearer Token
$auth = aws cognito-idp initiate-auth `
  --client-id $CLIENT_ID `
  --auth-flow USER_PASSWORD_AUTH `
  --auth-parameters "USERNAME=$USERNAME,PASSWORD=$PASSWORD" `
  --region $REGION | ConvertFrom-Json
$BEARER_TOKEN = $auth.AuthenticationResult.AccessToken

# Output
Write-Host "Pool ID: $POOL_ID"
Write-Host "Discovery URL: https://cognito-idp.$REGION.amazonaws.com/$POOL_ID/.well-known/openid-configuration"
Write-Host "Client ID: $CLIENT_ID"
Write-Host "Client Secret: $CLIENT_SECRET"
Write-Host "Bearer Token: $BEARER_TOKEN"

# Set environment variables for current session
$env:BEARER_TOKEN = $BEARER_TOKEN
$env:COGNITO_CLIENT_ID = $CLIENT_ID
