# FIS Recommender MCP

MCP server that recommends and creates AWS FIS experiments based on resilience findings.

## Deployment Options

### Option 1: MCP Server (for DevOps Agent)

#### 1. Deploy MCP Server

```bash
# Install toolkit
pip install bedrock-agentcore-starter-toolkit

# Configure and deploy
agentcore configure -e server.py --protocol MCP
agentcore launch
```

#### 2. Setup OAuth (Cognito)

```bash
chmod +x setup_cognito.sh
source setup_cognito.sh
```

Save the output (Client ID, Discovery URL, Bearer Token).

#### 3. Register in DevOps Agent Console

1. Go to AIDevOps → Your Agent → Settings → MCP Servers
2. Add Server:
   - **Endpoint**: `https://bedrock-agentcore.{REGION}.amazonaws.com/runtimes/{ENCODED_ARN}/invocations`
   - **Client ID**: From step 2
   - **Exchange URL**: `https://{COGNITO_DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/token`
   - **Authorization URL**: `https://{COGNITO_DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/authorize`
   - **Scopes**: `openid`
   - **PKCE**: Enabled

#### 4. Test

Ask DevOps Agent:
```
"Recommend FIS experiments for network latency issues"
```

### Option 2: Lambda Client (for API Gateway, EventBridge)

```bash
chmod +x deploy_lambda.sh
./deploy_lambda.sh

# Test
aws lambda invoke --function-name fis-recommender-mcp-client --region {REGION} \
  --payload '{"tool":"recommend_fis_experiments","arguments":{"finding":{"summary":"network latency"}}}' \
  response.json && cat response.json
```

## Available Tools

### recommend_fis_experiments
Get FIS experiment recommendations.

**Input**: `{"finding": {"summary": "network latency"}}`

**Keywords**: network, latency, database, cpu, lambda

### create_fis_template
Create FIS experiment template in AWS.

**Input**:
```json
{
  "recommendation": {
    "action": "aws:network:disrupt-connectivity",
    "duration": "PT5M",
    "description": "Test network resilience"
  },
  "target": {
    "resourceType": "aws:ec2:instance",
    "selectionMode": "COUNT(1)",
    "tags": {"Environment": "staging"},
    "roleArn": "arn:aws:iam::ACCOUNT:role/FISRole"
  }
}
```

## Documentation

- [Setup Guide](SETUP.md) - Complete setup instructions
- [Architecture](ARCHITECTURE.md) - System design
- [Agent Instructions](AGENT_INSTRUCTIONS.md) - For DevOps Agent
- [Lambda Deploy](LAMBDA_DEPLOY.md) - Lambda client setup

## Local Testing

```bash
# Start server
python server.py

# Test (new terminal)
python my_mcp_test.py
```
