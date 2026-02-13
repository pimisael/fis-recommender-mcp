# FIS Recommender MCP Server

An MCP (Model Context Protocol) server that automatically recommends AWS Fault Injection Simulator (FIS) experiments based on DevOps Agent findings. Helps teams quickly design chaos engineering experiments to validate system resilience.

## Features

- 🔍 Analyzes DevOps findings and suggests relevant FIS experiments
- 🎯 Maps issues to appropriate fault injection actions
- 📋 Generates complete FIS experiment templates
- ⚡ Integrates seamlessly with Kiro CLI and other MCP clients

## Installation

### Clone the Repository

```bash
git clone https://github.com/pimisael/fis-recommender-mcp.git
cd fis-recommender-mcp
chmod +x server.py
```

### Configure MCP Client

#### For Kiro CLI

Add to `~/.kiro/mcp-servers.json`:

```json
{
  "mcpServers": {
    "fis-recommender": {
      "command": "python3",
      "args": ["/absolute/path/to/fis-recommender-mcp/server.py"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

#### For Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fis-recommender": {
      "command": "python3",
      "args": ["/absolute/path/to/fis-recommender-mcp/server.py"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

## Usage Examples

### Example 1: Network Latency Issue

**Prompt:**
```
I have a DevOps finding about network latency causing timeouts in my application. 
Can you recommend FIS experiments to test this?

Finding details:
- ID: finding-001
- Summary: "High network latency between services causing request timeouts"
- Type: NETWORK_ISSUE
```

**Response:**
The MCP server will recommend:
- Action: `aws:network:disrupt-connectivity`
- Duration: 10 minutes
- Target: Network interfaces
- Stop condition: CloudWatch alarm on error rate

### Example 2: Database Availability

**Prompt:**
```
Recommend FIS experiments for this finding:
{
  "id": "finding-db-001",
  "summary": "Database connection failures during peak load",
  "type": "DATABASE_ISSUE"
}
```

**Response:**
- Action: `aws:rds:reboot-db-instances`
- Duration: 2 minutes
- Target: RDS instances
- Tests application's database failover handling

### Example 3: CPU Stress Testing

**Prompt:**
```
We had a CPU spike incident. Generate a FIS template to test our auto-scaling.

Finding: "CPU utilization reached 95% causing service degradation"
```

**Response:**
Complete FIS experiment template with:
- EC2 instance stop action
- 3-minute duration
- CloudWatch alarm stop condition
- Target selection by tags

### Example 4: Memory Pressure

**Prompt:**
```
Create FIS experiments to validate our memory monitoring:
- Finding ID: mem-leak-001
- Issue: Memory leak caused OOM errors
- Need to test alerting and recovery
```

**Response:**
- Action: `aws:ssm:send-command` (memory stress)
- Duration: 5 minutes
- SSM document for memory consumption
- Tests monitoring and auto-recovery

## Standalone Testing

Run the example script to test without an MCP client:

```bash
python3 example.py
```

This will analyze sample findings and display recommendations.

## Supported Finding Types

| Finding Keyword | FIS Action | Duration | Use Case |
|----------------|------------|----------|----------|
| network | aws:network:disrupt-connectivity | 5 min | Test network partition handling |
| latency | aws:network:disrupt-connectivity | 10 min | Validate timeout configurations |
| database | aws:rds:reboot-db-instances | 2 min | Test database failover |
| cpu | aws:ec2:stop-instances | 3 min | Validate auto-scaling policies |
| memory | aws:ssm:send-command | 5 min | Test OOM handling |
| availability | aws:ec2:stop-instances | 5 min | Test high availability setup |

## Available Tools

### 1. recommend_fis_experiments

Analyzes DevOps Agent findings and returns FIS experiment recommendations.

**Input:**
```json
{
  "finding": {
    "id": "finding-123",
    "summary": "Network latency caused timeouts",
    "type": "AVAILABILITY_ISSUE"
  }
}
```

**Output:**
```json
{
  "recommendations": [
    {
      "action": "aws:network:disrupt-connectivity",
      "duration": "PT10M",
      "description": "Simulates network disruption to test timeout handling",
      "targets": ["NetworkInterface"],
      "stopConditions": ["CloudWatch alarm on error rate > 5%"]
    }
  ],
  "finding_id": "finding-123",
  "count": 1
}
```

### 2. create_fis_template

Generates a complete, ready-to-deploy FIS experiment template.

**Input:**
```json
{
  "recommendation": {
    "action": "aws:ec2:stop-instances",
    "duration": "PT3M",
    "description": "Test instance failure recovery"
  },
  "target_config": {
    "resourceType": "aws:ec2:instance",
    "selectionMode": "COUNT(1)",
    "tags": {
      "Environment": "staging",
      "Team": "platform"
    },
    "roleArn": "arn:aws:iam::123456789012:role/FISRole"
  }
}
```

**Output:**
Complete CloudFormation-compatible FIS experiment template ready for deployment.

## Customization

### Adding New Finding Mappings

Edit `server.py` and add to the `finding_mappings` dictionary:

```python
finding_mappings = {
    "disk": {
        "action": "aws:ebs:pause-volume-io",
        "duration": "PT5M",
        "description": "Simulates disk I/O issues"
    },
    # Add your custom mappings here
}
```

### Adjusting Durations

Modify duration values in ISO 8601 format:
- `PT2M` = 2 minutes
- `PT5M` = 5 minutes
- `PT10M` = 10 minutes
- `PT1H` = 1 hour

## Requirements

- Python 3.7+
- AWS credentials configured (for actual FIS deployment)
- MCP-compatible client (Kiro CLI, Claude Desktop, etc.)

## License

MIT

## Contributing

Issues and pull requests welcome at https://github.com/pimisael/fis-recommender-mcp
