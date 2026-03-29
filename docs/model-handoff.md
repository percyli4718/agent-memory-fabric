# Model Handoff

## Purpose

This document exists so another model, agent, or contributor can continue the project with minimal context
loss if the current session ends or the current model quota is exhausted.

## Current Project Identity

- Project name: `Agent Memory Fabric`
- Slogan: `One memory layer for every agent.`
- Location: `/home/sanding/workspace/openProject/agent-memory-fabric`

## Core Product Direction

Agent Memory Fabric is an open source, vendor-neutral memory infrastructure project for coding agents and
enterprise AI workflows. The open core is responsible for protocols, interfaces, runtime, and governance.
Enterprise customization is expected to extend the project rather than contaminate the open core boundary.

## Agreed Architectural Direction

1. MCP is the primary interoperability layer
2. AGENTS.md is the preferred behavior-contract layer for repository instructions
3. Skills or workflow packs should orchestrate memory usage, not replace storage
4. Plugins are packaging and distribution units, not the memory substrate
5. Structured memory is preferred over full raw transcript capture

## Agreed Boundaries

The open source core should include:

- memory schemas
- MCP server
- policy model
- audit and scope primitives
- reference storage backends
- reference deployment patterns

The enterprise layer can extend:

- SSO and organization auth
- private connectors
- stronger multi-tenant operations
- enterprise compliance integrations
- advanced governance workflows

## Files Created So Far

- [README.md](/home/sanding/workspace/openProject/agent-memory-fabric/README.md)
- [SECURITY.md](/home/sanding/workspace/openProject/agent-memory-fabric/SECURITY.md)
- [AGENTS.md](/home/sanding/workspace/openProject/agent-memory-fabric/AGENTS.md)
- [pyproject.toml](/home/sanding/workspace/openProject/agent-memory-fabric/pyproject.toml)
- [docs/strategy-notes.zh-CN.md](/home/sanding/workspace/openProject/agent-memory-fabric/docs/strategy-notes.zh-CN.md)
- [docs/repository-structure.md](/home/sanding/workspace/openProject/agent-memory-fabric/docs/repository-structure.md)
- [docs/mcp-tools.md](/home/sanding/workspace/openProject/agent-memory-fabric/docs/mcp-tools.md)
- [docs/v0.1-milestone.md](/home/sanding/workspace/openProject/agent-memory-fabric/docs/v0.1-milestone.md)
- [docs/roadmap.md](/home/sanding/workspace/openProject/agent-memory-fabric/docs/roadmap.md)
- [docs/tech-stack.md](/home/sanding/workspace/openProject/agent-memory-fabric/docs/tech-stack.md)
- [docs/architecture.md](/home/sanding/workspace/openProject/agent-memory-fabric/docs/architecture.md)
- [docs/threat-model.md](/home/sanding/workspace/openProject/agent-memory-fabric/docs/threat-model.md)
- [examples/python-quickstart.md](/home/sanding/workspace/openProject/agent-memory-fabric/examples/python-quickstart.md)

## What Is Missing Next

The next implementation-focused tasks should be:

1. replace the stdio skeleton with a fully compliant MCP SDK implementation
2. add tests for schema validation and SQLite storage behavior
3. add repository and project scope policy enforcement beyond simple query filters
4. add issue templates and CI validation for schemas and packaging
5. add architecture and threat-model refinements as implementation evolves
6. implement the remaining v0.1 tools beyond `search_memory` and `write_memory`

## Recommended Next Prompt For Another Model

Use this prompt to continue:

```text
Continue the Agent Memory Fabric project at /home/sanding/workspace/openProject/agent-memory-fabric.
Read README.md, docs/roadmap.md, docs/model-handoff.md, docs/mcp-tools.md, and docs/strategy-notes.zh-CN.md first.
Keep the open-core boundary intact: protocol, interfaces, runtime, and governance belong in core; enterprise-specific
identity, connectors, and compliance integrations should stay out of the open-source core.
Next, implement the project health files and the first memory schemas for v0.1.
Next, review docs/architecture.md, docs/threat-model.md, and docs/tech-stack.md, then extend the Python
implementation under src/agent_memory_fabric/ from the current SQLite-backed stdio skeleton toward a fully
compliant MCP server with tests.
```

## Handoff Rules

- do not rename the project unless the user explicitly asks
- preserve vendor neutrality
- prefer small auditable MCP surfaces
- do not add secret storage features
- do not widen retrieval across scopes without a policy model
