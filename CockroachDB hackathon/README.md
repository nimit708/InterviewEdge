# LedgerMind — AI-Powered Payment Operations Agent for SMEs

## Overview

LedgerMind is an intelligent payment operations platform that uses an AI agent backed by CockroachDB as agentic memory. The agent observes payment activity, detects anomalies, explains root causes, recommends actions, and learns from outcomes — all with SME approval before consequential actions execute.

## Architecture

```
SME User → React Dashboard (Amplify) → Cognito Auth
                ↓
        ALB → FastAPI (ECS Fargate)
                ↓
    ┌───────────────────────────────────┐
    │  LedgerMind Agent (ECS Fargate)   │
    │  ├── Amazon Bedrock (LLM)         │
    │  ├── CockroachDB (Agentic Memory) │
    │  └── Vector Search (Semantic)     │
    └───────────────────────────────────┘
                ↓
    Stripe Connect → Payment Webhook → SQS → Ingestion Worker
```

## Agent Capabilities

### Core Loop
1. **Observe** — Monitor current payment activity in real-time
2. **Retrieve** — Fetch relevant structured + semantic memory from CockroachDB
3. **Compare** — Measure current behaviour against learned baselines
4. **Explain** — Identify likely cause of anomalies
5. **Recommend** — Suggest actions to the SME
6. **Store** — Record decisions and approval state
7. **Check** — Verify outcomes of approved actions
8. **Learn** — Use outcomes to improve future incident handling

### Agent Tasks
- Investigate payment failure spikes
- Create customer-recovery lists
- Follow up with inactive customers
- Monitor anomalies for 24 hours
- Prepare campaign suggestions
- Schedule later performance checks

### Human-in-the-Loop
All consequential actions require SME approval before execution.

## Project Structure

```
/frontend          — React dashboard (Amplify hosted)
/backend
  /api             — FastAPI application
  /agent           — LedgerMind agent service
  /worker          — Ingestion worker (SQS consumer)
  /webhook         — Stripe payment webhook handler
/infra             — Terraform IaC
/shared            — Shared schemas, types, utilities
```

## Tech Stack

| Layer          | Technology                     |
|----------------|--------------------------------|
| Frontend       | React + TypeScript + Amplify   |
| Auth           | Amazon Cognito (MFA)           |
| API            | FastAPI (Python)               |
| Agent          | Python + LangChain + Bedrock   |
| Database       | CockroachDB Cloud              |
| Vector Search  | CockroachDB pgvector           |
| Queue          | Amazon SQS                     |
| Payments       | Stripe Connect                 |
| Hosting        | ECS Fargate + ALB              |
| IaC            | Terraform                      |

## Getting Started

See individual service READMEs for setup instructions.
