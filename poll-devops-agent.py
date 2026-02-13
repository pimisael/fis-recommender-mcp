#!/usr/bin/env python3
"""
Poll DevOps Agent API and generate FIS recommendations
"""
import json
import subprocess
import boto3
import time

def get_devops_agent_investigations():
    """Fetch recent DevOps Agent investigations"""
    # Replace with actual DevOps Agent API call
    client = boto3.client('devops-agent', region_name='us-east-1')
    
    try:
        response = client.list_investigations(
            AgentSpaceId='YOUR_AGENT_SPACE_ID',
            MaxResults=10
        )
        return response.get('Investigations', [])
    except Exception as e:
        print(f"Error fetching investigations: {e}")
        return []

def call_fis_recommender(investigation):
    """Generate FIS recommendations"""
    finding = {
        "id": investigation.get('InvestigationId'),
        "summary": investigation.get('Summary'),
        "type": investigation.get('Type'),
        "description": investigation.get('Description', '')
    }
    
    mcp_request = {
        "method": "tools/call",
        "params": {
            "name": "recommend_fis_experiments",
            "arguments": {"finding": finding}
        }
    }
    
    proc = subprocess.Popen(
        ["python3", "/Users/pimisael/fis-recommender-mcp/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    
    stdout, _ = proc.communicate(json.dumps(mcp_request) + "\n")
    return json.loads(stdout)

def main():
    """Main polling loop"""
    processed_ids = set()
    
    while True:
        investigations = get_devops_agent_investigations()
        
        for inv in investigations:
            inv_id = inv.get('InvestigationId')
            
            if inv_id not in processed_ids:
                print(f"Processing investigation: {inv_id}")
                
                recommendations = call_fis_recommender(inv)
                
                # Save recommendations
                with open(f'/tmp/fis-rec-{inv_id}.json', 'w') as f:
                    json.dump(recommendations, f, indent=2)
                
                print(f"Recommendations saved for {inv_id}")
                processed_ids.add(inv_id)
        
        time.sleep(300)  # Poll every 5 minutes

if __name__ == "__main__":
    main()
