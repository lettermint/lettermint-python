"""Full API endpoints for the Lettermint SDK."""

from __future__ import annotations

from typing import cast

from .. import types as lm_types
from .endpoint import AsyncEndpoint, Endpoint

Query = dict[str, str]


class DomainsEndpoint(Endpoint):
    def list(self, query: Query | None = None) -> lm_types.DomainIndexResponse:
        return cast(lm_types.DomainIndexResponse, self._client.get("/domains", params=query))

    def create(self, data: lm_types.DomainStoreRequest) -> lm_types.DomainStoreResponse:
        return cast(lm_types.DomainStoreResponse, self._client.post("/domains", data=data))

    def retrieve(self, domain_id: str, query: Query | None = None) -> lm_types.DomainShowResponse:
        return cast(
            lm_types.DomainShowResponse,
            self._client.get(self._path("/domains/{domainId}", domainId=domain_id), params=query),
        )

    def delete(self, domain_id: str) -> lm_types.DomainDestroyResponse:
        return cast(
            lm_types.DomainDestroyResponse,
            self._client.delete(self._path("/domains/{domainId}", domainId=domain_id)),
        )

    def verify_dns_records(self, domain_id: str) -> lm_types.DomainVerifyDnsRecordsResponse:
        return cast(
            lm_types.DomainVerifyDnsRecordsResponse,
            self._client.post(
                self._path("/domains/{domainId}/dns-records/verify", domainId=domain_id),
                data={},
            ),
        )

    def verify_dns_record(
        self, domain_id: str, record_id: str
    ) -> lm_types.DomainVerifySpecificDnsRecordResponse:
        return cast(
            lm_types.DomainVerifySpecificDnsRecordResponse,
            self._client.post(
                self._path(
                    "/domains/{domainId}/dns-records/{recordId}/verify",
                    domainId=domain_id,
                    recordId=record_id,
                ),
                data={},
            ),
        )

    def update_projects(
        self, domain_id: str, data: lm_types.DomainUpdateProjectsRequest
    ) -> lm_types.DomainUpdateProjectsResponse:
        return cast(
            lm_types.DomainUpdateProjectsResponse,
            self._client.put(
                self._path("/domains/{domainId}/projects", domainId=domain_id),
                data=data,
            ),
        )


class MessagesEndpoint(Endpoint):
    def list(self, query: Query | None = None) -> lm_types.MessageIndexResponse:
        return cast(lm_types.MessageIndexResponse, self._client.get("/messages", params=query))

    def retrieve(self, message_id: str, query: Query | None = None) -> lm_types.MessageShowResponse:
        return cast(
            lm_types.MessageShowResponse,
            self._client.get(
                self._path("/messages/{messageId}", messageId=message_id),
                params=query,
            ),
        )

    def reschedule(
        self, message_id: str, data: lm_types.RescheduleMessageRequest
    ) -> lm_types.RescheduleMessageResponse:
        return cast(
            lm_types.RescheduleMessageResponse,
            self._client.patch(
                self._path("/messages/{messageId}", messageId=message_id), data=data
            ),
        )

    def cancel(self, message_id: str) -> lm_types.RescheduleMessageResponse:
        return cast(
            lm_types.RescheduleMessageResponse,
            self._client.post(
                self._path("/messages/{messageId}/cancel", messageId=message_id), data={}
            ),
        )

    def process(self, message_id: str) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            self._client.post(
                self._path("/messages/{messageId}/process", messageId=message_id), data={}
            ),
        )

    def events(self, message_id: str, query: Query | None = None) -> lm_types.MessageEventsResponse:
        return cast(
            lm_types.MessageEventsResponse,
            self._client.get(
                self._path("/messages/{messageId}/events", messageId=message_id),
                params=query,
            ),
        )

    def source(self, message_id: str) -> str:
        return self._client.get_raw(
            self._path("/messages/{messageId}/source", messageId=message_id)
        )

    def html(self, message_id: str) -> str:
        return self._client.get_raw(self._path("/messages/{messageId}/html", messageId=message_id))

    def text(self, message_id: str) -> str:
        return self._client.get_raw(self._path("/messages/{messageId}/text", messageId=message_id))


class ProjectsEndpoint(Endpoint):
    def list(self, query: Query | None = None) -> lm_types.ProjectIndexResponse:
        return cast(lm_types.ProjectIndexResponse, self._client.get("/projects", params=query))

    def create(self, data: lm_types.ProjectStoreRequest) -> lm_types.ProjectStoreResponse:
        return cast(lm_types.ProjectStoreResponse, self._client.post("/projects", data=data))

    def retrieve(self, project_id: str, query: Query | None = None) -> lm_types.ProjectShowResponse:
        return cast(
            lm_types.ProjectShowResponse,
            self._client.get(
                self._path("/projects/{projectId}", projectId=project_id),
                params=query,
            ),
        )

    def update(
        self, project_id: str, data: lm_types.ProjectUpdateRequest
    ) -> lm_types.ProjectUpdateResponse:
        return cast(
            lm_types.ProjectUpdateResponse,
            self._client.put(self._path("/projects/{projectId}", projectId=project_id), data=data),
        )

    def delete(self, project_id: str) -> lm_types.ProjectDestroyResponse:
        return cast(
            lm_types.ProjectDestroyResponse,
            self._client.delete(self._path("/projects/{projectId}", projectId=project_id)),
        )

    def rotate_token(self, project_id: str) -> lm_types.ProjectRotateTokenResponse:
        return cast(
            lm_types.ProjectRotateTokenResponse,
            self._client.post(
                self._path("/projects/{projectId}/rotate-token", projectId=project_id),
                data={},
            ),
        )

    def routes(self, project_id: str, query: Query | None = None) -> lm_types.RouteIndexResponse:
        return cast(
            lm_types.RouteIndexResponse,
            self._client.get(
                self._path("/projects/{projectId}/routes", projectId=project_id),
                params=query,
            ),
        )

    def create_route(
        self, project_id: str, data: lm_types.RouteStoreRequest
    ) -> lm_types.RouteStoreResponse:
        return cast(
            lm_types.RouteStoreResponse,
            self._client.post(
                self._path("/projects/{projectId}/routes", projectId=project_id),
                data=data,
            ),
        )


class RoutesEndpoint(Endpoint):
    def retrieve(self, route_id: str, query: Query | None = None) -> lm_types.RouteShowResponse:
        return cast(
            lm_types.RouteShowResponse,
            self._client.get(self._path("/routes/{routeId}", routeId=route_id), params=query),
        )

    def update(
        self, route_id: str, data: lm_types.RouteUpdateRequest
    ) -> lm_types.RouteUpdateResponse:
        return cast(
            lm_types.RouteUpdateResponse,
            self._client.put(self._path("/routes/{routeId}", routeId=route_id), data=data),
        )

    def delete(self, route_id: str) -> lm_types.RouteDestroyResponse:
        return cast(
            lm_types.RouteDestroyResponse,
            self._client.delete(self._path("/routes/{routeId}", routeId=route_id)),
        )

    def verify_inbound_domain(self, route_id: str) -> lm_types.RouteVerifyInboundDomainResponse:
        return cast(
            lm_types.RouteVerifyInboundDomainResponse,
            self._client.post(
                self._path("/routes/{routeId}/verify-inbound-domain", routeId=route_id),
                data={},
            ),
        )


class StatsEndpoint(Endpoint):
    def retrieve(self, query: Query | None = None) -> lm_types.StatsIndexResponse:
        return cast(lm_types.StatsIndexResponse, self._client.get("/stats", params=query))


class SuppressionsEndpoint(Endpoint):
    def list(self, query: Query | None = None) -> lm_types.SuppressionIndexResponse:
        return cast(
            lm_types.SuppressionIndexResponse, self._client.get("/suppressions", params=query)
        )

    def create(self, data: lm_types.SuppressionStoreRequest) -> lm_types.SuppressionStoreResponse:
        return cast(
            lm_types.SuppressionStoreResponse, self._client.post("/suppressions", data=data)
        )

    def delete(self, suppression_id: str) -> lm_types.SuppressionDestroyResponse:
        return cast(
            lm_types.SuppressionDestroyResponse,
            self._client.delete(
                self._path("/suppressions/{suppressionId}", suppressionId=suppression_id)
            ),
        )


class TeamEndpoint(Endpoint):
    def retrieve(self, query: Query | None = None) -> lm_types.TeamShowResponse:
        return cast(lm_types.TeamShowResponse, self._client.get("/team", params=query))

    def update(self, data: lm_types.TeamUpdateRequest) -> lm_types.TeamUpdateResponse:
        return cast(lm_types.TeamUpdateResponse, self._client.put("/team", data=data))

    def usage(self) -> lm_types.TeamUsageResponse:
        return cast(lm_types.TeamUsageResponse, self._client.get("/team/usage"))

    def roles(self) -> lm_types.TeamRolesResponse:
        return cast(lm_types.TeamRolesResponse, self._client.get("/team/roles"))

    def members(self, query: Query | None = None) -> lm_types.TeamMembersResponse:
        return cast(lm_types.TeamMembersResponse, self._client.get("/team/members", params=query))

    def member(self, user_id: str) -> lm_types.TeamMembersShowResponse:
        return cast(
            lm_types.TeamMembersShowResponse,
            self._client.get(self._path("/team/members/{userId}", userId=user_id)),
        )

    def update_member_assignment(
        self, user_id: str, data: lm_types.TeamMembersAssignmentUpdateRequest
    ) -> lm_types.TeamMembersAssignmentUpdateResponse:
        return cast(
            lm_types.TeamMembersAssignmentUpdateResponse,
            self._client.put(
                self._path("/team/members/{userId}/assignment", userId=user_id),
                data=data,
            ),
        )


class WebhooksEndpoint(Endpoint):
    def list(self, query: Query | None = None) -> lm_types.WebhookIndexResponse:
        return cast(lm_types.WebhookIndexResponse, self._client.get("/webhooks", params=query))

    def create(self, data: lm_types.WebhookStoreRequest) -> lm_types.WebhookStoreResponse:
        return cast(lm_types.WebhookStoreResponse, self._client.post("/webhooks", data=data))

    def retrieve(self, webhook_id: str) -> lm_types.WebhookShowResponse:
        return cast(
            lm_types.WebhookShowResponse,
            self._client.get(self._path("/webhooks/{webhookId}", webhookId=webhook_id)),
        )

    def update(
        self, webhook_id: str, data: lm_types.WebhookUpdateRequest
    ) -> lm_types.WebhookUpdateResponse:
        return cast(
            lm_types.WebhookUpdateResponse,
            self._client.put(
                self._path("/webhooks/{webhookId}", webhookId=webhook_id),
                data=data,
            ),
        )

    def delete(self, webhook_id: str) -> lm_types.WebhookDestroyResponse:
        return cast(
            lm_types.WebhookDestroyResponse,
            self._client.delete(self._path("/webhooks/{webhookId}", webhookId=webhook_id)),
        )

    def test(self, webhook_id: str) -> lm_types.WebhookTestResponse:
        return cast(
            lm_types.WebhookTestResponse,
            self._client.post(
                self._path("/webhooks/{webhookId}/test", webhookId=webhook_id),
                data={},
            ),
        )

    def regenerate_secret(self, webhook_id: str) -> lm_types.WebhookRegenerateSecretResponse:
        return cast(
            lm_types.WebhookRegenerateSecretResponse,
            self._client.post(
                self._path("/webhooks/{webhookId}/regenerate-secret", webhookId=webhook_id),
                data={},
            ),
        )

    def deliveries(
        self, webhook_id: str, query: Query | None = None
    ) -> lm_types.WebhookDeliveriesResponse:
        return cast(
            lm_types.WebhookDeliveriesResponse,
            self._client.get(
                self._path("/webhooks/{webhookId}/deliveries", webhookId=webhook_id),
                params=query,
            ),
        )

    def delivery(self, webhook_id: str, delivery_id: str) -> lm_types.WebhookShowDeliveryResponse:
        return cast(
            lm_types.WebhookShowDeliveryResponse,
            self._client.get(
                self._path(
                    "/webhooks/{webhookId}/deliveries/{deliveryId}",
                    webhookId=webhook_id,
                    deliveryId=delivery_id,
                )
            ),
        )


class AsyncDomainsEndpoint(AsyncEndpoint):
    async def list(self, query: Query | None = None) -> lm_types.DomainIndexResponse:
        return cast(lm_types.DomainIndexResponse, await self._client.get("/domains", params=query))

    async def create(self, data: lm_types.DomainStoreRequest) -> lm_types.DomainStoreResponse:
        return cast(lm_types.DomainStoreResponse, await self._client.post("/domains", data=data))

    async def retrieve(
        self, domain_id: str, query: Query | None = None
    ) -> lm_types.DomainShowResponse:
        return cast(
            lm_types.DomainShowResponse,
            await self._client.get(
                self._path("/domains/{domainId}", domainId=domain_id), params=query
            ),
        )

    async def reschedule(
        self, message_id: str, data: lm_types.RescheduleMessageRequest
    ) -> lm_types.RescheduleMessageResponse:
        return cast(
            lm_types.RescheduleMessageResponse,
            await self._client.patch(
                self._path("/messages/{messageId}", messageId=message_id), data=data
            ),
        )

    async def cancel(self, message_id: str) -> lm_types.RescheduleMessageResponse:
        return cast(
            lm_types.RescheduleMessageResponse,
            await self._client.post(
                self._path("/messages/{messageId}/cancel", messageId=message_id), data={}
            ),
        )

    async def process(self, message_id: str) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._client.post(
                self._path("/messages/{messageId}/process", messageId=message_id), data={}
            ),
        )

    async def delete(self, domain_id: str) -> lm_types.DomainDestroyResponse:
        return cast(
            lm_types.DomainDestroyResponse,
            await self._client.delete(self._path("/domains/{domainId}", domainId=domain_id)),
        )

    async def verify_dns_records(self, domain_id: str) -> lm_types.DomainVerifyDnsRecordsResponse:
        return cast(
            lm_types.DomainVerifyDnsRecordsResponse,
            await self._client.post(
                self._path("/domains/{domainId}/dns-records/verify", domainId=domain_id), data={}
            ),
        )

    async def verify_dns_record(
        self, domain_id: str, record_id: str
    ) -> lm_types.DomainVerifySpecificDnsRecordResponse:
        return cast(
            lm_types.DomainVerifySpecificDnsRecordResponse,
            await self._client.post(
                self._path(
                    "/domains/{domainId}/dns-records/{recordId}/verify",
                    domainId=domain_id,
                    recordId=record_id,
                ),
                data={},
            ),
        )

    async def update_projects(
        self, domain_id: str, data: lm_types.DomainUpdateProjectsRequest
    ) -> lm_types.DomainUpdateProjectsResponse:
        return cast(
            lm_types.DomainUpdateProjectsResponse,
            await self._client.put(
                self._path("/domains/{domainId}/projects", domainId=domain_id), data=data
            ),
        )


class AsyncMessagesEndpoint(AsyncEndpoint):
    async def list(self, query: Query | None = None) -> lm_types.MessageIndexResponse:
        return cast(
            lm_types.MessageIndexResponse, await self._client.get("/messages", params=query)
        )

    async def retrieve(
        self, message_id: str, query: Query | None = None
    ) -> lm_types.MessageShowResponse:
        return cast(
            lm_types.MessageShowResponse,
            await self._client.get(
                self._path("/messages/{messageId}", messageId=message_id), params=query
            ),
        )

    async def events(
        self, message_id: str, query: Query | None = None
    ) -> lm_types.MessageEventsResponse:
        return cast(
            lm_types.MessageEventsResponse,
            await self._client.get(
                self._path("/messages/{messageId}/events", messageId=message_id), params=query
            ),
        )

    async def source(self, message_id: str) -> str:
        return await self._client.get_raw(
            self._path("/messages/{messageId}/source", messageId=message_id)
        )

    async def html(self, message_id: str) -> str:
        return await self._client.get_raw(
            self._path("/messages/{messageId}/html", messageId=message_id)
        )

    async def text(self, message_id: str) -> str:
        return await self._client.get_raw(
            self._path("/messages/{messageId}/text", messageId=message_id)
        )


class AsyncProjectsEndpoint(AsyncEndpoint):
    async def list(self, query: Query | None = None) -> lm_types.ProjectIndexResponse:
        return cast(
            lm_types.ProjectIndexResponse, await self._client.get("/projects", params=query)
        )

    async def create(self, data: lm_types.ProjectStoreRequest) -> lm_types.ProjectStoreResponse:
        return cast(lm_types.ProjectStoreResponse, await self._client.post("/projects", data=data))

    async def retrieve(
        self, project_id: str, query: Query | None = None
    ) -> lm_types.ProjectShowResponse:
        return cast(
            lm_types.ProjectShowResponse,
            await self._client.get(
                self._path("/projects/{projectId}", projectId=project_id), params=query
            ),
        )

    async def update(
        self, project_id: str, data: lm_types.ProjectUpdateRequest
    ) -> lm_types.ProjectUpdateResponse:
        return cast(
            lm_types.ProjectUpdateResponse,
            await self._client.put(
                self._path("/projects/{projectId}", projectId=project_id), data=data
            ),
        )

    async def delete(self, project_id: str) -> lm_types.ProjectDestroyResponse:
        return cast(
            lm_types.ProjectDestroyResponse,
            await self._client.delete(self._path("/projects/{projectId}", projectId=project_id)),
        )

    async def rotate_token(self, project_id: str) -> lm_types.ProjectRotateTokenResponse:
        return cast(
            lm_types.ProjectRotateTokenResponse,
            await self._client.post(
                self._path("/projects/{projectId}/rotate-token", projectId=project_id), data={}
            ),
        )

    async def routes(
        self, project_id: str, query: Query | None = None
    ) -> lm_types.RouteIndexResponse:
        return cast(
            lm_types.RouteIndexResponse,
            await self._client.get(
                self._path("/projects/{projectId}/routes", projectId=project_id), params=query
            ),
        )

    async def create_route(
        self, project_id: str, data: lm_types.RouteStoreRequest
    ) -> lm_types.RouteStoreResponse:
        return cast(
            lm_types.RouteStoreResponse,
            await self._client.post(
                self._path("/projects/{projectId}/routes", projectId=project_id), data=data
            ),
        )


class AsyncRoutesEndpoint(AsyncEndpoint):
    async def retrieve(
        self, route_id: str, query: Query | None = None
    ) -> lm_types.RouteShowResponse:
        return cast(
            lm_types.RouteShowResponse,
            await self._client.get(self._path("/routes/{routeId}", routeId=route_id), params=query),
        )

    async def update(
        self, route_id: str, data: lm_types.RouteUpdateRequest
    ) -> lm_types.RouteUpdateResponse:
        return cast(
            lm_types.RouteUpdateResponse,
            await self._client.put(self._path("/routes/{routeId}", routeId=route_id), data=data),
        )

    async def delete(self, route_id: str) -> lm_types.RouteDestroyResponse:
        return cast(
            lm_types.RouteDestroyResponse,
            await self._client.delete(self._path("/routes/{routeId}", routeId=route_id)),
        )

    async def verify_inbound_domain(
        self, route_id: str
    ) -> lm_types.RouteVerifyInboundDomainResponse:
        return cast(
            lm_types.RouteVerifyInboundDomainResponse,
            await self._client.post(
                self._path("/routes/{routeId}/verify-inbound-domain", routeId=route_id), data={}
            ),
        )


class AsyncStatsEndpoint(AsyncEndpoint):
    async def retrieve(self, query: Query | None = None) -> lm_types.StatsIndexResponse:
        return cast(lm_types.StatsIndexResponse, await self._client.get("/stats", params=query))


class AsyncSuppressionsEndpoint(AsyncEndpoint):
    async def list(self, query: Query | None = None) -> lm_types.SuppressionIndexResponse:
        return cast(
            lm_types.SuppressionIndexResponse, await self._client.get("/suppressions", params=query)
        )

    async def create(
        self, data: lm_types.SuppressionStoreRequest
    ) -> lm_types.SuppressionStoreResponse:
        return cast(
            lm_types.SuppressionStoreResponse, await self._client.post("/suppressions", data=data)
        )

    async def delete(self, suppression_id: str) -> lm_types.SuppressionDestroyResponse:
        return cast(
            lm_types.SuppressionDestroyResponse,
            await self._client.delete(
                self._path("/suppressions/{suppressionId}", suppressionId=suppression_id)
            ),
        )


class AsyncTeamEndpoint(AsyncEndpoint):
    async def retrieve(self, query: Query | None = None) -> lm_types.TeamShowResponse:
        return cast(lm_types.TeamShowResponse, await self._client.get("/team", params=query))

    async def update(self, data: lm_types.TeamUpdateRequest) -> lm_types.TeamUpdateResponse:
        return cast(lm_types.TeamUpdateResponse, await self._client.put("/team", data=data))

    async def usage(self) -> lm_types.TeamUsageResponse:
        return cast(lm_types.TeamUsageResponse, await self._client.get("/team/usage"))

    async def roles(self) -> lm_types.TeamRolesResponse:
        return cast(lm_types.TeamRolesResponse, await self._client.get("/team/roles"))

    async def members(self, query: Query | None = None) -> lm_types.TeamMembersResponse:
        return cast(
            lm_types.TeamMembersResponse, await self._client.get("/team/members", params=query)
        )

    async def member(self, user_id: str) -> lm_types.TeamMembersShowResponse:
        return cast(
            lm_types.TeamMembersShowResponse,
            await self._client.get(self._path("/team/members/{userId}", userId=user_id)),
        )

    async def update_member_assignment(
        self, user_id: str, data: lm_types.TeamMembersAssignmentUpdateRequest
    ) -> lm_types.TeamMembersAssignmentUpdateResponse:
        return cast(
            lm_types.TeamMembersAssignmentUpdateResponse,
            await self._client.put(
                self._path("/team/members/{userId}/assignment", userId=user_id),
                data=data,
            ),
        )


class AsyncWebhooksEndpoint(AsyncEndpoint):
    async def list(self, query: Query | None = None) -> lm_types.WebhookIndexResponse:
        return cast(
            lm_types.WebhookIndexResponse, await self._client.get("/webhooks", params=query)
        )

    async def create(self, data: lm_types.WebhookStoreRequest) -> lm_types.WebhookStoreResponse:
        return cast(lm_types.WebhookStoreResponse, await self._client.post("/webhooks", data=data))

    async def retrieve(self, webhook_id: str) -> lm_types.WebhookShowResponse:
        return cast(
            lm_types.WebhookShowResponse,
            await self._client.get(self._path("/webhooks/{webhookId}", webhookId=webhook_id)),
        )

    async def update(
        self, webhook_id: str, data: lm_types.WebhookUpdateRequest
    ) -> lm_types.WebhookUpdateResponse:
        return cast(
            lm_types.WebhookUpdateResponse,
            await self._client.put(
                self._path("/webhooks/{webhookId}", webhookId=webhook_id), data=data
            ),
        )

    async def delete(self, webhook_id: str) -> lm_types.WebhookDestroyResponse:
        return cast(
            lm_types.WebhookDestroyResponse,
            await self._client.delete(self._path("/webhooks/{webhookId}", webhookId=webhook_id)),
        )

    async def test(self, webhook_id: str) -> lm_types.WebhookTestResponse:
        return cast(
            lm_types.WebhookTestResponse,
            await self._client.post(
                self._path("/webhooks/{webhookId}/test", webhookId=webhook_id), data={}
            ),
        )

    async def regenerate_secret(self, webhook_id: str) -> lm_types.WebhookRegenerateSecretResponse:
        return cast(
            lm_types.WebhookRegenerateSecretResponse,
            await self._client.post(
                self._path("/webhooks/{webhookId}/regenerate-secret", webhookId=webhook_id), data={}
            ),
        )

    async def deliveries(
        self, webhook_id: str, query: Query | None = None
    ) -> lm_types.WebhookDeliveriesResponse:
        return cast(
            lm_types.WebhookDeliveriesResponse,
            await self._client.get(
                self._path("/webhooks/{webhookId}/deliveries", webhookId=webhook_id), params=query
            ),
        )

    async def delivery(
        self, webhook_id: str, delivery_id: str
    ) -> lm_types.WebhookShowDeliveryResponse:
        return cast(
            lm_types.WebhookShowDeliveryResponse,
            await self._client.get(
                self._path(
                    "/webhooks/{webhookId}/deliveries/{deliveryId}",
                    webhookId=webhook_id,
                    deliveryId=delivery_id,
                )
            ),
        )
