#!/usr/bin/env python3
import json
import sys
from typing import Any

class FISRecommenderMCP:
    def __init__(self):
        self.finding_mappings = {
            # Network & Connectivity
            "network": {
                "action": "aws:network:disrupt-connectivity",
                "duration": "PT5M",
                "description": "Test network resilience by disrupting connectivity"
            },
            "latency": {
                "action": "aws:network:disrupt-connectivity",
                "duration": "PT10M",
                "description": "Inject network latency to test timeout handling"
            },
            "packet loss": {
                "action": "aws:ecs:task-network-packet-loss",
                "duration": "PT5M",
                "description": "Simulate packet loss to test network reliability"
            },
            "vpc endpoint": {
                "action": "aws:network:disrupt-vpc-endpoint",
                "duration": "PT5M",
                "description": "Test VPC endpoint failure handling"
            },
            "cross-region": {
                "action": "aws:network:route-table-disrupt-cross-region-connectivity",
                "duration": "PT10M",
                "description": "Test multi-region connectivity failures"
            },
            "transit gateway": {
                "action": "aws:network:transit-gateway-disrupt-cross-region-connectivity",
                "duration": "PT10M",
                "description": "Test transit gateway connectivity issues"
            },
            
            # Database & Storage
            "database": {
                "action": "aws:rds:reboot-db-instances",
                "duration": "PT2M",
                "description": "Test database failover and connection retry logic"
            },
            "rds": {
                "action": "aws:rds:failover-db-cluster",
                "duration": "PT3M",
                "description": "Test RDS cluster failover scenarios"
            },
            "dynamodb": {
                "action": "aws:dynamodb:global-table-pause-replication",
                "duration": "PT5M",
                "description": "Test DynamoDB global table replication pause"
            },
            "aurora dsql": {
                "action": "aws:dsql:cluster-connection-failure",
                "duration": "PT5M",
                "description": "Test Aurora DSQL connection failure handling"
            },
            "disk": {
                "action": "aws:ebs:pause-volume-io",
                "duration": "PT3M",
                "description": "Test disk I/O failure scenarios"
            },
            "ebs": {
                "action": "aws:ebs:volume-io-latency",
                "duration": "PT5M",
                "description": "Inject EBS volume I/O latency"
            },
            "s3 replication": {
                "action": "aws:s3:bucket-pause-replication",
                "duration": "PT10M",
                "description": "Test S3 cross-region replication pause"
            },
            
            # Compute & Containers
            "cpu": {
                "action": "aws:ec2:stop-instances",
                "duration": "PT3M",
                "description": "Test auto-scaling and instance recovery"
            },
            "memory": {
                "action": "aws:ssm:send-command",
                "duration": "PT5M",
                "description": "Inject memory pressure to test OOM handling"
            },
            "instance": {
                "action": "aws:ec2:reboot-instances",
                "duration": "PT2M",
                "description": "Test instance reboot resilience"
            },
            "spot": {
                "action": "aws:ec2:send-spot-instance-interruptions",
                "duration": "PT2M",
                "description": "Test spot instance interruption handling"
            },
            "capacity": {
                "action": "aws:ec2:api-insufficient-instance-capacity-error",
                "duration": "PT5M",
                "description": "Test insufficient capacity error handling"
            },
            "auto scaling": {
                "action": "aws:ec2:asg-insufficient-instance-capacity-error",
                "duration": "PT5M",
                "description": "Test ASG capacity error scenarios"
            },
            
            # ECS & Containers
            "ecs": {
                "action": "aws:ecs:stop-task",
                "duration": "PT2M",
                "description": "Test ECS task failure and restart"
            },
            "container cpu": {
                "action": "aws:ecs:task-cpu-stress",
                "duration": "PT5M",
                "description": "Inject CPU stress on ECS tasks"
            },
            "container memory": {
                "action": "aws:ecs:task-io-stress",
                "duration": "PT5M",
                "description": "Inject I/O stress on ECS tasks"
            },
            "container network": {
                "action": "aws:ecs:task-network-latency",
                "duration": "PT5M",
                "description": "Inject network latency on ECS tasks"
            },
            "drain": {
                "action": "aws:ecs:drain-container-instances",
                "duration": "PT5M",
                "description": "Test container instance draining"
            },
            
            # EKS & Kubernetes
            "eks": {
                "action": "aws:eks:pod-delete",
                "duration": "PT2M",
                "description": "Test pod deletion and recovery"
            },
            "pod cpu": {
                "action": "aws:eks:pod-cpu-stress",
                "duration": "PT5M",
                "description": "Inject CPU stress on Kubernetes pods"
            },
            "pod memory": {
                "action": "aws:eks:pod-memory-stress",
                "duration": "PT5M",
                "description": "Inject memory stress on Kubernetes pods"
            },
            "pod network": {
                "action": "aws:eks:pod-network-latency",
                "duration": "PT5M",
                "description": "Inject network latency on pods"
            },
            "nodegroup": {
                "action": "aws:eks:terminate-nodegroup-instances",
                "duration": "PT3M",
                "description": "Test node group instance termination"
            },
            "kubernetes": {
                "action": "aws:eks:inject-kubernetes-custom-resource",
                "duration": "PT5M",
                "description": "Inject custom Kubernetes resource faults"
            },
            
            # Lambda & Serverless
            "lambda": {
                "action": "aws:lambda:invocation-error",
                "duration": "PT5M",
                "description": "Inject Lambda invocation errors"
            },
            "lambda latency": {
                "action": "aws:lambda:invocation-add-delay",
                "duration": "PT5M",
                "description": "Add delay to Lambda invocations"
            },
            "lambda http": {
                "action": "aws:lambda:invocation-http-integration-response",
                "duration": "PT5M",
                "description": "Test Lambda HTTP integration failures"
            },
            
            # Caching & Streaming
            "elasticache": {
                "action": "aws:elasticache:replicationgroup-interrupt-az-power",
                "duration": "PT5M",
                "description": "Test ElastiCache AZ power interruption"
            },
            "memorydb": {
                "action": "aws:memorydb:multi-region-cluster-pause-replication",
                "duration": "PT5M",
                "description": "Test MemoryDB replication pause"
            },
            "kinesis": {
                "action": "aws:kinesis:stream-provisioned-throughput-exception",
                "duration": "PT5M",
                "description": "Test Kinesis throughput exception handling"
            },
            "kinesis iterator": {
                "action": "aws:kinesis:stream-expired-iterator-exception",
                "duration": "PT3M",
                "description": "Test Kinesis expired iterator handling"
            },
            
            # API & Throttling
            "api throttle": {
                "action": "aws:fis:inject-api-throttle-error",
                "duration": "PT5M",
                "description": "Inject API throttling errors"
            },
            "api error": {
                "action": "aws:fis:inject-api-internal-error",
                "duration": "PT5M",
                "description": "Inject API internal errors"
            },
            "api unavailable": {
                "action": "aws:fis:inject-api-unavailable-error",
                "duration": "PT5M",
                "description": "Inject API unavailable errors"
            },
            
            # Availability & Recovery
            "availability": {
                "action": "aws:ec2:stop-instances",
                "duration": "PT5M",
                "description": "Test AZ failure scenarios"
            },
            "zonal": {
                "action": "aws:arc:start-zonal-autoshift",
                "duration": "PT10M",
                "description": "Test zonal autoshift for AZ impairment"
            },
            "direct connect": {
                "action": "aws:directconnect:virtual-interface-disconnect",
                "duration": "PT5M",
                "description": "Test Direct Connect virtual interface disconnect"
            },
            
            # Monitoring & Validation
            "alarm": {
                "action": "aws:cloudwatch:assert-alarm-state",
                "duration": "PT1M",
                "description": "Validate CloudWatch alarm states"
            }
        }
    
    def recommend(self, finding: dict) -> dict:
        finding_text = json.dumps(finding).lower()
        recommendations = []
        
        for keyword, config in self.finding_mappings.items():
            if keyword in finding_text:
                recommendations.append({
                    "experiment_name": f"test-{keyword}-resilience",
                    "fis_action": config["action"],
                    "parameters": {"duration": config["duration"]},
                    "description": config["description"],
                    "rationale": f"Addresses finding: {finding.get('summary', 'N/A')}"
                })
        
        return {
            "recommendations": recommendations,
            "finding_id": finding.get("id", "unknown"),
            "count": len(recommendations)
        }
    
    def create_template(self, recommendation: dict, target_config: dict) -> dict:
        template = {
            "description": recommendation["description"],
            "actions": {
                "mainAction": {
                    "actionId": recommendation["fis_action"],
                    "parameters": recommendation["parameters"],
                    "targets": {"Instances": "targetInstances"}
                }
            },
            "targets": {
                "targetInstances": {
                    "resourceType": target_config.get("resourceType", "aws:ec2:instance"),
                    "selectionMode": target_config.get("selectionMode", "COUNT(1)"),
                    "resourceTags": target_config.get("tags", {})
                }
            },
            "stopConditions": [{"source": "none"}],
            "roleArn": target_config.get("roleArn", "")
        }
        return template
    
    def handle_request(self, request: dict) -> dict:
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "tools/list":
            return {
                "tools": [
                    {
                        "name": "recommend_fis_experiments",
                        "description": "Analyze DevOps Agent findings and recommend FIS experiments",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "finding": {
                                    "type": "object",
                                    "description": "DevOps Agent finding object"
                                }
                            },
                            "required": ["finding"]
                        }
                    },
                    {
                        "name": "create_fis_template",
                        "description": "Generate FIS experiment template from recommendation",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "recommendation": {"type": "object"},
                                "target_config": {"type": "object"}
                            },
                            "required": ["recommendation", "target_config"]
                        }
                    }
                ]
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "recommend_fis_experiments":
                result = self.recommend(arguments.get("finding", {}))
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif tool_name == "create_fis_template":
                result = self.create_template(
                    arguments.get("recommendation", {}),
                    arguments.get("target_config", {})
                )
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        return {"error": "Unknown method"}
    
    def run(self):
        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except Exception as e:
                print(json.dumps({"error": str(e)}), flush=True)

if __name__ == "__main__":
    server = FISRecommenderMCP()
    server.run()
