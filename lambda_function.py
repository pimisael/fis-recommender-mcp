import asyncio
import json
import os
import boto3
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

cognito = boto3.client('cognito-idp')

def get_bearer_token():
    """Get fresh bearer token from Cognito"""
    response = cognito.initiate_auth(
        ClientId=os.environ['COGNITO_CLIENT_ID'],
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': os.environ['COGNITO_USERNAME'],
            'PASSWORD': os.environ['COGNITO_PASSWORD']
        }
    )
    return response['AuthenticationResult']['AccessToken']

async def call_mcp_tool(tool_name, arguments):
    """Call MCP tool and return result"""
    agent_arn = os.environ['AGENT_ARN']
    bearer_token = get_bearer_token()
    
    region = agent_arn.split(':')[3]
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    headers = {"authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
    
    async with streamablehttp_client(mcp_url, headers, timeout=120, terminate_on_close=False) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text

def lambda_handler(event, context):
    """
    Lambda handler to call FIS Recommender MCP
    
    Event format:
    {
        "tool": "recommend_fis_experiments" | "create_fis_template",
        "arguments": {...}
    }
    
    Examples:
    1. Get recommendations:
       {"tool": "recommend_fis_experiments", "arguments": {"finding": {"summary": "network latency"}}}
    
    2. Create template:
       {
         "tool": "create_fis_template",
         "arguments": {
           "recommendation": {"action": "aws:network:disrupt-connectivity", "duration": "PT5M", "description": "Test network"},
           "target": {"resourceType": "aws:ec2:instance", "selectionMode": "COUNT(1)", "tags": {"Env": "staging"}, "roleArn": "arn:aws:iam::ACCOUNT:role/FISRole"}
         }
       }
    """
    tool_name = event.get('tool', 'recommend_fis_experiments')
    arguments = event.get('arguments', {})
    
    result = asyncio.run(call_mcp_tool(tool_name, arguments))
    
    return {
        'statusCode': 200,
        'body': json.dumps({'result': result})
    }
