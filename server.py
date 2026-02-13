#!/usr/bin/env python3
import json
import sys
from typing import Any

class FISRecommenderMCP:
    def __init__(self):
        self.finding_mappings = {
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
            "database": {
                "action": "aws:rds:reboot-db-instances",
                "duration": "PT2M",
                "description": "Test database failover and connection retry logic"
            },
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
            "availability": {
                "action": "aws:ec2:stop-instances",
                "duration": "PT5M",
                "description": "Test AZ failure scenarios"
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
