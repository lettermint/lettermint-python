"""Verify Lettermint webhook deliveries in a Flask app.

LETTERMINT_WEBHOOK_SECRET=whsec_... flask --app examples/webhook_verification.py run
"""

import os

from flask import Flask, request

from lettermint import Webhook, WebhookVerificationError

app = Flask(__name__)
webhook = Webhook(os.environ["LETTERMINT_WEBHOOK_SECRET"])


@app.post("/webhooks/lettermint")
def lettermint_webhook() -> tuple[str, int]:
    try:
        event = webhook.verify(request.get_data(), request.headers)
    except WebhookVerificationError as error:
        app.logger.warning("Rejected a webhook delivery: %s", error.reason)
        return "Invalid signature", 400
    app.logger.info("Received %s", event["event"])
    return "", 204
