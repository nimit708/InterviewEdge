"""
Amazon Bedrock Client — LLM and Embedding interface.

Provides:
- Chat/reasoning via Claude on Bedrock
- Text embeddings via Titan Embeddings V2
- Structured tool_use for MCP integration
"""

import os
import json
import boto3
from typing import Optional


BEDROCK_REGION = os.getenv("AWS_REGION", "eu-west-2")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-20250514-v1:0")
EMBEDDING_MODEL_ID = os.getenv(
    "BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0"
)


class BedrockClient:
    """Client for Amazon Bedrock — reasoning and embeddings."""

    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime", region_name=BEDROCK_REGION
        )
        self.model_id = MODEL_ID
        self.embedding_model_id = EMBEDDING_MODEL_ID

    async def invoke_agent(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
    ) -> dict:
        """
        Invoke Bedrock for agent reasoning.
        Supports tool_use for MCP tool calls.
        """
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": messages,
        }

        if tools:
            body["tools"] = tools

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        result = json.loads(response["body"].read())
        return result

    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate a text embedding using Amazon Titan Embeddings V2.
        Returns a 1024-dimensional vector for CockroachDB pgvector.
        """
        body = {
            "inputText": text,
            "dimensions": 1024,
            "normalize": True,
        }

        response = self.client.invoke_model(
            modelId=self.embedding_model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        result = json.loads(response["body"].read())
        return result.get("embedding", [])

    async def analyze_for_brief(
        self, data: dict
    ) -> dict:
        """Generate a daily brief analysis."""
        system = (
            "You are LedgerMind, an AI payment operations agent. "
            "Generate a concise daily business brief based on the data. "
            "Include a headline, action items, and forecast summary."
        )
        messages = [
            {
                "role": "user",
                "content": f"Generate a daily brief from this data:\n{json.dumps(data, indent=2)}",
            }
        ]
        result = await self.invoke_agent(system, messages)
        # Parse structured response from LLM
        return self._parse_brief_response(result)

    async def reason_about_anomaly(
        self,
        anomaly: dict,
        baselines: list,
        similar_incidents: list,
    ) -> dict:
        """Use LLM to explain an anomaly and suggest actions."""
        system = (
            "You are LedgerMind, an AI payment operations agent. "
            "Analyze this anomaly, explain the likely cause, and recommend an action. "
            "Consider the baselines and similar past incidents provided."
        )
        context = {
            "anomaly": anomaly,
            "baselines": baselines,
            "similar_past_incidents": similar_incidents,
        }
        messages = [
            {
                "role": "user",
                "content": f"Analyze this anomaly:\n{json.dumps(context, indent=2)}",
            }
        ]
        result = await self.invoke_agent(system, messages)
        return self._parse_analysis_response(result)

    def _parse_brief_response(self, result: dict) -> dict:
        """Extract structured brief from LLM response."""
        content = result.get("content", [])
        text = ""
        for block in content:
            if block.get("type") == "text":
                text = block.get("text", "")
                break
        return {
            "headline": text[:100] if text else "Daily Brief",
            "action_items": [],
            "forecast": "See detailed analysis",
        }

    def _parse_analysis_response(self, result: dict) -> dict:
        """Extract structured analysis from LLM response."""
        content = result.get("content", [])
        text = ""
        for block in content:
            if block.get("type") == "text":
                text = block.get("text", "")
                break
        return {
            "explanation": text,
            "recommended_action": "",
            "confidence": 0.7,
            "risk_level": "medium",
        }
