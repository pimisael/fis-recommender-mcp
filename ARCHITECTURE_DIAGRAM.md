# FIS Recommender - Solutions Library Architecture Diagram

## High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                                │
│                          AWS Cloud (Customer Account)                          │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                            │ │
│  │                      Amazon Bedrock AgentCore                             │ │
│  │                                                                            │ │
│  │    ┌────────────────────────────────────────────────────────────────┐    │ │
│  │    │                                                                  │    │ │
│  │    │              AgentCore Runtime Environment                       │    │ │
│  │    │                                                                  │    │ │
│  │    │   ┌──────────────────────────────────────────────────────┐     │    │ │
│  │    │   │                                                        │     │    │ │
│  │    │   │      FIS Recommender MCP Server (Container)           │     │    │ │
│  │    │   │                                                        │     │    │ │
│  │    │   │   Tools:                                              │     │    │ │
│  │    │   │   • recommend_fis_experiments                         │     │    │ │
│  │    │   │   • create_fis_template                               │     │    │ │
│  │    │   │                                                        │     │    │ │
│  │    │   │   Finding Mappings: 50+ AWS service scenarios         │     │    │ │
│  │    │   │                                                        │     │    │ │
│  │    │   └──────────────────────────────────────────────────────┘     │    │ │
│  │    │                                                                  │    │ │
│  │    │   Protocol: HTTP/HTTPS (Stateless)                              │    │ │
│  │    │   Session: Mcp-Session-Id header                                │    │ │
│  │    │                                                                  │    │ │
│  │    └────────────────────────────────────────────────────────────────┘    │ │
│  │                                                                            │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                    ▲                                           │
│                                    │                                           │
│                                    │ HTTPS/MCP Protocol                        │
│                                    │                                           │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                            │ │
│  │                          MCP Client Layer                                 │ │
│  │                                                                            │ │
│  │   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │ │
│  │   │          │    │          │    │          │    │                    │  │ │
│  │   │ Kiro CLI │    │  Claude  │    │ Amazon Q │    │ Custom Apps      │  │ │
│  │   │          │    │ Desktop  │    │Developer │    │ (MCP SDK)        │  │ │
│  │   │          │    │          │    │          │    │                    │  │ │
│  │   └──────────┘    └──────────┘    └──────────┘    └──────────────────┘  │ │
│  │                                                                            │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                            │ │
│  │                      AWS Services Integration                             │ │
│  │                                                                            │ │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │ │
│  │   │              │  │              │  │              │  │            │  │ │
│  │   │   AWS FIS    │  │  CloudWatch  │  │     SSM      │  │ CloudTrail │  │ │
│  │   │              │  │   Alarms     │  │              │  │            │  │ │
│  │   │              │  │              │  │              │  │            │  │ │
│  │   └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘  │ │
│  │                                                                            │ │
│  │   Experiment       Stop Conditions    Custom Faults    Audit Logging      │ │
│  │   Execution        & Monitoring       Injection        & Compliance       │ │
│  │                                                                            │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                            │ │
│  │                      Security & Access Control                            │ │
│  │                                                                            │ │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │ │
│  │   │              │  │              │  │              │  │            │  │ │
│  │   │  IAM Roles   │  │  AWS KMS     │  │   Secrets    │  │    VPC     │  │ │
│  │   │  & Policies  │  │  Encryption  │  │   Manager    │  │  Endpoints │  │ │
│  │   │              │  │              │  │              │  │            │  │ │
│  │   └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘  │ │
│  │                                                                            │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘

                                  Data Flow
                                  ─────────

    ┌─────────────┐
    │   DevOps    │
    │   Agent     │──────┐
    │  (Findings) │      │
    └─────────────┘      │
                         │ 1. Operational Finding
                         ▼
    ┌─────────────────────────────────────┐
    │        MCP Client                   │
    │  (Kiro CLI / Claude / Amazon Q)     │
    └─────────────────────────────────────┘
                         │
                         │ 2. MCP Request
                         │    (recommend_fis_experiments)
                         ▼
    ┌─────────────────────────────────────┐
    │   FIS Recommender MCP Server        │
    │   (AgentCore Runtime)               │
    │                                     │
    │   • Analyze finding keywords        │
    │   • Match to FIS actions            │
    │   • Generate recommendations        │
    └─────────────────────────────────────┘
                         │
                         │ 3. Recommendations
                         ▼
    ┌─────────────────────────────────────┐
    │        MCP Client                   │
    │  Reviews recommendations            │
    └─────────────────────────────────────┘
                         │
                         │ 4. MCP Request
                         │    (create_fis_template)
                         ▼
    ┌─────────────────────────────────────┐
    │   FIS Recommender MCP Server        │
    │                                     │
    │   • Generate FIS template           │
    │   • Include target config           │
    │   • Add stop conditions             │
    └─────────────────────────────────────┘
                         │
                         │ 5. FIS Template
                         ▼
    ┌─────────────────────────────────────┐
    │        Customer                     │
    │  Deploys to AWS FIS                 │
    └─────────────────────────────────────┘
                         │
                         │ 6. Execute Experiment
                         ▼
    ┌─────────────────────────────────────┐
    │         AWS FIS                     │
    │  Runs chaos engineering experiment  │
    └─────────────────────────────────────┘
                         │
                         │ 7. Monitor
                         ▼
    ┌─────────────────────────────────────┐
    │       CloudWatch                    │
    │  Metrics, Alarms, Stop Conditions   │
    └─────────────────────────────────────┘
```

## Deployment Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                                │
│                    Infrastructure as Code Deployment                          │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                            │ │
│  │                      Deployment Options                                   │ │
│  │                                                                            │ │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │ │
│  │   │              │    │              │    │                          │  │ │
│  │   │ CloudFormation│   │   AWS CDK    │    │      Terraform           │  │ │
│  │   │   Template   │    │  (TypeScript)│    │       (HCL)              │  │ │
│  │   │              │    │              │    │                          │  │ │
│  │   │  • YAML      │    │  • Python    │    │  • Multi-cloud           │  │ │
│  │   │  • One-click │    │  • TypeScript│    │  • Enterprise            │  │ │
│  │   │  • Console   │    │  • Java      │    │  • State management      │  │ │
│  │   │              │    │              │    │                          │  │ │
│  │   └──────────────┘    └──────────────┘    └──────────────────────────┘  │ │
│  │                                                                            │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                           │
│                                    │ Provisions                                │
│                                    ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                            │ │
│  │                      Provisioned Resources                                │ │
│  │                                                                            │ │
│  │   • AgentCore Runtime environment                                         │ │
│  │   • FIS Recommender MCP Server (container)                                │ │
│  │   • IAM roles and policies                                                │ │
│  │   • CloudWatch log groups                                                 │ │
│  │   • (Optional) VPC endpoints                                              │ │
│  │   • (Optional) KMS encryption keys                                        │ │
│  │                                                                            │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Key Features for Solutions Library

1. **One-Click Deployment**
   - CloudFormation template in S3
   - Launch Stack button in AWS Console
   - Automated resource provisioning

2. **Infrastructure as Code**
   - CloudFormation (YAML/JSON)
   - AWS CDK (TypeScript, Python, Java)
   - Terraform (HCL)

3. **Well-Architected**
   - All 6 pillars addressed
   - Security best practices
   - Cost optimization

4. **Comprehensive Documentation**
   - Implementation guide
   - Architecture diagrams
   - API reference
   - Troubleshooting guide

5. **Sample Code**
   - GitHub repository
   - Example integrations
   - Test scripts

6. **Cost Transparency**
   - Estimated monthly costs
   - Pay-per-use pricing
   - No upfront costs
