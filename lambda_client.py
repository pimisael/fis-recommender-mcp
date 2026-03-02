import json
import boto3
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

async def invoke_mcp(finding):
    runtime_arn = "arn:aws:bedrock-agentcore:us-west-2:815635340291:runtime/fisMCP-mYiu7rC4kg"
    region = "us-west-2"
    
    # Get credentials
    session = boto3.Session()
    credentials = session.get_credentials()
    
    # Build URL
    encoded_arn = runtime_arn.replace(':', '%3A').replace('/', '%2F')
    url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations"
    
    # Sign request
    request = AWSRequest(method='POST', url=url, headers={'Content-Type': 'application/json'})
    SigV4Auth(credentials, 'bedrock-agentcore', region).add_auth(request)
    
    # Connect via MCP
    async with streamablehttp_client(url, dict(request.headers)) as (read, write, _):
        async with ClientSession(read, write) as mcp:
            await mcp.initialize()
            
            result = await mcp.call_tool(
                "recommend_fis_experiments",
                arguments={"finding": finding}
            )
            
            return result.content[0].text

def lambda_handler(event, context):
    import asyncio
    
    finding = event.get('finding', {"summary": "network latency"})
    result = asyncio.run(invoke_mcp(finding))
    
    return {
        'statusCode': 200,
        'body': result
    }
