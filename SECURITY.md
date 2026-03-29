# Security Policy

## Scope

Agent Memory Fabric stores and retrieves operational memory that may include architecture decisions,
incident notes, bugfix summaries, workflow conventions, and repository context. Because this data can
be sensitive, security controls are part of the core design rather than an optional add-on.

## Security Objectives

- Protect secrets and credentials from ingestion and retrieval
- Prevent cross-tenant and cross-project memory leakage
- Ensure memory writes are attributable and auditable
- Support redaction, deletion, and retention workflows
- Minimize tool abuse through scoped permissions and explicit actions

## Non-Goals

- Storing raw secrets, tokens, passwords, or API keys
- Acting as a vault or secret manager
- Persisting unrestricted full-session transcripts by default
- Bypassing enterprise identity, approval, or audit systems

## Threat Model Priorities

1. Prompt injection through external content
2. Over-broad memory recall across repositories or tenants
3. Sensitive data capture during write operations
4. Unauthorized or weakly-attributed mutation of memory records
5. Supply chain compromise in dependencies, containers, or MCP transports

## Baseline Controls

- Scope every memory record by tenant, project, repository, and visibility
- Separate read tools from write tools
- Require explicit author and source metadata for write operations
- Support redact and delete actions with audit trails
- Add retention policies and optional time-to-live support
- Log retrieval and mutation events for later review
- Ship schema validation on all MCP inputs

## Recommended Open Source Project Files

The repository should include and maintain:

- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `LICENSE`
- signed releases
- SBOM generation
- dependency and provenance checks in CI

## Vulnerability Disclosure

Until a dedicated security inbox is configured, do not disclose vulnerabilities in public issue threads.
Use a private reporting path and coordinate a fix before public disclosure.

## Roadmap Security Work

- Add a formal threat model document
- Publish supported deployment modes and trust boundaries
- Add secret detection and redaction guidance
- Add SLSA provenance and release signing
- Add OpenSSF Scorecard checks in CI
