# ============================================================
# FILE_NAME: setup_eventbridge_cross.py
# AUTHOR: vsharmro
# DATE: 2026-04-12
# VERSION: 1.0
# PURPOSE: Prompts user for input config store., ensures sns topic, Create Lambda execution role if it doesn't exist.
# DEPENDENCIES: config_store, json, os, sys, tempfile, time, utils
# EXPORTS: get_account_id, ensure_sns_topic, ensure_iam_role, ensure_eventbridge_rule, generate_lambda_code, main
# ISSUE : None
# ============================================================
#!/usr/bin/env python3
import json
import os
import sys
import time
import tempfile
from utils import run_aws
import config_store

REGION = "us-east-1"
SNS_TOPIC_NAME = "devops-agent-fis-recommendations"
RULE_NAME = "DevOpsAgentFISRecommendations"
FUNCTION_NAME = "DevOpsAgentFISRecommender"
ROLE_NAME = "DevOpsAgentFISRecommenderRole"


# ============================================================
# NAME: get_account_id
# TYPE: function
# AUTHOR: vsharmro
# DATE: 2026-04-12
# PURPOSE: Exits on error, outputs to stdout.
# CALLED BY: main
# ISSUE : None
# ============================================================
def get_account_id():
    result = run_aws(["sts", "get-caller-identity"], region=REGION)
    if not result:
        print("❌ Could not get AWS account ID.")
        sys.exit(1)
    return result["Account"]


# ============================================================
# NAME: ensure_sns_topic
# TYPE: function
# AUTHOR: vsharmro
# DATE: 2026-04-12
# PARAMETERS: account_id
# PURPOSE: Computes and returns a result, outputs to stdout, using SNS.
# CALLED BY: main
# ISSUE : None
# ============================================================
def ensure_sns_topic(account_id):
    topic_arn = f"arn:aws:sns:{REGION}:{account_id}:{SNS_TOPIC_NAME}"
    result = run_aws(["sns", "get-topic-attributes", "--topic-arn", topic_arn], region=REGION)
    if result:
        print(f"✅ SNS topic exists: {topic_arn}")
        config_store.save({"sns_topic_arn": topic_arn})
        return topic_arn

    result = run_aws(["sns", "create-topic", "--name", SNS_TOPIC_NAME], region=REGION, check=True)
    topic_arn = result["TopicArn"]
    print(f"✅ Created SNS topic: {topic_arn}")
    config_store.save({"sns_topic_arn": topic_arn})
    return topic_arn


# ============================================================
# NAME: ensure_iam_role
# TYPE: function
# AUTHOR: vsharmro
# DATE: 2026-04-12
# PARAMETERS: account_id
# PURPOSE: Create Lambda execution role if it doesn't exist.
# CALLED BY: main
# ISSUE : None
# ============================================================
def ensure_iam_role(account_id):
    """Create Lambda execution role if it doesn't exist."""
    existing = run_aws(["iam", "get-role", "--role-name", ROLE_NAME], region=REGION)
    if existing:
        arn = existing["Role"]["Arn"]
        print(f"✅ IAM role exists: {arn}")
        return arn

    print("🔧 Creating IAM role...")
    trust_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    })

    run_aws([
        "iam", "create-role",
        "--role-name", ROLE_NAME,
        "--assume-role-policy-document", trust_policy,
    ], region=REGION, check=True)

    run_aws([
        "iam", "attach-role-policy",
        "--role-name", ROLE_NAME,
        "--policy-arn", "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    ], region=REGION, check=True)

    # SNS publish permission
    sns_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": "sns:Publish",
            "Resource": f"arn:aws:sns:{REGION}:{account_id}:{SNS_TOPIC_NAME}"
        }]
    })
    run_aws([
        "iam", "put-role-policy",
        "--role-name", ROLE_NAME,
        "--policy-name", "sns-publish",
        "--policy-document", sns_policy,
    ], region=REGION, check=True)

    arn = f"arn:aws:iam::{account_id}:role/{ROLE_NAME}"
    print(f"✅ Created IAM role: {arn}")

    print("   Waiting 10s for role propagation...")
    time.sleep(10)
    return arn


# ============================================================
# NAME: ensure_eventbridge_rule
# TYPE: function
# AUTHOR: vsharmro
# DATE: 2026-04-12
# PARAMETERS: account_id
# PURPOSE: Create EventBridge rule for DevOps Agent events.
# CALLED BY: main
# ISSUE : None
# ============================================================
def ensure_eventbridge_rule(account_id):
    """Create EventBridge rule for DevOps Agent events."""
    existing = run_aws([
        "events", "describe-rule", "--name", RULE_NAME,
    ], region=REGION)
    if existing:
        print(f"✅ EventBridge rule exists: {RULE_NAME}")
        return existing.get("Arn")

    event_pattern = json.dumps({
        "source": ["aws.devops-agent"],
        "detail-type": ["DevOps Agent Investigation Complete"]
    })

    result = run_aws([
        "events", "put-rule",
        "--name", RULE_NAME,
        "--event-pattern", event_pattern,
        "--state", "ENABLED",
        "--description", "Trigger FIS recommendations on DevOps Agent investigations",
    ], region=REGION, check=True)

    rule_arn = result.get("RuleArn")
    print(f"✅ Created EventBridge rule: {rule_arn}")
    return rule_arn


# ============================================================
# NAME: generate_lambda_code
# TYPE: function
# AUTHOR: vsharmro
# DATE: 2026-04-12
# PARAMETERS: sns_topic_arn
# PURPOSE: Generate Lambda function code with dynamic SNS ARN.
# CALLED BY: main
# ISSUE : None
# ============================================================
def generate_lambda_code(sns_topic_arn):
    """Generate Lambda function code with dynamic SNS ARN."""
    return f'''\
import json
import os
import base64
import urllib.request
import urllib.parse
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import asyncio
import boto3

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "{sns_topic_arn}")


def get_bearer_token():
    """Get FIS bearer token via client_credentials."""
    client_id = os.environ["COGNITO_CLIENT_ID"]
    client_secret = os.environ["COGNITO_CLIENT_SECRET"]
    token_url = os.environ["COGNITO_TOKEN_URL"]
    scope = os.environ.get("COGNITO_SCOPE", "default-fis-resource-server/read")

    auth = base64.b64encode(f"{{client_id}}:{{client_secret}}".encode()).decode()
    data = urllib.parse.urlencode({{"grant_type": "client_credentials", "scope": scope}}).encode()

    req = urllib.request.Request(token_url, data=data)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", f"Basic {{auth}}")

    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["access_token"]


async def call_mcp(finding):
    """Call MCP server and get recommendations."""
    agent_arn = os.environ["AGENT_ARN"]
    bearer_token = get_bearer_token()

    region = agent_arn.split(":")[3]
    encoded_arn = agent_arn.replace(":", "%3A").replace("/", "%2F")
    mcp_url = f"https://bedrock-agentcore.{{region}}.amazonaws.com/runtimes/{{encoded_arn}}/invocations?qualifier=DEFAULT"
    headers = {{"authorization": f"Bearer {{bearer_token}}", "Content-Type": "application/json"}}

    async with streamablehttp_client(mcp_url, headers, timeout=120, terminate_on_close=False) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.call_tool("recommend_fis_experiments", arguments={{"finding": finding}})
            return result.content[0].text


def lambda_handler(event, context):
    finding = {{
        "id": event.get("detail", {{}}).get("investigationId", "unknown"),
        "summary": event.get("detail", {{}}).get("summary", ""),
        "type": event.get("detail", {{}}).get("findingType", ""),
        "description": event.get("detail", {{}}).get("description", ""),
    }}

    recommendations = asyncio.run(call_mcp(finding))

    sns = boto3.client("sns")
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"FIS Recommendations for {{finding['id']}}",
        Message=recommendations,
    )

    return {{"statusCode": 200, "body": recommendations}}
'''


# ============================================================
# NAME: main
# TYPE: function
# AUTHOR: vsharmro
# DATE: 2026-04-12
# PURPOSE: Writes output to file, outputs to stdout.
# CALLED BY: <module>
# ISSUE : None
# ============================================================
def main():
    print("=" * 60)
    print("FIS Recommender — EventBridge Integration Setup")
    print("=" * 60)
    print()
    print("This sets up automatic FIS recommendations on every")
    print("DevOps Agent investigation via EventBridge + Lambda + SNS.")
    print()

    account_id = get_account_id()
    print(f"   Account: {account_id}")
    print(f"   Region:  {REGION}")
    print()

    # Collect FIS values
    print("Enter values from setup_cognito_fis.py and agentcore deploy:")
    print()
    agent_arn = config_store.prompt("Agent ARN", "agent_arn")
    client_id = config_store.prompt("FIS Client ID", "client_id")
    client_secret = config_store.prompt("FIS Client Secret", "client_secret")
    token_url = config_store.prompt("Token URL", "exchange_url")
    scope = config_store.prompt("Scope", "fis_scope", "default-fis-resource-server/read")
    email = config_store.prompt("Notification email (for SNS subscription)", "notification_email")
    print()

    if not all([agent_arn, client_id, client_secret, token_url]):
        print("❌ Agent ARN and Cognito values are required.")
        return

    # Create resources
    sns_topic_arn = ensure_sns_topic(account_id)
    role_arn = ensure_iam_role(account_id)
    ensure_eventbridge_rule(account_id)

    # Generate and save Lambda code
    lambda_code = generate_lambda_code(sns_topic_arn)
    output_path = os.path.join(tempfile.gettempdir(), "devops-agent-fis-lambda.py")
    with open(output_path, "w") as f:
        f.write(lambda_code)

    print(f"\n📄 Lambda code generated at: {output_path}")

    # Subscribe email to SNS
    if email:
        run_aws([
            "sns", "subscribe",
            "--topic-arn", sns_topic_arn,
            "--protocol", "email",
            "--notification-endpoint", email,
        ], region=REGION)
        print(f"📧 SNS subscription sent to {email} (check inbox to confirm)")
    else:
        print("⚠️  No email provided. To subscribe later, run:")
        print(f"  aws sns subscribe --topic-arn {sns_topic_arn} --protocol email --notification-endpoint YOUR_EMAIL --region {REGION}")

    # Summary
    print()
    print("=" * 60)
    print("EVENTBRIDGE SETUP COMPLETE")
    print("=" * 60)
    print(f"  SNS Topic:        {sns_topic_arn}")
    print(f"  EventBridge Rule: {RULE_NAME}")
    print(f"  IAM Role:         {role_arn}")
    print(f"  Lambda Code:      {output_path}")
    print()
    print("Next steps:")
    print("  1. Deploy the Lambda using: python deploy_lambda.py")
    print("     (use the generated Lambda code as lambda_function.py)")
    print("  2. Add EventBridge target:")
    print(f"     aws events put-targets --rule {RULE_NAME} \\")
    print(f"       --targets Id=1,Arn=arn:aws:lambda:{REGION}:{account_id}:function:{FUNCTION_NAME}")
    print("  3. Grant EventBridge permission to invoke Lambda:")
    print(f"     aws lambda add-permission --function-name {FUNCTION_NAME} \\")
    print(f"       --statement-id eventbridge-invoke \\")
    print(f"       --action lambda:InvokeFunction \\")
    print(f"       --principal events.amazonaws.com \\")
    print(f"       --source-arn arn:aws:events:{REGION}:{account_id}:rule/{RULE_NAME}")
    print()
    print("  Lambda environment variables needed:")
    print(f"    AGENT_ARN={agent_arn}")
    print(f"    COGNITO_CLIENT_ID={client_id}")
    print(f"    COGNITO_CLIENT_SECRET={client_secret}")
    print(f"    COGNITO_TOKEN_URL={token_url}")
    print(f"    COGNITO_SCOPE={scope}")
    print(f"    SNS_TOPIC_ARN={sns_topic_arn}")
    print("=" * 60)


if __name__ == "__main__":
    main()
