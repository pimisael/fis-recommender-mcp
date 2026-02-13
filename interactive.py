#!/usr/bin/env python3
"""
Interactive tool to get FIS recommendations from DevOps Agent findings
"""
import json
import subprocess

def get_fis_recommendations():
    print("=" * 60)
    print("FIS Recommender - DevOps Agent Integration")
    print("=" * 60)
    print()
    print("Paste your DevOps Agent finding (JSON format):")
    print("Or describe the issue in plain text:")
    print()
    
    lines = []
    while True:
        try:
            line = input()
            if not line:
                break
            lines.append(line)
        except EOFError:
            break
    
    finding_text = '\n'.join(lines)
    
    # Try to parse as JSON
    try:
        finding = json.loads(finding_text)
    except:
        # Plain text - create finding object
        finding = {
            "id": "manual-finding",
            "summary": finding_text[:200],
            "type": "MANUAL",
            "description": finding_text
        }
    
    # Call MCP server
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
    result = json.loads(stdout)
    
    # Display recommendations
    print("\n" + "=" * 60)
    print("FIS EXPERIMENT RECOMMENDATIONS")
    print("=" * 60)
    
    if result.get('content'):
        content = json.loads(result['content'][0]['text'])
        recs = content.get('recommendations', [])
        
        if recs:
            for i, rec in enumerate(recs, 1):
                print(f"\n{i}. {rec['experiment_name']}")
                print(f"   Action: {rec['fis_action']}")
                print(f"   Duration: {rec['parameters']['duration']}")
                print(f"   Description: {rec['description']}")
                print(f"   Rationale: {rec['rationale']}")
            
            print(f"\n\nTotal recommendations: {len(recs)}")
            
            # Ask if user wants to create template
            print("\nGenerate FIS template? (y/n): ", end='')
            if input().lower() == 'y':
                print("\nEnter target configuration (JSON):")
                target_lines = []
                while True:
                    try:
                        line = input()
                        if not line:
                            break
                        target_lines.append(line)
                    except EOFError:
                        break
                
                target_config = json.loads('\n'.join(target_lines))
                
                # Generate template for first recommendation
                template_request = {
                    "method": "tools/call",
                    "params": {
                        "name": "create_fis_template",
                        "arguments": {
                            "recommendation": recs[0],
                            "target_config": target_config
                        }
                    }
                }
                
                proc = subprocess.Popen(
                    ["python3", "/Users/pimisael/fis-recommender-mcp/server.py"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    text=True
                )
                
                stdout, _ = proc.communicate(json.dumps(template_request) + "\n")
                template_result = json.loads(stdout)
                
                print("\n" + "=" * 60)
                print("FIS EXPERIMENT TEMPLATE")
                print("=" * 60)
                print(json.dumps(json.loads(template_result['content'][0]['text']), indent=2))
        else:
            print("\nNo recommendations found.")
    else:
        print("\nError generating recommendations.")

if __name__ == "__main__":
    get_fis_recommendations()
