# AGENTS.md

## Mission

Build Agent Memory Fabric as a vendor-neutral memory layer for coding agents and enterprise AI workflows.

## Core Constraints

- Keep the core protocol and storage model vendor neutral
- Treat MCP as the primary interoperability surface
- Prefer structured memory over raw transcript capture
- Never store secrets by default
- Preserve auditability, scope isolation, and deletion support

## Design Priorities

1. Safety before convenience
2. Clear schemas before broad features
3. Small MCP tool surfaces before automation sprawl
4. Portable adapters before vendor-specific optimization

## Working Rules

- Any new memory write path must define scope, author, source, and visibility
- Any retrieval path must define access boundaries
- New adapters must not bypass policy enforcement
- Documentation changes should keep the open core and enterprise extension boundary explicit
