"""The official Python SDK for Lettermint.

::

    from lettermint import Lettermint

    lettermint = Lettermint(sending_token=os.environ["LETTERMINT_PROJECT_TOKEN"])
    result = lettermint.emails.send({
        "from": "Acme <hello@acme.com>",
        "to": ["jane@example.com"],
        "subject": "Welcome to Acme",
        "html": "<p>Thanks for signing up.</p>",
    })

``AsyncLettermint`` has the same surface for ``asyncio`` and ``trio``. Request
and response types are in :mod:`lettermint.types`. Upgrading from 2.x? Read
``UPGRADE.md``.
"""

from . import types
from ._async import (
    AsyncDomains,
    AsyncEmailBuilder,
    AsyncEmails,
    AsyncLettermint,
    AsyncMessages,
    AsyncProjects,
    AsyncReportForwarding,
    AsyncRoutes,
    AsyncStats,
    AsyncSuppressions,
    AsyncTeam,
    AsyncTeamMembers,
    AsyncWebhookDeliveries,
    AsyncWebhooks,
)
from ._emails import BaseEmailBuilder, EmailAttachment, EmailMessage
from ._generated.types import CursorPage
from ._sync import (
    Domains,
    EmailBuilder,
    Emails,
    Lettermint,
    Messages,
    Projects,
    ReportForwarding,
    Routes,
    Stats,
    Suppressions,
    Team,
    TeamMembers,
    WebhookDeliveries,
    Webhooks,
)
from ._version import __version__
from .exceptions import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    ConflictError,
    LettermintConfigError,
    LettermintError,
    LettermintValidationError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    RedirectError,
    ServerError,
    UnexpectedResponseError,
    ValidationError,
    WebhookVerificationError,
    WebhookVerificationReason,
)
from .webhook import Webhook, WebhookHeaders, WebhookPayload

__all__ = [
    "APIConnectionError",
    "APIError",
    "APITimeoutError",
    "AsyncDomains",
    "AsyncEmailBuilder",
    "AsyncEmails",
    "AsyncLettermint",
    "AsyncMessages",
    "AsyncProjects",
    "AsyncReportForwarding",
    "AsyncRoutes",
    "AsyncStats",
    "AsyncSuppressions",
    "AsyncTeam",
    "AsyncTeamMembers",
    "AsyncWebhookDeliveries",
    "AsyncWebhooks",
    "AuthenticationError",
    "BaseEmailBuilder",
    "ConflictError",
    "CursorPage",
    "Domains",
    "EmailAttachment",
    "EmailBuilder",
    "EmailMessage",
    "Emails",
    "Lettermint",
    "LettermintConfigError",
    "LettermintError",
    "LettermintValidationError",
    "Messages",
    "NotFoundError",
    "PermissionDeniedError",
    "Projects",
    "RateLimitError",
    "RedirectError",
    "ReportForwarding",
    "Routes",
    "ServerError",
    "Stats",
    "Suppressions",
    "Team",
    "TeamMembers",
    "UnexpectedResponseError",
    "ValidationError",
    "Webhook",
    "WebhookDeliveries",
    "WebhookHeaders",
    "WebhookPayload",
    "WebhookVerificationError",
    "WebhookVerificationReason",
    "Webhooks",
    "__version__",
    "types",
]
