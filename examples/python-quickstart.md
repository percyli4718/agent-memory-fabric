# Python Quickstart

## Local Development

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
amf-mcp-server --db-path ./tmp/amf.db
```

## Current State

The current server uses the official Python MCP SDK through `FastMCP` and a SQLite-backed reference store
for the first tools.

## Next Steps

- add richer validation and tests
- add project- and repo-scoped retrieval helpers
