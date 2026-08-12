"""Tests for v2 API surface and full API endpoint coverage."""

from __future__ import annotations

import json
from typing import get_args

import pytest
import respx
from httpx import Response

from lettermint import AsyncLettermint, Lettermint
from lettermint import types as lm_types


class TestV2Entrypoints:
    @respx.mock
    def test_email_entrypoint_uses_sending_auth_and_raw_ping(self) -> None:
        route = respx.get("https://api.lettermint.co/v1/ping").mock(
            return_value=Response(200, text=" pong")
        )

        with Lettermint.email("sending-token") as email:
            assert email.ping() == "pong"

        request = route.calls.last.request
        assert request.headers["x-lettermint-token"] == "sending-token"
        assert "authorization" not in request.headers

    @respx.mock
    def test_api_entrypoint_uses_bearer_auth_and_raw_ping(self) -> None:
        route = respx.get("https://api.lettermint.co/v1/ping").mock(
            return_value=Response(200, text=" pong")
        )

        with Lettermint.api("api-token") as api:
            assert api.ping() == "pong"

        request = route.calls.last.request
        assert request.headers["authorization"] == "Bearer api-token"
        assert "x-lettermint-token" not in request.headers

    @respx.mock
    def test_api_blocked_file_types_uses_bearer_auth(self) -> None:
        route = respx.get("https://api.lettermint.co/v1/blocked-file-types").mock(
            return_value=Response(
                200,
                json={
                    "extensions": ["exe"],
                    "mime_types": ["application/x-msdownload"],
                },
            )
        )

        with Lettermint.api("api-token") as api:
            response = api.blocked_file_types()

        assert response["extensions"] == ["exe"]
        request = route.calls.last.request
        assert request.headers["authorization"] == "Bearer api-token"
        assert "x-lettermint-token" not in request.headers

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_entrypoints_use_matching_auth(self) -> None:
        email_route = respx.get("https://api.lettermint.co/v1/ping").mock(
            return_value=Response(200, text="pong")
        )

        async with AsyncLettermint.email("sending-token") as email:
            assert await email.ping() == "pong"

        assert email_route.calls.last.request.headers["x-lettermint-token"] == "sending-token"

        api_route = respx.get("https://api.lettermint.co/v1/ping").mock(
            return_value=Response(200, text="pong")
        )

        async with AsyncLettermint.api("api-token") as api:
            assert await api.ping() == "pong"

        assert api_route.calls.last.request.headers["authorization"] == "Bearer api-token"

    def test_async_api_exposes_full_endpoint_groups(self) -> None:
        api = AsyncLettermint.api("api-token")

        assert hasattr(api, "domains")
        assert hasattr(api, "messages")
        assert hasattr(api, "projects")
        assert hasattr(api, "routes")
        assert hasattr(api, "stats")
        assert hasattr(api, "suppressions")
        assert hasattr(api, "team")
        assert hasattr(api, "webhooks")
        assert hasattr(api, "blocked_file_types")
        assert hasattr(api.team, "roles")
        assert hasattr(api.team, "member")
        assert hasattr(api.team, "update_member_assignment")


class TestSendingEndpoint:
    @respx.mock
    def test_send_batch_posts_list_payload(self) -> None:
        route = respx.post("https://api.lettermint.co/v1/send/batch").mock(
            return_value=Response(200, json=[{"message_id": "msg_123", "status": "queued"}])
        )

        with Lettermint.email("sending-token") as email:
            response = email.send_batch(
                [
                    {
                        "from": "sender@example.com",
                        "to": ["recipient@example.com"],
                        "subject": "Hello",
                    }
                ]
            )

        assert response[0]["message_id"] == "msg_123"
        assert json.loads(route.calls.last.request.content)[0]["subject"] == "Hello"


class TestFullApiEndpoints:
    @respx.mock
    def test_domain_endpoints_map_requests(self) -> None:
        list_route = respx.get("https://api.lettermint.co/v1/domains").mock(
            return_value=Response(200, json={"data": []})
        )
        retrieve_route = respx.get("https://api.lettermint.co/v1/domains/domain%201").mock(
            return_value=Response(200, json={"data": {"id": "domain 1"}})
        )
        create_route = respx.post("https://api.lettermint.co/v1/domains").mock(
            return_value=Response(201, json={"data": {"id": "domain 1"}})
        )
        delete_route = respx.delete("https://api.lettermint.co/v1/domains/domain%201").mock(
            return_value=Response(200, json={"deleted": True})
        )

        with Lettermint.api("api-token") as api:
            assert api.domains.list({"page[size]": "5"})["data"] == []
            assert api.domains.retrieve("domain 1")["data"]["id"] == "domain 1"
            assert api.domains.create({"domain": "example.com"})["data"]["id"] == "domain 1"
            assert api.domains.delete("domain 1")["deleted"] is True

        assert list_route.calls.last.request.url.params["page[size]"] == "5"
        assert retrieve_route.called
        assert json.loads(create_route.calls.last.request.content) == {"domain": "example.com"}
        assert delete_route.called

    @respx.mock
    def test_message_raw_body_endpoints(self) -> None:
        source_route = respx.get("https://api.lettermint.co/v1/messages/message-id/source").mock(
            return_value=Response(200, text="raw source")
        )
        html_route = respx.get("https://api.lettermint.co/v1/messages/message-id/html").mock(
            return_value=Response(200, text="<p>Hello</p>")
        )
        text_route = respx.get("https://api.lettermint.co/v1/messages/message-id/text").mock(
            return_value=Response(200, text="Hello")
        )

        with Lettermint.api("api-token") as api:
            assert api.messages.source("message-id") == "raw source"
            assert api.messages.html("message-id") == "<p>Hello</p>"
            assert api.messages.text("message-id") == "Hello"

        assert source_route.called
        assert html_route.called
        assert text_route.called

    @respx.mock
    def test_team_role_and_member_assignment_endpoints(self) -> None:
        roles_route = respx.get("https://api.lettermint.co/v1/team/roles").mock(
            return_value=Response(200, json={"data": []})
        )
        member_route = respx.get("https://api.lettermint.co/v1/team/members/user%2Fid").mock(
            return_value=Response(200, json={"id": "user/id"})
        )
        assignment_route = respx.put(
            "https://api.lettermint.co/v1/team/members/user%2Fid/assignment"
        ).mock(return_value=Response(200, json={"id": "user/id"}))
        assignment: lm_types.TeamMembersAssignmentUpdateRequest = {
            "role_id": "role_123",
            "project_access": {"scope": "all"},
        }

        with Lettermint.api("api-token") as api:
            assert api.team.roles()["data"] == []
            assert api.team.member("user/id")["id"] == "user/id"
            assert api.team.update_member_assignment("user/id", assignment)["id"] == "user/id"

        assert roles_route.called
        assert member_route.called
        assert json.loads(assignment_route.calls.last.request.content) == assignment

    def test_documented_operations_are_exposed(self) -> None:
        operations = [
            (Lettermint.email("token"), "send"),
            (Lettermint.email("token"), "send_batch"),
            (Lettermint.email("token"), "ping"),
            (Lettermint.api("token"), "ping"),
            (Lettermint.api("token"), "blocked_file_types"),
            (Lettermint.api("token").domains, "list"),
            (Lettermint.api("token").domains, "create"),
            (Lettermint.api("token").domains, "retrieve"),
            (Lettermint.api("token").domains, "delete"),
            (Lettermint.api("token").domains, "verify_dns_records"),
            (Lettermint.api("token").domains, "verify_dns_record"),
            (Lettermint.api("token").domains, "update_projects"),
            (Lettermint.api("token").messages, "list"),
            (Lettermint.api("token").messages, "retrieve"),
            (Lettermint.api("token").messages, "events"),
            (Lettermint.api("token").messages, "source"),
            (Lettermint.api("token").messages, "html"),
            (Lettermint.api("token").messages, "text"),
            (Lettermint.api("token").projects, "list"),
            (Lettermint.api("token").projects, "create"),
            (Lettermint.api("token").projects, "retrieve"),
            (Lettermint.api("token").projects, "update"),
            (Lettermint.api("token").projects, "delete"),
            (Lettermint.api("token").projects, "rotate_token"),
            (Lettermint.api("token").projects, "routes"),
            (Lettermint.api("token").projects, "create_route"),
            (Lettermint.api("token").routes, "retrieve"),
            (Lettermint.api("token").routes, "update"),
            (Lettermint.api("token").routes, "delete"),
            (Lettermint.api("token").routes, "verify_inbound_domain"),
            (Lettermint.api("token").stats, "retrieve"),
            (Lettermint.api("token").suppressions, "list"),
            (Lettermint.api("token").suppressions, "create"),
            (Lettermint.api("token").suppressions, "delete"),
            (Lettermint.api("token").team, "retrieve"),
            (Lettermint.api("token").team, "update"),
            (Lettermint.api("token").team, "usage"),
            (Lettermint.api("token").team, "roles"),
            (Lettermint.api("token").team, "members"),
            (Lettermint.api("token").team, "member"),
            (Lettermint.api("token").team, "update_member_assignment"),
            (Lettermint.api("token").webhooks, "list"),
            (Lettermint.api("token").webhooks, "create"),
            (Lettermint.api("token").webhooks, "retrieve"),
            (Lettermint.api("token").webhooks, "update"),
            (Lettermint.api("token").webhooks, "delete"),
            (Lettermint.api("token").webhooks, "test"),
            (Lettermint.api("token").webhooks, "regenerate_secret"),
            (Lettermint.api("token").webhooks, "deliveries"),
            (Lettermint.api("token").webhooks, "delivery"),
        ]

        missing = [method for endpoint, method in operations if not hasattr(endpoint, method)]

        assert missing == []

    def test_generated_types_match_current_team_schema(self) -> None:
        assert "auto_replied" in get_args(lm_types.MessageEventType)
        assert "message.auto_replied" in get_args(lm_types.WebhookEvent)
        assert "admin" in get_args(lm_types.BuiltInTeamRole)
        assert "members:manage" in get_args(lm_types.RbacPermission)
        assert "enforced" in get_args(lm_types.TlsPolicy)
        assert "global" in get_args(lm_types.SuppressionScope)

        assert "short_token" in lm_types.StoreProjectData.__annotations__
        assert "redact_email_content" in lm_types.ProjectData.__annotations__
        assert "redact_email_content" in lm_types.UpdateProjectData.__annotations__
        assert hasattr(lm_types, "UpdateRouteSettingsData")
        assert hasattr(lm_types, "UpdateRouteInboundSettingsData")
        assert hasattr(lm_types, "BlockedFileTypesResponse")
        assert "extensions" in lm_types.BlockedFileTypesResponse.__annotations__
        assert "mime_types" in lm_types.BlockedFileTypesResponse.__annotations__
        assert "redact_email_content" in lm_types.UpdateRouteSettingsData.__annotations__
        assert "generate_plaintext_fallback" in lm_types.UpdateRouteSettingsData.__annotations__
        assert "tls" in lm_types.UpdateRouteSettingsData.__annotations__
        assert "inbound_spam_threshold" in lm_types.UpdateRouteInboundSettingsData.__annotations__
        assert "included_volume" in lm_types.TeamData.__annotations__
        assert "assignable" in lm_types.TeamRoleData.__annotations__
        assert "role_id" in lm_types.UpdateTeamMemberAssignmentData.__annotations__
        assert "dkim_mode" in lm_types.DomainData.__annotations__
        assert "source_message" in lm_types.SuppressedRecipientData.__annotations__
        assert "spam_score" in lm_types.MessageListData.__annotations__
