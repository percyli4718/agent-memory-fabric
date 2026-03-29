# Contributing

Thanks for considering a contribution to Agent Memory Fabric.

## Project Priorities

Please align contributions with the current project direction:

- preserve vendor neutrality
- keep MCP as the primary interoperability surface
- prefer structured memory over raw transcript capture
- protect scope boundaries and auditability
- keep the open core and enterprise extension boundary explicit

## Before You Start

Read these files first:

- [README.md](/home/sanding/workspace/openProject/agent-memory-fabric/README.md)
- [AGENTS.md](/home/sanding/workspace/openProject/agent-memory-fabric/AGENTS.md)
- [docs/roadmap.md](/home/sanding/workspace/openProject/agent-memory-fabric/docs/roadmap.md)
- [docs/model-handoff.md](/home/sanding/workspace/openProject/agent-memory-fabric/docs/model-handoff.md)
- [SECURITY.md](/home/sanding/workspace/openProject/agent-memory-fabric/SECURITY.md)

## Good First Contributions

- refine schemas in `schemas/`
- improve docs and examples
- add tests around scope and visibility handling
- improve MCP tool validation and error messages
- add reference adapters that do not weaken policy enforcement

## Change Guidelines

- keep changes scoped and easy to review
- add or update documentation when behavior changes
- preserve backward compatibility for public contracts when possible
- avoid adding vendor-specific assumptions to the open core
- do not add secret capture or broad transcript ingestion features by default

## Pull Request Expectations

Each pull request should explain:

- what changed
- why it changed
- which roadmap phase it supports
- whether it affects schemas, tool contracts, or policy behavior
- any security implications

## Security-Sensitive Changes

If your change affects auth, policy enforcement, memory visibility, redaction, deletion, or data retention,
call that out explicitly in the PR description.

Do not file public issues for undisclosed vulnerabilities. Follow
[SECURITY.md](/home/sanding/workspace/openProject/agent-memory-fabric/SECURITY.md).
