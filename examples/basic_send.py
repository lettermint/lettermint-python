"""
Basic email sending example using the synchronous Lettermint client.
"""

import os

from lettermint import Lettermint

# Initialize the client with your API token
client = Lettermint(os.environ["LETTERMINT_API_TOKEN"])

# Send a simple email using the fluent builder
response = (
    client.email()
    .from_("sender@example.com")
    .to("recipient@example.com")
    .subject("Hello from Lettermint!")
    .html("<h1>Welcome!</h1><p>This is a test email.</p>")
    .send()
)

print(f"Email sent! ID: {response['id']}")
