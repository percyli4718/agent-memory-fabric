# Repository Structure

## Top Level Layout

```text
agent-memory-fabric/
├── core/
├── mcp-server/
├── adapters/
├── sdk/
├── schemas/
├── policies/
├── deploy/
├── examples/
├── docs/
└── .github/workflows/
```

## Directory Responsibilities

### `core/`

- memory record model
- indexing and retrieval logic
- summarization and compaction pipeline contracts
- retention and visibility evaluation

### `mcp-server/`

- MCP transport entrypoints
- tool registration
- request validation
- auth and policy hooks

### `adapters/`

- agent platform adapters
- repo-local bootstrap helpers
- compatibility shims for different tool ecosystems

### `sdk/`

- typed client libraries
- memory write and read helper functions
- integration utilities for applications and services

### `schemas/`

- JSON schemas
- versioned tool request and response contracts
- memory record definitions

### `policies/`

- retention policy examples
- scope and visibility policies
- redaction rules
- deployment guidance for policy enforcement

### `deploy/`

- local development deployment
- reference Compose or Kubernetes manifests
- production deployment templates

### `examples/`

- example MCP configurations
- sample AGENTS.md files
- example repository integrations

### `docs/`

- architecture notes
- threat model drafts
- roadmap documents
- design proposals

### `.github/workflows/`

- linting
- tests
- SBOM generation
- provenance and release checks
- OpenSSF Scorecard integration
