# FIS Recommender MCP Server

Automatically recommends AWS FIS experiments based on DevOps Agent findings.

## Installation

1. Make server executable:
```bash
chmod +x ~/fis-recommender-mcp/server.py
```

2. Add to Kiro CLI config (`~/.kiro/mcp-servers.json`):
```json
{
  "mcpServers": {
    "fis-recommender": {
      "command": "python3",
      "args": ["/Users/pimisael/fis-recommender-mcp/server.py"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

## Usage

### In Kiro CLI

```
Analyze this DevOps Agent finding and recommend FIS experiments:
{
  "id": "finding-123",
  "summary": "Network latency caused timeouts",
  "type": "AVAILABILITY_ISSUE"
}
```

### Standalone Test

```bash
cd ~/fis-recommender-mcp
python3 example.py
```

## Supported Finding Types

| Finding Keyword | FIS Action | Duration |
|----------------|------------|----------|
| network | aws:network:disrupt-connectivity | 5 min |
| latency | aws:network:disrupt-connectivity | 10 min |
| database | aws:rds:reboot-db-instances | 2 min |
| cpu | aws:ec2:stop-instances | 3 min |
| memory | aws:ssm:send-command | 5 min |
| availability | aws:ec2:stop-instances | 5 min |

## Tools Available

### recommend_fis_experiments
Analyzes DevOps Agent findings and returns FIS experiment recommendations.

**Input:**
```json
{
  "finding": {
    "id": "string",
    "summary": "string",
    "type": "string"
  }
}
```

**Output:**
```json
{
  "recommendations": [...],
  "finding_id": "string",
  "count": 0
}
```

### create_fis_template
Generates complete FIS experiment template.

**Input:**
```json
{
  "recommendation": {...},
  "target_config": {
    "resourceType": "aws:ec2:instance",
    "selectionMode": "COUNT(1)",
    "tags": {},
    "roleArn": "arn:aws:iam::..."
  }
}
```

## Customization

Edit `server.py` to add more finding mappings in the `finding_mappings` dictionary.
