"""Generated type definitions for the Lettermint SDK."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

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
        "settings": "NotRequired[dict[str, Any] | None]",
        "html": "NotRequired[str | None]",
        "text": "NotRequired[str | None]",
        "attachments": "NotRequired[list[dict[str, Any]]]",
    },
)

SendBatchMailRequest: TypeAlias = list[dict[str, Any]]
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

MessageRecipientData = TypedDict(
    "MessageRecipientData",
    {
        "email": "Required[str]",
        "name": "Required[str | None]",
    },
)

MessageType: TypeAlias = Literal["inbound", "outbound"]
SpamSymbol = TypedDict(
    "SpamSymbol",
    {
        "name": "Required[str]",
        "score": "Required[float]",
        "options": "Required[list[str]]",
        "description": "Required[str | None]",
    },
)

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
    },
)

ProjectListData = TypedDict(
    "ProjectListData",
    {
        "id": "Required[str]",
        "name": "Required[str]",
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
    "messages:read",
    "messages:read_content",
    "messages:send",
    "suppressions:read",
    "suppressions:add",
    "suppressions:remove",
]
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
        "initial_routes": "NotRequired[InitialRoutes]",
        "short_token": "NotRequired[bool]",
    },
)

StoreRouteData = TypedDict(
    "StoreRouteData",
    {
        "name": "Required[str]",
        "route_type": "Required[RouteType]",
        "slug": "NotRequired[str | None]",
    },
)

SuppressionReason: TypeAlias = Literal["spam_complaint", "hard_bounce", "unsubscribe", "manual"]
SuppressionScope: TypeAlias = Literal["global", "team", "project", "route"]
StoreSuppressionData = TypedDict(
    "StoreSuppressionData",
    {
        "email": "NotRequired[str | None]",
        "emails": "NotRequired[list[str] | None]",
        "reason": "Required[SuppressionReason]",
        "scope": "Required[SuppressionScope]",
        "route_id": "NotRequired[str | None]",
        "project_id": "NotRequired[str | None]",
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
    "suppression.added",
    "suppression.removed",
    "webhook.test",
]
StoreWebhookData = TypedDict(
    "StoreWebhookData",
    {
        "route_id": "Required[str]",
        "name": "Required[str]",
        "url": "Required[str]",
        "events": "Required[list[WebhookEvent]]",
        "enabled": "NotRequired[bool | None]",
        "include_machine_events": "NotRequired[bool | None]",
    },
)

SuppressionType: TypeAlias = Literal["email", "domain", "extension"]
SuppressionSourceMessageData = TypedDict(
    "SuppressionSourceMessageData",
    {
        "id": "Required[str]",
        "available": "Required[bool]",
        "subject": "Required[str | None]",
        "created_at": "Required[str | None]",
    },
)

SuppressedRecipientData = TypedDict(
    "SuppressedRecipientData",
    {
        "id": "Required[str]",
        "type": "Required[SuppressionType]",
        "value": "Required[str]",
        "reason": "Required[SuppressionReason]",
        "scope": "Required[SuppressionScope]",
        "project_id": "Required[str | None]",
        "route_id": "Required[str | None]",
        "source_message": "NotRequired[SuppressionSourceMessageData | None]",
        "created_at": "Required[str]",
        "updated_at": "Required[str]",
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
    },
)

UpdateTeamData = TypedDict(
    "UpdateTeamData",
    {
        "name": "NotRequired[str | None]",
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
    },
)

WebhookData = TypedDict(
    "WebhookData",
    {
        "id": "Required[str]",
        "route_id": "Required[str]",
        "name": "Required[str]",
        "url": "Required[str]",
        "events": "Required[list[str]]",
        "enabled": "Required[bool]",
        "include_machine_events": "Required[bool]",
        "secret": "NotRequired[str]",
        "last_called_at": "Required[str | None]",
        "created_at": "Required[str]",
        "updated_at": "Required[str]",
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
    },
)

WebhookDeliveryListData = TypedDict(
    "WebhookDeliveryListData",
    {
        "id": "Required[str]",
        "webhook_id": "Required[str]",
        "event_type": "Required[WebhookEvent]",
        "status": "Required[WebhookDeliveryStatus]",
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
        "route_id": "Required[str]",
        "name": "Required[str]",
        "url": "Required[str]",
        "events": "Required[list[WebhookEvent]]",
        "enabled": "Required[bool]",
        "last_called_at": "Required[str | None]",
        "created_at": "Required[str]",
        "updated_at": "Required[str]",
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
        "status": "Required[MessageStatus]",
        "scheduled_at": "NotRequired[str]",
    },
)

RescheduleMessageRequest = TypedDict(
    "RescheduleMessageRequest",
    {"scheduled_at": "Required[str]"},
)
RescheduleMessageResponse = TypedDict(
    "RescheduleMessageResponse",
    {
        "message_id": "Required[str]",
        "status": "Required[MessageStatus | None]",
        "scheduled_at": "Required[str | None]",
    },
)

SendBatchMailResponse: TypeAlias = list[dict[str, Any]]
PingResponse: TypeAlias = Literal[200]
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

MessageIndexResponse = TypedDict(
    "MessageIndexResponse",
    {
        "data": "Required[list[MessageListData]]",
        "links": "Required[list[str]]",
        "meta": "Required[dict[str, Any]]",
    },
)

MessageShowResponse: TypeAlias = MessageData
ProcessInboundMessageResponse = TypedDict(
    "ProcessInboundMessageResponse",
    {
        "data": "Required[dict[str, str | int]]",
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
        "message": "Required[Literal['Project created successfully.']]",
        "api_token": "Required[str]",
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
        "path": "Required[str | None]",
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
        "success": "Required[bool]",
        "status": "Required[Literal['removed']]",
        "message": "Required[str]",
        "confidence": "NotRequired[float]",
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
        "data": "Required[WebhookData]",
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
        "data": "Required[WebhookData]",
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
