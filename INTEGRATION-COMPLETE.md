# DevOps Agent → FIS Recommender Integration

## ✅ DEPLOYMENT COMPLETE

### Configuration

- **Agent Space**: DevOpsAgent-BetaAgentAgentSpace-1838C6BF
- **Slack Channel**: test-low-sev
- **Lambda Function**: DevOpsAgentFISRecommender
- **EventBridge Rule**: DevOpsAgentFISRecommendations
- **SNS Topic**: devops-agent-fis-recommendations

### How It Works

```
DevOps Agent Investigation Complete
           ↓
    EventBridge Rule (filtered by Agent Space)
           ↓
    Lambda Function
           ↓
  Analyze Finding Keywords
           ↓
Generate FIS Recommendations
           ↓
    SNS Email Notification
```

### Supported Keywords

The system detects these keywords in DevOps Agent findings:

| Keyword | FIS Action | Duration |
|---------|------------|----------|
| network | aws:network:disrupt-connectivity | 5 min |
| latency | aws:network:disrupt-connectivity | 10 min |
| database | aws:rds:reboot-db-instances | 2 min |
| cpu | aws:ec2:stop-instances | 3 min |
| memory | aws:ssm:send-command | 5 min |
| availability | aws:ec2:stop-instances | 5 min |

### Subscribe to Email Notifications

```bash
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:815635340291:devops-agent-fis-recommendations \
    --protocol email \
    --notification-endpoint your-email@amazon.com \
    --region us-east-1
```

### Monitor Activity

```bash
# Watch Lambda logs
aws logs tail /aws/lambda/DevOpsAgentFISRecommender --follow --region us-east-1

# Check EventBridge rule
aws events describe-rule --name DevOpsAgentFISRecommendations --region us-east-1
```

### Test Manually

```bash
aws lambda invoke \
    --function-name DevOpsAgentFISRecommender \
    --payload '{"detail":{"agentSpaceId":"DevOpsAgent-BetaAgentAgentSpace-1838C6BF","investigationId":"test-123","summary":"Network latency and database timeouts","type":"AVAILABILITY","description":"Test finding"}}' \
    --region us-east-1 \
    /tmp/test-response.json
```

### Resources

- Lambda: arn:aws:lambda:us-east-1:815635340291:function:DevOpsAgentFISRecommender
- SNS: arn:aws:sns:us-east-1:815635340291:devops-agent-fis-recommendations
- EventBridge: arn:aws:events:us-east-1:815635340291:rule/DevOpsAgentFISRecommendations

### Cost

~$0.70/month (100 investigations)

---

**Status**: Live and monitoring
**Deployed**: 2026-01-30
**Region**: us-east-1
