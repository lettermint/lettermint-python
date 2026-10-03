"""Send a batch of emails with the asynchronous client.

LETTERMINT_PROJECT_TOKEN=lm_... python examples/async_send.py
"""

import asyncio
import os
from pathlib import Path

from lettermint import AsyncLettermint


async def main() -> None:
    async with AsyncLettermint(sending_token=os.environ["LETTERMINT_PROJECT_TOKEN"]) as lettermint:
        base = lettermint.emails.compose().from_("billing@acme.com").subject("Your invoice")
        invoice = Path(__file__).read_bytes()  # any bytes; the SDK encodes them
        results = await lettermint.emails.send_batch(
            [
                base.to("jane@example.com")
                .text("Hi Jane")
                .attach("invoice.txt", invoice, content_type="text/plain"),
                base.to("john@example.com").text("Hi John"),
            ]
        )
        for result in results:
            print(result["message_id"], result["status"])


asyncio.run(main())
