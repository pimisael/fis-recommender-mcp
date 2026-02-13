#!/bin/bash
# Setup EventBridge integration for DevOps Agent → FIS Recommender

# Create Lambda function that calls FIS Recommender MCP
cat > /tmp/devops-agent-fis-lambda.py << 'EOF'
import json
import subprocess
import boto3

def lambda_handler(event, context):
    # Extract DevOps Agent finding from event
    finding = {
        "id": event['detail'].get('investigationId'),
        "summary": event['detail'].get('summary'),
        "type": event['detail'].get('findingType'),
        "description": event['detail'].get('description', '')
    }
    
    # Call FIS Recommender MCP Server
    mcp_request = {
        "method": "tools/call",
        "params": {
            "name": "recommend_fis_experiments",
            "arguments": {"finding": finding}
        }
    }
    
    # Run MCP server
    proc = subprocess.Popen(
        ["python3", "/opt/fis-recommender/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    
    stdout, _ = proc.communicate(json.dumps(mcp_request) + "\n")
    recommendations = json.loads(stdout)
    
    # Post to Slack or SNS
    sns = boto3.client('sns')
    sns.publish(
        TopicArn='arn:aws:sns:us-east-1:815635340291:devops-agent-fis-recommendations',
        Subject=f'FIS Recommendations for {finding["id"]}',
        Message=json.dumps(recommendations, indent=2)
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(recommendations)
    }
EOF

echo "Lambda function code created at /tmp/devops-agent-fis-lambda.py"
echo ""
echo "Next steps:"
echo "1. Package Lambda with MCP server"
echo "2. Create EventBridge rule for DevOps Agent events"
echo "3. Configure SNS topic for notifications"
