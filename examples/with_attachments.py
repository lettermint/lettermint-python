"""
Email with attachments example.

Demonstrates how to attach files to emails using base64 encoding.
"""

import base64
import os
from pathlib import Path

from lettermint import Lettermint

client = Lettermint(os.environ["LETTERMINT_API_TOKEN"])


def attach_file(filepath: str) -> dict:
    """Helper to create an attachment dict from a file path."""
    path = Path(filepath)
    content = base64.b64encode(path.read_bytes()).decode("utf-8")

    return {
        "filename": path.name,
        "content": content,
    }


# Send email with attachments
response = (
    client.email()
    .from_("sender@example.com")
    .to("recipient@example.com")
    .subject("Monthly Report")
    .html("<p>Please find the monthly report attached.</p>")
    .attach(attach_file("report.pdf"))
    .attach(attach_file("data.csv"))
    .send()
)

print(f"Email with attachments sent! ID: {response['id']}")
