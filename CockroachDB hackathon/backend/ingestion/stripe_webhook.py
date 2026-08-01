"""
Stripe Webhook Ingestion — Automatic ingestion of Stripe test-mode events.

Handles:
- payment_intent.succeeded / payment_failed
- charge.succeeded / failed / refunded
- customer.subscription.* lifecycle
- invoice.* events
- payout events

All events are validated via Stripe signature, then stored in CockroachDB
and published to SQS for async processing.
"""

import os
import json
import stripe
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
import boto3

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "eu-west-2")

sqs = boto3.client("sqs", region_name=AWS_REGION)

# All event types we ingest
TRACKED_EVENTS = {
    # Payments
    "payment_intent.succeeded",
    "payment_intent.payment_failed",
    "charge.succeeded",
    "charge.failed",
    "charge.refunded",
    "charge.dispute.created",
    # Subscriptions
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "customer.subscription.trial_will_end",
    # Invoices
    "invoice.paid",
    "invoice.payment_failed",
    "invoice.finalized",
    # Customers
    "customer.created",
    "customer.updated",
    # Payouts
    "payout.paid",
    "payout.failed",
}


@router.post("/stripe")
async def handle_stripe_webhook(request: Request):
    """
    Receive and process Stripe Connect webhook events.
    Validates the Stripe signature, stores raw event, and queues for processing.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    event_data = event["data"]["object"]
    connected_account = event.get("account")  # Stripe Connect account ID

    if event_type in TRACKED_EVENTS:
        # Publish to SQS for async processing by ingestion worker
        message_body = json.dumps({
            "source": "stripe_webhook",
            "event_id": event["id"],
            "event_type": event_type,
            "data": event_data,
            "account": connected_account,
            "created": event["created"],
            "received_at": datetime.utcnow().isoformat(),
        })

        sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=message_body,
            MessageGroupId=connected_account or "default",
            MessageDeduplicationId=event["id"],
        )

    return {"status": "received", "event_type": event_type}


@router.get("/stripe/connection-status")
async def check_stripe_connection():
    """Check if Stripe is connected and in test mode."""
    try:
        account = stripe.Account.retrieve()
        return {
            "connected": True,
            "livemode": account.get("charges_enabled", False) and not stripe.api_key.startswith("sk_test"),
            "test_mode": stripe.api_key.startswith("sk_test"),
            "account_id": account.get("id"),
            "business_name": account.get("business_profile", {}).get("name"),
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
        }
