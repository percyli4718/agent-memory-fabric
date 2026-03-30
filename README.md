# Agent Memory Fabric

> One memory layer for every agent.

Agent Memory Fabric is a vendor-neutral memory layer for coding agents and enterprise AI workflows.
It helps teams persist, search, govern, and reuse memory across sessions, repositories, and agent tools
without binding the core system to one model vendor, one IDE, or one runtime.

## Positioning

Agent Memory Fabric is designed around four principles:

1. Protocol first
   The primary integration surface is MCP so multiple agent platforms can use the same memory system.
2. Vendor neutrality
   The core does not depend on one model provider, one embedding provider, or one client tool.
3. Governance by design
   Auditability, scope isolation, redaction, retention, and policy controls are first-class concerns.
4. Open core, enterprise extension
   The open source core focuses on protocols, interfaces, runtime, and governance. Enterprise-specific
   customization can extend the system without forking the model.

## What This Project Is

- A memory runtime for agent workflows
- An MCP server for read and write memory operations
- A schema and policy layer for memory scope, retention, and visibility
- A reference architecture for cross-platform agent memory
- A foundation for repository-level and team-level memory search across sessions

## What This Project Is Not

- A plugin locked to one vendor or one coding tool
- A closed SaaS backend
- A system that stores raw secrets or unrestricted chat transcripts by default
- A replacement for source control, issue trackers, or document stores

## Architecture

The project is split into four main layers:

1. `core/`
   The memory domain model, indexing pipeline, retrieval logic, retention rules, and policy evaluation.
2. `mcp-server/`
   The canonical protocol surface that exposes memory operations to agent tools.
3. `adapters/`
   Client integrations for different agent platforms and hosting environments.
4. `policies/` and `schemas/`
   Shared contracts for visibility, tenancy, data typing, redaction, and tool permissions.

## Repository Structure

```text
agent-memory-fabric/
├── README.md
├── SECURITY.md
├── AGENTS.md
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

See [docs/repository-structure.md](docs/repository-structure.md)
for the intended responsibilities of each directory.

## Additional Docs

- Architecture: [docs/architecture.md](docs/architecture.md)
- Threat model: [docs/threat-model.md](docs/threat-model.md)
- Tech stack: [docs/tech-stack.md](docs/tech-stack.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## MCP Surface

The initial MCP tool surface is intentionally small and auditable:

- `search_memory`
- `write_memory`
- `get_recent_project_context`
- `get_decisions`
- `get_open_questions`
- `upsert_fact`
- `list_memories_by_repo`
- `redact_memory`

See [docs/mcp-tools.md](docs/mcp-tools.md) for the v0.1 design.

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Run MCP server
amf-mcp-server --db-path ~/.amf/memory.db

# Run verification
python examples/v0.1-verification.py
```

## Client Integration

Configure Agent Memory Fabric in your preferred agent platform:

- **Claude Code**: Add to `~/.claude/settings.json`
- **Codex (VS Code)**: Add to `.vscode/mcp.json`
- **Gemini CLI**: Add to `~/.gemini/mcp_config.json`
- **Cursor**: Settings → Features → MCP

See [docs/mcp-client-integration.md](docs/mcp-client-integration.md) for detailed setup instructions.

## Planning

The project now includes both a multi-phase roadmap and an explicit model handoff document so work can
continue smoothly across sessions, contributors, and agent tools.

- Overall roadmap: [docs/roadmap.md](docs/roadmap.md)
- Model handoff: [docs/model-handoff.md](docs/model-handoff.md)
- Strategy notes in Chinese: [docs/strategy-notes.zh-CN.md](docs/strategy-notes.zh-CN.md)

## Security and Compliance

This project treats memory as sensitive operational data.
The default design assumes:

- no raw secret storage
- scoped read and write permissions
- auditable writes
- retention and deletion controls
- tenant, project, repository, and user boundaries

See [SECURITY.md](SECURITY.md)
for the initial security model and disclosure guidance.

## v0.1 Scope

The first milestone targets a small but complete vertical slice:

- memory domain model
- reference MCP server
- SQLite and PostgreSQL storage adapters
- basic retrieval and structured write flow
- repository and project scoped memory
- session summary persistence
- local deployment example

See [docs/v0.1-milestone.md](docs/v0.1-milestone.md)
for the milestone checklist.

## Python Skeleton

The repository now includes an initial Python package layout under `src/agent_memory_fabric/`, a
`pyproject.toml`, a SQLite-backed reference store, and a minimal stdio server skeleton for the first tools.

See [examples/python-quickstart.md](examples/python-quickstart.md)
for the current local development flow.

## Why This Exists

Modern agent tools can reason well within a single session, but teams still lose valuable knowledge between
sessions, across repositories, and across tools. Agent Memory Fabric aims to provide one shared memory layer
that remains portable, inspectable, and governable.
