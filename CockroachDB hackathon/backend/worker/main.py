"""
Ingestion Worker — SQS consumer running on ECS Fargate.

Processes payment events from SQS and:
1. Stores transactions in CockroachDB
2. Updates customer records
3. Triggers anomaly detection if thresholds are breached
4. Generates embeddings for semantic memory
"""

import os
import json
import asyncio
import boto3
from datetime import datetime

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "eu-west-2")

sqs = boto3.client("sqs", region_name=AWS_REGION)


async def process_message(message: dict):
    """Process a single payment event from SQS."""
    body = json.loads(message["Body"])
    event_type = body["event_type"]
    data = body["data"]
    account_id = body.get("account")

    print(f"Processing event: {event_type} for account: {account_id}")

    if event_type in ("payment_intent.succeeded", "charge.succeeded"):
        await handle_successful_payment(account_id, data)
    elif event_type in ("payment_intent.payment_failed", "charge.failed"):
        await handle_failed_payment(account_id, data)
    elif event_type == "charge.refunded":
        await handle_refund(account_id, data)
    elif event_type.startswith("customer.subscription"):
        await handle_subscription_event(event_type, account_id, data)
    elif event_type.startswith("invoice"):
        await handle_invoice_event(event_type, account_id, data)


async def handle_successful_payment(account_id: str, data: dict):
    """Store successful payment and update customer metrics."""
    # TODO: Insert into transactions table
    # TODO: Update customer.last_transaction_at, total_transactions, total_revenue
    # TODO: Check if this resolves a previous failure (for agent learning)
    pass


async def handle_failed_payment(account_id: str, data: dict):
    """Store failed payment and check if this triggers an anomaly."""
    # TODO: Insert into transactions table with failure_reason
    # TODO: Check failure rate against baselines
    # TODO: If anomaly detected, create agent task to investigate
    pass


async def handle_refund(account_id: str, data: dict):
    """Process a refund event."""
    # TODO: Update transaction status, adjust customer revenue
    pass


async def handle_subscription_event(event_type: str, account_id: str, data: dict):
    """Process subscription lifecycle events."""
    # TODO: Update customer subscription status
    pass


async def handle_invoice_event(event_type: str, account_id: str, data: dict):
    """Process invoice events."""
    # TODO: Track invoice payment status
    pass


async def poll_sqs():
    """Continuously poll SQS for new messages."""
    print(f"Starting SQS worker, polling: {SQS_QUEUE_URL}")

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20,  # Long polling
                VisibilityTimeout=60,
            )

            messages = response.get("Messages", [])

            for message in messages:
                try:
                    await process_message(message)
                    # Delete message after successful processing
                    sqs.delete_message(
                        QueueUrl=SQS_QUEUE_URL,
                        ReceiptHandle=message["ReceiptHandle"],
                    )
                except Exception as e:
                    print(f"Error processing message: {e}")
                    # Message will become visible again after VisibilityTimeout

        except Exception as e:
            print(f"Error polling SQS: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(poll_sqs())
