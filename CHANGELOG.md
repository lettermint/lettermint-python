# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v3.3.0 - 2026-10-30

### What's Changed

* feat: add the inbound.rejected webhook event by @bjarn in https://github.com/lettermint/lettermint-python/pull/45
* feat: manage project API tokens by @bjarn in https://github.com/lettermint/lettermint-python/pull/46
* feat: manage team API tokens by @bjarn in https://github.com/lettermint/lettermint-python/pull/47

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v3.2.0...v3.3.0

## v3.2.0 - 2026-10-23

### What's Changed

* feat: add messages resend by @bjarn in https://github.com/lettermint/lettermint-python/pull/36
* feat: add per-email idempotency keys to batch send by @bjarn in https://github.com/lettermint/lettermint-python/pull/37
* feat: add webhook delivery retry by @bjarn in https://github.com/lettermint/lettermint-python/pull/39
* build(deps): bump actions/create-github-app-token from 3.2.0 to 3.3.0 by @dependabot[bot] in https://github.com/lettermint/lettermint-python/pull/44
* feat: add team invites by @bjarn in https://github.com/lettermint/lettermint-python/pull/40
* feat: add team role management by @bjarn in https://github.com/lettermint/lettermint-python/pull/41
* feat: add team member removal and a project filter for the member list by @bjarn in https://github.com/lettermint/lettermint-python/pull/42

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v3.1.0...v3.2.0

## v3.1.0 - 2026-10-11

### What's Changed

* docs: add the v2.7.0 and v3.0.0 changelog entries by @bjarn in https://github.com/lettermint/lettermint-python/pull/35
* feat: add analytics_pages, retry_after on server errors and the latest API types by @bjarn in https://github.com/lettermint/lettermint-python/pull/34

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v3.0.0...v3.1.0

## v3.0.0 - 2026-10-04

### What's Changed

* feat(webhooks)!: add Basic Auth and required read flags by @bjarn in https://github.com/lettermint/lettermint-python/pull/32
* feat!: Lettermint Python SDK 3.0 by @bjarn in https://github.com/lettermint/lettermint-python/pull/33

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v2.7.0...v3.0.0

## v2.7.0 - 2026-10-01

### What's Changed

* Use the SDK release bot for changelog updates by @bjarn in https://github.com/lettermint/lettermint-python/pull/26
* build(deps): bump actions/create-github-app-token from 2.2.2 to 3.2.0 by @dependabot[bot] in https://github.com/lettermint/lettermint-python/pull/27
* Read the release bot identity from GitHub by @bjarn in https://github.com/lettermint/lettermint-python/pull/28
* feat(api): align sandbox responses with OpenAPI by @bjarn in https://github.com/lettermint/lettermint-python/pull/29
* feat(api): add analytics and project report forwarding by @bjarn in https://github.com/lettermint/lettermint-python/pull/30
* fix(types): expose nullable inbound route domains by @bjarn in https://github.com/lettermint/lettermint-python/pull/31

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v2.6.0...v2.7.0

## v2.6.0 - 2026-09-14

### What's Changed

* feat: add typed message tags by @bjarn in https://github.com/lettermint/lettermint-python/pull/24
* chore: add all team as code owners by @bjarn in https://github.com/lettermint/lettermint-python/pull/25

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v2.5.0...v2.6.0

## v2.5.0 - 2026-09-05

### What's Changed

* feat(api): support quarantined inbound message processing by @bjarn in https://github.com/lettermint/lettermint-python/pull/22

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v2.4.0...v2.5.0

## v2.4.0 - 2026-08-27

### What's Changed

* feat(api): support scheduled message delivery by @bjarn in https://github.com/lettermint/lettermint-python/pull/21

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v2.3.0...v2.4.0

## v2.3.0 - 2026-08-19

### What's Changed

* feat(api): support message tags and disposable email suppression by @bjarn in https://github.com/lettermint/lettermint-python/pull/20

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v2.2.0...v2.3.0

## v2.2.0 - 2026-08-13

### What's Changed

* build(deps): bump actions/setup-python from 6 to 7 by @dependabot[bot] in https://github.com/lettermint/lettermint-python/pull/18
* feat(api): add team RBAC and complete sync and async email options by @bjarn in https://github.com/lettermint/lettermint-python/pull/19

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v2.1.0...v2.2.0

## v2.1.0 - 2026-07-07

### What's Changed

* Delete .github/workflows/dependabot-auto-merge.yml by @bjarn in https://github.com/lettermint/lettermint-python/pull/13
* chore: update README for v2 API by @bjarn in https://github.com/lettermint/lettermint-python/pull/14
* build(deps): bump actions/checkout from 6 to 7 by @dependabot[bot] in https://github.com/lettermint/lettermint-python/pull/15
* ci(release): validate Python release tags by @bjarn in https://github.com/lettermint/lettermint-python/pull/17
* feat: add route settings, webhook auto-reply events, and blocked file types by @bjarn in https://github.com/lettermint/lettermint-python/pull/16

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v2.0.0...v2.1.0

## v2.0.0 - 2026-05-11

### What's Changed

* chore: add Discord badge to README by @bjarn in https://github.com/lettermint/lettermint-python/pull/8
* build(deps): bump dependabot/fetch-metadata from 2 to 3 by @dependabot[bot] in https://github.com/lettermint/lettermint-python/pull/11
* build(deps): bump actions/upload-artifact from 6 to 7 by @dependabot[bot] in https://github.com/lettermint/lettermint-python/pull/9
* feat: implement Team API API endpoints by @bjarn in https://github.com/lettermint/lettermint-python/pull/12

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v1.0.2...v2.0.0

## v1.0.2 - 2025-12-23

### What's Changed

* feat: set custom User-Agent in API requests by @bjarn in https://github.com/lettermint/lettermint-python/pull/7

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v1.0.1...v1.0.2

## v1.0.1 - 2025-12-23

### What's Changed

* build(deps): bump stefanzweifel/git-auto-commit-action from 5 to 7 by @dependabot[bot] in https://github.com/lettermint/lettermint-python/pull/5
* build(deps): bump actions/setup-python from 5 to 6 by @dependabot[bot] in https://github.com/lettermint/lettermint-python/pull/1
* build(deps): bump actions/checkout from 4 to 6 by @dependabot[bot] in https://github.com/lettermint/lettermint-python/pull/2
* build(deps): bump actions/upload-artifact from 4 to 6 by @dependabot[bot] in https://github.com/lettermint/lettermint-python/pull/4
* feat: add badges to README and update type hints in tests by @bjarn in https://github.com/lettermint/lettermint-python/pull/6

### New Contributors

* @dependabot[bot] made their first contribution in https://github.com/lettermint/lettermint-python/pull/5
* @bjarn made their first contribution in https://github.com/lettermint/lettermint-python/pull/6

**Full Changelog**: https://github.com/lettermint/lettermint-python/compare/v1.0.0...v1.0.1

## v1.0.0 - 2025-12-23

*This release is published under the MIT License.*

- Initial release

## [Unreleased]

## [0.1.0] - 2024-01-01

### Added

- Initial release
- `Lettermint` and `AsyncLettermint` clients for sync/async API access
- Email endpoint with fluent builder interface
- Webhook signature verification
- Full type hints with `py.typed` marker
- Support for Python 3.9+
