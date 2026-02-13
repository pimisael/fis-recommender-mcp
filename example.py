#!/usr/bin/env python3
"""
Example usage of FIS Recommender MCP Server
"""
import json
import subprocess

# Example DevOps Agent finding
devops_agent_finding = {
    "id": "finding-12345",
    "type": "AVAILABILITY_ISSUE",
    "summary": "Network latency spike caused API timeouts",
    "description": "Observed 500ms+ latency between app tier and database tier",
    "affected_resources": ["i-abc123", "i-def456"],
    "timestamp": "2026-01-29T10:00:00Z"
}

# Call MCP server
request = {
    "method": "tools/call",
    "params": {
        "name": "recommend_fis_experiments",
        "arguments": {
            "finding": devops_agent_finding
        }
    }
}

# Simulate MCP call
print("DevOps Agent Finding:")
print(json.dumps(devops_agent_finding, indent=2))
print("\n" + "="*60 + "\n")

# In real usage, this would go through MCP protocol
# For demo, we'll call the server directly
proc = subprocess.Popen(
    ["python3", "server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

stdout, stderr = proc.communicate(json.dumps(request) + "\n")

print("FIS Experiment Recommendations:")
print(stdout)

# Example: Create FIS template
target_config = {
    "resourceType": "aws:ec2:instance",
    "selectionMode": "COUNT(2)",
    "tags": {"app": "api-service"},
    "roleArn": "arn:aws:iam::123456789012:role/FISRole"
}

print("\n" + "="*60 + "\n")
print("Example FIS Template Configuration:")
print(json.dumps(target_config, indent=2))
