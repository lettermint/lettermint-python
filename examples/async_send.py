"""
Async email sending example using the AsyncLettermint client.

Useful for high-throughput applications or when integrating with
async frameworks like FastAPI, Starlette, or aiohttp.
"""

import asyncio
import os

from lettermint import AsyncLettermint


async def send_emails():
    # Initialize the async client
    client = AsyncLettermint(os.environ["LETTERMINT_API_TOKEN"])

    # Send multiple emails concurrently
    emails = [
        {"to": "user1@example.com", "name": "Alice"},
        {"to": "user2@example.com", "name": "Bob"},
        {"to": "user3@example.com", "name": "Charlie"},
    ]

    tasks = [
        client.email()
        .from_("sender@example.com")
        .to(email["to"])
        .subject(f"Hello {email['name']}!")
        .html(f"<p>Welcome aboard, {email['name']}!</p>")
        .send()
        for email in emails
    ]

    # Send all emails concurrently
    results = await asyncio.gather(*tasks)

    for result in results:
        print(f"Email sent! ID: {result['id']}")


if __name__ == "__main__":
    asyncio.run(send_emails())
