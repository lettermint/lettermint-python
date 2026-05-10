"""Generated type definitions for the Lettermint SDK."""

from __future__ import annotations

from typing import Any, Literal, TypedDict, Union

from typing_extensions import NotRequired, Required, TypeAlias

MessageStatus: TypeAlias = Literal['pending', 'queued', 'suppressed', 'processed', 'delivered', 'opened', 'clicked', 'soft_bounced', 'hard_bounced', 'spam_complaint', 'failed', 'blocked', 'policy_rejected', 'unsubscribed']
SendMailRequest = TypedDict(
    'SendMailRequest',
    {
    'route': 'NotRequired[str]',
    'from': 'Required[str]',
    'subject': 'Required[str]',
    'tag': 'NotRequired[str | None]',
    'html': 'NotRequired[str | None]',
    'text': 'NotRequired[str | None]',
    'to': 'Required[list[str]]',
    'cc': 'NotRequired[list[str]]',
    'bcc': 'NotRequired[list[str]]',
    'reply_to': 'NotRequired[list[str]]',
    'headers': 'NotRequired[dict[str, str]]',
    'metadata': 'NotRequired[dict[str, str]]',
    'settings': 'NotRequired[dict[str, Any] | None]',
    'attachments': 'NotRequired[list[dict[str, Any]]]',
    },
)

SendBatchMailRequest: TypeAlias = list[dict[str, Any]]
AttachmentDelivery: TypeAlias = Literal['inline', 'url']
DnsRecordStatus: TypeAlias = Literal['active', 'failed', 'pending']
RecordType: TypeAlias = Literal['TXT', 'CNAME', 'MX']
DomainDnsRecordData = TypedDict(
    'DomainDnsRecordData',
    {
    'id': 'Required[str]',
    'type': 'Required[RecordType]',
    'hostname': 'Required[str]',
    'fqdn': 'Required[str]',
    'content': 'Required[str]',
    'status': 'Required[DnsRecordStatus]',
    'verified_at': 'Required[str | None]',
    'last_checked_at': 'Required[str | None]',
    },
)

DomainData = TypedDict(
    'DomainData',
    {
    'id': 'Required[str]',
    'domain': 'Required[str]',
    'status_changed_at': 'Required[str | None]',
    'dns_records': 'NotRequired[list[DomainDnsRecordData]]',
    'projects': 'NotRequired[list[dict[str, Any]]]',
    'created_at': 'Required[str]',
    },
)

DomainStatus: TypeAlias = Literal['verified', 'partially_verified', 'pending_verification', 'failed_verification']
DomainListData = TypedDict(
    'DomainListData',
    {
    'id': 'Required[str]',
    'domain': 'Required[str]',
    'status': 'Required[DomainStatus]',
    'status_changed_at': 'Required[str | None]',
    'created_at': 'Required[str]',
    },
)

InitialRoutes: TypeAlias = Literal['both', 'transactional', 'broadcast']
MessageAttachmentData = TypedDict(
    'MessageAttachmentData',
    {
    'size': 'Required[int]',
    'filename': 'Required[str]',
    'content_id': 'Required[str | None]',
    'content_type': 'Required[str]',
    },
)

MessageRecipientData = TypedDict(
    'MessageRecipientData',
    {
    'email': 'Required[str]',
    'name': 'Required[str | None]',
    },
)

SpamSymbol = TypedDict(
    'SpamSymbol',
    {
    'name': 'Required[str]',
    'score': 'Required[float]',
    'options': 'Required[list[str]]',
    'description': 'Required[str | None]',
    },
)

MessageType: TypeAlias = Literal['inbound', 'outbound']
MessageData = TypedDict(
    'MessageData',
    {
    'id': 'Required[str]',
    'type': 'Required[MessageType]',
    'status': 'Required[MessageStatus]',
    'status_changed_at': 'Required[str | None]',
    'tag': 'Required[str | None]',
    'from_email': 'Required[str]',
    'from_name': 'Required[str | None]',
    'reply_to': 'Required[list[str] | None]',
    'subject': 'Required[str | None]',
    'to': 'Required[list[MessageRecipientData] | None]',
    'cc': 'Required[list[MessageRecipientData] | None]',
    'bcc': 'Required[list[MessageRecipientData] | None]',
    'attachments': 'Required[list[MessageAttachmentData] | None]',
    'metadata': 'Required[dict[str, str] | None]',
    'spam_score': 'NotRequired[float | None]',
    'spam_symbols': 'NotRequired[list[SpamSymbol]]',
    'route_id': 'Required[str]',
    'created_at': 'Required[str]',
    },
)

MessageEventType: TypeAlias = Literal['queued', 'processed', 'suppressed', 'delivered', 'soft_bounced', 'hard_bounced', 'spam_complaint', 'failed', 'blocked', 'policy_rejected', 'unsubscribed', 'opened', 'clicked', 'inbound_received', 'inbound_queued', 'inbound_spam_blocked', 'inbound_processed', 'inbound_retry']
MessageEventData = TypedDict(
    'MessageEventData',
    {
    'message_id': 'Required[str]',
    'event': 'Required[MessageEventType]',
    'metadata': 'Required[dict[str, Any] | None]',
    'timestamp': 'Required[str]',
    },
)

MessageListData = TypedDict(
    'MessageListData',
    {
    'id': 'Required[str]',
    'type': 'Required[MessageType]',
    'status': 'Required[MessageStatus]',
    'from_email': 'Required[str]',
    'from_name': 'Required[str | None]',
    'subject': 'Required[str | None]',
    'to': 'Required[list[MessageRecipientData] | None]',
    'cc': 'Required[list[MessageRecipientData] | None]',
    'bcc': 'Required[list[MessageRecipientData] | None]',
    'reply_to': 'Required[list[str] | None]',
    'tag': 'Required[str | None]',
    'created_at': 'Required[str]',
    },
)

MessageStatsData = TypedDict(
    'MessageStatsData',
    {
    'messages_transactional': 'Required[int]',
    'messages_broadcast': 'Required[int]',
    'messages_inbound': 'Required[int]',
    'deliverability': 'Required[float]',
    },
)

Plan: TypeAlias = Literal['free', 'starter', 'growth', 'pro']
UserData = TypedDict(
    'UserData',
    {
    'id': 'Required[str]',
    'name': 'Required[str]',
    'email': 'Required[str]',
    'avatar': 'Required[str | None]',
    },
)

TeamMemberData = TypedDict(
    'TeamMemberData',
    {
    'id': 'Required[str]',
    'user': 'NotRequired[UserData]',
    'role': 'Required[str | None]',
    'joined_at': 'Required[str | None]',
    },
)

RouteType: TypeAlias = Literal['transactional', 'broadcast', 'inbound']
RouteStatisticData = TypedDict(
    'RouteStatisticData',
    {
    'date': 'Required[str]',
    'sent_count': 'Required[int]',
    'delivered_count': 'Required[int]',
    'opened_count': 'Required[int]',
    'clicked_count': 'Required[int]',
    'hard_bounce_count': 'Required[int]',
    'spam_complaint_count': 'Required[int]',
    'inbound_received_count': 'Required[int]',
    'effective_opened_count': 'Required[int | None]',
    'machine_opened_count': 'Required[int | None]',
    'machine_clicked_count': 'Required[int | None]',
    },
)

RouteData = TypedDict(
    'RouteData',
    {
    'id': 'Required[str]',
    'project_id': 'Required[str]',
    'slug': 'Required[str]',
    'name': 'Required[str]',
    'route_type': 'Required[RouteType]',
    'is_default': 'Required[bool]',
    'inbound_address': 'NotRequired[str]',
    'inbound_domain': 'NotRequired[str]',
    'inbound_domain_verified_at': 'NotRequired[str]',
    'inbound_spam_threshold': 'NotRequired[float]',
    'attachment_delivery': 'NotRequired[AttachmentDelivery]',
    'project': 'NotRequired[ProjectData]',
    'webhooks_count': 'NotRequired[int]',
    'suppressed_recipients_count': 'NotRequired[int]',
    'statistics': 'NotRequired[Union[dict[str, Any], list[RouteStatisticData]]]',
    'created_at': 'Required[str]',
    'updated_at': 'Required[str]',
    },
)

ProjectData = TypedDict(
    'ProjectData',
    {
    'id': 'Required[str]',
    'name': 'Required[str]',
    'smtp_enabled': 'Required[bool]',
    'default_route_id': 'Required[str | None]',
    'token_generated_at': 'Required[str | None]',
    'token_last_used_at': 'Required[str | None]',
    'token_last_used_ip': 'Required[str | None]',
    'routes': 'NotRequired[list[RouteData]]',
    'routes_count': 'NotRequired[int]',
    'domains': 'NotRequired[list[DomainData]]',
    'domains_count': 'NotRequired[int]',
    'team_members': 'NotRequired[list[TeamMemberData]]',
    'team_members_count': 'NotRequired[int]',
    'last_28_days': 'NotRequired[Union[MessageStatsData, Any]]',
    'created_at': 'Required[str]',
    'updated_at': 'Required[str]',
    },
)

ProjectListData = TypedDict(
    'ProjectListData',
    {
    'id': 'Required[str]',
    'name': 'Required[str]',
    'smtp_enabled': 'Required[bool]',
    'routes_count': 'Required[int]',
    'domains_count': 'Required[int]',
    'team_members_count': 'Required[int]',
    'last_28_days': 'Required[MessageStatsData]',
    'created_at': 'Required[str]',
    'updated_at': 'Required[str]',
    },
)

RouteListData = TypedDict(
    'RouteListData',
    {
    'id': 'Required[str]',
    'slug': 'Required[str]',
    'name': 'Required[str]',
    'route_type': 'Required[RouteType]',
    'is_default': 'Required[bool]',
    'webhooks_count': 'Required[int]',
    'suppressed_recipients_count': 'Required[int]',
    'created_at': 'Required[str]',
    'updated_at': 'Required[str]',
    },
)

StatsTypeData = TypedDict(
    'StatsTypeData',
    {
    'sent': 'Required[int]',
    'hard_bounced': 'Required[int]',
    'spam_complaints': 'Required[int]',
    },
)

StatsInboundData = TypedDict(
    'StatsInboundData',
    {
    'received': 'Required[int]',
    },
)

StatsDailyData = TypedDict(
    'StatsDailyData',
    {
    'date': 'Required[str]',
    'sent': 'Required[int]',
    'delivered': 'Required[int]',
    'hard_bounced': 'Required[int]',
    'spam_complaints': 'Required[int]',
    'opened': 'Required[int | None]',
    'clicked': 'Required[int | None]',
    'inbound': 'Required[StatsInboundData]',
    'transactional': 'Required[Union[StatsTypeData, Any]]',
    'broadcast': 'Required[Union[StatsTypeData, Any]]',
    'effective_opened': 'Required[int | None]',
    'machine_opened': 'Required[int | None]',
    'machine_clicked': 'Required[int | None]',
    },
)

StatsTotalsData = TypedDict(
    'StatsTotalsData',
    {
    'sent': 'Required[int]',
    'delivered': 'Required[int]',
    'hard_bounced': 'Required[int]',
    'spam_complaints': 'Required[int]',
    'opened': 'Required[int | None]',
    'clicked': 'Required[int | None]',
    'inbound': 'Required[StatsInboundData]',
    'transactional': 'Required[Union[StatsTypeData, Any]]',
    'broadcast': 'Required[Union[StatsTypeData, Any]]',
    'effective_opened': 'Required[int | None]',
    'machine_opened': 'Required[int | None]',
    'machine_clicked': 'Required[int | None]',
    },
)

StatsData = TypedDict(
    'StatsData',
    {
    'from': 'Required[str]',
    'to': 'Required[str]',
    'totals': 'Required[StatsTotalsData]',
    'daily': 'Required[list[StatsDailyData]]',
    },
)

StatsRequestData = TypedDict(
    'StatsRequestData',
    {
    'from': 'Required[str]',
    'to': 'Required[str]',
    'project_id': 'NotRequired[str | None]',
    'include_machine': 'NotRequired[bool]',
    },
)

StoreDomainData = TypedDict(
    'StoreDomainData',
    {
    'domain': 'Required[str]',
    },
)

StoreProjectData = TypedDict(
    'StoreProjectData',
    {
    'name': 'Required[str]',
    'smtp_enabled': 'NotRequired[bool]',
    'initial_routes': 'NotRequired[InitialRoutes]',
    },
)

StoreRouteData = TypedDict(
    'StoreRouteData',
    {
    'name': 'Required[str]',
    'route_type': 'Required[RouteType]',
    'slug': 'NotRequired[str | None]',
    },
)

SuppressionReason: TypeAlias = Literal['spam_complaint', 'hard_bounce', 'unsubscribe', 'manual']
StoreSuppressionData = TypedDict(
    'StoreSuppressionData',
    {
    'email': 'NotRequired[str | None]',
    'reason': 'Required[SuppressionReason]',
    'scope': "Required[Literal['team', 'project', 'route']]",
    'route_id': 'NotRequired[str | None]',
    'project_id': 'NotRequired[str | None]',
    'emails': 'NotRequired[list[str] | None]',
    },
)

WebhookEvent: TypeAlias = Literal['message.created', 'message.sent', 'message.delivered', 'message.hard_bounced', 'message.soft_bounced', 'message.spam_complaint', 'message.failed', 'message.suppressed', 'message.unsubscribed', 'message.opened', 'message.clicked', 'message.inbound', 'message.policy_rejected', 'webhook.test']
StoreWebhookData = TypedDict(
    'StoreWebhookData',
    {
    'route_id': 'Required[str]',
    'name': 'Required[str]',
    'url': 'Required[str]',
    'enabled': 'NotRequired[bool | None]',
    'include_machine_events': 'NotRequired[bool | None]',
    'events': 'Required[list[WebhookEvent]]',
    },
)

SuppressionScope: TypeAlias = Literal['global', 'team', 'project', 'route']
SuppressionType: TypeAlias = Literal['email', 'domain', 'extension']
SuppressedRecipientData = TypedDict(
    'SuppressedRecipientData',
    {
    'id': 'Required[str]',
    'type': 'Required[SuppressionType]',
    'value': 'Required[str]',
    'reason': 'Required[SuppressionReason]',
    'scope': 'Required[SuppressionScope]',
    'project_id': 'Required[str | None]',
    'route_id': 'Required[str | None]',
    'created_at': 'Required[str]',
    'updated_at': 'Required[str]',
    },
)

TeamAddonData = TypedDict(
    'TeamAddonData',
    {
    'type': 'Required[str | None]',
    'expires_at': 'Required[str | None]',
    },
)

VolumeTier: TypeAlias = Literal[300, 10000, 50000, 125000, 500000, 750000, 1000000, 1500000]
TeamType: TypeAlias = Literal['personal', 'business']
TeamData = TypedDict(
    'TeamData',
    {
    'id': 'Required[str]',
    'name': 'Required[str]',
    'type': 'Required[TeamType]',
    'plan': 'Required[Plan]',
    'tier': 'Required[VolumeTier]',
    'verified_at': 'Required[str | None]',
    'features': 'NotRequired[list[str]]',
    'addons': 'NotRequired[list[TeamAddonData]]',
    'created_at': 'Required[str]',
    'domains_count': 'NotRequired[int]',
    'projects_count': 'NotRequired[int]',
    'members_count': 'NotRequired[int]',
    },
)

TeamUsagePeriodData = TypedDict(
    'TeamUsagePeriodData',
    {
    'usage': 'Required[int]',
    'last_incremented_at': 'Required[str | None]',
    'period_start': 'Required[str]',
    'period_end': 'Required[str]',
    },
)

TeamUsageDetailData = TypedDict(
    'TeamUsageDetailData',
    {
    'current_period': 'Required[TeamUsagePeriodData]',
    'historical_usage': 'Required[list[TeamUsagePeriodData]]',
    },
)

UpdateDomainProjectsData = TypedDict(
    'UpdateDomainProjectsData',
    {
    'project_ids': 'Required[list[str]]',
    },
)

UpdateProjectData = TypedDict(
    'UpdateProjectData',
    {
    'name': 'NotRequired[str | None]',
    'smtp_enabled': 'NotRequired[bool | None]',
    'default_route_id': 'NotRequired[str | None]',
    },
)

UpdateProjectMembersData = TypedDict(
    'UpdateProjectMembersData',
    {
    'team_member_ids': 'Required[list[str]]',
    },
)

UpdateRouteData = TypedDict(
    'UpdateRouteData',
    {
    'name': 'NotRequired[str | None]',
    'settings': 'NotRequired[dict[str, Any]]',
    'inbound_settings': 'NotRequired[dict[str, Any]]',
    },
)

UpdateTeamData = TypedDict(
    'UpdateTeamData',
    {
    'name': 'NotRequired[str | None]',
    },
)

UpdateWebhookData = TypedDict(
    'UpdateWebhookData',
    {
    'name': 'NotRequired[str]',
    'url': 'NotRequired[str]',
    'enabled': 'NotRequired[bool]',
    'include_machine_events': 'NotRequired[bool]',
    'events': 'NotRequired[list[WebhookEvent]]',
    },
)

WebhookData = TypedDict(
    'WebhookData',
    {
    'id': 'Required[str]',
    'route_id': 'Required[str]',
    'name': 'Required[str]',
    'url': 'Required[str]',
    'events': 'Required[list[str]]',
    'enabled': 'Required[bool]',
    'include_machine_events': 'Required[bool]',
    'secret': 'NotRequired[str]',
    'last_called_at': 'Required[str | None]',
    'created_at': 'Required[str]',
    'updated_at': 'Required[str]',
    },
)

WebhookDeliveryStatus: TypeAlias = Literal['pending', 'success', 'failed', 'client_error', 'server_error', 'timeout']
WebhookDeliveryData = TypedDict(
    'WebhookDeliveryData',
    {
    'id': 'Required[str]',
    'webhook_id': 'Required[str]',
    'event_type': 'Required[WebhookEvent]',
    'status': 'Required[WebhookDeliveryStatus]',
    'attempt_number': 'Required[int]',
    'http_status_code': 'Required[int | None]',
    'duration_ms': 'Required[int | None]',
    'payload': 'Required[list[str]]',
    'response_body': 'Required[str | None]',
    'response_headers': 'Required[list[str] | None]',
    'error_message': 'Required[str | None]',
    'delivered_at': 'Required[str | None]',
    'timestamp': 'Required[str]',
    },
)

WebhookDeliveryListData = TypedDict(
    'WebhookDeliveryListData',
    {
    'id': 'Required[str]',
    'webhook_id': 'Required[str]',
    'event_type': 'Required[WebhookEvent]',
    'status': 'Required[WebhookDeliveryStatus]',
    'attempt_number': 'Required[int]',
    'http_status_code': 'Required[int | None]',
    'duration_ms': 'Required[int | None]',
    'delivered_at': 'Required[str | None]',
    'created_at': 'Required[str]',
    },
)

WebhookListData = TypedDict(
    'WebhookListData',
    {
    'id': 'Required[str]',
    'route_id': 'Required[str]',
    'name': 'Required[str]',
    'url': 'Required[str]',
    'events': 'Required[list[WebhookEvent]]',
    'enabled': 'Required[bool]',
    'last_called_at': 'Required[str | None]',
    'created_at': 'Required[str]',
    'updated_at': 'Required[str]',
    },
)

EmailAttachment = TypedDict(
    'EmailAttachment',
    {
        'filename': 'Required[str]',
        'content': 'Required[str]',
        'content_type': 'NotRequired[str | None]',
        'content_id': 'NotRequired[str | None]',
    },
)
EmailPayload: TypeAlias = SendMailRequest
EmailStatus: TypeAlias = MessageStatus
SendMailResponse = TypedDict(
    'SendMailResponse',
    {
    'message_id': 'Required[str]',
    'status': 'Required[MessageStatus]',
    },
)

SendBatchMailResponse: TypeAlias = list[dict[str, Any]]
PingResponse: TypeAlias = Literal[200]
DomainIndexResponse = TypedDict(
    'DomainIndexResponse',
    {
    'data': 'Required[list[DomainListData]]',
    'path': 'Required[str | None]',
    'per_page': 'Required[int]',
    'next_cursor': 'Required[str | None]',
    'next_page_url': 'Required[str | None]',
    'prev_cursor': 'Required[str | None]',
    'prev_page_url': 'Required[str | None]',
    },
)

DomainStoreRequest: TypeAlias = StoreDomainData
DomainStoreResponse: TypeAlias = DomainData
DomainShowResponse: TypeAlias = DomainData
DomainDestroyResponse = TypedDict(
    'DomainDestroyResponse',
    {
    'message': "Required[Literal['Domain deleted successfully.']]",
    },
)

DomainVerifyDnsRecordsResponse = TypedDict(
    'DomainVerifyDnsRecordsResponse',
    {
    'message': 'Required[str]',
    },
)

DomainVerifySpecificDnsRecordResponse = TypedDict(
    'DomainVerifySpecificDnsRecordResponse',
    {
    'message': "Required[Literal['DNS record verified successfully.']]",
    },
)

DomainUpdateProjectsRequest: TypeAlias = UpdateDomainProjectsData
DomainUpdateProjectsResponse = TypedDict(
    'DomainUpdateProjectsResponse',
    {
    'data': 'Required[DomainData]',
    'message': "Required[Literal['Domain projects updated successfully.']]",
    },
)

MessageIndexResponse: TypeAlias = Union[dict[str, Any], list[MessageListData]]
MessageShowResponse: TypeAlias = MessageData
MessageEventsResponse = TypedDict(
    'MessageEventsResponse',
    {
    'data': 'Required[list[MessageEventData]]',
    'path': 'Required[str | None]',
    'per_page': 'Required[int]',
    'next_cursor': 'Required[str | None]',
    'next_page_url': 'Required[str | None]',
    'prev_cursor': 'Required[str | None]',
    'prev_page_url': 'Required[str | None]',
    },
)

ProjectIndexResponse = TypedDict(
    'ProjectIndexResponse',
    {
    'data': 'Required[list[ProjectListData]]',
    'path': 'Required[str | None]',
    'per_page': 'Required[int]',
    'next_cursor': 'Required[str | None]',
    'next_page_url': 'Required[str | None]',
    'prev_cursor': 'Required[str | None]',
    'prev_page_url': 'Required[str | None]',
    },
)

ProjectStoreRequest: TypeAlias = StoreProjectData
ProjectStoreResponse = TypedDict(
    'ProjectStoreResponse',
    {
    'data': 'Required[ProjectData]',
    'message': "Required[Literal['Project created successfully.']]",
    'api_token': 'Required[str]',
    },
)

ProjectShowResponse: TypeAlias = ProjectData
ProjectUpdateRequest: TypeAlias = UpdateProjectData
ProjectUpdateResponse = TypedDict(
    'ProjectUpdateResponse',
    {
    'data': 'Required[ProjectData]',
    'message': "Required[Literal['Project updated successfully.']]",
    },
)

ProjectDestroyResponse = TypedDict(
    'ProjectDestroyResponse',
    {
    'message': "Required[Literal['Project deleted successfully.']]",
    },
)

ProjectRotateTokenResponse = TypedDict(
    'ProjectRotateTokenResponse',
    {
    'data': 'Required[ProjectData]',
    'new_token': 'Required[str]',
    'message': "Required[Literal['API token rotated successfully. Please update your integrations.']]",
    },
)

ProjectUpdateMembersRequest: TypeAlias = UpdateProjectMembersData
ProjectUpdateMembersResponse = TypedDict(
    'ProjectUpdateMembersResponse',
    {
    'data': 'Required[ProjectData]',
    'message': "Required[Literal['Project members updated successfully.']]",
    },
)

ProjectAddMemberResponse = TypedDict(
    'ProjectAddMemberResponse',
    {
    'message': "Required[Literal['Team member added to project successfully.']]",
    },
)

ProjectRemoveMemberResponse = TypedDict(
    'ProjectRemoveMemberResponse',
    {
    'message': "Required[Literal['Team member removed from project successfully.']]",
    },
)

RouteIndexResponse = TypedDict(
    'RouteIndexResponse',
    {
    'data': 'Required[list[RouteListData]]',
    'path': 'Required[str | None]',
    'per_page': 'Required[int]',
    'next_cursor': 'Required[str | None]',
    'next_page_url': 'Required[str | None]',
    'prev_cursor': 'Required[str | None]',
    'prev_page_url': 'Required[str | None]',
    },
)

RouteStoreRequest: TypeAlias = StoreRouteData
RouteStoreResponse = TypedDict(
    'RouteStoreResponse',
    {
    'data': 'Required[RouteData]',
    'message': "Required[Literal['Route created successfully.']]",
    },
)

RouteShowResponse: TypeAlias = RouteData
RouteUpdateRequest: TypeAlias = UpdateRouteData
RouteUpdateResponse = TypedDict(
    'RouteUpdateResponse',
    {
    'data': 'Required[RouteData]',
    'message': "Required[Literal['Route updated successfully.']]",
    },
)

RouteDestroyResponse = TypedDict(
    'RouteDestroyResponse',
    {
    'message': "Required[Literal['Route deleted successfully.']]",
    },
)

RouteVerifyInboundDomainResponse = TypedDict(
    'RouteVerifyInboundDomainResponse',
    {
    'data': 'Required[dict[str, Any]]',
    },
)

StatsIndexResponse: TypeAlias = StatsData
SuppressionIndexResponse = TypedDict(
    'SuppressionIndexResponse',
    {
    'data': 'Required[list[SuppressedRecipientData]]',
    'path': 'Required[str | None]',
    'per_page': 'Required[int]',
    'next_cursor': 'Required[str | None]',
    'next_page_url': 'Required[str | None]',
    'prev_cursor': 'Required[str | None]',
    'prev_page_url': 'Required[str | None]',
    },
)

SuppressionStoreRequest: TypeAlias = StoreSuppressionData
SuppressionStoreResponse = TypedDict(
    'SuppressionStoreResponse',
    {
    'message': "Required[Union[str, Literal['No emails were added.']]]",
    'data': 'Required[dict[str, Any]]',
    },
)

SuppressionDestroyResponse = TypedDict(
    'SuppressionDestroyResponse',
    {
    'message': "Required[Literal['Email removed from suppression list successfully.']]",
    },
)

TeamShowResponse: TypeAlias = TeamData
TeamUpdateRequest: TypeAlias = UpdateTeamData
TeamUpdateResponse = TypedDict(
    'TeamUpdateResponse',
    {
    'data': 'Required[TeamData]',
    'message': "Required[Literal['Team settings updated successfully.']]",
    },
)

TeamUsageResponse: TypeAlias = TeamUsageDetailData
TeamMembersResponse = TypedDict(
    'TeamMembersResponse',
    {
    'data': 'Required[list[TeamMemberData]]',
    'path': 'Required[str | None]',
    'per_page': 'Required[int]',
    'next_cursor': 'Required[str | None]',
    'next_page_url': 'Required[str | None]',
    'prev_cursor': 'Required[str | None]',
    'prev_page_url': 'Required[str | None]',
    },
)

WebhookIndexResponse = TypedDict(
    'WebhookIndexResponse',
    {
    'data': 'Required[list[WebhookListData]]',
    'path': 'Required[str | None]',
    'per_page': 'Required[int]',
    'next_cursor': 'Required[str | None]',
    'next_page_url': 'Required[str | None]',
    'prev_cursor': 'Required[str | None]',
    'prev_page_url': 'Required[str | None]',
    },
)

WebhookStoreRequest: TypeAlias = StoreWebhookData
WebhookStoreResponse = TypedDict(
    'WebhookStoreResponse',
    {
    'data': 'Required[WebhookData]',
    'message': "Required[Literal['Webhook created successfully. Please save the secret as it will not be shown again.']]",
    },
)

WebhookShowResponse: TypeAlias = WebhookData
WebhookUpdateRequest: TypeAlias = UpdateWebhookData
WebhookUpdateResponse = TypedDict(
    'WebhookUpdateResponse',
    {
    'data': 'Required[WebhookData]',
    'message': "Required[Literal['Webhook updated successfully.']]",
    },
)

WebhookDestroyResponse = TypedDict(
    'WebhookDestroyResponse',
    {
    'message': "Required[Literal['Webhook deleted successfully.']]",
    },
)

WebhookTestResponse = TypedDict(
    'WebhookTestResponse',
    {
    'message': "Required[Literal['Test webhook dispatched successfully. Check the deliveries endpoint for results.']]",
    'delivery_id': 'Required[str]',
    },
)

WebhookRegenerateSecretResponse = TypedDict(
    'WebhookRegenerateSecretResponse',
    {
    'data': 'Required[WebhookData]',
    'message': "Required[Literal['Webhook secret regenerated successfully. Please update your integration.']]",
    },
)

WebhookDeliveriesResponse = TypedDict(
    'WebhookDeliveriesResponse',
    {
    'data': 'Required[list[WebhookDeliveryListData]]',
    'path': 'Required[str | None]',
    'per_page': 'Required[int]',
    'next_cursor': 'Required[str | None]',
    'next_page_url': 'Required[str | None]',
    'prev_cursor': 'Required[str | None]',
    'prev_page_url': 'Required[str | None]',
    },
)

WebhookShowDeliveryResponse: TypeAlias = WebhookDeliveryData
SendEmailResponse: TypeAlias = SendMailResponse
SendBatchEmailResponse: TypeAlias = SendBatchMailResponse
