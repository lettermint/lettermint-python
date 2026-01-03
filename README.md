# Lettermint Python SDK

[![PyPI Version](https://img.shields.io/pypi/v/lettermint?style=flat-square)](https://pypi.org/project/lettermint/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/lettermint?style=flat-square)](https://pypi.org/project/lettermint/)
[![Python Version](https://img.shields.io/pypi/pyversions/lettermint?style=flat-square)](https://pypi.org/project/lettermint/)
[![GitHub Tests](https://img.shields.io/github/actions/workflow/status/lettermint/lettermint-python/ci.yml?branch=main&label=tests&style=flat-square)](https://github.com/lettermint/lettermint-python/actions?query=workflow%3ACI+branch%3Amain)
[![License](https://img.shields.io/github/license/lettermint/lettermint-python?style=flat-square)](https://github.com/lettermint/lettermint-python/blob/main/LICENSE)
[![Join our Discord server](https://img.shields.io/discord/1305510095588819035?logo=discord&logoColor=eee&label=Discord&labelColor=464ce5&color=0D0E28&cacheSeconds=43200)](https://lettermint.co/r/discord)

Official Python SDK for the [Lettermint](https://lettermint.co) email API.

## Installation

```bash
pip install lettermint
```

## Quick Start

### Sending Emails (Synchronous)

```python
from lettermint import Lettermint

client = Lettermint(api_token="your-api-token")

response = (
    client.email
    .from_("sender@example.com")
    .to("recipient@example.com")
    .subject("Hello from Python!")
    .html("<h1>Welcome!</h1>")
    .text("Welcome!")
    .send()
)

print(response["message_id"])
```

### Sending Emails (Asynchronous)

```python
from lettermint import AsyncLettermint

async with AsyncLettermint(api_token="your-api-token") as client:
    response = await (
        client.email
        .from_("sender@example.com")
        .to("recipient@example.com")
        .subject("Hello from Python!")
        .html("<h1>Welcome!</h1>")
        .send()
    )
    print(response["message_id"])
```

## Email Options

### Multiple Recipients

```python
client.email.from_("sender@example.com").to(
    "recipient1@example.com",
    "recipient2@example.com"
).subject("Hello").send()
```

### CC and BCC

```python
client.email.from_("sender@example.com").to("recipient@example.com").cc(
    "cc1@example.com",
    "cc2@example.com"
).bcc("bcc@example.com").subject("Hello").send()
```

### Reply-To

```python
client.email.from_("sender@example.com").to("recipient@example.com").reply_to(
    "reply@example.com"
).subject("Hello").send()
```

### RFC 5322 Addresses

```python
client.email.from_("John Doe <john@example.com>").to(
    "Jane Doe <jane@example.com>"
).subject("Hello").send()
```

### Attachments

```python
import base64

# Read and encode your file
with open("document.pdf", "rb") as f:
    content = base64.b64encode(f.read()).decode()

# Regular attachment
client.email.from_("sender@example.com").to("recipient@example.com").subject(
    "Your Document"
).attach("document.pdf", content).send()

# Inline attachment (for embedding in HTML)
client.email.from_("sender@example.com").to("recipient@example.com").subject(
    "Welcome"
).html('<img src="cid:logo@example.com">').attach(
    "logo.png", logo_content, "logo@example.com"
).send()
```

### Custom Headers

```python
client.email.from_("sender@example.com").to("recipient@example.com").subject(
    "Hello"
).headers({"X-Custom-Header": "value"}).send()
```

### Metadata and Tags

```python
client.email.from_("sender@example.com").to("recipient@example.com").subject(
    "Hello"
).metadata({"campaign_id": "123", "user_id": "456"}).tag("welcome-campaign").send()
```

### Routing

```python
client.email.from_("sender@example.com").to("recipient@example.com").subject(
    "Hello"
).route("my-route").send()
```

### Idempotency Key

Prevent duplicate sends when retrying failed requests:

```python
client.email.from_("sender@example.com").to("recipient@example.com").subject(
    "Hello"
).idempotency_key("unique-request-id").send()
```

## Webhook Verification

Verify webhook signatures to ensure authenticity:

```python
from lettermint import Webhook

# Create a webhook verifier
webhook = Webhook(secret="your-webhook-secret")

# Verify using headers (recommended)
payload = webhook.verify_headers(request.headers, request.body)

# Or verify using the signature directly
payload = webhook.verify(
    payload=request.body,
    signature=request.headers["X-Lettermint-Signature"],
)

print(payload["event"])
```

### Static Method

For one-off verification:

```python
from lettermint import Webhook

payload = Webhook.verify_signature(
    payload=request.body,
    signature=request.headers["X-Lettermint-Signature"],
    secret="your-webhook-secret",
)
```

### Custom Tolerance

Adjust the timestamp tolerance (default: 300 seconds):

```python
webhook = Webhook(secret="your-webhook-secret", tolerance=600)
```

## Error Handling

```python
from lettermint import Lettermint
from lettermint.exceptions import (
    ValidationError,
    ClientError,
    HttpRequestError,
    TimeoutError,
)

client = Lettermint(api_token="your-api-token")

try:
    response = client.email.from_("sender@example.com").to("recipient@example.com").subject(
        "Hello"
    ).send()
except ValidationError as e:
    # 422 errors (e.g., daily limit exceeded)
    print(f"Validation error: {e.error_type}")
    print(f"Response: {e.response_body}")
except ClientError as e:
    # 400 errors
    print(f"Client error: {e}")
except TimeoutError as e:
    # Request timeout
    print(f"Timeout: {e}")
except HttpRequestError as e:
    # Other HTTP errors
    print(f"HTTP error {e.status_code}: {e}")
```

### Webhook Errors

```python
from lettermint import Webhook
from lettermint.exceptions import (
    InvalidSignatureError,
    TimestampToleranceError,
    JsonDecodeError,
    WebhookVerificationError,
)

try:
    payload = webhook.verify_headers(headers, body)
except InvalidSignatureError:
    print("Invalid signature - request may be forged")
except TimestampToleranceError:
    print("Timestamp too old - possible replay attack")
except JsonDecodeError:
    print("Invalid JSON in payload")
except WebhookVerificationError as e:
    print(f"Verification failed: {e}")
```

## Configuration

### Custom Base URL

```python
client = Lettermint(
    api_token="your-api-token",
    base_url="https://custom.api.com/v1",
)
```

### Custom Timeout

```python
client = Lettermint(
    api_token="your-api-token",
    timeout=60.0,  # 60 seconds
)
```

## Context Manager

Both sync and async clients support context managers for proper resource cleanup:

```python
# Sync
with Lettermint(api_token="your-api-token") as client:
    client.email.from_("sender@example.com").to("recipient@example.com").send()

# Async
async with AsyncLettermint(api_token="your-api-token") as client:
    await client.email.from_("sender@example.com").to("recipient@example.com").send()
```

## Type Hints

This SDK is fully typed with `py.typed` marker. You'll get full autocomplete and type checking in your IDE.

## Requirements

- Python 3.9+
- httpx

## License

MIT
