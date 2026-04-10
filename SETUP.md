# FIS Recommender MCP - Setup Instructions

## Prerequisites

- Python 3.10+
- AWS CLI configured
- AWS account with appropriate permissions

## 1. Project Setup

### Linux/macOS
```bash
mkdir fis-recommender-mcp && cd fis-recommender-mcp
touch server.py requirements.txt __init__.py
```

### Windows (PowerShell)
```powershell
mkdir fis-recommender-mcp; cd fis-recommender-mcp
New-Item server.py, requirements.txt, __init__.py
```

**requirements.txt**:
```
mcp
boto3
```

**server.py**: Create MCP server with FastMCP and tool decorators

## 2. Install AgentCore Toolkit

```bash
pip install bedrock-agentcore-starter-toolkit
```

## 3. Configure MCP Deployment

```bash
agentcore configure -e server.py --protocol MCP
```

**Prompts**:
- Execution role: Use existing IAM role or create one
- ECR: Press enter to auto-create
- OAuth: Type `yes`
- Discovery URL: (from Cognito setup below)
- Client ID: (from Cognito setup below)

## 4. Deploy to AWS

```bash
agentcore launch
```

**Output**: Agent ARN like `arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/NAME-ID`

## 5. Setup Cognito OAuth

### Linux/macOS
```bash
chmod +x setup_cognito.sh
source setup_cognito.sh
```

### Windows (PowerShell)
```powershell
.\setup_cognito.ps1
```

### Manual Steps (any OS)

```bash
# Set variables
export REGION=us-east-1
export USERNAME=fisMcpUser
export PASSWORD=fisMcpUser123

# Create User Pool
export POOL_ID=$(aws cognito-idp create-user-pool \
  --pool-name "FisMcpPool" \
  --policies '{"PasswordPolicy":{"MinimumLength":8}}' \
  --region $REGION | jq -r '.UserPool.Id')

# Create App Client
export CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $POOL_ID \
  --client-name "FisMcpClient" \
  --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" \
  --region $REGION | jq -r '.UserPoolClient.ClientId')

# Create User
aws cognito-idp admin-create-user \
  --user-pool-id $POOL_ID \
  --username $USERNAME \
  --region $REGION \
  --message-action SUPPRESS

# Set Password
aws cognito-idp admin-set-user-password \
  --user-pool-id $POOL_ID \
  --username $USERNAME \
  --password $PASSWORD \
  --region $REGION \
  --permanent

# Get Bearer Token
export BEARER_TOKEN=$(aws cognito-idp initiate-auth \
  --client-id "$CLIENT_ID" \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=$USERNAME,PASSWORD=$PASSWORD \
  --region $REGION | jq -r '.AuthenticationResult.AccessToken')

# Print OAuth details
echo "Client ID: $CLIENT_ID"
echo "Discovery URL: https://cognito-idp.$REGION.amazonaws.com/$POOL_ID/.well-known/openid-configuration"
```

## 6. Create Cognito Domain (for DevOps Agent Console)

**AWS Console**:
1. Go to Cognito → User Pools → your pool
2. App integration → Domain → Create domain
3. Domain name: e.g. `fismcp` (no underscores)

**CLI (Linux/macOS)**:
```bash
aws cognito-idp create-user-pool-domain \
  --domain fismcp \
  --user-pool-id $POOL_ID \
  --region $REGION
```

**CLI (Windows PowerShell)**:
```powershell
aws cognito-idp create-user-pool-domain `
  --domain fismcp `
  --user-pool-id $POOL_ID `
  --region $REGION
```

**OAuth URLs**:
- Exchange URL: `https://{DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/token`
- Authorization URL: `https://{DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/authorize`

## 7. Configure Callback URL

**AWS Console**:
1. Cognito → User Pools → FisMcpPool
2. App integration → App clients → FisMcpClient → Edit
3. Hosted UI settings:
   - Callback URLs: `https://api.prod.cp.aidevops.us-east-1.api.aws/v1/register/mcpserver/callback`
   - OAuth flows: Authorization code grant
   - OAuth scopes: openid
4. Save changes

## 8. Register in DevOps Agent Console

1. Go to AIDevOps → Your Agent → Settings → MCP Servers
2. Add Server:
   - **Name**: FIS Recommender
   - **Endpoint**: `https://bedrock-agentcore.{REGION}.amazonaws.com/runtimes/{ENCODED_ARN}/invocations`
   - **Client ID**: `<from step 5>`
   - **Exchange URL**: `https://{DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/token`
   - **Authorization URL**: `https://{DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/authorize`
   - **Scopes**: `openid`
   - **PKCE**: Enabled

## 9. Test Locally

### Linux/macOS
```bash
python server.py
# New terminal:
python mcp_test.py
```

### Windows (PowerShell)
```powershell
python server.py
# New terminal:
python mcp_test.py
```

## 10. Test Remote

### Linux/macOS
```bash
export AGENT_ARN="<from step 4>"
export BEARER_TOKEN="<from step 5>"
python mcp_remote_test.py
```

### Windows (PowerShell)
```powershell
$env:AGENT_ARN = "<from step 4>"
$env:BEARER_TOKEN = "<from step 5>"
python mcp_remote_test.py
```

## Optional: Deploy Lambda Client

### Linux/macOS
```bash
chmod +x deploy_lambda.sh
./deploy_lambda.sh
```

### Windows (PowerShell)
```powershell
.\deploy_lambda.ps1
```

## Quick Reference

**Refresh Token (Linux/macOS)**:
```bash
aws cognito-idp initiate-auth \
  --client-id $CLIENT_ID \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=$USERNAME,PASSWORD=$PASSWORD \
  --region $REGION | jq -r '.AuthenticationResult.AccessToken'
```

**Refresh Token (Windows PowerShell)**:
```powershell
(aws cognito-idp initiate-auth `
  --client-id $CLIENT_ID `
  --auth-flow USER_PASSWORD_AUTH `
  --auth-parameters "USERNAME=$USERNAME,PASSWORD=$PASSWORD" `
  --region $REGION | ConvertFrom-Json).AuthenticationResult.AccessToken
```

**Encode ARN for URL (any OS)**:
```bash
python -c "from urllib.parse import quote; print(quote('arn:aws:...', safe=''))"
```

**Generate Secret for DevOps Agent**:
```bash
aws cognito-idp create-user-pool-client --user-pool-id $POOL_ID --client-name MyClient --generate-secret --region $REGION
```