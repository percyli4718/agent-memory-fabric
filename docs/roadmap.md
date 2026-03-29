# Roadmap

## Planning Goal

This roadmap is designed to make the project executable in stages and easy to hand off between different
models, contributors, and sessions without losing architectural intent.

## North Star

Build a vendor-neutral, governance-ready memory layer that allows agent tools to persist, search, and
reuse structured memory across sessions, repositories, and teams through MCP.

## Phase Overview

### Phase 0: Foundation and Project Framing

Goal:
Lock the product boundary, naming, architecture direction, and open source expectations.

Deliverables:

- project naming and slogan
- README positioning
- strategy and boundary notes
- repository structure draft
- MCP tool design draft
- security direction and threat priorities

Exit criteria:

- the project story is coherent
- the open core and enterprise extension boundary is explicit
- the first implementation phase has a clear scope

### Phase 1: Open Core v0.1

Goal:
Ship the smallest useful vertical slice that proves cross-session memory search through MCP.

Deliverables:

- `memory_record` schema
- SQLite backend
- PostgreSQL backend
- basic MCP server
- structured write flow
- bounded search flow
- local quickstart
- sample AGENTS.md integration

Exit criteria:

- a user can run the MCP server locally
- an agent can write structured memory
- a later session can search and retrieve it
- scope boundaries are enforced at repository or project level

### Phase 2: Team-Ready v0.2

Goal:
Make the system usable by a small team with basic governance and operational confidence.

Deliverables:

- audit log model
- retention and deletion policies
- redact workflow
- repository and project adapters
- access control hooks
- policy examples
- basic deployment templates

Exit criteria:

- memory mutations are auditable
- redaction and deletion flows exist
- team deployments can isolate project and repository scopes
- docs explain trust boundaries and expected operations

### Phase 3: Enterprise-Ready v0.3

Goal:
Add the controls required for serious organizational adoption without compromising the open core boundary.

Deliverables:

- multi-tenant model
- stronger auth integration points
- policy engine expansion
- SBOM and provenance pipelines
- signed releases
- OpenSSF Scorecard integration
- compatibility matrix across agent platforms

Exit criteria:

- the project has an auditable supply-chain posture
- deployment and security docs are production-oriented
- the project can articulate supported trust and tenancy models

### Phase 4: Ecosystem and Portability v1.0

Goal:
Become a credible shared memory substrate across multiple agent ecosystems.

Deliverables:

- stable MCP tool contracts
- versioned schemas
- SDKs or reference clients
- adapters for major agent platforms
- migration guide
- upgrade and compatibility policy

Exit criteria:

- contracts are stable enough for third-party integrations
- platform adapters have documented support status
- maintainers can accept community integrations without destabilizing the core

## Workstreams

### 1. Core Runtime

- memory schema
- storage abstraction
- indexing and retrieval
- summarization and compaction contracts

### 2. MCP Surface

- tool definitions
- schema validation
- auth hooks
- error model

### 3. Governance

- scope and visibility model
- retention and deletion model
- audit trail model
- redaction model

### 4. Ecosystem Integration

- AGENTS.md patterns
- adapter conventions
- example repository integration
- client configuration examples

### 5. Open Source Readiness

- repo health files
- CI basics
- release process
- supply-chain security

## Suggested Execution Order

1. Finalize `memory_record` schema and enums
2. Define JSON Schemas for the first MCP tools
3. Build SQLite reference backend
4. Build minimal MCP server with `search_memory` and `write_memory`
5. Add project and repo scope enforcement
6. Add recent-context and decision retrieval tools
7. Add local deployment example
8. Add governance and audit primitives
9. Expand adapters and ecosystem docs

## Risks To Watch Early

- tool surface grows faster than governance
- memory capture becomes raw transcript dumping
- vendor-specific shortcuts leak into the core
- retrieval ignores scope boundaries
- security posture lags behind project visibility
