# Upgrade To v2

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

