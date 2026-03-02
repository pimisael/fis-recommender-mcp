# Deploy Lambda to Call AgentCore MCP

## Quick Deploy

```bash
chmod +x deploy_lambda.sh
./deploy_lambda.sh
```

## What It Does

1. Creates IAM role `fis-mcp-lambda-role` with:
   - Lambda execution permissions
   - Cognito InitiateAuth access
2. Packages Lambda with MCP dependencies
3. Creates/updates Lambda function with environment variables

## Test

```bash
aws lambda invoke --function-name fis-recommender-mcp-client \
  --payload '{"tool":"recommend_fis_experiments","arguments":{"finding":{"summary":"network latency"}}}' \
  response.json && cat response.json
```

## Environment Variables

Set in Lambda:
- `AGENT_ARN`: AgentCore runtime ARN
- `COGNITO_CLIENT_ID`: Cognito app client ID
- `COGNITO_USERNAME`: Cognito user
- `COGNITO_PASSWORD`: Cognito password
