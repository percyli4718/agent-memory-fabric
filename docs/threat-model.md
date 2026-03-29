# Threat Model

## Purpose

This document outlines the initial security concerns for Agent Memory Fabric so implementation decisions stay
aligned with the project's governance and safety goals.

## Assets To Protect

- structured memory records
- tenant and repository boundaries
- author and source metadata
- audit trails
- deployment credentials and infrastructure access

## Primary Trust Boundaries

- between agent clients and the MCP server
- between the MCP server and storage backends
- between one tenant, project, or repository scope and another
- between open core components and enterprise integrations

## Key Threats

### 1. Prompt Injection

An attacker can attempt to manipulate memory writes or recalls through untrusted content.

Mitigations:

- validate structured inputs
- avoid raw transcript ingestion by default
- require explicit write operations

### 2. Scope Leakage

Memory from one repository, project, or tenant may be returned to another scope.

Mitigations:

- require explicit scope on writes
- filter retrieval by bounded scope
- separate policy evaluation from adapter logic

### 3. Sensitive Data Ingestion

Secrets or personal data may enter the memory system unintentionally.

Mitigations:

- discourage raw transcript capture
- define redaction paths
- support policy-based filtering and future secret scanning

### 4. Unauthorized Mutation

Attackers or buggy clients may alter memory without attribution or policy controls.

Mitigations:

- require author and source metadata
- maintain audit trails
- separate read and write permissions

### 5. Supply Chain Risks

Dependencies, packages, or images may introduce compromise into the memory runtime.

Mitigations:

- signed releases
- SBOM generation
- provenance checks
- dependency review in CI

## Initial Security Priorities

1. schema validation
2. scope enforcement
3. auditability
4. redaction support
5. supply-chain hygiene
