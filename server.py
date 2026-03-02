from mcp.server.fastmcp import FastMCP

mcp = FastMCP(host="0.0.0.0", stateless_http=True)

@mcp.tool()
def recommend_fis_experiments(finding: dict) -> str:
    """Recommend FIS experiments based on findings"""
    import json
    
    mappings = {
        "network": {"action": "aws:network:disrupt-connectivity", "duration": "PT5M", "description": "Test network resilience"},
        "latency": {"action": "aws:network:disrupt-connectivity", "duration": "PT10M", "description": "Inject network latency"},
        "database": {"action": "aws:rds:reboot-db-instances", "duration": "PT2M", "description": "Test database failover"},
        "cpu": {"action": "aws:ec2:stop-instances", "duration": "PT3M", "description": "Test auto-scaling"},
        "lambda": {"action": "aws:lambda:invocation-error", "duration": "PT5M", "description": "Test Lambda error handling"}
    }
    
    text = json.dumps(finding).lower()
    recs = [{"action": v["action"], "duration": v["duration"], "description": v["description"]} 
            for k, v in mappings.items() if k in text]
    
    return json.dumps({"recommendations": recs}, indent=2)

@mcp.tool()
def create_fis_template(recommendation: dict, target: dict) -> str:
    """Create FIS experiment template in AWS account"""
    import boto3
    import json
    
    fis = boto3.client('fis')
    template = {
        "description": recommendation["description"],
        "actions": {
            "action1": {
                "actionId": recommendation["action"],
                "parameters": {"duration": recommendation["duration"]},
                "targets": {"Instances": "target1"}
            }
        },
        "targets": {
            "target1": {
                "resourceType": target.get("resourceType", "aws:ec2:instance"),
                "selectionMode": target.get("selectionMode", "COUNT(1)"),
                "resourceTags": target.get("tags", {})
            }
        },
        "stopConditions": [{"source": "none"}],
        "roleArn": target["roleArn"]
    }
    resp = fis.create_experiment_template(**template)
    return json.dumps({"templateId": resp["experimentTemplate"]["id"], "arn": resp["experimentTemplate"]["arn"]}, indent=2)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
