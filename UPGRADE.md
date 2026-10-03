# Upgrade guide

- [Upgrade from 2.x to 3.0](#upgrade-from-2x-to-30)
- [Upgrade from 1.x to 2.0](#upgrade-to-v2)

# Upgrade from 2.x to 3.0

2.x no longer receives updates, including fixes. Upgrade to 3.0 to keep getting them.

3.0 is a new major version. The main reason is safety: in 2.x, `client.email` returned one cached, mutable builder per client. Two emails composed at the same time on one client (two threads, or two requests in a web app) could mix recipients, content and the `Idempotency-Key`, and an email abandoned halfway (for example because `tags()` raised) leaked into the next send. 3.0 stores nothing about a message on the client.

## Highlights

- One client per mode with the same methods: `Lettermint` and `AsyncLettermint`. They take `sending_token` and/or `team_token`, or one token string. They replace `Lettermint.email()`, `Lettermint.api()`, `ApiClient` and `AsyncApiClient`.
- Sending is stateless: `emails.send(message, idempotency_key=...)`, `emails.send_batch(messages, ...)` and an immutable `emails.compose()` builder. The `Idempotency-Key` is a per-call argument.
- Each part uses its own token: `emails` uses the sending token, the Team API the team token. The SDK never falls back to the other token.
- Typed exceptions for every outcome. `httpx` exceptions never escape, so no exception carries the request or its token.
- Redirects are never followed, so tokens are never sent to another host. The timeout covers the whole request, including the body.
- Tokens never appear in `repr()`, `vars()`, logs or pickles.
- Webhook verification requires both signature headers, accepts any `v1` signature, takes the body first and reports a `reason`.
- Typed nested query objects (`{"page": {"size": 30}}`) and `iterate()` generators that follow `next_cursor`.
- Types are generated from the current API specification and use its names (see [Type names](#type-names)). Enums are open: `Literal[...] | str`.
- Python 3.10 or newer. Python 3.9 reached end of life in October 2025.

## Requirements

- Python 3.10 or newer.
- `httpx` 0.27 or newer (below 1.0), `anyio` 3.5 or newer and `typing_extensions` 4.7 or newer. `anyio` already comes with `httpx`.

## Upgrade with a coding agent

You can let a coding agent (Claude Code, Codex, Cursor, Copilot, ...) do the upgrade. Copy this instruction into the agent from your project's root, then review its changes:

````text
Upgrade this project from the `lettermint` Python SDK 2.x to 3.0.

1. Install `lettermint>=3,<4` with the project's package manager (pip, uv, Poetry, PDM, ...) and update the lock file. 3.0 needs Python 3.10 or newer: check `requires-python`, CI workflows, Dockerfiles and runtime files, and report anything older.
2. Read the upgrade guide before changing code: `UPGRADE.md` inside the installed package (print its path with `python -c "import importlib.resources as r; print(r.files('lettermint') / 'UPGRADE.md')"`), or https://github.com/lettermint/lettermint-python/blob/main/UPGRADE.md. Treat it as the source of truth and don't guess APIs; when unsure, read the installed package (`lettermint/__init__.py`, `lettermint/_sync/`, `lettermint/types.py`).
3. Find every use of the SDK: `import lettermint`, `from lettermint`, `Lettermint(`, `AsyncLettermint(`, `Lettermint.email(`, `Lettermint.api(`, `api_token=`, `.email.`, `.idempotency_key(`, `.attach(`, `.send_batch(`, `Webhook`, `verify_headers(`, `verify_signature(`, `MessageTag`, `lettermint.exceptions`, the 2.x exception classes and the 2.x type names from the guide's type-name table.
4. Rewrite each use following the guide's before/after examples:
   - Create one client with `Lettermint(sending_token=...)` (or `AsyncLettermint` in async code), adding `team_token=...` only where the Team API is used. Keep the project's existing environment variable names. Create it once and reuse it; close it at shutdown or use it as a context manager.
   - Replace builder chains on `client.email` with `client.emails.send({...})`, or with `client.emails.compose()` per email. Builders are immutable: assign the result of every setter. Never keep a half-built email in module scope.
   - Move idempotency keys into `send(..., idempotency_key=...)` / `send_batch(..., idempotency_key=...)`. Attachments: `.attach(filename, content, content_type=..., content_id=...)`, with keyword arguments; bytes are encoded by the SDK.
   - Team API: use the same client (`client.domains`, ...), nested query dicts instead of `"page[size]"`-style keys, and the renamed methods from the guide.
   - Errors: switch to the 3.0 classes (`APIError`, `ValidationError`, `RateLimitError`, `APITimeoutError`, `APIConnectionError`, ...). Rename `status_code` to `status` and `response_body` to `body`.
   - Webhooks: `Webhook(secret).verify(raw_body, headers)`. Keep passing the raw request body, keep the secret's `whsec_` prefix, and make sure the `X-Lettermint-Signature` and `X-Lettermint-Delivery` headers reach the handler.
   - Rename types using the guide's type-name table.
5. Run the type checker (mypy or pyright), the linter and the tests, and fix every error. Don't send real email or call the live API while testing.
6. Finish with a summary: the files you changed, anything you could not migrate with certainty, and behaviour changes I should review.

Never print, log or commit API tokens or webhook secrets.
````

## Create the client

`Lettermint.email()`, `Lettermint.api()`, `AsyncLettermint.email()`, `AsyncLettermint.api()`, `ApiClient`, `AsyncApiClient`, the `api_token` argument and the `client.email` attribute are removed.

```python
# 2.x
from lettermint import Lettermint

email = Lettermint.email(os.environ["LETTERMINT_PROJECT_TOKEN"], timeout=10.0)
api = Lettermint.api(os.environ["LETTERMINT_TEAM_TOKEN"])
legacy = Lettermint(api_token=os.environ["LETTERMINT_PROJECT_TOKEN"])

# 3.0
from lettermint import Lettermint

lettermint = Lettermint(
    sending_token=os.environ["LETTERMINT_PROJECT_TOKEN"],  # for lettermint.emails
    team_token=os.environ["LETTERMINT_TEAM_TOKEN"],  # for the Team API
    timeout=10.0,
)
```

```python
# 2.x
from lettermint import AsyncLettermint

email = AsyncLettermint.email(token)
api = AsyncLettermint.api(team_token)

# 3.0
from lettermint import AsyncLettermint

lettermint = AsyncLettermint(sending_token=token, team_token=team_token)
```

Pass one token or both. With only one token, calling a part that needs the other raises `LettermintConfigError` (for example `domains.list needs team_token; pass Lettermint(team_token=...).`) before any request.

You can also pass one token string as the first argument. The SDK picks the token type by its format: `lm_team_` followed by letters and digits is a team token, any other `lm_` followed by letters and digits is a sending token:

```python
lettermint = Lettermint("lm_team_...")  # team token
lettermint = Lettermint("lm_...")  # project sending token
lettermint = Lettermint(token, timeout=10.0)  # with options
```

Any other format (SSO tokens, OAuth tokens, an empty string) raises `LettermintConfigError`; pass `sending_token=` or `team_token=` for those. Passing a token string and `sending_token`/`team_token` together is also an error.

`base_url` and `timeout` (seconds) work as before. `http_client` is new: an `httpx.Client` (or `httpx.AsyncClient` for `AsyncLettermint`) to send requests with, for example for a proxy. The SDK does not close a client it did not create.

### Closing the client

The client owns an HTTP connection pool. Create it once and share it; it holds no per-email state. `close()` and the context managers work as before, and close only the client itself (in 2.x, the context manager of an endpoint closed the shared HTTP client):

```python
# 2.x
with Lettermint(api_token=token) as client:
    client.email.from_("hello@acme.com").to("jane@example.com").subject("Hi").send()

# 3.0
with Lettermint(sending_token=token) as lettermint:
    lettermint.emails.compose().from_("hello@acme.com").to("jane@example.com").subject("Hi").send()

async with AsyncLettermint(sending_token=token) as lettermint:
    await lettermint.emails.send({"from": "hello@acme.com", "to": ["jane@example.com"], "subject": "Hi"})
```

After `close()`, calls raise `LettermintConfigError`.

## Send an email

The 2.x builder lived on the client and was reset after each send. In 3.0, `emails.compose()` returns an immutable builder: each setter returns a new builder and leaves the old one unchanged. Chaining works as before. If you built an email over several statements, assign the result of each setter.

```python
# 2.x
client = Lettermint(api_token=token)
response = (
    client.email
    .from_("Acme <hello@acme.com>")
    .to("jane@example.com")
    .subject("Welcome")
    .html("<p>Hi Jane</p>")
    .idempotency_key("welcome-jane")
    .send()
)

# 3.0: builder
response = (
    lettermint.emails.compose()
    .from_("Acme <hello@acme.com>")
    .to("jane@example.com")
    .subject("Welcome")
    .html("<p>Hi Jane</p>")
    .send(idempotency_key="welcome-jane")
)

# 3.0: a plain dict in the API's format
response = lettermint.emails.send(
    {"from": "Acme <hello@acme.com>", "to": ["jane@example.com"], "subject": "Welcome", "html": "<p>Hi Jane</p>"},
    idempotency_key="welcome-jane",
)
```

```python
# 2.x: statements changed the shared builder
email = client.email
email.from_("hello@acme.com")
email.to("jane@example.com")
if copy:
    email.cc("team@acme.com")
email.subject("Hi").send()

# 3.0: keep the returned builder
draft = lettermint.emails.compose().from_("hello@acme.com").to("jane@example.com")
if copy:
    draft = draft.cc("team@acme.com")
draft.subject("Hi").send()
```

A base builder can now be shared safely, also between threads and tasks:

```python
welcome = lettermint.emails.compose().from_("Acme <hello@acme.com>").subject("Welcome")
welcome.to("jane@example.com").html(jane_html).send()
welcome.to("john@example.com").html(john_html).send(idempotency_key="welcome-john")
```

In `AsyncLettermint`, `send()` is a coroutine: `await builder.send()`. The setters are the same.

### Changed builder methods

| 2.x | 3.0 |
| --- | --- |
| `client.email.from_(x)` and the other setters change the client's builder and return it | Return a new builder: `lettermint.emails.compose().from_(x)` |
| `.idempotency_key(key).send()` | `.send(idempotency_key=key)` |
| `.attach(filename, content, content_id=None, content_type=None)` (base64 text) | `.attach(filename, content, *, content_type=None, content_id=None)`; `content` may also be `bytes`. `content_type` and `content_id` are keyword-only, so a 2.x call with positional `content_id` raises `TypeError` instead of swapping them. |
| `.html(None)`, `.text(None)` were ignored | `None` removes the field; so do `tag(None)` and `scheduled_at(None)` |
| `.scheduled_at(str)` | `.scheduled_at(str \| datetime)`; a datetime must be timezone-aware |
| `.tags()` / `.tag()` raised `ValueError` | They raise `LettermintValidationError` (with `field`) and leave the builder unchanged |
| `.tags([MessageTag(name=..., value=...)])` | `.tags([{"name": ..., "value": ...}])` |
| `.send()` | `.send(idempotency_key=None, timeout=None)`; the builder can be sent again |
| `.send_batch(payload)` on the builder | `lettermint.emails.send_batch(messages)` |
| `.ping()` on the builder | `lettermint.emails.ping()` |
| — | `.build()` returns the message in the API's format |

Unchanged setters: `to`, `cc`, `bcc`, `reply_to` (each replaces its list), `subject`, `headers`, `metadata`, `route`, `settings`, `tag`, `sandbox_result`.

Attachment content is base64-encoded by the SDK when you pass bytes:

```python
# 2.x
content = base64.b64encode(pdf_bytes).decode()
client.email.attach("invoice.pdf", content, None, "application/pdf")
client.email.attach("logo.png", logo_base64, "logo")

# 3.0
builder = builder.attach("invoice.pdf", pdf_bytes, content_type="application/pdf")
builder = builder.attach("logo.png", logo_base64, content_id="logo")
```

### Tags

`MessageTag` (the 2.x frozen dataclass that validated on construction) is removed. Tags are dicts, validated before the request by `tags()`, `send()` and `send_batch()`. `lettermint.types.MessageTag` is now the generated type of tags in responses, and `MessageTagInput` the type of tags you send; both are `TypedDict`s, so `MessageTag(name="campaign", value="welcome")` still builds the same dict.

```python
# 2.x
from lettermint import MessageTag
client.email.tags([MessageTag(name="campaign", value="welcome")])

# 3.0
builder = builder.tags([{"name": "campaign", "value": "welcome"}])
```

## Batch sending and ping

```python
# 2.x
Lettermint.email(token).idempotency_key("batch-1").send_batch([message1, message2])
Lettermint.email(token).ping()
Lettermint.api(team_token).ping()

# 3.0
lettermint.emails.send_batch([message1, message2], idempotency_key="batch-1")
lettermint.emails.send_batch([builder1, builder2])  # builders work too
lettermint.emails.ping()  # sending token
lettermint.ping()  # team token if configured, otherwise the sending token
```

`send_batch()` validates the tags of every message and names the bad one (`messages[2].tags`).

## Team API

The sub-clients move from `Lettermint.api(token).x` to `lettermint.x`. Query parameters are nested dicts instead of `dict[str, str]` with bracket keys. Request bodies are the first argument after the IDs (named `body`, 2.x: `data`). Every list also has an `iterate()` generator that follows `next_cursor`, and every method takes a keyword-only `timeout`.

```python
# 2.x
api = Lettermint.api(team_token)
page = api.domains.list({"page[size]": "10", "filter[status]": "verified"})

# 3.0
lettermint = Lettermint(team_token=team_token)
page = lettermint.domains.list({"page": {"size": 10}, "filter": {"status": "verified"}})
for domain in lettermint.domains.iterate({"filter": {"status": "verified"}}):
    print(domain["domain"])

# 3.0, async
async for domain in async_lettermint.domains.iterate({"filter": {"status": "verified"}}):
    print(domain["domain"])
```

| 2.x (`api = Lettermint.api(token)`) | 3.0 (`lettermint = Lettermint(team_token=...)`) |
| --- | --- |
| `api.ping()` | `lettermint.ping()` |
| `api.blocked_file_types()` | `lettermint.blocked_file_types()` |
| `api.analytics(data)` | `lettermint.analytics(query)` |
| `api.close()`, `with api:` | `lettermint.close()`, `with lettermint:` |
| `api.domains.list(query)` | `lettermint.domains.list(query)`, `lettermint.domains.iterate(query)` |
| `api.domains.create(data)` | `lettermint.domains.create(body)` |
| `api.domains.retrieve(domain_id, query)` | `lettermint.domains.retrieve(domain_id, query)` (`{"include": ["dnsRecords"]}`) |
| `api.domains.delete(domain_id)` | `lettermint.domains.delete(domain_id)` |
| `api.domains.verify_dns_records(domain_id)` | `lettermint.domains.verify_dns_records(domain_id)` |
| `api.domains.verify_dns_record(domain_id, record_id)` | `lettermint.domains.verify_dns_record(domain_id, record_id)` |
| `api.domains.update_projects(domain_id, data)` | `lettermint.domains.update_projects(domain_id, body)` |
| `api.messages.list(query)` | `lettermint.messages.list(query)`, `lettermint.messages.iterate(query)` |
| `api.messages.retrieve(message_id, query)` | `lettermint.messages.retrieve(message_id)` (the endpoint takes no query) |
| `api.messages.events(message_id, query)` | `lettermint.messages.events(message_id, query)`, `lettermint.messages.iterate_events(message_id, query)` |
| `api.messages.source(id)` / `.html(id)` / `.text(id)` | unchanged, on `lettermint.messages` |
| `api.messages.reschedule(message_id, data)` | `lettermint.messages.reschedule(message_id, body)` |
| `api.messages.cancel(message_id)` | `lettermint.messages.cancel(message_id)` |
| `api.messages.process(message_id)` | `lettermint.messages.process(message_id, idempotency_key=None)` |
| `api.projects.list(query)` | `lettermint.projects.list(query)`, `lettermint.projects.iterate(query)` |
| `api.projects.create(data)` | `lettermint.projects.create(body)` |
| `api.projects.retrieve(project_id, query)` | `lettermint.projects.retrieve(project_id, query)` |
| `api.projects.update(project_id, data)` | `lettermint.projects.update(project_id, body)` |
| `api.projects.delete(project_id)` | `lettermint.projects.delete(project_id)` |
| `api.projects.rotate_token(project_id)` | `lettermint.projects.rotate_token(project_id)` (deprecated by the API) |
| `api.projects.routes(project_id, query)` | `lettermint.routes.list(project_id, query)`, `lettermint.routes.iterate(project_id, query)` |
| `api.projects.create_route(project_id, data)` | `lettermint.routes.create(project_id, body)` |
| `api.projects.retrieve_report_forwarding(project_id)` | `lettermint.projects.report_forwarding.retrieve(project_id)` |
| `api.projects.update_report_forwarding(project_id, data)` | `lettermint.projects.report_forwarding.update(project_id, body)` |
| `api.projects.delete_report_forwarding(project_id)` | `lettermint.projects.report_forwarding.delete(project_id)` |
| `api.projects.verify_report_forwarding(project_id, data)` | `lettermint.projects.report_forwarding.verify(project_id, body)` |
| `api.projects.resend_report_forwarding_code(project_id)` | `lettermint.projects.report_forwarding.resend_code(project_id)` |
| `api.routes.retrieve(route_id, query)` | `lettermint.routes.retrieve(route_id, query)` |
| `api.routes.update(route_id, data)` | `lettermint.routes.update(route_id, body)` |
| `api.routes.delete(route_id)` | `lettermint.routes.delete(route_id)` |
| `api.routes.verify_inbound_domain(route_id)` | `lettermint.routes.verify_inbound_domain(route_id)` |
| `api.stats.retrieve(query)` | `lettermint.stats.retrieve({"from": ..., "to": ..., "project_id": ..., "include_machine": ...})` (`from` and `to` are required) |
| `api.suppressions.list(query)` | `lettermint.suppressions.list(query)`, `lettermint.suppressions.iterate(query)` |
| `api.suppressions.create(data)` | `lettermint.suppressions.create(body)` |
| `api.suppressions.delete(suppression_id)` | `lettermint.suppressions.delete(suppression_id)` |
| `api.team.retrieve(query)` | `lettermint.team.retrieve(query)` (`{"include": ["features"]}`) |
| `api.team.update(data)` | `lettermint.team.update(body)` |
| `api.team.usage()` | `lettermint.team.usage()` |
| `api.team.roles()` | `lettermint.team.roles()` |
| `api.team.members(query)` | `lettermint.team.members.list(query)`, `lettermint.team.members.iterate(query)` |
| `api.team.member(user_id)` | `lettermint.team.members.retrieve(user_id)` |
| `api.team.update_member_assignment(user_id, data)` | `lettermint.team.members.update_assignment(user_id, body)` |
| `api.webhooks.list(query)` | `lettermint.webhooks.list(query)`, `lettermint.webhooks.iterate(query)` |
| `api.webhooks.create(data)` | `lettermint.webhooks.create(body)` |
| `api.webhooks.retrieve(webhook_id)` | `lettermint.webhooks.retrieve(webhook_id)` |
| `api.webhooks.update(webhook_id, data)` | `lettermint.webhooks.update(webhook_id, body)` |
| `api.webhooks.delete(webhook_id)` | `lettermint.webhooks.delete(webhook_id)` |
| `api.webhooks.test(webhook_id)` | `lettermint.webhooks.test(webhook_id)` |
| `api.webhooks.regenerate_secret(webhook_id)` | `lettermint.webhooks.regenerate_secret(webhook_id)` |
| `api.webhooks.deliveries(webhook_id, query)` | `lettermint.webhooks.deliveries.list(webhook_id, query)`, `lettermint.webhooks.deliveries.iterate(webhook_id, query)` |
| `api.webhooks.delivery(webhook_id, delivery_id)` | `lettermint.webhooks.deliveries.retrieve(webhook_id, delivery_id)` |

The async client has the same methods; `await` them, and use `async for` with `iterate()`.

`messages.reschedule()` and `messages.cancel()` accept either token: the team token when configured, otherwise the sending token. This lets a sending-only client cancel the scheduled email it sent.

### Query parameters

Write bracketed names as nested dicts. Lists of values are joined with commas, lists of dicts are indexed, booleans are sent as `1`/`0` and `None` values are left out. The query types (`ListDomainsQuery`, ...) are in `lettermint.types`.

| 2.x | 3.0 |
| --- | --- |
| `{"page[size]": "30", "page[cursor]": c}` | `{"page": {"size": 30, "cursor": c}}` |
| `{"filter[status]": "verified"}` | `{"filter": {"status": "verified"}}` |
| `{"sort": "-created_at,domain"}` | `{"sort": ["-created_at", "domain"]}` |
| `{"filter[tags][0][name]": "a", "filter[tags][0][value]": "b"}` | `{"filter": {"tags": [{"name": "a", "value": "b"}]}}` |
| `{"filter[enabled]": "true"}` | `{"filter": {"enabled": True}}` |
| webhooks: `{"cursor": c}` | unchanged: `{"cursor": c}` (these lists use `cursor`, not `page[cursor]`) |

### Path parameters

IDs are still URL-encoded. An empty ID, `"."` or `".."` now raises `LettermintConfigError` before the request.

### Message lists

The 2.x types described message and event lists with a nested `meta` object. The API returns a flat cursor page, which 3.0 types as `CursorPage[T]`: read `page["next_cursor"]`, not `page["meta"]["next_cursor"]`. Or use `iterate()`.

## Errors

`HttpRequestError`, `ClientError`, `TimeoutError`, `InvalidSignatureError`, `TimestampToleranceError` and `JsonDecodeError` are removed. Every exception the SDK raises is a `LettermintError`, and raw `httpx` exceptions (and `json.JSONDecodeError`) no longer escape. The 3.0 classes avoid the names of Python's built-in `TimeoutError`, `ConnectionError` and `PermissionError`.

| Situation | 2.x | 3.0 |
| --- | --- | --- |
| HTTP 400 | `ClientError` (`status_code`, `response_body`) | `APIError` (`status`, `code`, `message`, `details`, `body`) |
| HTTP 401 | `HttpRequestError` | `AuthenticationError` |
| HTTP 403 | `HttpRequestError` | `PermissionDeniedError` |
| HTTP 404 | `HttpRequestError` | `NotFoundError` |
| HTTP 409 | `HttpRequestError` | `ConflictError` |
| HTTP 422 | `ValidationError` (`status_code`, `error_type`, `response_body`) | `ValidationError` (`status`, `code`, `errors`, `body`) |
| HTTP 429 | `HttpRequestError` | `RateLimitError` (`retry_after` in seconds) |
| HTTP 5xx | `HttpRequestError` | `ServerError` |
| Other 4xx | `HttpRequestError` | `APIError` |
| 2xx with an empty or invalid JSON body | `json.JSONDecodeError` | `UnexpectedResponseError` (`status`, `body_excerpt`) |
| Error page that is not JSON (a proxy's HTML 502) | `HttpRequestError` | `UnexpectedResponseError` |
| Redirect (3xx) | followed, with the token | `RedirectError` (`status`); never followed |
| Timeout | `lettermint.TimeoutError` | `APITimeoutError` (`timeout`); covers the whole request |
| Network failure (DNS, TLS, refused, reset) | raw `httpx.ConnectError` and friends, carrying the request and its token header | `APIConnectionError`, not chained to the `httpx` exception |
| Invalid tags, idempotency key or body | `ValueError` | `LettermintValidationError` (`field`) |
| Missing or wrong token, bad option or ID | — | `LettermintConfigError` |

Property renames: `status_code` → `status`, `response_body` → `body`, `error_type` → `code`. `code` comes from `{"error": {"code"}}`, or from a string `error` field. `message` is the API's message, or the HTTP reason phrase. The status classes (`AuthenticationError`, ..., `ServerError`) are `APIError` subclasses, so `except APIError` catches them all.

```python
# 2.x
from lettermint.exceptions import ClientError, HttpRequestError, TimeoutError, ValidationError

try:
    client.email.from_(sender).to(recipient).subject("Hi").send()
except ValidationError as e:
    print(e.status_code, e.error_type, e.response_body)
except HttpRequestError as e:
    if e.status_code == 429:
        retry_later()
except TimeoutError:
    ...

# 3.0
from lettermint import APIError, APITimeoutError, RateLimitError, ValidationError

try:
    lettermint.emails.send(message, idempotency_key=key)
except ValidationError as e:
    print(e.status, e.code, e.errors)
except RateLimitError as e:
    retry_later(e.retry_after)
except APITimeoutError:
    ...  # the outcome is unknown; retry with the same idempotency_key
except APIError as e:
    print(e.status, e.code, e.message)
```

The SDK does not retry requests. Pass an `idempotency_key` when you retry a send. Cancelling an `asyncio` or `trio` task cancels its request; the SDK lets the cancellation through unchanged.

Exceptions can be pickled (for Celery or `multiprocessing`); clients, builders and webhook verifiers cannot, because they hold credentials.

## Webhooks

`verify()` now takes the raw body first and the request headers second, and replaces `verify_headers()`. The 2.x `verify(payload, signature, timestamp)` is now `verify_signature()`, an instance method. The static `Webhook.verify_signature(payload, signature, secret, ...)` is removed.

```python
# 2.x
webhook = Webhook(secret)
payload = webhook.verify_headers(request.headers, request.body)
payload = webhook.verify(request.body, signature_header, int(delivery_header))
payload = Webhook.verify_signature(request.body, signature_header, secret)

# 3.0
webhook = Webhook(secret)
event = webhook.verify(request.body, request.headers)
event = webhook.verify_signature(request.body, signature_header, delivery_header)
```

- The body may be `str` or bytes (`bytes`, `bytearray`, `memoryview`). Pass it raw; parsed JSON raises `WebhookVerificationError` with reason `body_invalid`.
- The headers may be any mapping (a `dict`, Django `request.headers`, Flask, Starlette, `httpx.Headers`, an `email.message.Message`) or `(name, value)` pairs such as the raw ASGI headers. Names are case-insensitive.
- Both `X-Lettermint-Signature` and `X-Lettermint-Delivery` are required, and the delivery header must equal the signed timestamp. 2.x accepted a delivery without `X-Lettermint-Delivery` in `verify()`.
- Any `v1` signature in the header may match (2.x checked only the last one), so key rotation works.
- The tolerance applies in both directions (`|now - t| <= tolerance`).
- Malformed or non-ASCII signature headers raise `WebhookVerificationError` instead of crashing.
- `WebhookVerificationError` has a `reason`: `signature_header_missing`, `signature_header_malformed`, `delivery_header_missing`, `delivery_timestamp_mismatch`, `timestamp_out_of_tolerance`, `signature_mismatch`, `body_invalid` or `payload_invalid`. `InvalidSignatureError`, `TimestampToleranceError` and `JsonDecodeError` map to `signature_mismatch`, `timestamp_out_of_tolerance` and `payload_invalid`.
- An empty secret or a negative or non-integer `tolerance` raises `LettermintConfigError` (2.x: `ValueError` for an empty secret).
- The return value is typed as `WebhookPayload` (`event`, `data`, `id`, `timestamp`; other keys are kept).
- `lettermint.webhook.SIGNATURE_HEADER` and `DELIVERY_HEADER` are now lower case.

## Type names

The types are generated from the API specification of lettermint#2582 and use its names. Import them from `lettermint.types`; the package root exports only `CursorPage`, `EmailMessage` and `EmailAttachment`. Types not listed below keep their name. Some shapes also changed:

- Enums are open: `MessageStatus` is `Literal["pending", ...] | str`, so values the API adds later still type-check. Give `match` statements a default case.
- `SendMailResponse` is `PendingSendMailResponse | ScheduledSendMailResponse`; narrow on `status`.
- `MessageTag` describes tags in responses; `MessageTagInput` describes tags you send.
- Message and event lists are `CursorPage[T]` (see [Message lists](#message-lists)).
- Query parameters have types of their own, nested as the SDK sends them: `ListDomainsQuery`, `ListDomainsQueryPage`, `ListDomainsQueryFilter`, ...
- The API's error bodies are `ApiErrorBody` and `ValidationErrorBody`, because `APIError` and `ValidationError` are exception classes.
- `TypedDict`s set `__required_keys__` correctly at runtime.

| 2.x (`lettermint.types`) | 3.0 (`lettermint.types`) |
| --- | --- |
| `AnalyticsRequest` | `AnalyticsQuery` |
| `AnalyticsRequestFiltersItem` | `AnalyticsFilter` |
| `AnalyticsRequestSort` | `AnalyticsSort` |
| `AnalyticsResponseMeta` | `AnalyticsMeta` |
| `AnalyticsResponseMetaComparison` | `AnalyticsMetaComparison` |
| `AnalyticsResponsePagination` | `AnalyticsPagination` |
| `AnalyticsResponsePayload` | `AnalyticsResults` |
| `AnalyticsResponsePayloadBreakdownItem` | `AnalyticsBreakdownRow` |
| `AnalyticsResponsePayloadBreakdownItemMetrics` | `AnalyticsMetricValues` |
| `AnalyticsResponsePayloadBreakdownItemPrevious` | `AnalyticsComparisonValues` |
| `AnalyticsResponsePayloadBreakdownItemPreviousMetrics` | `AnalyticsMetricValues` |
| `AnalyticsResponsePayloadBreakdownItemPreviousRateBases` | `AnalyticsRateBases` |
| `AnalyticsResponsePayloadBreakdownItemPreviousRateBasesBounceRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemPreviousRateBasesComplaintRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemPreviousRateBasesDeferralRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemPreviousRateBasesDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemPreviousRateBasesEffectiveDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemPreviousRateBasesHumanClickRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemPreviousRateBasesHumanOpenRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemRateBases` | `AnalyticsRateBases` |
| `AnalyticsResponsePayloadBreakdownItemRateBasesBounceRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemRateBasesComplaintRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemRateBasesDeferralRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemRateBasesDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemRateBasesEffectiveDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemRateBasesHumanClickRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemRateBasesHumanOpenRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItem` | `AnalyticsTimeSeriesPoint` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemMetrics` | `AnalyticsMetricValues` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemPrevious` | `AnalyticsComparisonValues` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemPreviousMetrics` | `AnalyticsMetricValues` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBases` | `AnalyticsRateBases` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesBounceRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesComplaintRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesDeferralRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesEffectiveDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesHumanClickRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesHumanOpenRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemRateBases` | `AnalyticsRateBases` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesBounceRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesComplaintRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesDeferralRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesEffectiveDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesHumanClickRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesHumanOpenRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummary` | `AnalyticsSummary` |
| `AnalyticsResponsePayloadSummaryMetrics` | `AnalyticsMetricValues` |
| `AnalyticsResponsePayloadSummaryPrevious` | `AnalyticsComparisonValues` |
| `AnalyticsResponsePayloadSummaryPreviousMetrics` | `AnalyticsMetricValues` |
| `AnalyticsResponsePayloadSummaryPreviousRateBases` | `AnalyticsRateBases` |
| `AnalyticsResponsePayloadSummaryPreviousRateBasesBounceRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryPreviousRateBasesComplaintRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryPreviousRateBasesDeferralRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryPreviousRateBasesDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryPreviousRateBasesEffectiveDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryPreviousRateBasesHumanClickRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryPreviousRateBasesHumanOpenRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryRateBases` | `AnalyticsRateBases` |
| `AnalyticsResponsePayloadSummaryRateBasesBounceRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryRateBasesComplaintRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryRateBasesDeferralRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryRateBasesDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryRateBasesEffectiveDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryRateBasesHumanClickRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadSummaryRateBasesHumanOpenRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItem` | `AnalyticsTimeSeriesPoint` |
| `AnalyticsResponsePayloadTimeSeriesItemMetrics` | `AnalyticsMetricValues` |
| `AnalyticsResponsePayloadTimeSeriesItemPrevious` | `AnalyticsComparisonValues` |
| `AnalyticsResponsePayloadTimeSeriesItemPreviousMetrics` | `AnalyticsMetricValues` |
| `AnalyticsResponsePayloadTimeSeriesItemPreviousRateBases` | `AnalyticsRateBases` |
| `AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesBounceRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesComplaintRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesDeferralRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesEffectiveDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesHumanClickRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesHumanOpenRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemRateBases` | `AnalyticsRateBases` |
| `AnalyticsResponsePayloadTimeSeriesItemRateBasesBounceRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemRateBasesComplaintRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemRateBasesDeferralRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemRateBasesDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemRateBasesEffectiveDeliveryRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemRateBasesHumanClickRate` | `AnalyticsRateBase` |
| `AnalyticsResponsePayloadTimeSeriesItemRateBasesHumanOpenRate` | `AnalyticsRateBase` |
| `BlockedFileTypesResponse` | `BlockedFileTypes` |
| `CancelScheduledMessageResponse` | `ScheduledMessage` |
| `CursorPaginator` | `CursorPage[T]` (generic) |
| `DomainDestroyResponse` | `MessageResponse` |
| `DomainIndexResponse` | `ListDomainsResponse` |
| `DomainShowResponse` | `DomainData` |
| `DomainStoreRequest` | `StoreDomainData` |
| `DomainStoreResponse` | `DomainData` |
| `DomainUpdateProjectsRequest` | `UpdateDomainProjectsData` |
| `DomainUpdateProjectsResponse` | `DomainMutationResponse` |
| `DomainVerifyDnsRecordsResponse` | `DnsVerificationSuccessResponse` |
| `DomainVerifySpecificDnsRecordResponse` | `MessageResponse` |
| `EmailAttachment` | `MessageAttachmentInput` (wire format), or `lettermint.EmailAttachment` (content may be bytes) |
| `EmailPayload` | `SendMailRequest`, or `lettermint.EmailMessage` (attachment content may be bytes) |
| `EmailStatus` | `MessageStatus` |
| `MessageEventsResponse` | `ListMessageEventsResponse` |
| `MessageIndexResponse` | `ListMessagesResponse` |
| `MessageShowResponse` | `MessageData` |
| `ProjectDestroyResponse` | `MessageResponse` |
| `ProjectIndexResponse` | `ListProjectsResponse` |
| `ProjectRotateTokenResponse` | `RotateProjectTokenResponse` |
| `ProjectShowResponse` | `ProjectData` |
| `ProjectStoreRequest` | `StoreProjectData` |
| `ProjectStoreResponse` | `ProjectCreatedData` |
| `ProjectUpdateRequest` | `UpdateProjectData` |
| `ProjectUpdateResponse` | `ProjectMutationResponse` |
| `RescheduleMessageResponse` | `ScheduledMessage` |
| `RouteDestroyResponse` | `MessageResponse` |
| `RouteIndexResponse` | `ListRoutesResponse` |
| `RouteShowResponse` | `RouteData` |
| `RouteStoreRequest` | `StoreRouteData` |
| `RouteStoreResponse` | `RouteMutationResponse` |
| `RouteUpdateRequest` | `UpdateRouteData` |
| `RouteUpdateResponse` | `RouteMutationResponse` |
| `RouteVerifyInboundDomainResponse` | `InboundDomainVerificationResponse` |
| `SendBatchEmailResponse` | `SendBatchMailResponse` |
| `SendEmailResponse` | `SendMailResponse` (`PendingSendMailResponse \| ScheduledSendMailResponse`) |
| `StatsIndexResponse` | `StatsData` |
| `SuppressionDestroyResponse` | `DeleteSuppressionResponse` |
| `SuppressionIndexResponse` | `ListSuppressionsResponse` |
| `SuppressionStoreRequest` | `StoreSuppressionData` |
| `TeamMembersAssignmentUpdateRequest` | `UpdateTeamMemberAssignmentData` |
| `TeamMembersAssignmentUpdateResponse` | `TeamMemberData` |
| `TeamMembersResponse` | `ListTeamMembersResponse` |
| `TeamMembersShowResponse` | `TeamMemberData` |
| `TeamRolesResponse` | `TeamRoleListResponse` |
| `TeamShowResponse` | `TeamData` |
| `TeamUpdateRequest` | `UpdateTeamData` |
| `TeamUpdateResponse` | `TeamMutationResponse` |
| `TeamUsageResponse` | `TeamUsageDetailData` |
| `UpdateReportForwardingRequest` | `ReportForwardingRequest` |
| `WebhookDeliveriesResponse` | `ListWebhookDeliveriesResponse` |
| `WebhookDestroyResponse` | `MessageResponse` |
| `WebhookIndexResponse` | `ListWebhooksResponse` |
| `WebhookRegenerateSecretResponse` | `WebhookSecretResponse` |
| `WebhookShowDeliveryResponse` | `WebhookDeliveryData` |
| `WebhookShowResponse` | `WebhookData` |
| `WebhookStoreRequest` | `StoreWebhookData` |
| `WebhookStoreResponse` | `WebhookSecretResponse` |
| `WebhookTestResponse` | `TestWebhookResponse` |
| `WebhookUpdateRequest` | `UpdateWebhookData` |
| `WebhookUpdateResponse` | `WebhookMutationResponse` |
| `PingResponse` | `str` (`ping()` returns the text) |

### Removed types

lettermint#2582 removed these schemas from the API specification:

| 2.x | 3.0 |
| --- | --- |
| `AnalyticsResponseData` | Removed. Use `AnalyticsResponse` (`data: AnalyticsResults`). |
| `StatsRequestData` | Removed. Use `GetStatsQuery`, the parameters of `stats.retrieve()`. |
| Message list `meta` (`MessageIndexResponseMeta`) | Removed; not exported by 2.x. Lists are flat `CursorPage[T]`. |
| Message events `meta` (`MessageEventsResponseMeta`) | Removed; not exported by 2.x. |
| `SuppressionStoreResponseMessage1` | Removed; not exported by 2.x. `SuppressionStoreResponse["message"]` is a `str`. |

### Removed classes, modules and helpers

| 2.x | 3.0 |
| --- | --- |
| `Lettermint.email(token, ...)`, `AsyncLettermint.email(token, ...)` | `Lettermint(sending_token=token, ...).emails` |
| `Lettermint.api(token, ...)`, `AsyncLettermint.api(token, ...)` | `Lettermint(team_token=token, ...)` |
| `Lettermint(api_token=...)`, `client.email` | `Lettermint(sending_token=...)`, `lettermint.emails` |
| `ApiClient`, `AsyncApiClient` | `Lettermint`, `AsyncLettermint` |
| `lettermint.endpoints` (`EmailEndpoint`, `AsyncEmailEndpoint`, `Endpoint`, `AsyncEndpoint`, `DomainsEndpoint`, `MessagesEndpoint`, `ProjectsEndpoint`, `RoutesEndpoint`, `StatsEndpoint`, `SuppressionsEndpoint`, `TeamEndpoint`, `WebhooksEndpoint`, and `AsyncDomainsEndpoint`, `AsyncMessagesEndpoint`, `AsyncProjectsEndpoint`, `AsyncRoutesEndpoint`, `AsyncStatsEndpoint`, `AsyncSuppressionsEndpoint`, `AsyncTeamEndpoint`, `AsyncWebhooksEndpoint`) | `Emails`, `EmailBuilder`, `Domains`, `Messages`, `Projects`, `ReportForwarding`, `Routes`, `Stats`, `Suppressions`, `Team`, `TeamMembers`, `Webhooks`, `WebhookDeliveries` and their `Async*` versions, exported for type hints; use the attributes of the client |
| `lettermint.client` (`LettermintClient`, `AsyncLettermintClient` with `get`, `post`, `put`, `patch`, `delete`, `get_raw`; `DEFAULT_BASE_URL`, `DEFAULT_TIMEOUT`) | Removed. Every documented endpoint has a method. Pass `http_client=` to customize HTTP. |
| `lettermint.lettermint` | Removed; import from `lettermint` |
| `lettermint.message_tag` (`MessageTag`, `normalize_message_tags`) | Tags are dicts (`lettermint.types.MessageTagInput`), validated by the SDK |
| `lettermint.exceptions.HttpRequestError`, `ClientError` | `APIError` and its subclasses |
| `lettermint.exceptions.TimeoutError` | `APITimeoutError` |
| `InvalidSignatureError`, `TimestampToleranceError`, `JsonDecodeError` | `WebhookVerificationError` with a `reason` |
| `Webhook.verify_headers(headers, payload)` | `Webhook.verify(raw_body, headers)` |
| `Webhook.verify(payload, signature, timestamp)` | `Webhook.verify_signature(raw_body, signature_header, timestamp)` |
| `Webhook.verify_signature(payload, signature, secret, timestamp, tolerance)` (static) | `Webhook(secret, tolerance).verify_signature(raw_body, signature_header, timestamp)` |
| Top-level `EmailAttachment`, `EmailPayload`, `EmailStatus`, `SendEmailResponse`, `SendBatchEmailResponse` | `lettermint.EmailAttachment` (attachment of an `EmailMessage`), `lettermint.EmailMessage`, `lettermint.types.MessageStatus`, `SendMailResponse`, `SendBatchMailResponse` |

# Upgrade to v2

This guide covers upgrading from the latest released v1 Python SDK to v2.

## Highlights

- Sending email now lives behind `Lettermint.email(token)`.
- The full Lettermint API is available through `Lettermint.api(token)`.
- Sending tokens use `x-lettermint-token`; full API tokens use `Authorization: Bearer`.
- `ping()` returns the raw trimmed `pong` response.
- Request and response shapes are generated from the OpenAPI specs as `TypedDict`/`Literal` types.

## Replace Client Construction

```python
from lettermint import Lettermint

email = Lettermint.email("sending-token")
api = Lettermint.api("api-token")
```

Existing `Lettermint(api_token="...").email` sending usage still works.

## Batch Sending

```python
email.send_batch([
    {"from": "sender@example.com", "to": ["user@example.com"], "subject": "Hello", "text": "Hi"}
])
```

## Full API

```python
domains = api.domains.list()
message_html = api.messages.html("message-id")
```

