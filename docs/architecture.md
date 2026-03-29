# Architecture

## Goal

Agent Memory Fabric provides a vendor-neutral memory layer for agent tools. Its architecture is designed to
preserve portability, governance, and clear boundaries between open core responsibilities and enterprise
extensions.

## Core Layers

### 1. Memory Core

Responsibilities:

- define the memory domain model
- normalize writes into structured records
- evaluate scope, visibility, and retention
- execute retrieval and ranking
- support redaction and lifecycle transitions

### 2. MCP Server

Responsibilities:

- expose tool contracts for memory operations
- validate inputs and outputs against schemas
- enforce auth and policy hooks
- keep protocol behavior stable and auditable

### 3. Storage Adapters

Responsibilities:

- persist memory records and indexes
- support local development and team deployments
- keep storage implementation behind an abstraction boundary

Initial targets:

- SQLite for local use
- PostgreSQL for shared deployments

### 4. Ecosystem Adapters

Responsibilities:

- integrate with coding agents and surrounding tooling
- provide examples without weakening policy enforcement
- preserve the vendor-neutral core contract

## Data Flow

1. An agent invokes an MCP tool such as `write_memory`
2. The MCP server validates the request against schema
3. The core evaluates policy constraints such as scope and visibility
4. The storage adapter persists the record and metadata
5. Another session invokes `search_memory` or `get_recent_project_context`
6. The MCP server retrieves bounded results and returns structured records

## Boundary Rules

Open core includes:

- schemas
- MCP contracts
- runtime behavior
- storage abstraction
- policy primitives
- audit primitives

Enterprise extensions may add:

- SSO integrations
- advanced multi-tenant control planes
- organization-specific connectors
- compliance workflows and reporting

## Non-Goals

- raw secret storage
- unrestricted transcript dumps
- vendor-specific logic embedded in the core runtime
- cross-scope recall without policy checks
