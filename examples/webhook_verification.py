"""
Webhook signature verification example.

This example shows how to verify incoming webhooks from Lettermint
to ensure they are authentic and haven't been tampered with.
"""

import os

from lettermint import Webhook
from lettermint.exceptions import WebhookVerificationError

# Your webhook signing secret from the Lettermint dashboard
webhook_secret = os.environ["LETTERMINT_WEBHOOK_SECRET"]

webhook = Webhook(webhook_secret)


def handle_webhook(payload: str, signature: str, timestamp: str):
    """
    Handle an incoming webhook request.

    Args:
        payload: The raw request body as a string
        signature: The X-Lettermint-Signature header value
        timestamp: The X-Lettermint-Timestamp header value
    """
    try:
        # Verify the webhook signature
        # This will raise WebhookVerificationError if invalid
        webhook.verify(payload, signature, timestamp)

        # Process the verified webhook payload
        print("Webhook verified successfully!")
        print(f"Payload: {payload}")

    except WebhookVerificationError as e:
        print(f"Webhook verification failed: {e}")
        # Return 401 Unauthorized in your web framework


# Example: Flask integration
"""
from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    payload = request.get_data(as_text=True)
    signature = request.headers.get("X-Lettermint-Signature", "")
    timestamp = request.headers.get("X-Lettermint-Timestamp", "")

    try:
        webhook.verify(payload, signature, timestamp)
        # Process the webhook...
        return "OK", 200
    except WebhookVerificationError:
        return "Invalid signature", 401
"""

# Example: FastAPI integration
"""
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/webhook")
async def webhook_handler(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Lettermint-Signature", "")
    timestamp = request.headers.get("X-Lettermint-Timestamp", "")

    try:
        webhook.verify(payload.decode(), signature, timestamp)
        # Process the webhook...
        return {"status": "ok"}
    except WebhookVerificationError:
        raise HTTPException(status_code=401, detail="Invalid signature")
"""
