#!/bin/bash
set -e

FUNCTION_NAME="fis-mcp-client"
REGION="us-west-2"
RUNTIME_ARN="arn:aws:bedrock-agentcore:us-west-2:815635340291:runtime/fisMCP-mYiu7rC4kg"

echo "=== 1. Create Lambda layer with MCP SDK ==="
mkdir -p layer/python
docker run --rm -v "$PWD/layer":/var/task --entrypoint /bin/bash public.ecr.aws/lambda/python:3.11 \
  -c "pip install mcp boto3 httpx -t /var/task/python/"
cd layer && zip -r ../mcp-layer.zip python && cd ..
rm -rf layer

LAYER_ARN=$(aws lambda publish-layer-version \
  --layer-name mcp-sdk \
  --zip-file fileb://mcp-layer.zip \
  --compatible-runtimes python3.11 \
  --region $REGION \
  --query LayerVersionArn --output text)

echo "Layer ARN: $LAYER_ARN"

echo "=== 2. Create IAM role ==="
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

ROLE_ARN=$(aws iam create-role \
  --role-name ${FUNCTION_NAME}-role \
  --assume-role-policy-document file://trust-policy.json \
  --query Role.Arn --output text 2>/dev/null || \
  aws iam get-role --role-name ${FUNCTION_NAME}-role --query Role.Arn --output text)

aws iam attach-role-policy \
  --role-name ${FUNCTION_NAME}-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

cat > bedrock-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "bedrock-agentcore:InvokeRuntime",
    "Resource": "$RUNTIME_ARN"
  }]
}
EOF

aws iam put-role-policy \
  --role-name ${FUNCTION_NAME}-role \
  --policy-name BedrockAccess \
  --policy-document file://bedrock-policy.json

echo "Waiting for role to propagate..."
sleep 10

echo "=== 3. Package and deploy Lambda ==="
zip function.zip lambda_client.py

aws lambda create-function \
  --function-name $FUNCTION_NAME \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler lambda_client.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 512 \
  --layers $LAYER_ARN \
  --region $REGION 2>/dev/null || \
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --zip-file fileb://function.zip \
  --region $REGION

echo "=== 4. Test ==="
aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload '{"finding":{"summary":"network latency issues"}}' \
  --region $REGION \
  response.json

cat response.json

echo ""
echo "=== Cleanup ==="
rm -f mcp-layer.zip function.zip trust-policy.json bedrock-policy.json

echo ""
echo "Lambda deployed: $FUNCTION_NAME"
