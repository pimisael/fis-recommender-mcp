# DevOps Agent FIS Recommender - Deployment Summary

## ✅ Deployment Complete!

### Resources Created

1. **SNS Topic**
   - Name: devops-agent-fis-recommendations
   - ARN: arn:aws:sns:us-east-1:815635340291:devops-agent-fis-recommendations
   - Purpose: Sends FIS recommendations via email/SMS

2. **IAM Role**
   - Name: DevOpsAgentFISRecommenderRole
   - ARN: arn:aws:iam::815635340291:role/DevOpsAgentFISRecommenderRole
   - Permissions: Lambda execution, SNS publish

3. **Lambda Function**
   - Name: DevOpsAgentFISRecommender
   - ARN: arn:aws:lambda:us-east-1:815635340291:function:DevOpsAgentFISRecommender
   - Runtime: Python 3.11
   - Timeout: 60 seconds

4. **EventBridge Rule**
   - Name: DevOpsAgentFISRecommendations
   - ARN: arn:aws:events:us-east-1:815635340291:rule/DevOpsAgentFISRecommendations
   - Trigger: DevOps Agent investigation complete events

### How It Works

1. DevOps Agent completes an investigation
2. EventBridge captures the event
3. Lambda function analyzes the finding
4. FIS experiment recommendations generated
5. SNS sends notification with recommendations

### Next Steps

#### 1. Subscribe to SNS Topic (Get Notifications)

```bash
# Subscribe with your email
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:815635340291:devops-agent-fis-recommendations \
    --protocol email \
    --notification-endpoint your-email@amazon.com \
    --region us-east-1
```

#### 2. Test the Integration

```bash
# Manually invoke Lambda with test event
aws lambda invoke \
    --function-name DevOpsAgentFISRecommender \
    --payload '{"detail":{"investigationId":"test-123","summary":"Network latency spike","type":"AVAILABILITY","description":"High latency observed"}}' \
    --region us-east-1 \
    /tmp/lambda-response.json

cat /tmp/lambda-response.json
```

#### 3. Monitor Lambda Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/DevOpsAgentFISRecommender --follow --region us-east-1
```

### Supported Finding Keywords

The system automatically detects these keywords and recommends FIS experiments:

- **network** → aws:network:disrupt-connectivity (5 min)
- **latency** → aws:network:disrupt-connectivity (10 min)
- **database** → aws:rds:reboot-db-instances (2 min)
- **cpu** → aws:ec2:stop-instances (3 min)
- **memory** → aws:ssm:send-command (5 min)
- **availability** → aws:ec2:stop-instances (5 min)

### Customization

To add more finding types, update the Lambda function:

```bash
aws lambda update-function-code \
    --function-name DevOpsAgentFISRecommender \
    --zip-file fileb:///path/to/updated-lambda.zip \
    --region us-east-1
```

### Troubleshooting

**No notifications received?**
1. Check SNS subscription confirmation email
2. Verify EventBridge rule is enabled
3. Check Lambda CloudWatch logs

**Lambda errors?**
```bash
aws logs tail /aws/lambda/DevOpsAgentFISRecommender --region us-east-1
```

### Cost Estimate

- Lambda: ~$0.20/month (assuming 100 invocations)
- SNS: ~$0.50/month (100 notifications)
- EventBridge: Free tier covers usage
- **Total: ~$0.70/month**

### Cleanup (If Needed)

```bash
# Delete all resources
aws events remove-targets --rule DevOpsAgentFISRecommendations --ids 1 --region us-east-1
aws events delete-rule --name DevOpsAgentFISRecommendations --region us-east-1
aws lambda delete-function --function-name DevOpsAgentFISRecommender --region us-east-1
aws iam detach-role-policy --role-name DevOpsAgentFISRecommenderRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam detach-role-policy --role-name DevOpsAgentFISRecommenderRole --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess
aws iam delete-role --role-name DevOpsAgentFISRecommenderRole
aws sns delete-topic --topic-arn arn:aws:sns:us-east-1:815635340291:devops-agent-fis-recommendations --region us-east-1
```

---

**Deployment Date:** 2026-01-29
**Region:** us-east-1
**Account:** 815635340291
