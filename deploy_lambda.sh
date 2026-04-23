#!/bin/bash
set -e

FUNCTION_NAME="fis-recommender-mcp-client"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_NAME="fis-mcp-lambda-role"

# Create IAM role if it doesn't exist
if ! aws iam get-role --role-name $ROLE_NAME 2>/dev/null; then
    echo "Creating IAM role..."
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }'
    
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    aws iam put-role-policy \
        --role-name $ROLE_NAME \
        --policy-name cognito-access \
        --policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": "cognito-idp:InitiateAuth",
                "Resource": "*"
            }]
        }'
    
    echo "Waiting for role to propagate..."
    sleep 10
fi

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

# Create deployment package
echo "Creating deployment package..."
mkdir -p lambda_package
pip install -q --python-version 3.13 --platform manylinux2014_x86_64 --only-binary=:all: -r lambda_requirements.txt -t lambda_package/
cp lambda_function.py lambda_package/
cd lambda_package && zip -q -r ../lambda_deployment.zip . && cd ..

# Create or update Lambda
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Updating Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda_deployment.zip \
        --region $REGION
    
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --environment Variables="{
            AGENT_ARN=${AGENT_ARN},
            COGNITO_CLIENT_ID=${COGNITO_CLIENT_ID},
            COGNITO_USERNAME=${COGNITO_USERNAME},
            COGNITO_PASSWORD=${COGNITO_PASSWORD}
        }" \
        --region $REGION
else
    echo "Creating Lambda function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.13 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://lambda_deployment.zip \
        --timeout 120 \
        --memory-size 512 \
        --region $REGION \
        --environment Variables="{
            AGENT_ARN=${AGENT_ARN},
            COGNITO_CLIENT_ID=${COGNITO_CLIENT_ID},
            COGNITO_USERNAME=${COGNITO_USERNAME},
            COGNITO_PASSWORD=${COGNITO_PASSWORD}
        }"
fi

# Cleanup
rm -rf lambda_package lambda_deployment.zip

echo ""
echo "✓ Lambda deployed: $FUNCTION_NAME"
echo ""
echo "Set environment variables before deploying:"
echo "export AGENT_ARN='arn:aws:bedrock-agentcore:REGION:ACCOUNT:runtime/NAME'"
echo "export COGNITO_CLIENT_ID='your-client-id'"
echo "export COGNITO_USERNAME='your-username'"
echo "export COGNITO_PASSWORD='your-password'"
echo ""
echo "Test with:"
echo "aws lambda invoke --function-name $FUNCTION_NAME \\"
echo "  --payload '{\"tool\":\"recommend_fis_experiments\",\"arguments\":{\"finding\":{\"summary\":\"network latency\"}}}' \\"
echo "  response.json && cat response.json"
