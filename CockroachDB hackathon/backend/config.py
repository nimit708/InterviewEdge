"""
Application Configuration — reads from AWS Secrets Manager or env vars.

In ECS Fargate, secrets are injected as environment variables via task definition.
This module provides a clean interface and fallback for local development.
"""

import os
import json
import boto3
from functools import lru_cache
from typing import Optional


class Settings:
    """Application settings — resolved from env vars (injected by ECS from Secrets Manager)."""

    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "dev")
        self.aws_region = os.getenv("AWS_REGION", "eu-west-2")

        # Database (injected from Secrets Manager via ECS task definition)
        self.database_url = os.getenv("DATABASE_URL", "")

        # Cognito
        self.cognito_user_pool_id = os.getenv("COGNITO_USER_POOL_ID", "")
        self.cognito_app_client_id = os.getenv("COGNITO_APP_CLIENT_ID", "")
        self.cognito_region = os.getenv("COGNITO_REGION", self.aws_region)

        # Stripe
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "")
        self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

        # Bedrock
        self.bedrock_model_id = os.getenv(
            "BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-20250514-v1:0"
        )
        self.bedrock_embedding_model_id = os.getenv(
            "BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0"
        )

        # SQS
        self.sqs_payment_queue_url = os.getenv("SQS_PAYMENT_QUEUE_URL", "")
        self.sqs_agent_queue_url = os.getenv("SQS_AGENT_QUEUE_URL", "")

        # If DATABASE_URL is empty, try to load from Secrets Manager directly
        # (for local development without ECS secret injection)
        if not self.database_url and self.environment == "dev":
            self._load_from_secrets_manager()

    def _load_from_secrets_manager(self):
        """
        Fallback: load secrets directly from AWS Secrets Manager.
        Used for local development when not running in ECS.
        """
        try:
            client = boto3.client("secretsmanager", region_name=self.aws_region)
            project = os.getenv("PROJECT_NAME", "ledgermind")

            # CockroachDB
            if not self.database_url:
                secret = self._get_secret(client, f"{project}/{self.environment}/cockroachdb-url")
                if secret:
                    self.database_url = secret.get("url", "")

            # Stripe
            if not self.stripe_secret_key:
                secret = self._get_secret(client, f"{project}/{self.environment}/stripe")
                if secret:
                    self.stripe_secret_key = secret.get("secret_key", "")
                    self.stripe_webhook_secret = secret.get("webhook_secret", "")

            # Bedrock
            secret = self._get_secret(client, f"{project}/{self.environment}/bedrock")
            if secret:
                self.bedrock_model_id = secret.get("model_id", self.bedrock_model_id)
                self.bedrock_embedding_model_id = secret.get(
                    "embedding_model_id", self.bedrock_embedding_model_id
                )

            # App (Cognito)
            if not self.cognito_user_pool_id:
                secret = self._get_secret(client, f"{project}/{self.environment}/app")
                if secret:
                    self.cognito_user_pool_id = secret.get("cognito_user_pool_id", "")
                    self.cognito_app_client_id = secret.get("cognito_client_id", "")

        except Exception as e:
            print(f"Warning: Could not load from Secrets Manager: {e}")
            print("Using environment variables or defaults.")

    def _get_secret(self, client, secret_name: str) -> Optional[dict]:
        """Retrieve and parse a secret from Secrets Manager."""
        try:
            response = client.get_secret_value(SecretId=secret_name)
            return json.loads(response["SecretString"])
        except client.exceptions.ResourceNotFoundException:
            return None
        except Exception:
            return None


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
