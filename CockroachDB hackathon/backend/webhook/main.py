"""
Stripe Payment Webhook Handler — ECS Fargate service.

Receives Stripe Connect webhooks, validates them, and:
1. Stores transaction data in CockroachDB
2. Publishes events to SQS for the ingestion worker
"""

import os
import json
import stripe
from fastapi import FastAPI, Request, HTTPException
import boto3

app = FastAPI(title="LedgerMind Payment Webhook")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "us-east-1"))


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Handle incoming Stripe Connect webhook events.
    Validates signature and dispatches to SQS for processing.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Events we care about
    relevant_events = {
        "payment_intent.succeeded",
        "payment_intent.payment_failed",
        "charge.succeeded",
        "charge.failed",
        "charge.refunded",
        "customer.subscription.created",
        "customer.subscription.deleted",
        "invoice.paid",
        "invoice.payment_failed",
    }

    if event["type"] in relevant_events:
        # Publish to SQS for async processing by the ingestion worker
        sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps({
                "event_type": event["type"],
                "data": event["data"]["object"],
                "account": event.get("account"),  # Connected account ID
                "created": event["created"],
            }),
            MessageGroupId=event.get("account", "default"),
        )

    return {"status": "received"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ledgermind-webhook"}
