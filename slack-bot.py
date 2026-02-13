#!/usr/bin/env python3
"""
Slack bot that monitors DevOps Agent channel and recommends FIS experiments
"""
import json
import subprocess
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initialize Slack app
app = App(token="YOUR_SLACK_BOT_TOKEN")

def call_fis_recommender(finding_text):
    """Call FIS Recommender MCP server"""
    finding = {
        "id": "slack-finding",
        "summary": finding_text,
        "type": "INVESTIGATION",
        "description": finding_text
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

@app.message(re.compile(".*DevOps Agent.*investigation.*", re.IGNORECASE))
def handle_devops_agent_message(message, say):
    """Respond to DevOps Agent investigation messages"""
    text = message['text']
    
    # Call FIS recommender
    recommendations = call_fis_recommender(text)
    
    # Format response
    if recommendations.get('content'):
        content = json.loads(recommendations['content'][0]['text'])
        recs = content.get('recommendations', [])
        
        if recs:
            response = "🔬 *FIS Experiment Recommendations*\n\n"
            for i, rec in enumerate(recs, 1):
                response += f"{i}. *{rec['experiment_name']}*\n"
                response += f"   Action: `{rec['fis_action']}`\n"
                response += f"   Duration: {rec['parameters']['duration']}\n"
                response += f"   {rec['description']}\n\n"
            
            say(response, thread_ts=message.get('ts'))
        else:
            say("No FIS recommendations found for this finding.", thread_ts=message.get('ts'))

@app.command("/fis-recommend")
def handle_fis_command(ack, command, say):
    """Slash command to manually request FIS recommendations"""
    ack()
    
    finding_text = command['text']
    recommendations = call_fis_recommender(finding_text)
    
    if recommendations.get('content'):
        content = json.loads(recommendations['content'][0]['text'])
        say(f"```{json.dumps(content, indent=2)}```")
    else:
        say("Error generating recommendations")

if __name__ == "__main__":
    # Start the app
    handler = SocketModeHandler(app, "YOUR_APP_TOKEN")
    print("⚡️ FIS Recommender Slack bot is running!")
    handler.start()
