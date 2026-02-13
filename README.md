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

### Network & Connectivity
| Finding Keyword | FIS Action | Duration | Use Case |
|----------------|------------|----------|----------|
| network | aws:network:disrupt-connectivity | 5 min | Test network partition handling |
| latency | aws:network:disrupt-connectivity | 10 min | Validate timeout configurations |
| packet loss | aws:ecs:task-network-packet-loss | 5 min | Simulate packet loss scenarios |
| vpc endpoint | aws:network:disrupt-vpc-endpoint | 5 min | Test VPC endpoint failures |
| cross-region | aws:network:route-table-disrupt-cross-region-connectivity | 10 min | Test multi-region connectivity |
| transit gateway | aws:network:transit-gateway-disrupt-cross-region-connectivity | 10 min | Test transit gateway issues |
| direct connect | aws:directconnect:virtual-interface-disconnect | 5 min | Test Direct Connect failures |

### Database & Storage
| Finding Keyword | FIS Action | Duration | Use Case |
|----------------|------------|----------|----------|
| database | aws:rds:reboot-db-instances | 2 min | Test database failover |
| rds | aws:rds:failover-db-cluster | 3 min | Test RDS cluster failover |
| dynamodb | aws:dynamodb:global-table-pause-replication | 5 min | Test DynamoDB replication pause |
| aurora dsql | aws:dsql:cluster-connection-failure | 5 min | Test Aurora DSQL failures |
| disk | aws:ebs:pause-volume-io | 3 min | Test disk I/O failures |
| ebs | aws:ebs:volume-io-latency | 5 min | Inject EBS I/O latency |
| s3 replication | aws:s3:bucket-pause-replication | 10 min | Test S3 replication pause |

### Compute & Instances
| Finding Keyword | FIS Action | Duration | Use Case |
|----------------|------------|----------|----------|
| cpu | aws:ec2:stop-instances | 3 min | Validate auto-scaling policies |
| memory | aws:ssm:send-command | 5 min | Test OOM handling |
| instance | aws:ec2:reboot-instances | 2 min | Test instance reboot resilience |
| spot | aws:ec2:send-spot-instance-interruptions | 2 min | Test spot interruption handling |
| capacity | aws:ec2:api-insufficient-instance-capacity-error | 5 min | Test capacity error handling |
| auto scaling | aws:ec2:asg-insufficient-instance-capacity-error | 5 min | Test ASG capacity errors |

### ECS & Containers
| Finding Keyword | FIS Action | Duration | Use Case |
|----------------|------------|----------|----------|
| ecs | aws:ecs:stop-task | 2 min | Test ECS task failure recovery |
| container cpu | aws:ecs:task-cpu-stress | 5 min | Inject CPU stress on tasks |
| container memory | aws:ecs:task-io-stress | 5 min | Inject I/O stress on tasks |
| container network | aws:ecs:task-network-latency | 5 min | Inject network latency on tasks |
| drain | aws:ecs:drain-container-instances | 5 min | Test container draining |

### EKS & Kubernetes
| Finding Keyword | FIS Action | Duration | Use Case |
|----------------|------------|----------|----------|
| eks | aws:eks:pod-delete | 2 min | Test pod deletion recovery |
| pod cpu | aws:eks:pod-cpu-stress | 5 min | Inject CPU stress on pods |
| pod memory | aws:eks:pod-memory-stress | 5 min | Inject memory stress on pods |
| pod network | aws:eks:pod-network-latency | 5 min | Inject network latency on pods |
| nodegroup | aws:eks:terminate-nodegroup-instances | 3 min | Test node termination |
| kubernetes | aws:eks:inject-kubernetes-custom-resource | 5 min | Inject custom K8s faults |

### Lambda & Serverless
| Finding Keyword | FIS Action | Duration | Use Case |
|----------------|------------|----------|----------|
| lambda | aws:lambda:invocation-error | 5 min | Inject Lambda errors |
| lambda latency | aws:lambda:invocation-add-delay | 5 min | Add Lambda invocation delay |
| lambda http | aws:lambda:invocation-http-integration-response | 5 min | Test Lambda HTTP failures |

### Caching & Streaming
| Finding Keyword | FIS Action | Duration | Use Case |
|----------------|------------|----------|----------|
| elasticache | aws:elasticache:replicationgroup-interrupt-az-power | 5 min | Test ElastiCache AZ failure |
| memorydb | aws:memorydb:multi-region-cluster-pause-replication | 5 min | Test MemoryDB replication |
| kinesis | aws:kinesis:stream-provisioned-throughput-exception | 5 min | Test Kinesis throughput |
| kinesis iterator | aws:kinesis:stream-expired-iterator-exception | 3 min | Test expired iterator handling |

### API & Throttling
| Finding Keyword | FIS Action | Duration | Use Case |
|----------------|------------|----------|----------|
| api throttle | aws:fis:inject-api-throttle-error | 5 min | Inject API throttling |
| api error | aws:fis:inject-api-internal-error | 5 min | Inject API internal errors |
| api unavailable | aws:fis:inject-api-unavailable-error | 5 min | Inject API unavailable errors |

### Availability & Recovery
| Finding Keyword | FIS Action | Duration | Use Case |
|----------------|------------|----------|----------|
| availability | aws:ec2:stop-instances | 5 min | Test high availability setup |
| zonal | aws:arc:start-zonal-autoshift | 10 min | Test zonal autoshift |
| alarm | aws:cloudwatch:assert-alarm-state | 1 min | Validate alarm states |

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
