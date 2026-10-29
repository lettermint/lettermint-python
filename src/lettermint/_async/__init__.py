"""The asynchronous client. ``scripts/unasync.py`` generates ``lettermint._sync`` from it."""

from .client import AsyncLettermint
from .emails import AsyncEmailBuilder, AsyncEmails
from .resources import (
    AsyncDomains,
    AsyncMessages,
    AsyncProjectApiTokens,
    AsyncProjects,
    AsyncReportForwarding,
    AsyncResource,
    AsyncRoutes,
    AsyncStats,
    AsyncSuppressions,
    AsyncTeam,
    AsyncTeamInvites,
    AsyncTeamMembers,
    AsyncWebhookDeliveries,
    AsyncWebhooks,
)

__all__ = [
    "AsyncDomains",
    "AsyncEmailBuilder",
    "AsyncEmails",
    "AsyncLettermint",
    "AsyncMessages",
    "AsyncProjectApiTokens",
    "AsyncProjects",
    "AsyncReportForwarding",
    "AsyncResource",
    "AsyncRoutes",
    "AsyncStats",
    "AsyncSuppressions",
    "AsyncTeam",
    "AsyncTeamInvites",
    "AsyncTeamMembers",
    "AsyncWebhookDeliveries",
    "AsyncWebhooks",
]
