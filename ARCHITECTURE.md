# DevOps Agent → FIS Auto-Recommender Architecture

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AWS DevOps Agent                                 │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Agent Space: DevOpsAgent-BetaAgentAgentSpace-1838C6BF   │          │
│  │                                                            │          │
│  │  • Analyzes CloudWatch Alarms                             │          │
│  │  • Investigates Step Functions failures                   │          │
│  │  • Detects EMR cluster issues                             │          │
│  │  • Identifies database connection problems                │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                           │
│                              │ Investigation Complete                   │
│                              ▼                                           │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │ EventBridge Event
                               │ {
                               │   "source": "aws.devops-agent",
                               │   "detail-type": "Investigation Complete",
                               │   "detail": {
                               │     "agentSpaceId": "...",
                               │     "investigationId": "...",
                               │     "summary": "...",
                               │     "description": "..."
                               │   }
                               │ }
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Amazon EventBridge                               │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Rule: DevOpsAgentFISRecommendations                      │          │
│  │                                                            │          │
│  │  Event Pattern:                                            │          │
│  │  {                                                         │          │
│  │    "source": ["aws.devops-agent"],                        │          │
│  │    "detail-type": ["DevOps Agent Investigation Complete"],│          │
│  │    "detail": {                                             │          │
│  │      "agentSpaceId": ["DevOpsAgent-..."]                  │          │
│  │    }                                                       │          │
│  │  }                                                         │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                           │
│                              │ Triggers                                  │
│                              ▼                                           │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         AWS Lambda                                       │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Function: DevOpsAgentFISRecommender                      │          │
│  │  Runtime: Python 3.11 | Timeout: 60s                      │          │
│  │                                                            │          │
│  │  1. Parse Investigation Findings                          │          │
│  │     • Extract keywords (network, latency, database, etc)  │          │
│  │     • Map to FIS actions                                  │          │
│  │                                                            │          │
│  │  2. Generate Recommendations                              │          │
│  │     • Create experiment descriptions                      │          │
│  │     • Add root cause context                              │          │
│  │     • Include business justification                      │          │
│  │                                                            │          │
│  │  3. Create FIS Templates                                  │          │
│  │     • Build template configuration                        │          │
│  │     • Set targets (EC2, RDS)                              │          │
│  │     • Add tags (Source, Investigation ID)                 │          │
│  │     • Generate one-click run URLs                         │          │
│  │                                                            │          │
│  │  4. Send Notifications                                    │          │
│  │     • Publish to SNS topic                                │          │
│  │     • Include template IDs and URLs                       │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                           │
│                              │ Creates                                   │
│                              ▼                                           │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AWS Fault Injection Simulator                         │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Experiment Templates (Auto-Generated)                    │          │
│  │                                                            │          │
│  │  ┌────────────────────────────────────────────┐          │          │
│  │  │ test-network-resilience                     │          │          │
│  │  │ Action: aws:ec2:stop-instances              │          │          │
│  │  │ Target: EC2 instances (Environment=test)    │          │          │
│  │  │ Tags: Source=DevOpsAgent, AutoGenerated=true│          │          │
│  │  └────────────────────────────────────────────┘          │          │
│  │                                                            │          │
│  │  ┌────────────────────────────────────────────┐          │          │
│  │  │ test-latency-resilience                     │          │          │
│  │  │ Action: aws:ec2:stop-instances              │          │          │
│  │  │ Target: EC2 instances (Environment=test)    │          │          │
│  │  └────────────────────────────────────────────┘          │          │
│  │                                                            │          │
│  │  ┌────────────────────────────────────────────┐          │          │
│  │  │ test-database-resilience                    │          │          │
│  │  │ Action: aws:rds:reboot-db-instances         │          │          │
│  │  │ Target: RDS instances (Environment=test)    │          │          │
│  │  └────────────────────────────────────────────┘          │          │
│  └──────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │ Publishes
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Amazon SNS                                       │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Topic: devops-agent-fis-recommendations                  │          │
│  │                                                            │          │
│  │  Message Format:                                           │          │
│  │  ┌────────────────────────────────────────────┐          │          │
│  │  │ Subject: FIS Recommendations: Investigation │          │          │
│  │  │                                              │          │          │
│  │  │ Body:                                        │          │          │
│  │  │ • Investigation summary                      │          │          │
│  │  │ • 3 FIS templates created                    │          │          │
│  │  │ • Template IDs                               │          │          │
│  │  │ • One-click run URLs                         │          │          │
│  │  │ • Descriptions and justifications            │          │          │
│  │  └────────────────────────────────────────────┘          │          │
│  └──────────────────────────────────────────────────────────┘          │
│                              │                                           │
│                              │ Email                                     │
│                              ▼                                           │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │  Engineers   │
                        │              │
                        │ • Review     │
                        │ • Click URL  │
                        │ • Run Test   │
                        └─────────────┘
```

## Workflow Sequence

```
┌─────────┐
│ START   │
└────┬────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ 1. CloudWatch Alarm Triggers                            │
│    • Step Functions execution failures                  │
│    • EMR cluster idle/disruption                        │
│    • RDS connection timeouts                            │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. DevOps Agent Investigates                            │
│    • Analyzes metrics and logs                          │
│    • Correlates events across services                  │
│    • Identifies root cause                              │
│    • Generates investigation report                     │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Investigation Complete Event                         │
│    EventBridge receives:                                │
│    {                                                     │
│      "agentSpaceId": "DevOpsAgent-...",                 │
│      "investigationId": "Investigation 2026-...",       │
│      "summary": "Network latency caused failures",      │
│      "description": "Root cause: AZ latency..."         │
│    }                                                     │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ 4. EventBridge Rule Matches                             │
│    • Filters by Agent Space ID                          │
│    • Triggers Lambda function                           │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Lambda Analyzes Findings                             │
│    Keyword Detection:                                   │
│    • "network" → EC2 stop instances                     │
│    • "latency" → EC2 stop instances                     │
│    • "database" → RDS reboot                            │
│    • "emr" → EC2 stop instances                         │
│    • "stepfunctions" → EC2 stop instances               │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Generate Recommendations                             │
│    For each finding type:                               │
│    • Experiment name                                    │
│    • FIS action                                         │
│    • Target configuration                               │
│    • Description (what to test)                         │
│    • Why recommended                                    │
│    • Root cause context                                 │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ 7. Create FIS Templates                                 │
│    For each recommendation:                             │
│    • Build template JSON                                │
│    • Set targets (tag-based)                            │
│    • Configure stop conditions                          │
│    • Add metadata tags                                  │
│    • Call fis.create_experiment_template()              │
│    • Generate console URL                               │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ 8. Send SNS Notification                                │
│    Email includes:                                      │
│    • Investigation ID and summary                       │
│    • Number of templates created                        │
│    • Template IDs                                       │
│    • One-click run URLs                                 │
│    • Descriptions and justifications                    │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ 9. Engineer Reviews Email                               │
│    • Reads investigation summary                        │
│    • Reviews recommended experiments                    │
│    • Clicks one-click run URL                           │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ 10. Run FIS Experiment                                  │
│     • Opens FIS console with template                   │
│     • Reviews configuration                             │
│     • Starts experiment                                 │
│     • Monitors application behavior                     │
│     • Validates resilience                              │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────┐
│  END    │
└─────────┘
```

## Data Flow

```
Investigation Finding
        │
        │ {summary, description, type}
        ▼
Keyword Extraction
        │
        │ ["network", "latency", "database"]
        ▼
FIS Action Mapping
        │
        │ [
        │   {action: "aws:ec2:stop-instances", target: "ec2:instance"},
        │   {action: "aws:rds:reboot-db-instances", target: "rds:db"}
        │ ]
        ▼
Template Generation
        │
        │ {
        │   description: "Auto-generated from DevOps Agent...",
        │   actions: {...},
        │   targets: {...},
        │   roleArn: "arn:aws:iam::...:role/FISExperimentRole",
        │   tags: {Source: "DevOpsAgent", Investigation: "..."}
        │ }
        ▼
FIS API Call
        │
        │ create_experiment_template()
        ▼
Template Response
        │
        │ {
        │   experimentTemplate: {
        │     id: "EXThQfPUt3nnuW",
        │     ...
        │   }
        │ }
        ▼
URL Generation
        │
        │ "https://console.aws.amazon.com/fis/home?region=us-east-1#ExperimentTemplates/EXThQfPUt3nnuW"
        ▼
SNS Notification
        │
        │ Email with template IDs and URLs
        ▼
Engineer Action
```

## Component Details

### EventBridge Rule
- **Name**: DevOpsAgentFISRecommendations
- **Event Pattern**: Filters on Agent Space ID
- **Target**: Lambda function

### Lambda Function
- **Name**: DevOpsAgentFISRecommender
- **Runtime**: Python 3.11
- **Memory**: 128 MB
- **Timeout**: 60 seconds
- **Environment Variables**: SNS_TOPIC_ARN

### IAM Roles

**Lambda Execution Role** (DevOpsAgentFISRecommenderRole):
- AWSLambdaBasicExecutionRole
- sns:Publish
- fis:CreateExperimentTemplate

**FIS Experiment Role** (FISExperimentRole):
- ec2:StopInstances
- ec2:DescribeInstances
- rds:RebootDBInstance
- rds:DescribeDBInstances

### FIS Templates
- **Naming**: test-{type}-resilience
- **Targets**: Tag-based (Environment=test)
- **Selection**: COUNT(1) for safety
- **Stop Conditions**: None (manual stop)
- **Tags**: Source, Investigation, AutoGenerated

### SNS Topic
- **Name**: devops-agent-fis-recommendations
- **Protocol**: Email
- **Subscribers**: Engineering team

## Key Features

1. **Automatic Detection**: Keywords in findings trigger appropriate FIS actions
2. **One-Click Execution**: Direct console URLs for immediate testing
3. **Rich Context**: Each recommendation includes why and what to test
4. **Safety Tags**: All templates tagged for tracking and governance
5. **Scalable**: Handles multiple finding types in single investigation
6. **Cost-Effective**: ~$0.70/month for 100 investigations

## Success Metrics

- **Template Creation Rate**: 100% (4/4 in testing)
- **Time to Test**: < 2 minutes from investigation to running experiment
- **Manual Steps Eliminated**: 5 (template creation, configuration, tagging, documentation, URL sharing)
- **Engineer Productivity**: 15 minutes saved per investigation
