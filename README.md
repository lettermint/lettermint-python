# Lettermint Python SDK

[![PyPI Version](https://img.shields.io/pypi/v/lettermint?style=flat-square)](https://pypi.org/project/lettermint/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/lettermint?style=flat-square)](https://pypi.org/project/lettermint/)
[![Python Version](https://img.shields.io/pypi/pyversions/lettermint?style=flat-square)](https://pypi.org/project/lettermint/)
[![GitHub Tests](https://img.shields.io/github/actions/workflow/status/lettermint/lettermint-python/ci.yml?branch=main&label=tests&style=flat-square)](https://github.com/lettermint/lettermint-python/actions?query=workflow%3ACI+branch%3Amain)
[![License](https://img.shields.io/github/license/lettermint/lettermint-python?style=flat-square)](https://github.com/lettermint/lettermint-python/blob/main/LICENSE)
[![Join our Discord server](https://img.shields.io/discord/1305510095588819035?logo=discord&logoColor=eee&label=Discord&labelColor=464ce5&color=0D0E28&cacheSeconds=43200)](https://lettermint.co/r/discord)

The official Python SDK for [Lettermint](https://lettermint.co). It runs on Python 3.10 and newer, is fully typed, and has a synchronous and an asynchronous client with the same methods.

Upgrading from 2.x? Read [UPGRADE.md](UPGRADE.md).

## Installation

```bash
pip install lettermint
```

## Quick start

Create a client with a project sending token and send an email:

```python
import os

from lettermint import Lettermint

lettermint = Lettermint(sending_token=os.environ["LETTERMINT_PROJECT_TOKEN"])

result = lettermint.emails.send({
    "from": "Acme <hello@acme.com>",
    "to": ["jane@example.com"],
    "subject": "Welcome to Acme",
    "html": "<p>Thanks for signing up.</p>",
    "text": "Thanks for signing up.",
})

print(result["message_id"], result["status"])  # "…", "pending"
```

The asynchronous client works the same way, for `asyncio` and `trio`:

```python
from lettermint import AsyncLettermint

async with AsyncLettermint(sending_token=os.environ["LETTERMINT_PROJECT_TOKEN"]) as lettermint:
    result = await lettermint.emails.send({...})
```

## Tokens

Lettermint has two kinds of API tokens:

| Argument | Token | Used by | Sent as |
| --- | --- | --- | --- |
| `sending_token` | Project sending token (`lm_…`) | `lettermint.emails` | `x-lettermint-token` header |
| `team_token` | Team API token (`lm_team_…`) | Every other part (domains, messages, projects, …) | `Authorization: Bearer` header |

Pass one or both:

```python
lettermint = Lettermint(
    sending_token=os.environ["LETTERMINT_PROJECT_TOKEN"],
    team_token=os.environ["LETTERMINT_TEAM_TOKEN"],
)
```

Each part uses its own token and never falls back to the other one. If the token a method needs is missing, it raises `LettermintConfigError` that names the argument (`domains.list needs team_token; …`), before any request. `lettermint.ping()` uses the team token when it is set, otherwise the sending token. `messages.reschedule()` and `messages.cancel()` accept either token in the same way.

You can also pass a single token string. The SDK chooses its type by the format: `lm_team_` followed by letters and digits is a team token, and `lm_` followed by letters and digits is a sending token. Any other value, such as an SSO verification token (`lm_sso_…`), raises `LettermintConfigError`; pass `sending_token=` or `team_token=` explicitly in that case.

```python
lettermint = Lettermint(os.environ["LETTERMINT_TOKEN"])
lettermint = Lettermint(os.environ["LETTERMINT_TOKEN"], timeout=10)  # with options
```

Error messages never contain the token, and `repr(lettermint)` shows tokens as `[redacted]`.

### Options

| Argument | Default | Description |
| --- | --- | --- |
| `sending_token` | | Project sending token. |
| `team_token` | | Team API token. |
| `base_url` | `https://api.lettermint.co/v1` | API base URL. |
| `timeout` | `30` | Request timeout in seconds. It covers the whole request, including the response body. Every method also takes `timeout=`. |
| `http_client` | a new `httpx.Client` / `httpx.AsyncClient` | Your own `httpx` client, for example with a proxy. The SDK never follows redirects with it and does not close it. |

The client holds no per-email state, so create it once and share it, also between threads or tasks. It owns a connection pool: call `close()` (`await lettermint.close()` for the async client) when you are done, or use it as a context manager.

## Sending email

### The email builder

`emails.compose()` returns an immutable builder. Every setter returns a new builder and leaves the original unchanged, so you can keep a base builder and reuse it, also across threads and tasks:

```python
welcome = (
    lettermint.emails.compose()
    .from_("Acme <hello@acme.com>")
    .subject("Welcome to Acme")
    .tags([{"name": "campaign", "value": "welcome"}])
)

welcome.to("jane@example.com").html("<p>Hi Jane</p>").send()
welcome.to("john@example.com").html("<p>Hi John</p>").send()
```

When you build an email over several statements, keep the returned builder:

```python
email = lettermint.emails.compose().from_("hello@acme.com").to(user.email).subject("Your invoice")
if user.accountant:
    email = email.cc(user.accountant)
email.html(invoice_html).send()
```

Builder methods:

| Method | Description |
| --- | --- |
| `from_(address)` | Sender, for example `Acme <hello@acme.com>` (`from` is a Python keyword). |
| `to(*addresses)`, `cc(...)`, `bcc(...)`, `reply_to(...)` | Replace the recipient list. |
| `subject(text)` | Subject line. |
| `html(html \| None)`, `text(text \| None)` | Bodies. `None` removes one. |
| `headers(mapping)` | Custom email headers. |
| `metadata(mapping)` | Data stored with the message, not added as headers. |
| `tags([{"name", "value"}])`, `tag(name \| None)` | Name/value tags, and the legacy single tag. |
| `route(slug)` | The route to send through. |
| `scheduled_at(when \| None)` | Delivery time: an aware `datetime`, ISO 8601, or English such as `tomorrow 9am`. |
| `settings({"track_opens", "track_clicks", "tls"})` | Per-email settings that override the route. |
| `sandbox_result(result)` | The result a Sandbox project simulates. |
| `attach(filename, content, *, content_type=None, content_id=None)` | Adds an attachment. |
| `send(*, idempotency_key=None, timeout=None)` | Sends a snapshot of the email. The builder can be sent again. |
| `build()` | Returns the message in the API's format. |

`emails.compose(message)` starts a builder from an existing message. With `AsyncLettermint`, `send()` is a coroutine.

### Plain dicts

`emails.send()` takes the message in the API's format (`reply_to`, `scheduled_at`, `sandbox_result`, …). It is typed as `EmailMessage`:

```python
lettermint.emails.send({
    "from": "Acme <hello@acme.com>",
    "to": ["jane@example.com"],
    "reply_to": ["support@acme.com"],
    "subject": "Your order has shipped",
    "html": html,
    "metadata": {"order_id": "1234"},
})
```

### Batch sending

Send up to 500 emails in one request. The list may mix messages and builders:

```python
results = lettermint.emails.send_batch([
    {"from": "hello@acme.com", "to": ["jane@example.com"], "subject": "Hi Jane", "text": "Hello"},
    welcome.to("john@example.com").html("<p>Hi John</p>"),
])
```

### Idempotency

Pass an idempotency key to make retries safe. The API processes a key once, so a retry with the same key does not send the email again. The key applies only to the call it is passed to.

```python
lettermint.emails.send(message, idempotency_key=f"order-{order.id}-confirmation")
builder.send(idempotency_key="welcome-jane")
lettermint.emails.send_batch(messages, idempotency_key="newsletter-2026-10")
```

The SDK never retries on its own.

### Scheduling

```python
from datetime import datetime, timedelta, timezone

result = (
    lettermint.emails.compose()
    .from_("hello@acme.com")
    .to("jane@example.com")
    .subject("Your trial ends tomorrow")
    .text("…")
    .scheduled_at(datetime.now(timezone.utc) + timedelta(days=1))
    .send()
)

if result["status"] == "scheduled":
    print(result["scheduled_at"])

lettermint.messages.reschedule(result["message_id"], {"scheduled_at": "2026-10-20T09:00:00Z"})
lettermint.messages.cancel(result["message_id"])
```

### Sandbox

In a Sandbox project, nothing is delivered. Choose the simulated result per email:

```python
result = (
    lettermint.emails.compose()
    .from_("hello@acme.com")
    .to("jane@example.com")
    .subject("Test")
    .text("Test")
    .sandbox_result("hard_bounced")
    .send()
)

print(result.get("sandbox"), result.get("sandbox_result"))  # True, "hard_bounced"
```

### Tags

`tags()` accepts up to 20 case-sensitive name/value tags (19 when the legacy `tag()` is also set). Names match `^[A-Za-z0-9_-]{1,32}$`, may not start with `__lettermint` and must be unique. Values match `^[A-Za-z0-9_-]{1,64}$`. The SDK checks this before the request and raises `LettermintValidationError`. Because builders are immutable, a rejected tag leaves the builder unchanged.

### Attachments

`content` is base64 text or bytes (`bytes`, `bytearray`, `memoryview`); the SDK base64-encodes bytes.

```python
from pathlib import Path

(
    lettermint.emails.compose()
    .from_("billing@acme.com")
    .to("jane@example.com")
    .subject("Your invoice")
    .html('<img src="cid:logo"> Your invoice is attached.')
    .attach("invoice.pdf", Path("invoice.pdf").read_bytes(), content_type="application/pdf")
    .attach("logo.png", logo_base64, content_id="logo")
    .send()
)
```

`lettermint.blocked_file_types()` lists the extensions and MIME types the API rejects.

## Team API

With a team token, the client manages domains, messages, projects, routes, statistics, suppressions, the team and webhooks:

```python
lettermint = Lettermint(team_token=os.environ["LETTERMINT_TEAM_TOKEN"])

domain = lettermint.domains.create({"domain": "acme.com"})
lettermint.domains.verify_dns_records(domain["id"])

project = lettermint.projects.create({"name": "Production"})
print(project["api_token"])  # the new project's sending token, shown once

stats = lettermint.stats.retrieve({"from": "2026-10-01", "to": "2026-10-31"})
html = lettermint.messages.html("message-id")
```

| Attribute | Methods |
| --- | --- |
| `domains` | `list`, `iterate`, `create`, `retrieve`, `delete`, `verify_dns_records`, `verify_dns_record`, `update_projects` |
| `messages` | `list`, `iterate`, `retrieve`, `events`, `iterate_events`, `source`, `html`, `text`, `reschedule`, `cancel`, `process` |
| `projects` | `list`, `iterate`, `create`, `retrieve`, `update`, `delete`, `rotate_token` |
| `projects.report_forwarding` | `retrieve`, `update`, `delete`, `verify`, `resend_code` |
| `routes` | `list(project_id)`, `iterate(project_id)`, `create(project_id, …)`, `retrieve`, `update`, `delete`, `verify_inbound_domain` |
| `stats` | `retrieve` |
| `suppressions` | `list`, `iterate`, `create`, `delete` |
| `team` | `retrieve`, `update`, `usage`, `roles` |
| `team.members` | `list`, `iterate`, `retrieve`, `update_assignment` |
| `webhooks` | `list`, `iterate`, `create`, `retrieve`, `update`, `delete`, `test`, `regenerate_secret` |
| `webhooks.deliveries` | `list(webhook_id)`, `iterate(webhook_id)`, `retrieve(webhook_id, delivery_id)` |
| (root) | `ping`, `analytics`, `blocked_file_types` |

### Query parameters and pagination

Query parameters are typed nested dicts. The SDK sends them in the API's bracket syntax (`page[size]=30&filter[status]=verified&sort=-created_at`):

```python
page = lettermint.domains.list({
    "page": {"size": 30},
    "filter": {"status": "verified"},
    "sort": ["-created_at"],
})

print(len(page["data"]), page["next_cursor"])
```

Every list has an `iterate()` method that follows `next_cursor` until the last page. It requests the next page only when you get to it, so you can stop early with `break`:

```python
for message in lettermint.messages.iterate({"filter": {"status": "hard_bounced"}}):
    print(message["id"], message["subject"])

async for delivery in async_lettermint.webhooks.deliveries.iterate(webhook_id):
    ...
```

### Timeouts and cancellation

Every method takes a keyword-only `timeout` in seconds that overrides the client's. With `AsyncLettermint`, cancelling the task (for example with `asyncio.timeout()` or a `trio` cancel scope) cancels the request; the SDK lets the cancellation through.

## Errors

Every exception the SDK raises is a `LettermintError`:

| Class | When | Attributes |
| --- | --- | --- |
| `APIError` | Any 4xx or 5xx response with a JSON (or empty) body | `status`, `code`, `message`, `details`, `body` |
| `AuthenticationError` | 401 | |
| `PermissionDeniedError` | 403 | |
| `NotFoundError` | 404 | |
| `ConflictError` | 409 | |
| `ValidationError` | 422 | `errors` (field errors) |
| `RateLimitError` | 429 | `retry_after` (seconds) |
| `ServerError` | 5xx | |
| `APITimeoutError` | No complete response within the timeout | `timeout` |
| `APIConnectionError` | The request failed (DNS, TLS, refused, reset) | |
| `UnexpectedResponseError` | An empty or non-JSON body where JSON was expected, or an error page such as a proxy's HTML 502 | `status`, `body_excerpt` |
| `RedirectError` | A 3xx response. Redirects are never followed, so tokens never go elsewhere. | `status` |
| `LettermintConfigError` | A missing or unrecognised token, an invalid option or ID | |
| `LettermintValidationError` | The SDK rejected the request before sending it, such as invalid tags | `field` |
| `WebhookVerificationError` | A webhook delivery is not genuine | `reason` |

The status classes are `APIError` subclasses. `code` and `message` come from the API's error body (`{"error": {"code", "message", "details"}}` or `{"message", "errors"}`).

```python
from lettermint import APIError, APITimeoutError, RateLimitError, ValidationError

try:
    lettermint.emails.send(message, idempotency_key=key)
except ValidationError as error:
    print(error.message, error.errors)
except RateLimitError as error:
    time.sleep(error.retry_after or 1)  # then retry with the same idempotency_key
except APITimeoutError:
    ...  # the outcome is unknown; retry with the same idempotency_key
except APIError as error:
    print(error.status, error.code, error.message)
```

`httpx` exceptions never escape: the SDK translates them, and its exceptions are not chained to them, because they hold the request and its headers. No exception contains a token.

## Webhooks

Verify each webhook delivery before you trust it. Use the webhook's signing secret (`whsec_…`), not an API token, and pass the **raw** request body: the signature covers the exact bytes, so parsing and re-serializing the JSON breaks it.

```python
from lettermint import Webhook, WebhookVerificationError

webhook = Webhook(os.environ["LETTERMINT_WEBHOOK_SECRET"])

event = webhook.verify(raw_body, headers)
print(event["event"], event["data"])
```

`verify(raw_body, headers)` takes the body as `str` or bytes, and the headers as any mapping (a `dict`, Django's `request.headers`, Flask, Starlette, `httpx.Headers`, an `email.message.Message`) or a list of `(name, value)` pairs, such as raw ASGI headers. It requires `X-Lettermint-Signature` and `X-Lettermint-Delivery` (header names are case-insensitive), checks the HMAC-SHA256 signature in constant time against every `v1` value, checks that the delivery timestamp equals the signed one and is within the tolerance, and returns the parsed payload. Otherwise it raises `WebhookVerificationError` with a `reason`: `signature_header_missing`, `signature_header_malformed`, `delivery_header_missing`, `delivery_timestamp_mismatch`, `timestamp_out_of_tolerance`, `signature_mismatch`, `body_invalid` or `payload_invalid`.

### Flask

```python
from flask import Flask, request

app = Flask(__name__)
webhook = Webhook(os.environ["LETTERMINT_WEBHOOK_SECRET"])

@app.post("/webhooks/lettermint")
def lettermint_webhook():
    try:
        event = webhook.verify(request.get_data(), request.headers)
    except WebhookVerificationError:
        return "Invalid signature", 400
    # Handle event["event"] and event["data"] here.
    return "", 204
```

### FastAPI and Starlette

```python
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()
webhook = Webhook(os.environ["LETTERMINT_WEBHOOK_SECRET"])

@app.post("/webhooks/lettermint", status_code=204)
async def lettermint_webhook(request: Request) -> None:
    try:
        event = webhook.verify(await request.body(), request.headers)
    except WebhookVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    # Handle event["event"] and event["data"] here.
```

### Django

```python
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

webhook = Webhook(os.environ["LETTERMINT_WEBHOOK_SECRET"])

@csrf_exempt
@require_POST
def lettermint_webhook(request):
    try:
        event = webhook.verify(request.body, request.headers)
    except WebhookVerificationError:
        return HttpResponseBadRequest("Invalid signature")
    # Handle event["event"] and event["data"] here.
    return HttpResponse(status=204)
```

### Options and lower-level verification

The default tolerance is 300 seconds in either direction. Change it with `Webhook(secret, tolerance=60)`. `0` accepts only the current second; it does not disable the check. A valid signature does not prevent a repeated delivery within the tolerance, so track `event["id"]` if you must not process an event twice.

If the headers are not at hand, call `webhook.verify_signature(raw_body, signature_header, delivery_header)`.

The payload is typed as `WebhookPayload`, with `event` as a `WebhookEvent` (`"message.delivered"`, `"message.hard_bounced"`, …). Unknown event names pass through as strings.

## Types

Request and response types are generated from the Lettermint API specification and live in `lettermint.types`, for example `SendMailRequest`, `SendMailResponse`, `DomainData`, `ListDomainsQuery` and `ListDomainsResponse` (a `CursorPage[DomainListData]`). Responses are plain dicts typed as `TypedDict`s: optional keys are `NotRequired`, nullable values include `None`. Enums are open (`Literal["pending", "delivered", ...] | str`), so values that the API adds later still type-check; give `match` statements a default case. The API's error bodies are `ApiErrorBody` and `ValidationErrorBody`.

## Requirements

- Python 3.10, 3.11, 3.12, 3.13 or 3.14 (tested in CI).
- `httpx` (0.27 up to 1.0), `anyio` and `typing_extensions`.

## Development

```bash
pip install -e ".[dev]"
ruff check src tests scripts && ruff format --check src tests scripts
mypy
pytest
```

The synchronous client in `src/lettermint/_sync/` is generated from the asynchronous one in `src/lettermint/_async/`: edit the async code, then run `python scripts/unasync.py`. Everything that differs for real (sending requests, the deadline) is in `src/lettermint/_transport.py`, and the I/O-free core is shared. `python scripts/unasync.py --check` runs in CI.

`src/lettermint/_generated/` is generated by the private [SDK generator](https://github.com/lettermint/sdk-generator). Do not edit it by hand. With a checkout of the generator, `python scripts/generate.py` regenerates the files and `python scripts/generate.py --check` verifies them; set `LETTERMINT_SDK_GENERATOR` to the checkout (default `../sdk-generator`). Without the generator, as in CI, `--check` only verifies the generated headers.

## License

MIT
