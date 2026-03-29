# Tech Stack Decision

## Decision

Agent Memory Fabric uses:

- Python for the open core runtime and initial MCP server
- JSON Schema for language-neutral contracts
- TypeScript later for edge adapters and optional client SDKs

## Why Python First

Python is the best fit for the first implementation because the project's center of gravity is memory
runtime, policy enforcement, retrieval, storage integration, and AI infrastructure interoperability.

Python aligns well with:

- agent runtime ecosystems
- vector and retrieval tooling
- data validation and storage integration
- reference implementations that can be understood by a broad AI infrastructure audience

## Why Not TypeScript First

TypeScript is strong for edge integrations, frontend-adjacent tooling, and Node-centric agent apps, but the
open core of this project is more infrastructure-oriented than UI- or app-oriented. Starting with Python
reduces friction for SQLite, PostgreSQL, and retrieval experimentation in v0.1.

## Long-Term Position

The project remains vendor neutral and language aware:

- the runtime core starts in Python
- contracts stay in JSON Schema
- edge adapters and SDKs can later be added in TypeScript

## Implications For v0.1

- package with `pyproject.toml`
- Python source lives under `src/agent_memory_fabric/`
- the first server entrypoint uses the official Python MCP SDK
- storage starts with SQLite as the local reference backend

## Revisit Criteria

Revisit this decision only if:

- most integrations become Node-only
- contributors strongly cluster around TypeScript
- the Python runtime proves to be a portability bottleneck
