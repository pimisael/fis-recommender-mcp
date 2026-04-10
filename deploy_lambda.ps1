# deploy_lambda.ps1 - Windows PowerShell version

$ErrorActionPreference = "Stop"

$FUNCTION_NAME = "fis-recommender-mcp-client"
$REGION = "us-east-1"
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ROLE_NAME = "fis-mcp-lambda-role"

# Check required environment variables
if (-not $env:AGENT_ARN -or -not $env:COGNITO_CLIENT_ID -or -not $env:COGNITO_USERNAME -or -not $env:COGNITO_PASSWORD) {
    Write-Host "Set environment variables first:"
    Write-Host '  $env:AGENT_ARN = "arn:aws:bedrock-agentcore:REGION:ACCOUNT:runtime/NAME"'
    Write-Host '  $env:COGNITO_CLIENT_ID = "your-client-id"'
    Write-Host '  $env:COGNITO_USERNAME = "your-username"'
    Write-Host '  $env:COGNITO_PASSWORD = "your-password"'
    exit 1
}

# Create IAM role if it doesn't exist
try {
    aws iam get-role --role-name $ROLE_NAME 2>$null | Out-Null
} catch {
    Write-Host "Creating IAM role..."
    $trustPolicy = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
    aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document $trustPolicy

    aws iam attach-role-policy `
        --role-name $ROLE_NAME `
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    $cognitoPolicy = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"cognito-idp:InitiateAuth","Resource":"*"}]}'
    aws iam put-role-policy `
        --role-name $ROLE_NAME `
        --policy-name cognito-access `
        --policy-document $cognitoPolicy

    Write-Host "Waiting for role to propagate..."
    Start-Sleep -Seconds 10
}

$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

# Create deployment package
Write-Host "Creating deployment package..."
if (Test-Path lambda_package) { Remove-Item -Recurse -Force lambda_package }
New-Item -ItemType Directory -Path lambda_package | Out-Null

pip install -q --python-version 3.13 --platform manylinux2014_x86_64 --only-binary=:all: -r lambda_requirements.txt -t lambda_package/
Copy-Item lambda_function.py lambda_package/

# Create zip
if (Test-Path lambda_deployment.zip) { Remove-Item lambda_deployment.zip }
Compress-Archive -Path lambda_package\* -DestinationPath lambda_deployment.zip

# Environment variables string
$envVars = "AGENT_ARN=$($env:AGENT_ARN),COGNITO_CLIENT_ID=$($env:COGNITO_CLIENT_ID),COGNITO_USERNAME=$($env:COGNITO_USERNAME),COGNITO_PASSWORD=$($env:COGNITO_PASSWORD)"

# Create or update Lambda
try {
    aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>$null | Out-Null
    Write-Host "Updating Lambda function..."
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file fileb://lambda_deployment.zip `
        --region $REGION

    aws lambda update-function-configuration `
        --function-name $FUNCTION_NAME `
        --environment "Variables={$envVars}" `
        --region $REGION
} catch {
    Write-Host "Creating Lambda function..."
    aws lambda create-function `
        --function-name $FUNCTION_NAME `
        --runtime python3.13 `
        --role $ROLE_ARN `
        --handler lambda_function.lambda_handler `
        --zip-file fileb://lambda_deployment.zip `
        --timeout 120 `
        --memory-size 512 `
        --region $REGION `
        --environment "Variables={$envVars}"
}

# Cleanup
Remove-Item -Recurse -Force lambda_package
Remove-Item lambda_deployment.zip

Write-Host ""
Write-Host "Lambda deployed: $FUNCTION_NAME"
Write-Host ""
Write-Host "Test with:"
Write-Host "aws lambda invoke --function-name $FUNCTION_NAME --region $REGION --payload '{""tool"":""recommend_fis_experiments"",""arguments"":{""finding"":{""summary"":""network latency""}}}' response.json; Get-Content response.json"
