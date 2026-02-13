#!/bin/bash
# Quick check and redeploy script for DevOps Agent FIS Recommender

set -e

echo "🔍 Checking Lambda function..."

# Check if Lambda exists
if aws lambda get-function --function-name DevOpsAgentFISRecommender --region us-east-1 &>/dev/null; then
    echo "✅ Lambda function exists"
    aws lambda get-function --function-name DevOpsAgentFISRecommender --region us-east-1 --query 'Configuration.{Name:FunctionName,Runtime:Runtime,LastModified:LastModified,Role:Role}' --output table
else
    echo "❌ Lambda function NOT found"
    echo ""
    echo "📦 Redeploying Lambda function..."
    
    # Check if deployment package exists
    if [ ! -f /tmp/lambda-auto-fis/lambda-auto-fis.zip ]; then
        echo "❌ Deployment package not found at /tmp/lambda-auto-fis/lambda-auto-fis.zip"
        echo "Please run the deployment script first"
        exit 1
    fi
    
    # Get account ID
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    
    # Create Lambda function
    aws lambda create-function \
        --function-name DevOpsAgentFISRecommender \
        --runtime python3.11 \
        --role arn:aws:iam::${ACCOUNT_ID}:role/DevOpsAgentFISRecommenderRole \
        --handler lambda_function.lambda_handler \
        --zip-file fileb:///tmp/lambda-auto-fis/lambda-auto-fis.zip \
        --timeout 60 \
        --environment Variables={SNS_TOPIC_ARN=arn:aws:sns:us-east-1:${ACCOUNT_ID}:devops-agent-fis-recommendations} \
        --region us-east-1
    
    echo "✅ Lambda function created"
fi

echo ""
echo "🔍 Checking EventBridge rule..."
if aws events describe-rule --name DevOpsAgentFISRecommendations --region us-east-1 &>/dev/null; then
    echo "✅ EventBridge rule exists"
else
    echo "❌ EventBridge rule NOT found"
fi

echo ""
echo "🔍 Checking SNS topic..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if aws sns get-topic-attributes --topic-arn arn:aws:sns:us-east-1:${ACCOUNT_ID}:devops-agent-fis-recommendations --region us-east-1 &>/dev/null; then
    echo "✅ SNS topic exists"
else
    echo "❌ SNS topic NOT found"
fi

echo ""
echo "🔍 Checking IAM roles..."
if aws iam get-role --role-name DevOpsAgentFISRecommenderRole &>/dev/null; then
    echo "✅ Lambda execution role exists"
else
    echo "❌ Lambda execution role NOT found"
fi

if aws iam get-role --role-name FISExperimentRole &>/dev/null; then
    echo "✅ FIS experiment role exists"
else
    echo "❌ FIS experiment role NOT found"
fi
