# Generated from src/lettermint/_async/resources.py by scripts/unasync.py — do not edit.
"""The Team API sub-clients of :class:`~lettermint.Lettermint`.

Every method uses the team token, except ``messages.reschedule`` and
``messages.cancel``, which use the team token when it is set and otherwise
the sending token.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from typing import Any, cast

from .._generated.operations import OPERATIONS
from .._generated.types import (
    DeleteSuppressionResponse,
    DnsVerificationSuccessResponse,
    DomainData,
    DomainListData,
    DomainMutationResponse,
    GetDomainQuery,
    GetProjectQuery,
    GetReportForwardingResponse,
    GetRouteQuery,
    GetStatsQuery,
    GetTeamQuery,
    InboundDomainVerificationResponse,
    ListDomainsQuery,
    ListDomainsResponse,
    ListMessageEventsQuery,
    ListMessageEventsResponse,
    ListMessagesQuery,
    ListMessagesResponse,
    ListProjectsQuery,
    ListProjectsResponse,
    ListRoutesQuery,
    ListRoutesResponse,
    ListSuppressionsQuery,
    ListSuppressionsResponse,
    ListTeamMembersQuery,
    ListTeamMembersResponse,
    ListWebhookDeliveriesQuery,
    ListWebhookDeliveriesResponse,
    ListWebhooksQuery,
    ListWebhooksResponse,
    MessageData,
    MessageEventData,
    MessageListData,
    MessageResponse,
    ProcessInboundMessageResponse,
    ProjectCreatedData,
    ProjectData,
    ProjectListData,
    ProjectMutationResponse,
    ReportForwardingRequest,
    RescheduleMessageRequest,
    ResendReportForwardingCodeResponse,
    RotateProjectTokenResponse,
    RouteData,
    RouteListData,
    RouteMutationResponse,
    ScheduledMessage,
    StatsData,
    StoreDomainData,
    StoreProjectData,
    StoreRouteData,
    StoreSuppressionData,
    StoreWebhookData,
    SuppressedRecipientData,
    SuppressionStoreResponse,
    TeamData,
    TeamMemberData,
    TeamMutationResponse,
    TeamRoleListResponse,
    TeamUsageDetailData,
    TestWebhookResponse,
    UpdateDomainProjectsData,
    UpdateProjectData,
    UpdateReportForwardingResponse,
    UpdateRouteData,
    UpdateTeamData,
    UpdateTeamMemberAssignmentData,
    UpdateWebhookData,
    VerifyReportForwardingRequest,
    VerifyReportForwardingResponse,
    WebhookData,
    WebhookDeliveryData,
    WebhookDeliveryListData,
    WebhookListData,
    WebhookMutationResponse,
    WebhookSecretResponse,
)
from .._query import with_query_param
from .._transport import Transport
from ..exceptions import UnexpectedResponseError

__all__ = [
    "Domains",
    "Messages",
    "Projects",
    "ReportForwarding",
    "Routes",
    "Stats",
    "Suppressions",
    "Team",
    "TeamMembers",
    "WebhookDeliveries",
    "Webhooks",
]


def _paginate(
    transport: Transport,
    key: str,
    label: str,
    path: Mapping[str, str] | None,
    query: Mapping[str, Any] | None,
    timeout: float | None,
) -> Iterator[Any]:
    """Follows ``next_cursor`` until it is ``None``, or repeats a cursor."""
    pagination = OPERATIONS[key].pagination
    assert pagination is not None and pagination.cursor_param is not None
    seen: set[str] = set()
    current = query
    while True:
        page = transport.request(key, label=label, path=path, query=current, timeout=timeout)
        data = page.get("data") if isinstance(page, dict) else None
        if not isinstance(data, list):
            raise UnexpectedResponseError(
                f"{label}: the API returned a page without a data array.",
                status=200,
                body=json.dumps(page),
            )
        for item in data:
            yield item
        cursor = page.get("next_cursor")
        if not isinstance(cursor, str) or not cursor or cursor in seen:
            return
        seen.add(cursor)
        current = with_query_param(query, pagination.cursor_param, cursor)


class Resource:
    """Base of the sub-clients. ``repr()`` shows no configuration and no credentials."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def _request(self, key: str, label: str, **arguments: Any) -> Any:
        return self._transport.request(key, label=label, **arguments)

    def _paginate(
        self,
        key: str,
        label: str,
        *,
        path: Mapping[str, str] | None = None,
        query: Mapping[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Iterator[Any]:
        # Check the token, path parameters and options now, not at the first page.
        self._transport.prepare(key, label=label, path=path, query=query, timeout=timeout)
        return _paginate(self._transport, key, label, path, query, timeout)

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def __reduce__(self) -> Any:
        raise TypeError(f"{type(self).__name__} cannot be pickled")


class Domains(Resource):
    """Sending domains. Team token."""

    def list(
        self, query: ListDomainsQuery | None = None, *, timeout: float | None = None
    ) -> ListDomainsResponse:
        """Lists domains, one page at a time."""
        return cast(
            ListDomainsResponse,
            self._request("GET /domains", "domains.list", query=query, timeout=timeout),
        )

    def iterate(
        self, query: ListDomainsQuery | None = None, *, timeout: float | None = None
    ) -> Iterator[DomainListData]:
        """Iterates over every domain, following ``next_cursor``."""
        return self._paginate("GET /domains", "domains.iterate", query=query, timeout=timeout)

    def create(self, body: StoreDomainData, *, timeout: float | None = None) -> DomainData:
        return cast(
            DomainData,
            self._request("POST /domains", "domains.create", body=body, timeout=timeout),
        )

    def retrieve(
        self, domain_id: str, query: GetDomainQuery | None = None, *, timeout: float | None = None
    ) -> DomainData:
        return cast(
            DomainData,
            self._request(
                "GET /domains/{domainId}",
                "domains.retrieve",
                path={"domainId": domain_id},
                query=query,
                timeout=timeout,
            ),
        )

    def delete(self, domain_id: str, *, timeout: float | None = None) -> MessageResponse:
        return cast(
            MessageResponse,
            self._request(
                "DELETE /domains/{domainId}",
                "domains.delete",
                path={"domainId": domain_id},
                timeout=timeout,
            ),
        )

    def verify_dns_records(
        self, domain_id: str, *, timeout: float | None = None
    ) -> DnsVerificationSuccessResponse:
        """Checks every DNS record of the domain."""
        return cast(
            DnsVerificationSuccessResponse,
            self._request(
                "POST /domains/{domainId}/dns-records/verify",
                "domains.verify_dns_records",
                path={"domainId": domain_id},
                timeout=timeout,
            ),
        )

    def verify_dns_record(
        self, domain_id: str, record_id: str, *, timeout: float | None = None
    ) -> MessageResponse:
        """Checks one DNS record of the domain."""
        return cast(
            MessageResponse,
            self._request(
                "POST /domains/{domainId}/dns-records/{recordId}/verify",
                "domains.verify_dns_record",
                path={"domainId": domain_id, "recordId": record_id},
                timeout=timeout,
            ),
        )

    def update_projects(
        self, domain_id: str, body: UpdateDomainProjectsData, *, timeout: float | None = None
    ) -> DomainMutationResponse:
        """Replaces the projects that may send from the domain."""
        return cast(
            DomainMutationResponse,
            self._request(
                "PUT /domains/{domainId}/projects",
                "domains.update_projects",
                path={"domainId": domain_id},
                body=body,
                timeout=timeout,
            ),
        )


class Messages(Resource):
    """Sent and received messages. Team token.

    ``reschedule`` and ``cancel`` also accept the sending token when no team
    token is configured.
    """

    def list(
        self, query: ListMessagesQuery | None = None, *, timeout: float | None = None
    ) -> ListMessagesResponse:
        """Lists messages, one page at a time."""
        return cast(
            ListMessagesResponse,
            self._request("GET /messages", "messages.list", query=query, timeout=timeout),
        )

    def iterate(
        self, query: ListMessagesQuery | None = None, *, timeout: float | None = None
    ) -> Iterator[MessageListData]:
        """Iterates over every message, following ``next_cursor``."""
        return self._paginate("GET /messages", "messages.iterate", query=query, timeout=timeout)

    def retrieve(self, message_id: str, *, timeout: float | None = None) -> MessageData:
        return cast(
            MessageData,
            self._request(
                "GET /messages/{messageId}",
                "messages.retrieve",
                path={"messageId": message_id},
                timeout=timeout,
            ),
        )

    def events(
        self,
        message_id: str,
        query: ListMessageEventsQuery | None = None,
        *,
        timeout: float | None = None,
    ) -> ListMessageEventsResponse:
        """Lists the events of a message, one page at a time."""
        return cast(
            ListMessageEventsResponse,
            self._request(
                "GET /messages/{messageId}/events",
                "messages.events",
                path={"messageId": message_id},
                query=query,
                timeout=timeout,
            ),
        )

    def iterate_events(
        self,
        message_id: str,
        query: ListMessageEventsQuery | None = None,
        *,
        timeout: float | None = None,
    ) -> Iterator[MessageEventData]:
        """Iterates over every event of a message, following ``next_cursor``."""
        return self._paginate(
            "GET /messages/{messageId}/events",
            "messages.iterate_events",
            path={"messageId": message_id},
            query=query,
            timeout=timeout,
        )

    def source(self, message_id: str, *, timeout: float | None = None) -> str:
        """The raw RFC 822 source."""
        return cast(
            str,
            self._request(
                "GET /messages/{messageId}/source",
                "messages.source",
                path={"messageId": message_id},
                timeout=timeout,
            ),
        )

    def html(self, message_id: str, *, timeout: float | None = None) -> str:
        """The HTML body."""
        return cast(
            str,
            self._request(
                "GET /messages/{messageId}/html",
                "messages.html",
                path={"messageId": message_id},
                timeout=timeout,
            ),
        )

    def text(self, message_id: str, *, timeout: float | None = None) -> str:
        """The plain-text body."""
        return cast(
            str,
            self._request(
                "GET /messages/{messageId}/text",
                "messages.text",
                path={"messageId": message_id},
                timeout=timeout,
            ),
        )

    def reschedule(
        self, message_id: str, body: RescheduleMessageRequest, *, timeout: float | None = None
    ) -> ScheduledMessage:
        """Moves a scheduled message to another delivery time."""
        return cast(
            ScheduledMessage,
            self._request(
                "PATCH /messages/{messageId}",
                "messages.reschedule",
                path={"messageId": message_id},
                body=body,
                timeout=timeout,
            ),
        )

    def cancel(self, message_id: str, *, timeout: float | None = None) -> ScheduledMessage:
        """Cancels a scheduled message."""
        return cast(
            ScheduledMessage,
            self._request(
                "POST /messages/{messageId}/cancel",
                "messages.cancel",
                path={"messageId": message_id},
                timeout=timeout,
            ),
        )

    def process(
        self,
        message_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> ProcessInboundMessageResponse:
        """Releases one quarantined inbound message for webhook delivery."""
        return cast(
            ProcessInboundMessageResponse,
            self._request(
                "POST /messages/{messageId}/process",
                "messages.process",
                path={"messageId": message_id},
                idempotency_key=idempotency_key,
                timeout=timeout,
            ),
        )


class ReportForwarding(Resource):
    """DMARC and complaint report forwarding of a project. Team token."""

    def retrieve(
        self, project_id: str, *, timeout: float | None = None
    ) -> GetReportForwardingResponse:
        return cast(
            GetReportForwardingResponse,
            self._request(
                "GET /projects/{projectId}/report-forwarding",
                "projects.report_forwarding.retrieve",
                path={"projectId": project_id},
                timeout=timeout,
            ),
        )

    def update(
        self, project_id: str, body: ReportForwardingRequest, *, timeout: float | None = None
    ) -> UpdateReportForwardingResponse:
        return cast(
            UpdateReportForwardingResponse,
            self._request(
                "PUT /projects/{projectId}/report-forwarding",
                "projects.report_forwarding.update",
                path={"projectId": project_id},
                body=body,
                timeout=timeout,
            ),
        )

    def delete(self, project_id: str, *, timeout: float | None = None) -> None:
        """Disables report forwarding (HTTP 204)."""
        self._request(
            "DELETE /projects/{projectId}/report-forwarding",
            "projects.report_forwarding.delete",
            path={"projectId": project_id},
            timeout=timeout,
        )

    def verify(
        self, project_id: str, body: VerifyReportForwardingRequest, *, timeout: float | None = None
    ) -> VerifyReportForwardingResponse:
        return cast(
            VerifyReportForwardingResponse,
            self._request(
                "POST /projects/{projectId}/report-forwarding/verify",
                "projects.report_forwarding.verify",
                path={"projectId": project_id},
                body=body,
                timeout=timeout,
            ),
        )

    def resend_code(
        self, project_id: str, *, timeout: float | None = None
    ) -> ResendReportForwardingCodeResponse:
        return cast(
            ResendReportForwardingCodeResponse,
            self._request(
                "POST /projects/{projectId}/report-forwarding/resend-code",
                "projects.report_forwarding.resend_code",
                path={"projectId": project_id},
                timeout=timeout,
            ),
        )


class Projects(Resource):
    """Projects. Team token."""

    def __init__(self, transport: Transport) -> None:
        super().__init__(transport)
        #: Report forwarding of a project.
        self.report_forwarding = ReportForwarding(transport)

    def list(
        self, query: ListProjectsQuery | None = None, *, timeout: float | None = None
    ) -> ListProjectsResponse:
        """Lists projects, one page at a time."""
        return cast(
            ListProjectsResponse,
            self._request("GET /projects", "projects.list", query=query, timeout=timeout),
        )

    def iterate(
        self, query: ListProjectsQuery | None = None, *, timeout: float | None = None
    ) -> Iterator[ProjectListData]:
        """Iterates over every project, following ``next_cursor``."""
        return self._paginate("GET /projects", "projects.iterate", query=query, timeout=timeout)

    def create(
        self, body: StoreProjectData, *, timeout: float | None = None
    ) -> ProjectCreatedData:
        """Creates a project. The response holds its sending token once (``api_token``)."""
        return cast(
            ProjectCreatedData,
            self._request("POST /projects", "projects.create", body=body, timeout=timeout),
        )

    def retrieve(
        self, project_id: str, query: GetProjectQuery | None = None, *, timeout: float | None = None
    ) -> ProjectData:
        return cast(
            ProjectData,
            self._request(
                "GET /projects/{projectId}",
                "projects.retrieve",
                path={"projectId": project_id},
                query=query,
                timeout=timeout,
            ),
        )

    def update(
        self, project_id: str, body: UpdateProjectData, *, timeout: float | None = None
    ) -> ProjectMutationResponse:
        return cast(
            ProjectMutationResponse,
            self._request(
                "PUT /projects/{projectId}",
                "projects.update",
                path={"projectId": project_id},
                body=body,
                timeout=timeout,
            ),
        )

    def delete(self, project_id: str, *, timeout: float | None = None) -> MessageResponse:
        return cast(
            MessageResponse,
            self._request(
                "DELETE /projects/{projectId}",
                "projects.delete",
                path={"projectId": project_id},
                timeout=timeout,
            ),
        )

    def rotate_token(
        self, project_id: str, *, timeout: float | None = None
    ) -> RotateProjectTokenResponse:
        """Rotates the project's legacy sending token. Deprecated by the API."""
        return cast(
            RotateProjectTokenResponse,
            self._request(
                "POST /projects/{projectId}/rotate-token",
                "projects.rotate_token",
                path={"projectId": project_id},
                timeout=timeout,
            ),
        )


class Routes(Resource):
    """Routes of a project. Team token."""

    def list(
        self, project_id: str, query: ListRoutesQuery | None = None, *, timeout: float | None = None
    ) -> ListRoutesResponse:
        """Lists the routes of a project, one page at a time."""
        return cast(
            ListRoutesResponse,
            self._request(
                "GET /projects/{projectId}/routes",
                "routes.list",
                path={"projectId": project_id},
                query=query,
                timeout=timeout,
            ),
        )

    def iterate(
        self, project_id: str, query: ListRoutesQuery | None = None, *, timeout: float | None = None
    ) -> Iterator[RouteListData]:
        """Iterates over every route of a project, following ``next_cursor``."""
        return self._paginate(
            "GET /projects/{projectId}/routes",
            "routes.iterate",
            path={"projectId": project_id},
            query=query,
            timeout=timeout,
        )

    def create(
        self, project_id: str, body: StoreRouteData, *, timeout: float | None = None
    ) -> RouteMutationResponse:
        return cast(
            RouteMutationResponse,
            self._request(
                "POST /projects/{projectId}/routes",
                "routes.create",
                path={"projectId": project_id},
                body=body,
                timeout=timeout,
            ),
        )

    def retrieve(
        self, route_id: str, query: GetRouteQuery | None = None, *, timeout: float | None = None
    ) -> RouteData:
        return cast(
            RouteData,
            self._request(
                "GET /routes/{routeId}",
                "routes.retrieve",
                path={"routeId": route_id},
                query=query,
                timeout=timeout,
            ),
        )

    def update(
        self, route_id: str, body: UpdateRouteData, *, timeout: float | None = None
    ) -> RouteMutationResponse:
        return cast(
            RouteMutationResponse,
            self._request(
                "PUT /routes/{routeId}",
                "routes.update",
                path={"routeId": route_id},
                body=body,
                timeout=timeout,
            ),
        )

    def delete(self, route_id: str, *, timeout: float | None = None) -> MessageResponse:
        return cast(
            MessageResponse,
            self._request(
                "DELETE /routes/{routeId}",
                "routes.delete",
                path={"routeId": route_id},
                timeout=timeout,
            ),
        )

    def verify_inbound_domain(
        self, route_id: str, *, timeout: float | None = None
    ) -> InboundDomainVerificationResponse:
        return cast(
            InboundDomainVerificationResponse,
            self._request(
                "POST /routes/{routeId}/verify-inbound-domain",
                "routes.verify_inbound_domain",
                path={"routeId": route_id},
                timeout=timeout,
            ),
        )


class Stats(Resource):
    """Sending statistics. Team token."""

    def retrieve(self, query: GetStatsQuery, *, timeout: float | None = None) -> StatsData:
        """Daily statistics between ``from`` and ``to`` (``YYYY-MM-DD``, at most 90 days)."""
        return cast(
            StatsData,
            self._request("GET /stats", "stats.retrieve", query=query, timeout=timeout),
        )


class Suppressions(Resource):
    """The suppression list. Team token."""

    def list(
        self, query: ListSuppressionsQuery | None = None, *, timeout: float | None = None
    ) -> ListSuppressionsResponse:
        """Lists suppressions, one page at a time."""
        return cast(
            ListSuppressionsResponse,
            self._request(
                "GET /suppressions", "suppressions.list", query=query, timeout=timeout
            ),
        )

    def iterate(
        self, query: ListSuppressionsQuery | None = None, *, timeout: float | None = None
    ) -> Iterator[SuppressedRecipientData]:
        """Iterates over every suppression, following ``next_cursor``."""
        return self._paginate(
            "GET /suppressions", "suppressions.iterate", query=query, timeout=timeout
        )

    def create(
        self, body: StoreSuppressionData, *, timeout: float | None = None
    ) -> SuppressionStoreResponse:
        return cast(
            SuppressionStoreResponse,
            self._request(
                "POST /suppressions", "suppressions.create", body=body, timeout=timeout
            ),
        )

    def delete(
        self, suppression_id: str, *, timeout: float | None = None
    ) -> DeleteSuppressionResponse:
        return cast(
            DeleteSuppressionResponse,
            self._request(
                "DELETE /suppressions/{suppressionId}",
                "suppressions.delete",
                path={"suppressionId": suppression_id},
                timeout=timeout,
            ),
        )


class TeamMembers(Resource):
    """Team members. Team token."""

    def list(
        self, query: ListTeamMembersQuery | None = None, *, timeout: float | None = None
    ) -> ListTeamMembersResponse:
        """Lists team members, one page at a time."""
        return cast(
            ListTeamMembersResponse,
            self._request(
                "GET /team/members", "team.members.list", query=query, timeout=timeout
            ),
        )

    def iterate(
        self, query: ListTeamMembersQuery | None = None, *, timeout: float | None = None
    ) -> Iterator[TeamMemberData]:
        """Iterates over every team member, following ``next_cursor``."""
        return self._paginate(
            "GET /team/members", "team.members.iterate", query=query, timeout=timeout
        )

    def retrieve(self, user_id: str, *, timeout: float | None = None) -> TeamMemberData:
        return cast(
            TeamMemberData,
            self._request(
                "GET /team/members/{userId}",
                "team.members.retrieve",
                path={"userId": user_id},
                timeout=timeout,
            ),
        )

    def update_assignment(
        self, user_id: str, body: UpdateTeamMemberAssignmentData, *, timeout: float | None = None
    ) -> TeamMemberData:
        """Changes a member's role and project access."""
        return cast(
            TeamMemberData,
            self._request(
                "PUT /team/members/{userId}/assignment",
                "team.members.update_assignment",
                path={"userId": user_id},
                body=body,
                timeout=timeout,
            ),
        )


class Team(Resource):
    """The team of the token. Team token."""

    def __init__(self, transport: Transport) -> None:
        super().__init__(transport)
        #: Team members.
        self.members = TeamMembers(transport)

    def retrieve(
        self, query: GetTeamQuery | None = None, *, timeout: float | None = None
    ) -> TeamData:
        return cast(
            TeamData,
            self._request("GET /team", "team.retrieve", query=query, timeout=timeout),
        )

    def update(
        self, body: UpdateTeamData, *, timeout: float | None = None
    ) -> TeamMutationResponse:
        return cast(
            TeamMutationResponse,
            self._request("PUT /team", "team.update", body=body, timeout=timeout),
        )

    def usage(self, *, timeout: float | None = None) -> TeamUsageDetailData:
        """Usage of the current and previous billing periods."""
        return cast(
            TeamUsageDetailData,
            self._request("GET /team/usage", "team.usage", timeout=timeout),
        )

    def roles(self, *, timeout: float | None = None) -> TeamRoleListResponse:
        """The roles that can be assigned to members."""
        return cast(
            TeamRoleListResponse,
            self._request("GET /team/roles", "team.roles", timeout=timeout),
        )


class WebhookDeliveries(Resource):
    """Delivery attempts of a webhook. Team token."""

    def list(
        self,
        webhook_id: str,
        query: ListWebhookDeliveriesQuery | None = None,
        *,
        timeout: float | None = None,
    ) -> ListWebhookDeliveriesResponse:
        """Lists the deliveries of a webhook, one page at a time."""
        return cast(
            ListWebhookDeliveriesResponse,
            self._request(
                "GET /webhooks/{webhookId}/deliveries",
                "webhooks.deliveries.list",
                path={"webhookId": webhook_id},
                query=query,
                timeout=timeout,
            ),
        )

    def iterate(
        self,
        webhook_id: str,
        query: ListWebhookDeliveriesQuery | None = None,
        *,
        timeout: float | None = None,
    ) -> Iterator[WebhookDeliveryListData]:
        """Iterates over every delivery of a webhook, following ``next_cursor``."""
        return self._paginate(
            "GET /webhooks/{webhookId}/deliveries",
            "webhooks.deliveries.iterate",
            path={"webhookId": webhook_id},
            query=query,
            timeout=timeout,
        )

    def retrieve(
        self, webhook_id: str, delivery_id: str, *, timeout: float | None = None
    ) -> WebhookDeliveryData:
        return cast(
            WebhookDeliveryData,
            self._request(
                "GET /webhooks/{webhookId}/deliveries/{deliveryId}",
                "webhooks.deliveries.retrieve",
                path={"webhookId": webhook_id, "deliveryId": delivery_id},
                timeout=timeout,
            ),
        )


class Webhooks(Resource):
    """Webhook endpoints. Team token. To verify incoming deliveries, use :class:`~lettermint.Webhook`."""

    def __init__(self, transport: Transport) -> None:
        super().__init__(transport)
        #: Delivery attempts of a webhook.
        self.deliveries = WebhookDeliveries(transport)

    def list(
        self, query: ListWebhooksQuery | None = None, *, timeout: float | None = None
    ) -> ListWebhooksResponse:
        """Lists webhooks, one page at a time."""
        return cast(
            ListWebhooksResponse,
            self._request("GET /webhooks", "webhooks.list", query=query, timeout=timeout),
        )

    def iterate(
        self, query: ListWebhooksQuery | None = None, *, timeout: float | None = None
    ) -> Iterator[WebhookListData]:
        """Iterates over every webhook, following ``next_cursor``."""
        return self._paginate("GET /webhooks", "webhooks.iterate", query=query, timeout=timeout)

    def create(
        self, body: StoreWebhookData, *, timeout: float | None = None
    ) -> WebhookSecretResponse:
        """Creates a webhook. The response holds its signing secret once."""
        return cast(
            WebhookSecretResponse,
            self._request("POST /webhooks", "webhooks.create", body=body, timeout=timeout),
        )

    def retrieve(self, webhook_id: str, *, timeout: float | None = None) -> WebhookData:
        return cast(
            WebhookData,
            self._request(
                "GET /webhooks/{webhookId}",
                "webhooks.retrieve",
                path={"webhookId": webhook_id},
                timeout=timeout,
            ),
        )

    def update(
        self, webhook_id: str, body: UpdateWebhookData, *, timeout: float | None = None
    ) -> WebhookMutationResponse:
        return cast(
            WebhookMutationResponse,
            self._request(
                "PUT /webhooks/{webhookId}",
                "webhooks.update",
                path={"webhookId": webhook_id},
                body=body,
                timeout=timeout,
            ),
        )

    def delete(self, webhook_id: str, *, timeout: float | None = None) -> MessageResponse:
        return cast(
            MessageResponse,
            self._request(
                "DELETE /webhooks/{webhookId}",
                "webhooks.delete",
                path={"webhookId": webhook_id},
                timeout=timeout,
            ),
        )

    def test(self, webhook_id: str, *, timeout: float | None = None) -> TestWebhookResponse:
        """Sends a ``webhook.test`` delivery."""
        return cast(
            TestWebhookResponse,
            self._request(
                "POST /webhooks/{webhookId}/test",
                "webhooks.test",
                path={"webhookId": webhook_id},
                timeout=timeout,
            ),
        )

    def regenerate_secret(
        self, webhook_id: str, *, timeout: float | None = None
    ) -> WebhookSecretResponse:
        """Replaces the signing secret. The response holds the new secret once."""
        return cast(
            WebhookSecretResponse,
            self._request(
                "POST /webhooks/{webhookId}/regenerate-secret",
                "webhooks.regenerate_secret",
                path={"webhookId": webhook_id},
                timeout=timeout,
            ),
        )
