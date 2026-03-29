# MCP Tools Design

## Design Goals

- Keep the v0.1 tool surface small
- Make every mutation auditable
- Separate retrieval from mutation
- Preserve portability across agent tools

## Shared Concepts

Every memory record should include:

- `memory_id`
- `tenant`
- `project`
- `repository`
- `scope`
- `visibility`
- `type`
- `summary`
- `details`
- `tags`
- `author`
- `source`
- `created_at`
- `updated_at`

## v0.1 Tool Set

### `search_memory`

Purpose:
Search relevant memory by text query, filters, and scope.

Suggested input:

```json
{
  "query": "deployment rollback issue",
  "tenant": "default",
  "project": "payments",
  "repository": "api-gateway",
  "scope": ["repo", "project"],
  "types": ["incident", "decision", "bugfix"],
  "limit": 10
}
```

### `write_memory`

Purpose:
Create a new memory record from a structured summary rather than a raw transcript.

Suggested input:

```json
{
  "tenant": "default",
  "project": "payments",
  "repository": "api-gateway",
  "scope": "repo",
  "visibility": "team",
  "type": "decision",
  "summary": "Use canary deploys for gateway changes",
  "details": "Production rollouts should begin with a canary slice.",
  "tags": ["deploy", "gateway", "risk-control"],
  "author": "agent-or-user-id",
  "source": "session-summary"
}
```

### `get_recent_project_context`

Purpose:
Fetch a compact set of recent memories for the current project or repository.

v0.1 note:
The current implementation requires explicit scopes and supports `user`, `repo`, and `project`.

### `get_decisions`

Purpose:
Return architecture and workflow decisions within a given scope.

v0.1 note:
This currently returns only `decision` records within explicitly bounded scopes.

### `get_open_questions`

Purpose:
Return unresolved questions, risks, and TODO-style memory items.

v0.1 note:
This currently returns `question` and `todo` records within explicitly bounded scopes.

### `upsert_fact`

Purpose:
Create or update durable facts such as service ownership, deployment locations, or operational conventions.

### `list_memories_by_repo`

Purpose:
List recent or filtered memory records for a repository without semantic search.

### `redact_memory`

Purpose:
Redact sensitive content while preserving audit metadata and the record lifecycle.

## Deliberately Excluded From v0.1

- raw transcript ingestion
- unrestricted delete without audit trail
- autonomous background scraping of all repositories
- broad cross-tenant recall
- write paths without scope or author metadata

## v0.1 Policy Constraints

- writes support only `user`, `repo`, and `project` scopes
- `user` scope supports only `private` visibility
- `repo` scope supports `private` and `team` visibility
- `project` scope supports only `team` visibility
- retrieval requires an explicit scope list
- retrieval currently rejects `team` and `org` scopes until a stronger auth model exists
