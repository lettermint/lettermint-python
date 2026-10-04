"""Send an email with the synchronous client.

LETTERMINT_PROJECT_TOKEN=lm_... python examples/send_email.py
"""

import os

from lettermint import Lettermint

with Lettermint(sending_token=os.environ["LETTERMINT_PROJECT_TOKEN"]) as lettermint:
    result = (
        lettermint.emails.compose()
        .from_("Acme <hello@acme.com>")
        .to("jane@example.com")
        .subject("Welcome to Acme")
        .html("<h1>Welcome!</h1>")
        .text("Welcome!")
        .tags([{"name": "campaign", "value": "welcome"}])
        .send(idempotency_key="welcome-jane")
    )
    print(result["message_id"], result["status"])
