"""Generated type definitions for the Lettermint SDK."""

from __future__ import annotations

from typing import Any, Literal, Optional, TypedDict

from typing_extensions import NotRequired, Required, TypeAlias

MessageStatus: TypeAlias = Literal[
    "scheduled",
    "pending",
    "queued",
    "quarantined",
    "suppressed",
    "processed",
    "delivered",
    "opened",
    "clicked",
    "soft_bounced",
    "hard_bounced",
    "spam_complaint",
    "failed",
    "blocked",
    "policy_rejected",
    "unsubscribed",
    "canceled",
]
SandboxResult: TypeAlias = Literal[
    "delivered",
    "hard_bounced",
    "soft_bounced",
    "deferred",
    "failed",
    "suppressed",
    "spam_complaint",
    "auto_replied",
    "opened",
    "clicked",
    "unsubscribed",
]
TlsPolicy: TypeAlias = Literal["opportunistic", "enforced"]
SendMailRequest = TypedDict(
    "SendMailRequest",
    {
        "route": "NotRequired[str]",
        "from": "Required[str]",
        "to": "Required[list[str]]",
        "cc": "NotRequired[list[str]]",
        "bcc": "NotRequired[list[str]]",
        "reply_to": "NotRequired[list[str]]",
        "subject": "Required[str]",
        "scheduled_at": "NotRequired[str]",
        "headers": "NotRequired[dict[str, str]]",
        "metadata": "NotRequired[dict[str, str]]",
        "tag": "NotRequired[str | None]",
        "tags": "NotRequired[list[dict[str, Any]]]",
        "settings": "NotRequired[dict[str, Any]]",
        "html": "NotRequired[str | None]",
        "text": "NotRequired[str | None]",
        "attachments": "NotRequired[list[dict[str, Any]]]",
        "sandbox_result": "NotRequired[SandboxResult]",
    },
)

SendBatchMailRequest: TypeAlias = list[SendMailRequest]
AttachmentDelivery: TypeAlias = Literal["inline", "url"]
BuiltInTeamRole: TypeAlias = Literal["owner", "admin", "member"]
CursorPaginator = TypedDict(
    "CursorPaginator",
    {
        "data": "Required[list[str]]",
        "path": "Required[str | None]",
        "per_page": "Required[int]",
        "next_cursor": "Required[str | None]",
        "next_page_url": "Required[str | None]",
        "prev_cursor": "Required[str | None]",
        "prev_page_url": "Required[str | None]",
    },
)
DkimMode: TypeAlias = Literal["legacy_txt", "managed_cname"]
DnsRecordPurpose: TypeAlias = Literal[
    "return_path", "dmarc", "dkim_legacy", "dkim_primary", "dkim_secondary"
]
DnsRecordStatus: TypeAlias = Literal["active", "failed", "pending"]
DnsVerificationScope: TypeAlias = Literal["required", "recommended", "migration", "deprecated"]
RecordType: TypeAlias = Literal["TXT", "CNAME", "MX"]
DomainDnsRecordData = TypedDict(
    "DomainDnsRecordData",
    {
        "id": "Required[str]",
        "type": "Required[RecordType]",
        "hostname": "Required[str]",
        "fqdn": "Required[str]",
        "content": "Required[str]",
        "status": "Required[DnsRecordStatus]",
        "purpose": "Required[DnsRecordPurpose]",
        "verification_scope": "Required[DnsVerificationScope]",
        "required_for_verification": "Required[bool]",
        "verified_at": "Required[str | None]",
        "last_checked_at": "Required[str | None]",
    },
)

DomainData = TypedDict(
    "DomainData",
    {
        "id": "Required[str]",
        "domain": "Required[str]",
        "dkim_mode": "Required[DkimMode]",
        "rotation_ready": "Required[bool]",
        "status_changed_at": "Required[str | None]",
        "dns_records": "NotRequired[list[DomainDnsRecordData]]",
        "projects": "NotRequired[list[dict[str, Any]]]",
        "created_at": "Required[str]",
    },
)

DomainStatus: TypeAlias = Literal[
    "verified", "partially_verified", "pending_verification", "failed_verification"
]
DomainListData = TypedDict(
    "DomainListData",
    {
        "id": "Required[str]",
        "domain": "Required[str]",
        "status": "Required[DomainStatus]",
        "dkim_mode": "Required[DkimMode]",
        "status_changed_at": "Required[str | None]",
        "created_at": "Required[str]",
    },
)

InitialRoutes: TypeAlias = Literal["both", "transactional", "broadcast"]
MessageAttachmentData = TypedDict(
    "MessageAttachmentData",
    {
        "size": "Required[int]",
        "filename": "Required[str]",
        "content_id": "Required[str | None]",
        "content_type": "Required[str]",
    },
)

DeliveryMode: TypeAlias = Literal["live", "sandbox"]
MessageRecipientData = TypedDict(
    "MessageRecipientData",
    {
        "email": "Required[str]",
        "name": "Required[str | None]",
        "sandbox_result": "Required[SandboxResult | None]",
    },
)

SpamSymbol = TypedDict(
    "SpamSymbol",
    {
        "name": "Required[str]",
        "score": "Required[float]",
        "options": "Required[list[str]]",
        "description": "Required[str | None]",
    },
)

MessageType: TypeAlias = Literal["inbound", "outbound"]
MessageData = TypedDict(
    "MessageData",
    {
        "id": "Required[str]",
        "type": "Required[MessageType]",
        "status": "Required[MessageStatus]",
        "status_changed_at": "Required[str | None]",
        "scheduled_at": "Required[str | None]",
        "tag": "Required[str | None]",
        "tags": "Required[list[dict[str, Any]]]",
        "from_email": "Required[str]",
        "from_name": "Required[str | None]",
        "reply_to": "Required[list[str] | None]",
        "subject": "Required[str | None]",
        "to": "Required[list[MessageRecipientData] | None]",
        "cc": "Required[list[MessageRecipientData] | None]",
        "bcc": "Required[list[MessageRecipientData] | None]",
        "attachments": "Required[list[MessageAttachmentData] | None]",
        "metadata": "Required[dict[str, str] | None]",
        "spam_score": "NotRequired[float | None]",
        "spam_symbols": "NotRequired[list[SpamSymbol]]",
        "route_id": "Required[str]",
        "created_at": "Required[str]",
        "delivery_mode": "Required[DeliveryMode]",
        "sandbox_result": "Required[SandboxResult | None]",
    },
)

MessageEventType: TypeAlias = Literal[
    "scheduled",
    "rescheduled",
    "canceled",
    "released",
    "queued",
    "processed",
    "suppressed",
    "delivered",
    "auto_replied",
    "soft_bounced",
    "hard_bounced",
    "spam_complaint",
    "failed",
    "blocked",
    "policy_rejected",
    "unsubscribed",
    "opened",
    "clicked",
    "inbound_received",
    "inbound_queued",
    "inbound_spam_blocked",
    "inbound_released",
    "inbound_processed",
    "inbound_retry",
]
MessageEventData = TypedDict(
    "MessageEventData",
    {
        "message_id": "Required[str]",
        "event": "Required[MessageEventType]",
        "tag": "Required[str | None]",
        "tags": "Required[list[dict[str, Any]]]",
        "metadata": "Required[dict[str, Any] | None]",
        "timestamp": "Required[str]",
    },
)

MessageListData = TypedDict(
    "MessageListData",
    {
        "id": "Required[str]",
        "type": "Required[MessageType]",
        "status": "Required[MessageStatus]",
        "scheduled_at": "Required[str | None]",
        "spam_score": "NotRequired[float | None]",
        "from_email": "Required[str]",
        "from_name": "Required[str | None]",
        "subject": "Required[str | None]",
        "to": "Required[list[MessageRecipientData] | None]",
        "cc": "Required[list[MessageRecipientData] | None]",
        "bcc": "Required[list[MessageRecipientData] | None]",
        "reply_to": "Required[list[str] | None]",
        "tag": "Required[str | None]",
        "tags": "Required[list[dict[str, Any]]]",
        "status_changed_at": "Required[str | None]",
        "created_at": "Required[str]",
        "delivery_mode": "Required[DeliveryMode]",
        "sandbox_result": "Required[SandboxResult | None]",
    },
)

MessageStatsData = TypedDict(
    "MessageStatsData",
    {
        "messages_transactional": "Required[int]",
        "messages_broadcast": "Required[int]",
        "messages_inbound": "Required[int]",
        "deliverability": "Required[float]",
    },
)

Plan: TypeAlias = Literal["free", "starter", "growth", "pro"]
ProjectAccessScope: TypeAlias = Literal["all", "selected"]
RouteStatisticData = TypedDict(
    "RouteStatisticData",
    {
        "date": "Required[str]",
        "sent_count": "Required[int]",
        "delivered_count": "Required[int]",
        "opened_count": "Required[int]",
        "clicked_count": "Required[int]",
        "hard_bounce_count": "Required[int]",
        "spam_complaint_count": "Required[int]",
        "inbound_received_count": "Required[int]",
        "observed_opened_count": "NotRequired[int | None]",
        "human_opened_count": "NotRequired[int | None]",
        "privacy_opened_count": "NotRequired[int | None]",
        "effective_opened_count": "Required[int | None]",
        "machine_opened_count": "Required[int | None]",
        "machine_clicked_count": "Required[int | None]",
    },
)

RouteType: TypeAlias = Literal["transactional", "broadcast", "inbound"]
RouteData = TypedDict(
    "RouteData",
    {
        "id": "Required[str]",
        "project_id": "Required[str]",
        "slug": "Required[str]",
        "name": "Required[str]",
        "route_type": "Required[RouteType]",
        "is_default": "Required[bool]",
        "inbound_address": "NotRequired[str | None]",
        "inbound_mx_hostname": "NotRequired[str]",
        "inbound_route_domain": "NotRequired[str | None]",
        "inbound_domain": "NotRequired[str | None]",
        "inbound_domain_verified_at": "NotRequired[str | None]",
        "inbound_spam_threshold": "NotRequired[float | None]",
        "attachment_delivery": "NotRequired[AttachmentDelivery]",
        "settings": "NotRequired[dict[str, Any] | None]",
        "project": "NotRequired[ProjectData]",
        "webhooks_count": "NotRequired[int]",
        "suppressed_recipients_count": "NotRequired[int]",
        "statistics": "NotRequired[list[RouteStatisticData]]",
        "created_at": "Required[str]",
        "updated_at": "Required[str]",
    },
)

ProjectData = TypedDict(
    "ProjectData",
    {
        "id": "Required[str]",
        "name": "Required[str]",
        "smtp_enabled": "Required[bool]",
        "redact_email_content": "Required[bool]",
        "default_route_id": "Required[str | None]",
        "token_generated_at": "Required[str | None]",
        "token_last_used_at": "Required[str | None]",
        "token_last_used_ip": "Required[str | None]",
        "routes": "NotRequired[list[RouteData]]",
        "routes_count": "NotRequired[int]",
        "domains": "NotRequired[list[DomainData]]",
        "domains_count": "NotRequired[int]",
        "last_28_days": "NotRequired[MessageStatsData | None]",
        "created_at": "Required[str]",
        "updated_at": "Required[str]",
        "delivery_mode": "Required[DeliveryMode]",
    },
)

ProjectListData = TypedDict(
    "ProjectListData",
    {
        "id": "Required[str]",
        "name": "Required[str]",
        "delivery_mode": "Required[DeliveryMode]",
        "smtp_enabled": "Required[bool]",
        "routes_count": "Required[int]",
        "domains_count": "Required[int]",
        "last_28_days": "Required[MessageStatsData]",
        "created_at": "Required[str]",
        "updated_at": "Required[str]",
    },
)


RbacConflictCode: TypeAlias = Literal[
    "stale_resource",
    "owner_protected",
    "last_owner",
    "built_in_role_immutable",
    "custom_role_requires_pro",
]
RbacPermission: TypeAlias = Literal[
    "team:manage",
    "billing:manage",
    "security:manage",
    "audit:read",
    "support:manage",
    "members:read",
    "members:manage",
    "roles:manage",
    "team_tokens:read",
    "team_tokens:manage",
    "team_tokens:rotate",
    "team_tokens:revoke",
    "projects:create",
    "team_suppressions:read",
    "team_suppressions:add",
    "team_suppressions:remove",
    "projects:read",
    "projects:manage",
    "projects:delete",
    "routes:read",
    "routes:manage",
    "routes:delete",
    "domains:read",
    "domains:manage",
    "domains:delete",
    "project_tokens:read",
    "project_tokens:manage",
    "project_tokens:rotate",
    "project_tokens:revoke",
    "webhooks:read",
    "webhooks:manage",
    "webhooks:delete",
    "webhooks:rotate_secret",
    "stats:read",
    "analytics:read",
    "messages:read",
    "messages:read_content",
    "messages:send",
    "suppressions:read",
    "suppressions:add",
    "suppressions:remove",
]
RescheduleMessageRequest = TypedDict(
    "RescheduleMessageRequest",
    {
        "scheduled_at": "Required[str]",
    },
)

RouteListData = TypedDict(
    "RouteListData",
    {
        "id": "Required[str]",
        "slug": "Required[str]",
        "name": "Required[str]",
        "route_type": "Required[RouteType]",
        "is_default": "Required[bool]",
        "webhooks_count": "Required[int]",
        "suppressed_recipients_count": "Required[int]",
        "created_at": "Required[str]",
        "updated_at": "Required[str]",
    },
)

StatsInboundData = TypedDict(
    "StatsInboundData",
    {
        "received": "Required[int]",
    },
)

StatsTypeData = TypedDict(
    "StatsTypeData",
    {
        "sent": "Required[int]",
        "hard_bounced": "Required[int]",
        "spam_complaints": "Required[int]",
    },
)

StatsDailyData = TypedDict(
    "StatsDailyData",
    {
        "date": "Required[str]",
        "sent": "Required[int]",
        "delivered": "Required[int]",
        "hard_bounced": "Required[int]",
        "spam_complaints": "Required[int]",
        "opened": "Required[int | None]",
        "clicked": "Required[int | None]",
        "inbound": "Required[StatsInboundData]",
        "transactional": "Required[StatsTypeData | None]",
        "broadcast": "Required[StatsTypeData | None]",
        "observed_opened": "NotRequired[int | None]",
        "human_opened": "NotRequired[int | None]",
        "privacy_opened": "NotRequired[int | None]",
        "effective_opened": "Required[int | None]",
        "machine_opened": "Required[int | None]",
        "machine_clicked": "Required[int | None]",
    },
)

StatsTotalsData = TypedDict(
    "StatsTotalsData",
    {
        "sent": "Required[int]",
        "delivered": "Required[int]",
        "hard_bounced": "Required[int]",
        "spam_complaints": "Required[int]",
        "opened": "Required[int | None]",
        "clicked": "Required[int | None]",
        "inbound": "Required[StatsInboundData]",
        "transactional": "Required[StatsTypeData | None]",
        "broadcast": "Required[StatsTypeData | None]",
        "observed_opened": "NotRequired[int | None]",
        "human_opened": "NotRequired[int | None]",
        "privacy_opened": "NotRequired[int | None]",
        "effective_opened": "Required[int | None]",
        "machine_opened": "Required[int | None]",
        "machine_clicked": "Required[int | None]",
    },
)

StatsData = TypedDict(
    "StatsData",
    {
        "from": "Required[str]",
        "to": "Required[str]",
        "totals": "Required[StatsTotalsData]",
        "daily": "Required[list[StatsDailyData]]",
    },
)

StatsRequestData = TypedDict(
    "StatsRequestData",
    {
        "from": "Required[str]",
        "to": "Required[str]",
        "project_id": "NotRequired[str | None]",
        "include_machine": "NotRequired[bool]",
    },
)

StoreDomainData = TypedDict(
    "StoreDomainData",
    {
        "domain": "Required[str]",
    },
)

StoreProjectData = TypedDict(
    "StoreProjectData",
    {
        "name": "Required[str]",
        "smtp_enabled": "NotRequired[bool]",
        "delivery_mode": "NotRequired[DeliveryMode]",
        "initial_routes": "NotRequired[InitialRoutes]",
        "short_token": "NotRequired[bool]",
        "redact_email_content": "NotRequired[bool]",
    },
)


StoreRouteData = TypedDict(
    "StoreRouteData",
    {
        "name": "Required[str]",
        "route_type": "Required[RouteType]",
        "slug": "NotRequired[str | None]",
        "settings": "NotRequired[UpdateRouteSettingsData | None]",
        "inbound_settings": "NotRequired[UpdateRouteInboundSettingsData | None]",
        "inbound_domain": "NotRequired[str | None]",
        "inbound_spam_threshold": "NotRequired[float | None]",
        "attachment_delivery": "NotRequired[AttachmentDelivery | None]",
    },
)


SuppressionReason: TypeAlias = Literal["spam_complaint", "hard_bounce", "unsubscribe", "manual"]
SuppressionScope: TypeAlias = Literal["team", "project", "route"]
SuppressionAppliesTo: TypeAlias = Literal["all", "broadcast"]
StoreSuppressionData = TypedDict(
    "StoreSuppressionData",
    {
        "email": "NotRequired[str | None]",
        "emails": "NotRequired[list[str] | None]",
        "reason": "Required[SuppressionReason]",
        "scope": "Required[SuppressionScope]",
        "route_id": "NotRequired[str | None]",
        "project_id": "NotRequired[str | None]",
        "applies_to": "NotRequired[SuppressionAppliesTo | None]",
    },
)

WebhookEvent: TypeAlias = Literal[
    "message.created",
    "message.sent",
    "message.delivered",
    "message.auto_replied",
    "message.hard_bounced",
    "message.soft_bounced",
    "message.spam_complaint",
    "message.failed",
    "message.suppressed",
    "message.unsubscribed",
    "message.opened",
    "message.clicked",
    "message.inbound",
    "message.policy_rejected",
    "message.scheduled",
    "message.rescheduled",
    "message.canceled",
    "message.released",
    "suppression.added",
    "suppression.removed",
    "webhook.test",
]
WebhookScope: TypeAlias = Literal["team", "project", "route"]
WebhookDeliveryModeFilter: TypeAlias = Literal["live", "sandbox", "both"]
WebhookBasicAuthData = TypedDict(
    "WebhookBasicAuthData",
    {
        "username": "Required[str]",
        "password": "Required[str]",
    },
)

StoreWebhookData = TypedDict(
    "StoreWebhookData",
    {
        "name": "Required[str]",
        "url": "Required[str]",
        "events": "Required[list[WebhookEvent]]",
        "enabled": "NotRequired[bool | None]",
        "include_machine_events": "NotRequired[bool | None]",
        "scope": "NotRequired[WebhookScope | None]",
        "project_ids": "NotRequired[list[str]]",
        "route_ids": "NotRequired[list[str]]",
        "route_id": "NotRequired[str | None]",
        "delivery_mode_filter": "NotRequired[WebhookDeliveryModeFilter | None]",
        "basic_auth": "NotRequired[Optional[WebhookBasicAuthData]]",  # noqa: UP045 - Python 3.9 runtime hint resolution.
    },
)

SuppressionSourceMessageData = TypedDict(
    "SuppressionSourceMessageData",
    {
        "id": "Required[str]",
        "available": "Required[bool]",
        "subject": "Required[str | None]",
        "created_at": "Required[str | None]",
    },
)

SuppressionType: TypeAlias = Literal["email", "domain", "extension"]
SuppressedRecipientData = TypedDict(
    "SuppressedRecipientData",
    {
        "id": "Required[str]",
        "type": "Required[SuppressionType]",
        "value": "Required[str]",
        "reason": "Required[SuppressionReason]",
        "scope": "Required[SuppressionScope]",
        "applies_to": "Required[SuppressionAppliesTo]",
        "project_id": "Required[str | None]",
        "route_id": "Required[str | None]",
        "source_message": "NotRequired[SuppressionSourceMessageData | None]",
        "created_at": "Required[str]",
    },
)

TeamAddonData = TypedDict(
    "TeamAddonData",
    {
        "type": "Required[str | None]",
        "expires_at": "Required[str | None]",
    },
)

TeamType: TypeAlias = Literal["personal", "business"]
TeamData = TypedDict(
    "TeamData",
    {
        "id": "Required[str]",
        "name": "Required[str]",
        "type": "Required[TeamType]",
        "plan": "Required[Plan]",
        "included_volume": "Required[int]",
        "tier": "Required[int]",
        "verified_at": "Required[str | None]",
        "features": "NotRequired[list[str]]",
        "addons": "NotRequired[list[TeamAddonData]]",
        "created_at": "Required[str]",
        "domains_count": "NotRequired[int]",
        "projects_count": "NotRequired[int]",
        "members_count": "NotRequired[int]",
    },
)

TeamMemberProjectAccessData = TypedDict(
    "TeamMemberProjectAccessData",
    {
        "scope": "Required[ProjectAccessScope]",
        "projects": "Required[list[dict[str, Any]]]",
    },
)

TeamMemberData = TypedDict(
    "TeamMemberData",
    {
        "id": "Required[str]",
        "name": "Required[str]",
        "email": "Required[str]",
        "role": "Required[dict[str, Any]]",
        "project_access": "Required[TeamMemberProjectAccessData]",
        "joined_at": "Required[str | None]",
    },
)

TeamRoleData = TypedDict(
    "TeamRoleData",
    {
        "id": "Required[str]",
        "name": "Required[str]",
        "system_key": "Required[BuiltInTeamRole | None]",
        "permissions": "Required[list[RbacPermission]]",
        "assignable": "Required[bool]",
    },
)

TeamUsagePeriodData = TypedDict(
    "TeamUsagePeriodData",
    {
        "usage": "Required[int]",
        "last_incremented_at": "Required[str | None]",
        "period_start": "Required[str]",
        "period_end": "Required[str]",
    },
)

TeamUsageDetailData = TypedDict(
    "TeamUsageDetailData",
    {
        "current_period": "Required[TeamUsagePeriodData]",
        "historical_usage": "Required[list[TeamUsagePeriodData]]",
    },
)

UpdateDomainProjectsData = TypedDict(
    "UpdateDomainProjectsData",
    {
        "project_ids": "Required[list[str]]",
    },
)

UpdateProjectData = TypedDict(
    "UpdateProjectData",
    {
        "name": "NotRequired[str | None]",
        "smtp_enabled": "NotRequired[bool | None]",
        "redact_email_content": "NotRequired[bool | None]",
        "default_route_id": "NotRequired[str | None]",
        "delivery_mode": "NotRequired[DeliveryMode | None]",
    },
)

UpdateRouteInboundSettingsData = TypedDict(
    "UpdateRouteInboundSettingsData",
    {
        "inbound_domain": "NotRequired[str | None]",
        "inbound_spam_threshold": "NotRequired[float | None]",
        "attachment_delivery": "NotRequired[AttachmentDelivery | None]",
    },
)

UpdateRouteSettingsData = TypedDict(
    "UpdateRouteSettingsData",
    {
        "track_opens": "NotRequired[bool | None]",
        "track_clicks": "NotRequired[bool | None]",
        "generate_plaintext_fallback": "NotRequired[bool | None]",
        "suppress_auto_responders": "NotRequired[bool | None]",
        "suppress_disposable_recipients": "NotRequired[bool | None]",
        "tls": "NotRequired[TlsPolicy | None]",
        "disable_hosted_unsubscribe": "NotRequired[bool | None]",
        "redact_email_content": "NotRequired[bool | None]",
    },
)

UpdateRouteData = TypedDict(
    "UpdateRouteData",
    {
        "name": "NotRequired[str | None]",
        "settings": "NotRequired[UpdateRouteSettingsData | None]",
        "inbound_settings": "NotRequired[UpdateRouteInboundSettingsData | None]",
        "inbound_domain": "NotRequired[str | None]",
        "inbound_spam_threshold": "NotRequired[float | None]",
        "attachment_delivery": "NotRequired[AttachmentDelivery | None]",
    },
)


UpdateTeamData = TypedDict(
    "UpdateTeamData",
    {
        "name": "NotRequired[str]",
    },
)


UpdateTeamMemberAssignmentData = TypedDict(
    "UpdateTeamMemberAssignmentData",
    {
        "role_id": "Required[str]",
        "project_access": "Required[dict[str, Any]]",
    },
)

UpdateWebhookData = TypedDict(
    "UpdateWebhookData",
    {
        "name": "NotRequired[str]",
        "url": "NotRequired[str]",
        "events": "NotRequired[list[WebhookEvent]]",
        "enabled": "NotRequired[bool]",
        "include_machine_events": "NotRequired[bool]",
        "scope": "NotRequired[WebhookScope]",
        "project_ids": "NotRequired[list[str]]",
        "route_ids": "NotRequired[list[str]]",
        "route_id": "NotRequired[str | None]",
        "delivery_mode_filter": "NotRequired[WebhookDeliveryModeFilter]",
        "basic_auth": "NotRequired[Optional[WebhookBasicAuthData]]",  # noqa: UP045 - Python 3.9 runtime hint resolution.
    },
)

WebhookData = TypedDict(
    "WebhookData",
    {
        "id": "Required[str]",
        "scope": "Required[WebhookScope]",
        "project_ids": "Required[list[str]]",
        "route_ids": "Required[list[str]]",
        "route_id": "Required[str | None]",
        "name": "Required[str]",
        "url": "Required[str]",
        "has_basic_auth": "Required[bool]",
        "events": "Required[list[str]]",
        "enabled": "Required[bool]",
        "include_machine_events": "Required[bool]",
        "last_called_at": "Required[str | None]",
        "created_at": "Required[str]",
        "updated_at": "Required[str]",
        "delivery_mode_filter": "Required[WebhookDeliveryModeFilter]",
    },
)

WebhookDeliveryStatus: TypeAlias = Literal[
    "pending", "success", "failed", "client_error", "server_error", "timeout"
]
WebhookDeliveryData = TypedDict(
    "WebhookDeliveryData",
    {
        "id": "Required[str]",
        "webhook_id": "Required[str]",
        "event_type": "Required[WebhookEvent]",
        "source_scope": "Required[str | None]",
        "source_project_id": "Required[str | None]",
        "source_route_id": "Required[str | None]",
        "status": "Required[WebhookDeliveryStatus]",
        "attempt_number": "Required[int]",
        "http_status_code": "Required[int | None]",
        "duration_ms": "Required[int | None]",
        "payload": "Required[list[str]]",
        "response_body": "Required[str | None]",
        "response_headers": "Required[list[str] | None]",
        "error_message": "Required[str | None]",
        "delivered_at": "Required[str | None]",
        "timestamp": "Required[str]",
        "sandbox": "Required[bool]",
    },
)

WebhookDeliveryListData = TypedDict(
    "WebhookDeliveryListData",
    {
        "id": "Required[str]",
        "webhook_id": "Required[str]",
        "event_type": "Required[WebhookEvent]",
        "source_scope": "Required[str | None]",
        "source_project_id": "Required[str | None]",
        "source_route_id": "Required[str | None]",
        "status": "Required[WebhookDeliveryStatus]",
        "sandbox": "Required[bool]",
        "attempt_number": "Required[int]",
        "http_status_code": "Required[int | None]",
        "duration_ms": "Required[int | None]",
        "delivered_at": "Required[str | None]",
        "created_at": "Required[str]",
    },
)


WebhookListData = TypedDict(
    "WebhookListData",
    {
        "id": "Required[str]",
        "scope": "Required[WebhookScope]",
        "project_ids": "Required[list[str]]",
        "route_ids": "Required[list[str]]",
        "route_id": "Required[str | None]",
        "name": "Required[str]",
        "url": "Required[str]",
        "events": "Required[list[str]]",
        "enabled": "Required[bool]",
        "delivery_mode_filter": "Required[WebhookDeliveryModeFilter]",
        "last_called_at": "Required[str | None]",
        "created_at": "Required[str]",
        "updated_at": "Required[str]",
        "has_basic_auth": "Required[bool]",
    },
)


WebhookSecretData = TypedDict(
    "WebhookSecretData",
    {
        "id": "Required[str]",
        "scope": "Required[WebhookScope]",
        "project_ids": "Required[list[str]]",
        "route_ids": "Required[list[str]]",
        "route_id": "Required[str | None]",
        "name": "Required[str]",
        "url": "Required[str]",
        "events": "Required[list[str]]",
        "enabled": "Required[bool]",
        "include_machine_events": "Required[bool]",
        "secret": "Required[str]",
        "last_called_at": "Required[str | None]",
        "created_at": "Required[str]",
        "updated_at": "Required[str]",
        "delivery_mode_filter": "Required[WebhookDeliveryModeFilter]",
        "has_basic_auth": "Required[bool]",
    },
)

EmailAttachment = TypedDict(
    "EmailAttachment",
    {
        "filename": "Required[str]",
        "content": "Required[str]",
        "content_type": "NotRequired[str | None]",
        "content_id": "NotRequired[str | None]",
    },
)
EmailPayload: TypeAlias = SendMailRequest
EmailStatus: TypeAlias = MessageStatus
SendMailResponse = TypedDict(
    "SendMailResponse",
    {
        "message_id": "Required[str]",
        "status": "Required[Literal['pending', 'scheduled']]",
        "sandbox": "NotRequired[Literal[True]]",
        "sandbox_result": "NotRequired[SandboxResult]",
        "scheduled_at": "NotRequired[str]",
    },
)


SendBatchMailResponse: TypeAlias = list[SendMailResponse]
PingResponse: TypeAlias = str
DomainIndexResponse = TypedDict(
    "DomainIndexResponse",
    {
        "data": "Required[list[DomainListData]]",
        "path": "Required[str | None]",
        "per_page": "Required[int]",
        "next_cursor": "Required[str | None]",
        "next_page_url": "Required[str | None]",
        "prev_cursor": "Required[str | None]",
        "prev_page_url": "Required[str | None]",
    },
)

DomainStoreRequest: TypeAlias = StoreDomainData
DomainStoreResponse: TypeAlias = DomainData
DomainShowResponse: TypeAlias = DomainData
DomainDestroyResponse = TypedDict(
    "DomainDestroyResponse",
    {
        "message": "Required[Literal['Domain deleted successfully.']]",
    },
)

DomainVerifyDnsRecordsResponse = TypedDict(
    "DomainVerifyDnsRecordsResponse",
    {
        "message": "Required[str]",
        "recommended_failed_records": "Required[list[dict[str, Any]]]",
    },
)

DomainVerifySpecificDnsRecordResponse = TypedDict(
    "DomainVerifySpecificDnsRecordResponse",
    {
        "message": "Required[Literal['DNS record verified successfully.']]",
    },
)

DomainUpdateProjectsRequest: TypeAlias = UpdateDomainProjectsData
DomainUpdateProjectsResponse = TypedDict(
    "DomainUpdateProjectsResponse",
    {
        "data": "Required[DomainData]",
        "message": "Required[Literal['Domain projects updated successfully.']]",
    },
)

BlockedFileTypesResponse = TypedDict(
    "BlockedFileTypesResponse",
    {
        "extensions": "Required[list[str]]",
        "mime_types": "Required[list[str]]",
    },
)

RescheduleMessageResponse = TypedDict(
    "RescheduleMessageResponse",
    {
        "message_id": "Required[str]",
        "status": "Required[MessageStatus | None]",
        "scheduled_at": "Required[str | None]",
    },
)

MessageShowResponse: TypeAlias = MessageData
CancelScheduledMessageResponse = TypedDict(
    "CancelScheduledMessageResponse",
    {
        "message_id": "Required[str]",
        "status": "Required[MessageStatus | None]",
        "scheduled_at": "Required[str | None]",
    },
)

MessageIndexResponse = TypedDict(
    "MessageIndexResponse",
    {
        "data": "Required[list[MessageListData]]",
        "links": "Required[list[str]]",
        "meta": "Required[dict[str, Any]]",
    },
)

MessageEventsResponse = TypedDict(
    "MessageEventsResponse",
    {
        "data": "Required[list[MessageEventData]]",
        "links": "Required[list[str]]",
        "meta": "Required[dict[str, Any]]",
    },
)

ProcessInboundMessageResponse = TypedDict(
    "ProcessInboundMessageResponse",
    {
        "data": "Required[dict[str, Any]]",
    },
)

ProjectIndexResponse = TypedDict(
    "ProjectIndexResponse",
    {
        "data": "Required[list[ProjectListData]]",
        "path": "Required[str | None]",
        "per_page": "Required[int]",
        "next_cursor": "Required[str | None]",
        "next_page_url": "Required[str | None]",
        "prev_cursor": "Required[str | None]",
        "prev_page_url": "Required[str | None]",
    },
)

ProjectStoreRequest: TypeAlias = StoreProjectData
ProjectStoreResponse = TypedDict(
    "ProjectStoreResponse",
    {
        "data": "Required[ProjectData]",
        "message": "Required[str]",
        "api_token": "NotRequired[str]",
    },
)


ProjectShowResponse: TypeAlias = ProjectData
ProjectUpdateRequest: TypeAlias = UpdateProjectData
ProjectUpdateResponse = TypedDict(
    "ProjectUpdateResponse",
    {
        "data": "Required[ProjectData]",
        "message": "Required[Literal['Project updated successfully.']]",
    },
)

ProjectDestroyResponse = TypedDict(
    "ProjectDestroyResponse",
    {
        "message": "Required[Literal['Project deleted successfully.']]",
    },
)

ProjectRotateTokenResponse = TypedDict(
    "ProjectRotateTokenResponse",
    {
        "data": "Required[ProjectData]",
        "new_token": "Required[str]",
        "message": "Required[Literal['API token rotated successfully. Please update your integrations.']]",
    },
)

RouteIndexResponse = TypedDict(
    "RouteIndexResponse",
    {
        "data": "Required[list[RouteListData]]",
        "path": "Required[str | None]",
        "per_page": "Required[int]",
        "next_cursor": "Required[str | None]",
        "next_page_url": "Required[str | None]",
        "prev_cursor": "Required[str | None]",
        "prev_page_url": "Required[str | None]",
    },
)

RouteStoreRequest: TypeAlias = StoreRouteData
RouteStoreResponse = TypedDict(
    "RouteStoreResponse",
    {
        "data": "Required[RouteData]",
        "message": "Required[Literal['Route created successfully.']]",
    },
)

RouteShowResponse: TypeAlias = RouteData
RouteUpdateRequest: TypeAlias = UpdateRouteData
RouteUpdateResponse = TypedDict(
    "RouteUpdateResponse",
    {
        "data": "Required[RouteData]",
        "message": "Required[Literal['Route updated successfully.']]",
    },
)

RouteDestroyResponse = TypedDict(
    "RouteDestroyResponse",
    {
        "message": "Required[Literal['Route deleted successfully.']]",
    },
)

RouteVerifyInboundDomainResponse = TypedDict(
    "RouteVerifyInboundDomainResponse",
    {
        "data": "Required[dict[str, Any]]",
    },
)


StatsIndexResponse: TypeAlias = StatsData
SuppressionIndexResponse = TypedDict(
    "SuppressionIndexResponse",
    {
        "data": "Required[list[SuppressedRecipientData]]",
        "path": "Required[str]",
        "per_page": "Required[int]",
        "next_cursor": "Required[str | None]",
        "next_page_url": "Required[str | None]",
        "prev_cursor": "Required[str | None]",
        "prev_page_url": "Required[str | None]",
    },
)


SuppressionStoreRequest: TypeAlias = StoreSuppressionData
SuppressionStoreResponse = TypedDict(
    "SuppressionStoreResponse",
    {
        "message": "Required[str | Literal['No emails were added.']]",
        "data": "Required[dict[str, Any]]",
    },
)

SuppressionDestroyResponse = TypedDict(
    "SuppressionDestroyResponse",
    {
        "success": "Required[Literal[True]]",
        "status": "Required[Literal['removed', 'review_ticket_created', 'review_ticket_exists']]",
        "message": "Required[str]",
        "confidence": "NotRequired[float]",
        "ticket_identifier": "NotRequired[str]",
    },
)


TeamShowResponse: TypeAlias = TeamData
TeamUpdateRequest: TypeAlias = UpdateTeamData
TeamUpdateResponse = TypedDict(
    "TeamUpdateResponse",
    {
        "data": "Required[TeamData]",
        "message": "Required[Literal['Team settings updated successfully.']]",
    },
)

TeamUsageResponse: TypeAlias = TeamUsageDetailData
TeamRolesResponse = TypedDict(
    "TeamRolesResponse",
    {
        "data": "Required[list[TeamRoleData]]",
    },
)

TeamMembersResponse = TypedDict(
    "TeamMembersResponse",
    {
        "data": "Required[list[TeamMemberData]]",
        "path": "Required[str | None]",
        "per_page": "Required[int]",
        "next_cursor": "Required[str | None]",
        "next_page_url": "Required[str | None]",
        "prev_cursor": "Required[str | None]",
        "prev_page_url": "Required[str | None]",
    },
)

TeamMembersShowResponse: TypeAlias = TeamMemberData
TeamMembersAssignmentUpdateRequest: TypeAlias = UpdateTeamMemberAssignmentData
TeamMembersAssignmentUpdateResponse: TypeAlias = TeamMemberData
WebhookIndexResponse = TypedDict(
    "WebhookIndexResponse",
    {
        "data": "Required[list[WebhookListData]]",
        "path": "Required[str | None]",
        "per_page": "Required[int]",
        "next_cursor": "Required[str | None]",
        "next_page_url": "Required[str | None]",
        "prev_cursor": "Required[str | None]",
        "prev_page_url": "Required[str | None]",
    },
)

WebhookStoreRequest: TypeAlias = StoreWebhookData
WebhookStoreResponse = TypedDict(
    "WebhookStoreResponse",
    {
        "data": "Required[WebhookSecretData]",
        "message": "Required[Literal['Webhook created successfully. Please save the secret as it will not be shown again.']]",
    },
)

WebhookShowResponse: TypeAlias = WebhookData
WebhookUpdateRequest: TypeAlias = UpdateWebhookData
WebhookUpdateResponse = TypedDict(
    "WebhookUpdateResponse",
    {
        "data": "Required[WebhookData]",
        "message": "Required[Literal['Webhook updated successfully.']]",
    },
)

WebhookDestroyResponse = TypedDict(
    "WebhookDestroyResponse",
    {
        "message": "Required[Literal['Webhook deleted successfully.']]",
    },
)

WebhookTestResponse = TypedDict(
    "WebhookTestResponse",
    {
        "message": "Required[Literal['Test webhook dispatched successfully. Check the deliveries endpoint for results.']]",
        "delivery_id": "Required[str]",
    },
)

WebhookRegenerateSecretResponse = TypedDict(
    "WebhookRegenerateSecretResponse",
    {
        "data": "Required[WebhookSecretData]",
        "message": "Required[Literal['Webhook secret regenerated successfully. Please update your integration.']]",
    },
)

WebhookDeliveriesResponse = TypedDict(
    "WebhookDeliveriesResponse",
    {
        "data": "Required[list[WebhookDeliveryListData]]",
        "path": "Required[str | None]",
        "per_page": "Required[int]",
        "next_cursor": "Required[str | None]",
        "next_page_url": "Required[str | None]",
        "prev_cursor": "Required[str | None]",
        "prev_page_url": "Required[str | None]",
    },
)

WebhookShowDeliveryResponse: TypeAlias = WebhookDeliveryData
SendEmailResponse: TypeAlias = SendMailResponse
SendBatchEmailResponse: TypeAlias = SendBatchMailResponse

ProjectCreatedData = TypedDict(
    "ProjectCreatedData",
    {
        "data": "Required[ProjectData]",
        "message": "Required[str]",
        "api_token": "NotRequired[str]",
    },
)


ReportForwardingRequest = TypedDict(
    "ReportForwardingRequest",
    {
        "destination": "Required[str]",
    },
)


ReportForwardingResource = TypedDict(
    "ReportForwardingResource",
    {
        "destination": "Required[str | None]",
        "verified": "Required[bool]",
        "verified_at": "Required[str | None]",
    },
)


VerifyReportForwardingRequest = TypedDict(
    "VerifyReportForwardingRequest",
    {
        "code": "Required[str]",
    },
)


UpdateReportForwardingRequest: TypeAlias = ReportForwardingRequest

GetReportForwardingResponse = TypedDict(
    "GetReportForwardingResponse",
    {
        "data": "Required[ReportForwardingResource]",
    },
)


UpdateReportForwardingResponse = TypedDict(
    "UpdateReportForwardingResponse",
    {
        "data": "Required[ReportForwardingResource]",
    },
)


VerifyReportForwardingResponse = TypedDict(
    "VerifyReportForwardingResponse",
    {
        "data": "Required[ReportForwardingResource]",
    },
)


ResendReportForwardingCodeResponse = TypedDict(
    "ResendReportForwardingCodeResponse",
    {
        "data": "Required[ReportForwardingResource]",
    },
)


AnalyticsResponseData = TypedDict(
    "AnalyticsResponseData",
    {
        "data": "Required[dict[str, Any]]",
        "meta": "Required[dict[str, Any]]",
        "pagination": "Required[list[str]]",
    },
)


AnalyticsRequestFiltersItem = TypedDict(
    "AnalyticsRequestFiltersItem",
    {
        "dimension": "Required[str]",
        "operator": "Required[Literal['eq', 'in', 'not_in', 'is_null', 'is_not_null']]",
        "values": "NotRequired[list[str]]",
    },
)


AnalyticsRequestSort = TypedDict(
    "AnalyticsRequestSort",
    {
        "metric": "Required[Literal['accepted', 'processed', 'suppressed', 'policy_rejected', 'application_failed', 'mta_accepted', 'canceled', 'messages', 'delivered', 'bounced', 'soft_bounced', 'administratively_bounced', 'deferred_recipients', 'deferred_events', 'delivery_attempts', 'attempted_recipients', 'transport_outcome_recipients', 'effective_delivered', 'open_tracked_delivered', 'click_tracked_delivered', 'out_of_band_bounced_recipients', 'out_of_band_bounce_events', 'complained', 'unsubscribed', 'human_opens', 'human_opens_events', 'human_clicks', 'human_clicks_events', 'machine_opens', 'machine_opens_events', 'machine_clicks', 'machine_clicks_events', 'privacy_opens', 'privacy_opens_events', 'privacy_clicks', 'privacy_clicks_events', 'bot_opens', 'bot_opens_events', 'bot_clicks', 'bot_clicks_events', 'scanner_opens', 'scanner_opens_events', 'scanner_clicks', 'scanner_clicks_events', 'observed_opens', 'observed_opens_events', 'observed_clicks', 'observed_clicks_events', 'delivery_rate', 'effective_delivery_rate', 'bounce_rate', 'deferral_rate', 'complaint_rate', 'human_open_rate', 'human_click_rate', 'processing_latency_p50_ms', 'processing_latency_p95_ms', 'processing_latency_p99_ms', 'processing_latency_samples', 'delivery_latency_p50_ms', 'delivery_latency_p95_ms', 'delivery_latency_p99_ms', 'delivery_latency_samples', 'total_latency_p50_ms', 'total_latency_p95_ms', 'total_latency_p99_ms', 'total_latency_samples']]",
        "direction": "Required[Literal['asc', 'desc']]",
    },
)


AnalyticsRequest = TypedDict(
    "AnalyticsRequest",
    {
        "metrics": "Required[list[Literal['accepted', 'processed', 'suppressed', 'policy_rejected', 'application_failed', 'mta_accepted', 'canceled', 'messages', 'delivered', 'bounced', 'soft_bounced', 'administratively_bounced', 'deferred_recipients', 'deferred_events', 'delivery_attempts', 'attempted_recipients', 'transport_outcome_recipients', 'effective_delivered', 'open_tracked_delivered', 'click_tracked_delivered', 'out_of_band_bounced_recipients', 'out_of_band_bounce_events', 'complained', 'unsubscribed', 'human_opens', 'human_opens_events', 'human_clicks', 'human_clicks_events', 'machine_opens', 'machine_opens_events', 'machine_clicks', 'machine_clicks_events', 'privacy_opens', 'privacy_opens_events', 'privacy_clicks', 'privacy_clicks_events', 'bot_opens', 'bot_opens_events', 'bot_clicks', 'bot_clicks_events', 'scanner_opens', 'scanner_opens_events', 'scanner_clicks', 'scanner_clicks_events', 'observed_opens', 'observed_opens_events', 'observed_clicks', 'observed_clicks_events', 'delivery_rate', 'effective_delivery_rate', 'bounce_rate', 'deferral_rate', 'complaint_rate', 'human_open_rate', 'human_click_rate', 'processing_latency_p50_ms', 'processing_latency_p95_ms', 'processing_latency_p99_ms', 'processing_latency_samples', 'delivery_latency_p50_ms', 'delivery_latency_p95_ms', 'delivery_latency_p99_ms', 'delivery_latency_samples', 'total_latency_p50_ms', 'total_latency_p95_ms', 'total_latency_p99_ms', 'total_latency_samples']]]",
        "from": "NotRequired[str]",
        "to": "NotRequired[str]",
        "timezone": "NotRequired[str]",
        "include": "NotRequired[list[Literal['summary', 'time_series', 'breakdown']]]",
        "group_by": "NotRequired[list[str]]",
        "filters": "NotRequired[list[AnalyticsRequestFiltersItem]]",
        "interval": "NotRequired[Literal['hour', 'day']]",
        "compare": "NotRequired[Literal['previous_period']]",
        "include_trend": "NotRequired[bool]",
        "sort": "NotRequired[AnalyticsRequestSort]",
        "limit": "NotRequired[int]",
        "cursor": "NotRequired[str]",
    },
)


AnalyticsResponseMetaComparison = TypedDict(
    "AnalyticsResponseMetaComparison",
    {
        "from": "Required[str]",
        "to": "Required[str]",
        "partial": "Required[bool]",
    },
)


AnalyticsResponseMeta = TypedDict(
    "AnalyticsResponseMeta",
    {
        "time_basis": "NotRequired[Literal['event']]",
        "timezone": "NotRequired[str]",
        "interval": "NotRequired[Literal['hour', 'day']]",
        "from": "NotRequired[str]",
        "to": "NotRequired[str]",
        "effective_to": "NotRequired[str]",
        "alignment": "NotRequired[Literal['hour', 'day']]",
        "generated_at": "NotRequired[str]",
        "available_since": "NotRequired[str]",
        "partial": "NotRequired[bool]",
        "ongoing": "NotRequired[bool]",
        "collection_completeness": "NotRequired[Literal['best_effort']]",
        "last_ingested_at": "NotRequired[str | None]",
        "metric_definition_version": "NotRequired[str]",
        "ranked_group_limit": "NotRequired[int]",
        "comparison": "NotRequired[AnalyticsResponseMetaComparison]",
    },
)


AnalyticsResponsePagination = TypedDict(
    "AnalyticsResponsePagination",
    {
        "total_groups": "Required[int]",
        "returned_groups": "Required[int]",
        "next_cursor": "Required[str | None]",
        "truncated": "Required[bool]",
    },
)


AnalyticsResponse = TypedDict(
    "AnalyticsResponse",
    {
        "data": "Required[AnalyticsResponsePayload]",
        "meta": "Required[AnalyticsResponseMeta]",
        "pagination": "Required[AnalyticsResponsePagination]",
    },
)


AnalyticsResponsePayloadSummaryMetrics = TypedDict(
    "AnalyticsResponsePayloadSummaryMetrics",
    {
        "accepted": "NotRequired[int | None]",
        "processed": "NotRequired[int | None]",
        "suppressed": "NotRequired[int | None]",
        "policy_rejected": "NotRequired[int | None]",
        "application_failed": "NotRequired[int | None]",
        "mta_accepted": "NotRequired[int | None]",
        "canceled": "NotRequired[int | None]",
        "messages": "NotRequired[int | None]",
        "delivered": "NotRequired[int | None]",
        "bounced": "NotRequired[int | None]",
        "soft_bounced": "NotRequired[int | None]",
        "administratively_bounced": "NotRequired[int | None]",
        "deferred_recipients": "NotRequired[int | None]",
        "deferred_events": "NotRequired[int | None]",
        "delivery_attempts": "NotRequired[int | None]",
        "attempted_recipients": "NotRequired[int | None]",
        "transport_outcome_recipients": "NotRequired[int | None]",
        "effective_delivered": "NotRequired[int | None]",
        "open_tracked_delivered": "NotRequired[int | None]",
        "click_tracked_delivered": "NotRequired[int | None]",
        "out_of_band_bounced_recipients": "NotRequired[int | None]",
        "out_of_band_bounce_events": "NotRequired[int | None]",
        "complained": "NotRequired[int | None]",
        "unsubscribed": "NotRequired[int | None]",
        "human_opens": "NotRequired[int | None]",
        "human_opens_events": "NotRequired[int | None]",
        "human_clicks": "NotRequired[int | None]",
        "human_clicks_events": "NotRequired[int | None]",
        "machine_opens": "NotRequired[int | None]",
        "machine_opens_events": "NotRequired[int | None]",
        "machine_clicks": "NotRequired[int | None]",
        "machine_clicks_events": "NotRequired[int | None]",
        "privacy_opens": "NotRequired[int | None]",
        "privacy_opens_events": "NotRequired[int | None]",
        "privacy_clicks": "NotRequired[int | None]",
        "privacy_clicks_events": "NotRequired[int | None]",
        "bot_opens": "NotRequired[int | None]",
        "bot_opens_events": "NotRequired[int | None]",
        "bot_clicks": "NotRequired[int | None]",
        "bot_clicks_events": "NotRequired[int | None]",
        "scanner_opens": "NotRequired[int | None]",
        "scanner_opens_events": "NotRequired[int | None]",
        "scanner_clicks": "NotRequired[int | None]",
        "scanner_clicks_events": "NotRequired[int | None]",
        "observed_opens": "NotRequired[int | None]",
        "observed_opens_events": "NotRequired[int | None]",
        "observed_clicks": "NotRequired[int | None]",
        "observed_clicks_events": "NotRequired[int | None]",
        "delivery_rate": "NotRequired[float | None]",
        "effective_delivery_rate": "NotRequired[float | None]",
        "bounce_rate": "NotRequired[float | None]",
        "deferral_rate": "NotRequired[float | None]",
        "complaint_rate": "NotRequired[float | None]",
        "human_open_rate": "NotRequired[float | None]",
        "human_click_rate": "NotRequired[float | None]",
        "processing_latency_p50_ms": "NotRequired[float | None]",
        "processing_latency_p95_ms": "NotRequired[float | None]",
        "processing_latency_p99_ms": "NotRequired[float | None]",
        "processing_latency_samples": "NotRequired[int | None]",
        "delivery_latency_p50_ms": "NotRequired[float | None]",
        "delivery_latency_p95_ms": "NotRequired[float | None]",
        "delivery_latency_p99_ms": "NotRequired[float | None]",
        "delivery_latency_samples": "NotRequired[int | None]",
        "total_latency_p50_ms": "NotRequired[float | None]",
        "total_latency_p95_ms": "NotRequired[float | None]",
        "total_latency_p99_ms": "NotRequired[float | None]",
        "total_latency_samples": "NotRequired[int | None]",
    },
)


AnalyticsResponsePayloadSummaryRateBasesDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadSummaryRateBasesDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryRateBasesEffectiveDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadSummaryRateBasesEffectiveDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryRateBasesBounceRate = TypedDict(
    "AnalyticsResponsePayloadSummaryRateBasesBounceRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryRateBasesDeferralRate = TypedDict(
    "AnalyticsResponsePayloadSummaryRateBasesDeferralRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryRateBasesComplaintRate = TypedDict(
    "AnalyticsResponsePayloadSummaryRateBasesComplaintRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryRateBasesHumanOpenRate = TypedDict(
    "AnalyticsResponsePayloadSummaryRateBasesHumanOpenRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryRateBasesHumanClickRate = TypedDict(
    "AnalyticsResponsePayloadSummaryRateBasesHumanClickRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryRateBases = TypedDict(
    "AnalyticsResponsePayloadSummaryRateBases",
    {
        "delivery_rate": "NotRequired[AnalyticsResponsePayloadSummaryRateBasesDeliveryRate]",
        "effective_delivery_rate": "NotRequired[AnalyticsResponsePayloadSummaryRateBasesEffectiveDeliveryRate]",
        "bounce_rate": "NotRequired[AnalyticsResponsePayloadSummaryRateBasesBounceRate]",
        "deferral_rate": "NotRequired[AnalyticsResponsePayloadSummaryRateBasesDeferralRate]",
        "complaint_rate": "NotRequired[AnalyticsResponsePayloadSummaryRateBasesComplaintRate]",
        "human_open_rate": "NotRequired[AnalyticsResponsePayloadSummaryRateBasesHumanOpenRate]",
        "human_click_rate": "NotRequired[AnalyticsResponsePayloadSummaryRateBasesHumanClickRate]",
    },
)


AnalyticsResponsePayloadSummaryPreviousMetrics = TypedDict(
    "AnalyticsResponsePayloadSummaryPreviousMetrics",
    {
        "accepted": "NotRequired[int | None]",
        "processed": "NotRequired[int | None]",
        "suppressed": "NotRequired[int | None]",
        "policy_rejected": "NotRequired[int | None]",
        "application_failed": "NotRequired[int | None]",
        "mta_accepted": "NotRequired[int | None]",
        "canceled": "NotRequired[int | None]",
        "messages": "NotRequired[int | None]",
        "delivered": "NotRequired[int | None]",
        "bounced": "NotRequired[int | None]",
        "soft_bounced": "NotRequired[int | None]",
        "administratively_bounced": "NotRequired[int | None]",
        "deferred_recipients": "NotRequired[int | None]",
        "deferred_events": "NotRequired[int | None]",
        "delivery_attempts": "NotRequired[int | None]",
        "attempted_recipients": "NotRequired[int | None]",
        "transport_outcome_recipients": "NotRequired[int | None]",
        "effective_delivered": "NotRequired[int | None]",
        "open_tracked_delivered": "NotRequired[int | None]",
        "click_tracked_delivered": "NotRequired[int | None]",
        "out_of_band_bounced_recipients": "NotRequired[int | None]",
        "out_of_band_bounce_events": "NotRequired[int | None]",
        "complained": "NotRequired[int | None]",
        "unsubscribed": "NotRequired[int | None]",
        "human_opens": "NotRequired[int | None]",
        "human_opens_events": "NotRequired[int | None]",
        "human_clicks": "NotRequired[int | None]",
        "human_clicks_events": "NotRequired[int | None]",
        "machine_opens": "NotRequired[int | None]",
        "machine_opens_events": "NotRequired[int | None]",
        "machine_clicks": "NotRequired[int | None]",
        "machine_clicks_events": "NotRequired[int | None]",
        "privacy_opens": "NotRequired[int | None]",
        "privacy_opens_events": "NotRequired[int | None]",
        "privacy_clicks": "NotRequired[int | None]",
        "privacy_clicks_events": "NotRequired[int | None]",
        "bot_opens": "NotRequired[int | None]",
        "bot_opens_events": "NotRequired[int | None]",
        "bot_clicks": "NotRequired[int | None]",
        "bot_clicks_events": "NotRequired[int | None]",
        "scanner_opens": "NotRequired[int | None]",
        "scanner_opens_events": "NotRequired[int | None]",
        "scanner_clicks": "NotRequired[int | None]",
        "scanner_clicks_events": "NotRequired[int | None]",
        "observed_opens": "NotRequired[int | None]",
        "observed_opens_events": "NotRequired[int | None]",
        "observed_clicks": "NotRequired[int | None]",
        "observed_clicks_events": "NotRequired[int | None]",
        "delivery_rate": "NotRequired[float | None]",
        "effective_delivery_rate": "NotRequired[float | None]",
        "bounce_rate": "NotRequired[float | None]",
        "deferral_rate": "NotRequired[float | None]",
        "complaint_rate": "NotRequired[float | None]",
        "human_open_rate": "NotRequired[float | None]",
        "human_click_rate": "NotRequired[float | None]",
        "processing_latency_p50_ms": "NotRequired[float | None]",
        "processing_latency_p95_ms": "NotRequired[float | None]",
        "processing_latency_p99_ms": "NotRequired[float | None]",
        "processing_latency_samples": "NotRequired[int | None]",
        "delivery_latency_p50_ms": "NotRequired[float | None]",
        "delivery_latency_p95_ms": "NotRequired[float | None]",
        "delivery_latency_p99_ms": "NotRequired[float | None]",
        "delivery_latency_samples": "NotRequired[int | None]",
        "total_latency_p50_ms": "NotRequired[float | None]",
        "total_latency_p95_ms": "NotRequired[float | None]",
        "total_latency_p99_ms": "NotRequired[float | None]",
        "total_latency_samples": "NotRequired[int | None]",
    },
)


AnalyticsResponsePayloadSummaryPreviousRateBasesDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadSummaryPreviousRateBasesDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryPreviousRateBasesEffectiveDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadSummaryPreviousRateBasesEffectiveDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryPreviousRateBasesBounceRate = TypedDict(
    "AnalyticsResponsePayloadSummaryPreviousRateBasesBounceRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryPreviousRateBasesDeferralRate = TypedDict(
    "AnalyticsResponsePayloadSummaryPreviousRateBasesDeferralRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryPreviousRateBasesComplaintRate = TypedDict(
    "AnalyticsResponsePayloadSummaryPreviousRateBasesComplaintRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryPreviousRateBasesHumanOpenRate = TypedDict(
    "AnalyticsResponsePayloadSummaryPreviousRateBasesHumanOpenRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryPreviousRateBasesHumanClickRate = TypedDict(
    "AnalyticsResponsePayloadSummaryPreviousRateBasesHumanClickRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadSummaryPreviousRateBases = TypedDict(
    "AnalyticsResponsePayloadSummaryPreviousRateBases",
    {
        "delivery_rate": "NotRequired[AnalyticsResponsePayloadSummaryPreviousRateBasesDeliveryRate]",
        "effective_delivery_rate": "NotRequired[AnalyticsResponsePayloadSummaryPreviousRateBasesEffectiveDeliveryRate]",
        "bounce_rate": "NotRequired[AnalyticsResponsePayloadSummaryPreviousRateBasesBounceRate]",
        "deferral_rate": "NotRequired[AnalyticsResponsePayloadSummaryPreviousRateBasesDeferralRate]",
        "complaint_rate": "NotRequired[AnalyticsResponsePayloadSummaryPreviousRateBasesComplaintRate]",
        "human_open_rate": "NotRequired[AnalyticsResponsePayloadSummaryPreviousRateBasesHumanOpenRate]",
        "human_click_rate": "NotRequired[AnalyticsResponsePayloadSummaryPreviousRateBasesHumanClickRate]",
    },
)


AnalyticsResponsePayloadSummaryPrevious = TypedDict(
    "AnalyticsResponsePayloadSummaryPrevious",
    {
        "metrics": "Required[AnalyticsResponsePayloadSummaryPreviousMetrics]",
        "rate_bases": "Required[AnalyticsResponsePayloadSummaryPreviousRateBases]",
    },
)


AnalyticsResponsePayloadSummary = TypedDict(
    "AnalyticsResponsePayloadSummary",
    {
        "metrics": "NotRequired[AnalyticsResponsePayloadSummaryMetrics]",
        "rate_bases": "NotRequired[AnalyticsResponsePayloadSummaryRateBases]",
        "previous": "NotRequired[AnalyticsResponsePayloadSummaryPrevious]",
        "change": "NotRequired[dict[str, dict[str, Any]]]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemMetrics = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemMetrics",
    {
        "accepted": "NotRequired[int | None]",
        "processed": "NotRequired[int | None]",
        "suppressed": "NotRequired[int | None]",
        "policy_rejected": "NotRequired[int | None]",
        "application_failed": "NotRequired[int | None]",
        "mta_accepted": "NotRequired[int | None]",
        "canceled": "NotRequired[int | None]",
        "messages": "NotRequired[int | None]",
        "delivered": "NotRequired[int | None]",
        "bounced": "NotRequired[int | None]",
        "soft_bounced": "NotRequired[int | None]",
        "administratively_bounced": "NotRequired[int | None]",
        "deferred_recipients": "NotRequired[int | None]",
        "deferred_events": "NotRequired[int | None]",
        "delivery_attempts": "NotRequired[int | None]",
        "attempted_recipients": "NotRequired[int | None]",
        "transport_outcome_recipients": "NotRequired[int | None]",
        "effective_delivered": "NotRequired[int | None]",
        "open_tracked_delivered": "NotRequired[int | None]",
        "click_tracked_delivered": "NotRequired[int | None]",
        "out_of_band_bounced_recipients": "NotRequired[int | None]",
        "out_of_band_bounce_events": "NotRequired[int | None]",
        "complained": "NotRequired[int | None]",
        "unsubscribed": "NotRequired[int | None]",
        "human_opens": "NotRequired[int | None]",
        "human_opens_events": "NotRequired[int | None]",
        "human_clicks": "NotRequired[int | None]",
        "human_clicks_events": "NotRequired[int | None]",
        "machine_opens": "NotRequired[int | None]",
        "machine_opens_events": "NotRequired[int | None]",
        "machine_clicks": "NotRequired[int | None]",
        "machine_clicks_events": "NotRequired[int | None]",
        "privacy_opens": "NotRequired[int | None]",
        "privacy_opens_events": "NotRequired[int | None]",
        "privacy_clicks": "NotRequired[int | None]",
        "privacy_clicks_events": "NotRequired[int | None]",
        "bot_opens": "NotRequired[int | None]",
        "bot_opens_events": "NotRequired[int | None]",
        "bot_clicks": "NotRequired[int | None]",
        "bot_clicks_events": "NotRequired[int | None]",
        "scanner_opens": "NotRequired[int | None]",
        "scanner_opens_events": "NotRequired[int | None]",
        "scanner_clicks": "NotRequired[int | None]",
        "scanner_clicks_events": "NotRequired[int | None]",
        "observed_opens": "NotRequired[int | None]",
        "observed_opens_events": "NotRequired[int | None]",
        "observed_clicks": "NotRequired[int | None]",
        "observed_clicks_events": "NotRequired[int | None]",
        "delivery_rate": "NotRequired[float | None]",
        "effective_delivery_rate": "NotRequired[float | None]",
        "bounce_rate": "NotRequired[float | None]",
        "deferral_rate": "NotRequired[float | None]",
        "complaint_rate": "NotRequired[float | None]",
        "human_open_rate": "NotRequired[float | None]",
        "human_click_rate": "NotRequired[float | None]",
        "processing_latency_p50_ms": "NotRequired[float | None]",
        "processing_latency_p95_ms": "NotRequired[float | None]",
        "processing_latency_p99_ms": "NotRequired[float | None]",
        "processing_latency_samples": "NotRequired[int | None]",
        "delivery_latency_p50_ms": "NotRequired[float | None]",
        "delivery_latency_p95_ms": "NotRequired[float | None]",
        "delivery_latency_p99_ms": "NotRequired[float | None]",
        "delivery_latency_samples": "NotRequired[int | None]",
        "total_latency_p50_ms": "NotRequired[float | None]",
        "total_latency_p95_ms": "NotRequired[float | None]",
        "total_latency_p99_ms": "NotRequired[float | None]",
        "total_latency_samples": "NotRequired[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemRateBasesDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemRateBasesDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemRateBasesEffectiveDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemRateBasesEffectiveDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemRateBasesBounceRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemRateBasesBounceRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemRateBasesDeferralRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemRateBasesDeferralRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemRateBasesComplaintRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemRateBasesComplaintRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemRateBasesHumanOpenRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemRateBasesHumanOpenRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemRateBasesHumanClickRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemRateBasesHumanClickRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemRateBases = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemRateBases",
    {
        "delivery_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemRateBasesDeliveryRate]",
        "effective_delivery_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemRateBasesEffectiveDeliveryRate]",
        "bounce_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemRateBasesBounceRate]",
        "deferral_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemRateBasesDeferralRate]",
        "complaint_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemRateBasesComplaintRate]",
        "human_open_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemRateBasesHumanOpenRate]",
        "human_click_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemRateBasesHumanClickRate]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemPreviousMetrics = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemPreviousMetrics",
    {
        "accepted": "NotRequired[int | None]",
        "processed": "NotRequired[int | None]",
        "suppressed": "NotRequired[int | None]",
        "policy_rejected": "NotRequired[int | None]",
        "application_failed": "NotRequired[int | None]",
        "mta_accepted": "NotRequired[int | None]",
        "canceled": "NotRequired[int | None]",
        "messages": "NotRequired[int | None]",
        "delivered": "NotRequired[int | None]",
        "bounced": "NotRequired[int | None]",
        "soft_bounced": "NotRequired[int | None]",
        "administratively_bounced": "NotRequired[int | None]",
        "deferred_recipients": "NotRequired[int | None]",
        "deferred_events": "NotRequired[int | None]",
        "delivery_attempts": "NotRequired[int | None]",
        "attempted_recipients": "NotRequired[int | None]",
        "transport_outcome_recipients": "NotRequired[int | None]",
        "effective_delivered": "NotRequired[int | None]",
        "open_tracked_delivered": "NotRequired[int | None]",
        "click_tracked_delivered": "NotRequired[int | None]",
        "out_of_band_bounced_recipients": "NotRequired[int | None]",
        "out_of_band_bounce_events": "NotRequired[int | None]",
        "complained": "NotRequired[int | None]",
        "unsubscribed": "NotRequired[int | None]",
        "human_opens": "NotRequired[int | None]",
        "human_opens_events": "NotRequired[int | None]",
        "human_clicks": "NotRequired[int | None]",
        "human_clicks_events": "NotRequired[int | None]",
        "machine_opens": "NotRequired[int | None]",
        "machine_opens_events": "NotRequired[int | None]",
        "machine_clicks": "NotRequired[int | None]",
        "machine_clicks_events": "NotRequired[int | None]",
        "privacy_opens": "NotRequired[int | None]",
        "privacy_opens_events": "NotRequired[int | None]",
        "privacy_clicks": "NotRequired[int | None]",
        "privacy_clicks_events": "NotRequired[int | None]",
        "bot_opens": "NotRequired[int | None]",
        "bot_opens_events": "NotRequired[int | None]",
        "bot_clicks": "NotRequired[int | None]",
        "bot_clicks_events": "NotRequired[int | None]",
        "scanner_opens": "NotRequired[int | None]",
        "scanner_opens_events": "NotRequired[int | None]",
        "scanner_clicks": "NotRequired[int | None]",
        "scanner_clicks_events": "NotRequired[int | None]",
        "observed_opens": "NotRequired[int | None]",
        "observed_opens_events": "NotRequired[int | None]",
        "observed_clicks": "NotRequired[int | None]",
        "observed_clicks_events": "NotRequired[int | None]",
        "delivery_rate": "NotRequired[float | None]",
        "effective_delivery_rate": "NotRequired[float | None]",
        "bounce_rate": "NotRequired[float | None]",
        "deferral_rate": "NotRequired[float | None]",
        "complaint_rate": "NotRequired[float | None]",
        "human_open_rate": "NotRequired[float | None]",
        "human_click_rate": "NotRequired[float | None]",
        "processing_latency_p50_ms": "NotRequired[float | None]",
        "processing_latency_p95_ms": "NotRequired[float | None]",
        "processing_latency_p99_ms": "NotRequired[float | None]",
        "processing_latency_samples": "NotRequired[int | None]",
        "delivery_latency_p50_ms": "NotRequired[float | None]",
        "delivery_latency_p95_ms": "NotRequired[float | None]",
        "delivery_latency_p99_ms": "NotRequired[float | None]",
        "delivery_latency_samples": "NotRequired[int | None]",
        "total_latency_p50_ms": "NotRequired[float | None]",
        "total_latency_p95_ms": "NotRequired[float | None]",
        "total_latency_p99_ms": "NotRequired[float | None]",
        "total_latency_samples": "NotRequired[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesEffectiveDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesEffectiveDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesBounceRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesBounceRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesDeferralRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesDeferralRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesComplaintRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesComplaintRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesHumanOpenRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesHumanOpenRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesHumanClickRate = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesHumanClickRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemPreviousRateBases = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemPreviousRateBases",
    {
        "delivery_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesDeliveryRate]",
        "effective_delivery_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesEffectiveDeliveryRate]",
        "bounce_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesBounceRate]",
        "deferral_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesDeferralRate]",
        "complaint_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesComplaintRate]",
        "human_open_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesHumanOpenRate]",
        "human_click_rate": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemPreviousRateBasesHumanClickRate]",
    },
)


AnalyticsResponsePayloadTimeSeriesItemPrevious = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItemPrevious",
    {
        "metrics": "Required[AnalyticsResponsePayloadTimeSeriesItemPreviousMetrics]",
        "rate_bases": "Required[AnalyticsResponsePayloadTimeSeriesItemPreviousRateBases]",
    },
)


AnalyticsResponsePayloadTimeSeriesItem = TypedDict(
    "AnalyticsResponsePayloadTimeSeriesItem",
    {
        "metrics": "Required[AnalyticsResponsePayloadTimeSeriesItemMetrics]",
        "rate_bases": "Required[AnalyticsResponsePayloadTimeSeriesItemRateBases]",
        "previous": "NotRequired[AnalyticsResponsePayloadTimeSeriesItemPrevious]",
        "change": "NotRequired[dict[str, dict[str, Any]]]",
        "from": "Required[str]",
        "to": "Required[str]",
        "available": "Required[bool]",
        "partial": "Required[bool]",
    },
)


AnalyticsResponsePayloadBreakdownItemMetrics = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemMetrics",
    {
        "accepted": "NotRequired[int | None]",
        "processed": "NotRequired[int | None]",
        "suppressed": "NotRequired[int | None]",
        "policy_rejected": "NotRequired[int | None]",
        "application_failed": "NotRequired[int | None]",
        "mta_accepted": "NotRequired[int | None]",
        "canceled": "NotRequired[int | None]",
        "messages": "NotRequired[int | None]",
        "delivered": "NotRequired[int | None]",
        "bounced": "NotRequired[int | None]",
        "soft_bounced": "NotRequired[int | None]",
        "administratively_bounced": "NotRequired[int | None]",
        "deferred_recipients": "NotRequired[int | None]",
        "deferred_events": "NotRequired[int | None]",
        "delivery_attempts": "NotRequired[int | None]",
        "attempted_recipients": "NotRequired[int | None]",
        "transport_outcome_recipients": "NotRequired[int | None]",
        "effective_delivered": "NotRequired[int | None]",
        "open_tracked_delivered": "NotRequired[int | None]",
        "click_tracked_delivered": "NotRequired[int | None]",
        "out_of_band_bounced_recipients": "NotRequired[int | None]",
        "out_of_band_bounce_events": "NotRequired[int | None]",
        "complained": "NotRequired[int | None]",
        "unsubscribed": "NotRequired[int | None]",
        "human_opens": "NotRequired[int | None]",
        "human_opens_events": "NotRequired[int | None]",
        "human_clicks": "NotRequired[int | None]",
        "human_clicks_events": "NotRequired[int | None]",
        "machine_opens": "NotRequired[int | None]",
        "machine_opens_events": "NotRequired[int | None]",
        "machine_clicks": "NotRequired[int | None]",
        "machine_clicks_events": "NotRequired[int | None]",
        "privacy_opens": "NotRequired[int | None]",
        "privacy_opens_events": "NotRequired[int | None]",
        "privacy_clicks": "NotRequired[int | None]",
        "privacy_clicks_events": "NotRequired[int | None]",
        "bot_opens": "NotRequired[int | None]",
        "bot_opens_events": "NotRequired[int | None]",
        "bot_clicks": "NotRequired[int | None]",
        "bot_clicks_events": "NotRequired[int | None]",
        "scanner_opens": "NotRequired[int | None]",
        "scanner_opens_events": "NotRequired[int | None]",
        "scanner_clicks": "NotRequired[int | None]",
        "scanner_clicks_events": "NotRequired[int | None]",
        "observed_opens": "NotRequired[int | None]",
        "observed_opens_events": "NotRequired[int | None]",
        "observed_clicks": "NotRequired[int | None]",
        "observed_clicks_events": "NotRequired[int | None]",
        "delivery_rate": "NotRequired[float | None]",
        "effective_delivery_rate": "NotRequired[float | None]",
        "bounce_rate": "NotRequired[float | None]",
        "deferral_rate": "NotRequired[float | None]",
        "complaint_rate": "NotRequired[float | None]",
        "human_open_rate": "NotRequired[float | None]",
        "human_click_rate": "NotRequired[float | None]",
        "processing_latency_p50_ms": "NotRequired[float | None]",
        "processing_latency_p95_ms": "NotRequired[float | None]",
        "processing_latency_p99_ms": "NotRequired[float | None]",
        "processing_latency_samples": "NotRequired[int | None]",
        "delivery_latency_p50_ms": "NotRequired[float | None]",
        "delivery_latency_p95_ms": "NotRequired[float | None]",
        "delivery_latency_p99_ms": "NotRequired[float | None]",
        "delivery_latency_samples": "NotRequired[int | None]",
        "total_latency_p50_ms": "NotRequired[float | None]",
        "total_latency_p95_ms": "NotRequired[float | None]",
        "total_latency_p99_ms": "NotRequired[float | None]",
        "total_latency_samples": "NotRequired[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemRateBasesDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemRateBasesDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemRateBasesEffectiveDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemRateBasesEffectiveDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemRateBasesBounceRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemRateBasesBounceRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemRateBasesDeferralRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemRateBasesDeferralRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemRateBasesComplaintRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemRateBasesComplaintRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemRateBasesHumanOpenRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemRateBasesHumanOpenRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemRateBasesHumanClickRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemRateBasesHumanClickRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemRateBases = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemRateBases",
    {
        "delivery_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemRateBasesDeliveryRate]",
        "effective_delivery_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemRateBasesEffectiveDeliveryRate]",
        "bounce_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemRateBasesBounceRate]",
        "deferral_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemRateBasesDeferralRate]",
        "complaint_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemRateBasesComplaintRate]",
        "human_open_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemRateBasesHumanOpenRate]",
        "human_click_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemRateBasesHumanClickRate]",
    },
)


AnalyticsResponsePayloadBreakdownItemPreviousMetrics = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemPreviousMetrics",
    {
        "accepted": "NotRequired[int | None]",
        "processed": "NotRequired[int | None]",
        "suppressed": "NotRequired[int | None]",
        "policy_rejected": "NotRequired[int | None]",
        "application_failed": "NotRequired[int | None]",
        "mta_accepted": "NotRequired[int | None]",
        "canceled": "NotRequired[int | None]",
        "messages": "NotRequired[int | None]",
        "delivered": "NotRequired[int | None]",
        "bounced": "NotRequired[int | None]",
        "soft_bounced": "NotRequired[int | None]",
        "administratively_bounced": "NotRequired[int | None]",
        "deferred_recipients": "NotRequired[int | None]",
        "deferred_events": "NotRequired[int | None]",
        "delivery_attempts": "NotRequired[int | None]",
        "attempted_recipients": "NotRequired[int | None]",
        "transport_outcome_recipients": "NotRequired[int | None]",
        "effective_delivered": "NotRequired[int | None]",
        "open_tracked_delivered": "NotRequired[int | None]",
        "click_tracked_delivered": "NotRequired[int | None]",
        "out_of_band_bounced_recipients": "NotRequired[int | None]",
        "out_of_band_bounce_events": "NotRequired[int | None]",
        "complained": "NotRequired[int | None]",
        "unsubscribed": "NotRequired[int | None]",
        "human_opens": "NotRequired[int | None]",
        "human_opens_events": "NotRequired[int | None]",
        "human_clicks": "NotRequired[int | None]",
        "human_clicks_events": "NotRequired[int | None]",
        "machine_opens": "NotRequired[int | None]",
        "machine_opens_events": "NotRequired[int | None]",
        "machine_clicks": "NotRequired[int | None]",
        "machine_clicks_events": "NotRequired[int | None]",
        "privacy_opens": "NotRequired[int | None]",
        "privacy_opens_events": "NotRequired[int | None]",
        "privacy_clicks": "NotRequired[int | None]",
        "privacy_clicks_events": "NotRequired[int | None]",
        "bot_opens": "NotRequired[int | None]",
        "bot_opens_events": "NotRequired[int | None]",
        "bot_clicks": "NotRequired[int | None]",
        "bot_clicks_events": "NotRequired[int | None]",
        "scanner_opens": "NotRequired[int | None]",
        "scanner_opens_events": "NotRequired[int | None]",
        "scanner_clicks": "NotRequired[int | None]",
        "scanner_clicks_events": "NotRequired[int | None]",
        "observed_opens": "NotRequired[int | None]",
        "observed_opens_events": "NotRequired[int | None]",
        "observed_clicks": "NotRequired[int | None]",
        "observed_clicks_events": "NotRequired[int | None]",
        "delivery_rate": "NotRequired[float | None]",
        "effective_delivery_rate": "NotRequired[float | None]",
        "bounce_rate": "NotRequired[float | None]",
        "deferral_rate": "NotRequired[float | None]",
        "complaint_rate": "NotRequired[float | None]",
        "human_open_rate": "NotRequired[float | None]",
        "human_click_rate": "NotRequired[float | None]",
        "processing_latency_p50_ms": "NotRequired[float | None]",
        "processing_latency_p95_ms": "NotRequired[float | None]",
        "processing_latency_p99_ms": "NotRequired[float | None]",
        "processing_latency_samples": "NotRequired[int | None]",
        "delivery_latency_p50_ms": "NotRequired[float | None]",
        "delivery_latency_p95_ms": "NotRequired[float | None]",
        "delivery_latency_p99_ms": "NotRequired[float | None]",
        "delivery_latency_samples": "NotRequired[int | None]",
        "total_latency_p50_ms": "NotRequired[float | None]",
        "total_latency_p95_ms": "NotRequired[float | None]",
        "total_latency_p99_ms": "NotRequired[float | None]",
        "total_latency_samples": "NotRequired[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemPreviousRateBasesDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemPreviousRateBasesDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemPreviousRateBasesEffectiveDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemPreviousRateBasesEffectiveDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemPreviousRateBasesBounceRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemPreviousRateBasesBounceRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemPreviousRateBasesDeferralRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemPreviousRateBasesDeferralRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemPreviousRateBasesComplaintRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemPreviousRateBasesComplaintRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemPreviousRateBasesHumanOpenRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemPreviousRateBasesHumanOpenRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemPreviousRateBasesHumanClickRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemPreviousRateBasesHumanClickRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemPreviousRateBases = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemPreviousRateBases",
    {
        "delivery_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemPreviousRateBasesDeliveryRate]",
        "effective_delivery_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemPreviousRateBasesEffectiveDeliveryRate]",
        "bounce_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemPreviousRateBasesBounceRate]",
        "deferral_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemPreviousRateBasesDeferralRate]",
        "complaint_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemPreviousRateBasesComplaintRate]",
        "human_open_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemPreviousRateBasesHumanOpenRate]",
        "human_click_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemPreviousRateBasesHumanClickRate]",
    },
)


AnalyticsResponsePayloadBreakdownItemPrevious = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemPrevious",
    {
        "metrics": "Required[AnalyticsResponsePayloadBreakdownItemPreviousMetrics]",
        "rate_bases": "Required[AnalyticsResponsePayloadBreakdownItemPreviousRateBases]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemMetrics = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemMetrics",
    {
        "accepted": "NotRequired[int | None]",
        "processed": "NotRequired[int | None]",
        "suppressed": "NotRequired[int | None]",
        "policy_rejected": "NotRequired[int | None]",
        "application_failed": "NotRequired[int | None]",
        "mta_accepted": "NotRequired[int | None]",
        "canceled": "NotRequired[int | None]",
        "messages": "NotRequired[int | None]",
        "delivered": "NotRequired[int | None]",
        "bounced": "NotRequired[int | None]",
        "soft_bounced": "NotRequired[int | None]",
        "administratively_bounced": "NotRequired[int | None]",
        "deferred_recipients": "NotRequired[int | None]",
        "deferred_events": "NotRequired[int | None]",
        "delivery_attempts": "NotRequired[int | None]",
        "attempted_recipients": "NotRequired[int | None]",
        "transport_outcome_recipients": "NotRequired[int | None]",
        "effective_delivered": "NotRequired[int | None]",
        "open_tracked_delivered": "NotRequired[int | None]",
        "click_tracked_delivered": "NotRequired[int | None]",
        "out_of_band_bounced_recipients": "NotRequired[int | None]",
        "out_of_band_bounce_events": "NotRequired[int | None]",
        "complained": "NotRequired[int | None]",
        "unsubscribed": "NotRequired[int | None]",
        "human_opens": "NotRequired[int | None]",
        "human_opens_events": "NotRequired[int | None]",
        "human_clicks": "NotRequired[int | None]",
        "human_clicks_events": "NotRequired[int | None]",
        "machine_opens": "NotRequired[int | None]",
        "machine_opens_events": "NotRequired[int | None]",
        "machine_clicks": "NotRequired[int | None]",
        "machine_clicks_events": "NotRequired[int | None]",
        "privacy_opens": "NotRequired[int | None]",
        "privacy_opens_events": "NotRequired[int | None]",
        "privacy_clicks": "NotRequired[int | None]",
        "privacy_clicks_events": "NotRequired[int | None]",
        "bot_opens": "NotRequired[int | None]",
        "bot_opens_events": "NotRequired[int | None]",
        "bot_clicks": "NotRequired[int | None]",
        "bot_clicks_events": "NotRequired[int | None]",
        "scanner_opens": "NotRequired[int | None]",
        "scanner_opens_events": "NotRequired[int | None]",
        "scanner_clicks": "NotRequired[int | None]",
        "scanner_clicks_events": "NotRequired[int | None]",
        "observed_opens": "NotRequired[int | None]",
        "observed_opens_events": "NotRequired[int | None]",
        "observed_clicks": "NotRequired[int | None]",
        "observed_clicks_events": "NotRequired[int | None]",
        "delivery_rate": "NotRequired[float | None]",
        "effective_delivery_rate": "NotRequired[float | None]",
        "bounce_rate": "NotRequired[float | None]",
        "deferral_rate": "NotRequired[float | None]",
        "complaint_rate": "NotRequired[float | None]",
        "human_open_rate": "NotRequired[float | None]",
        "human_click_rate": "NotRequired[float | None]",
        "processing_latency_p50_ms": "NotRequired[float | None]",
        "processing_latency_p95_ms": "NotRequired[float | None]",
        "processing_latency_p99_ms": "NotRequired[float | None]",
        "processing_latency_samples": "NotRequired[int | None]",
        "delivery_latency_p50_ms": "NotRequired[float | None]",
        "delivery_latency_p95_ms": "NotRequired[float | None]",
        "delivery_latency_p99_ms": "NotRequired[float | None]",
        "delivery_latency_samples": "NotRequired[int | None]",
        "total_latency_p50_ms": "NotRequired[float | None]",
        "total_latency_p95_ms": "NotRequired[float | None]",
        "total_latency_p99_ms": "NotRequired[float | None]",
        "total_latency_samples": "NotRequired[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesEffectiveDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesEffectiveDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesBounceRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesBounceRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesDeferralRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesDeferralRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesComplaintRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesComplaintRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesHumanOpenRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesHumanOpenRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesHumanClickRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesHumanClickRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemRateBases = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemRateBases",
    {
        "delivery_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesDeliveryRate]",
        "effective_delivery_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesEffectiveDeliveryRate]",
        "bounce_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesBounceRate]",
        "deferral_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesDeferralRate]",
        "complaint_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesComplaintRate]",
        "human_open_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesHumanOpenRate]",
        "human_click_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemRateBasesHumanClickRate]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemPreviousMetrics = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemPreviousMetrics",
    {
        "accepted": "NotRequired[int | None]",
        "processed": "NotRequired[int | None]",
        "suppressed": "NotRequired[int | None]",
        "policy_rejected": "NotRequired[int | None]",
        "application_failed": "NotRequired[int | None]",
        "mta_accepted": "NotRequired[int | None]",
        "canceled": "NotRequired[int | None]",
        "messages": "NotRequired[int | None]",
        "delivered": "NotRequired[int | None]",
        "bounced": "NotRequired[int | None]",
        "soft_bounced": "NotRequired[int | None]",
        "administratively_bounced": "NotRequired[int | None]",
        "deferred_recipients": "NotRequired[int | None]",
        "deferred_events": "NotRequired[int | None]",
        "delivery_attempts": "NotRequired[int | None]",
        "attempted_recipients": "NotRequired[int | None]",
        "transport_outcome_recipients": "NotRequired[int | None]",
        "effective_delivered": "NotRequired[int | None]",
        "open_tracked_delivered": "NotRequired[int | None]",
        "click_tracked_delivered": "NotRequired[int | None]",
        "out_of_band_bounced_recipients": "NotRequired[int | None]",
        "out_of_band_bounce_events": "NotRequired[int | None]",
        "complained": "NotRequired[int | None]",
        "unsubscribed": "NotRequired[int | None]",
        "human_opens": "NotRequired[int | None]",
        "human_opens_events": "NotRequired[int | None]",
        "human_clicks": "NotRequired[int | None]",
        "human_clicks_events": "NotRequired[int | None]",
        "machine_opens": "NotRequired[int | None]",
        "machine_opens_events": "NotRequired[int | None]",
        "machine_clicks": "NotRequired[int | None]",
        "machine_clicks_events": "NotRequired[int | None]",
        "privacy_opens": "NotRequired[int | None]",
        "privacy_opens_events": "NotRequired[int | None]",
        "privacy_clicks": "NotRequired[int | None]",
        "privacy_clicks_events": "NotRequired[int | None]",
        "bot_opens": "NotRequired[int | None]",
        "bot_opens_events": "NotRequired[int | None]",
        "bot_clicks": "NotRequired[int | None]",
        "bot_clicks_events": "NotRequired[int | None]",
        "scanner_opens": "NotRequired[int | None]",
        "scanner_opens_events": "NotRequired[int | None]",
        "scanner_clicks": "NotRequired[int | None]",
        "scanner_clicks_events": "NotRequired[int | None]",
        "observed_opens": "NotRequired[int | None]",
        "observed_opens_events": "NotRequired[int | None]",
        "observed_clicks": "NotRequired[int | None]",
        "observed_clicks_events": "NotRequired[int | None]",
        "delivery_rate": "NotRequired[float | None]",
        "effective_delivery_rate": "NotRequired[float | None]",
        "bounce_rate": "NotRequired[float | None]",
        "deferral_rate": "NotRequired[float | None]",
        "complaint_rate": "NotRequired[float | None]",
        "human_open_rate": "NotRequired[float | None]",
        "human_click_rate": "NotRequired[float | None]",
        "processing_latency_p50_ms": "NotRequired[float | None]",
        "processing_latency_p95_ms": "NotRequired[float | None]",
        "processing_latency_p99_ms": "NotRequired[float | None]",
        "processing_latency_samples": "NotRequired[int | None]",
        "delivery_latency_p50_ms": "NotRequired[float | None]",
        "delivery_latency_p95_ms": "NotRequired[float | None]",
        "delivery_latency_p99_ms": "NotRequired[float | None]",
        "delivery_latency_samples": "NotRequired[int | None]",
        "total_latency_p50_ms": "NotRequired[float | None]",
        "total_latency_p95_ms": "NotRequired[float | None]",
        "total_latency_p99_ms": "NotRequired[float | None]",
        "total_latency_samples": "NotRequired[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesEffectiveDeliveryRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesEffectiveDeliveryRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesBounceRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesBounceRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesDeferralRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesDeferralRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesComplaintRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesComplaintRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesHumanOpenRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesHumanOpenRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesHumanClickRate = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesHumanClickRate",
    {
        "numerator": "Required[int | None]",
        "denominator": "Required[int | None]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBases = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBases",
    {
        "delivery_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesDeliveryRate]",
        "effective_delivery_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesEffectiveDeliveryRate]",
        "bounce_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesBounceRate]",
        "deferral_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesDeferralRate]",
        "complaint_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesComplaintRate]",
        "human_open_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesHumanOpenRate]",
        "human_click_rate": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBasesHumanClickRate]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItemPrevious = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItemPrevious",
    {
        "metrics": "Required[AnalyticsResponsePayloadBreakdownItemTrendItemPreviousMetrics]",
        "rate_bases": "Required[AnalyticsResponsePayloadBreakdownItemTrendItemPreviousRateBases]",
    },
)


AnalyticsResponsePayloadBreakdownItemTrendItem = TypedDict(
    "AnalyticsResponsePayloadBreakdownItemTrendItem",
    {
        "metrics": "Required[AnalyticsResponsePayloadBreakdownItemTrendItemMetrics]",
        "rate_bases": "Required[AnalyticsResponsePayloadBreakdownItemTrendItemRateBases]",
        "previous": "NotRequired[AnalyticsResponsePayloadBreakdownItemTrendItemPrevious]",
        "change": "NotRequired[dict[str, dict[str, Any]]]",
        "from": "Required[str]",
        "to": "Required[str]",
        "available": "Required[bool]",
        "partial": "Required[bool]",
    },
)


AnalyticsResponsePayloadBreakdownItem = TypedDict(
    "AnalyticsResponsePayloadBreakdownItem",
    {
        "metrics": "Required[AnalyticsResponsePayloadBreakdownItemMetrics]",
        "rate_bases": "Required[AnalyticsResponsePayloadBreakdownItemRateBases]",
        "previous": "NotRequired[AnalyticsResponsePayloadBreakdownItemPrevious]",
        "change": "NotRequired[dict[str, dict[str, Any]]]",
        "dimensions": "Required[dict[str, str | None]]",
        "trend": "NotRequired[list[AnalyticsResponsePayloadBreakdownItemTrendItem]]",
    },
)


AnalyticsResponsePayload = TypedDict(
    "AnalyticsResponsePayload",
    {
        "summary": "NotRequired[AnalyticsResponsePayloadSummary]",
        "time_series": "NotRequired[list[AnalyticsResponsePayloadTimeSeriesItem]]",
        "breakdown": "NotRequired[list[AnalyticsResponsePayloadBreakdownItem]]",
    },
)
