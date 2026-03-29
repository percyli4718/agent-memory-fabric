from __future__ import annotations

import argparse
from typing import Any

from mcp.server.fastmcp import FastMCP

from agent_memory_fabric.schema_loader import load_schema
from agent_memory_fabric.storage.sqlite import SQLiteMemoryStore


def build_mcp(db_path: str) -> FastMCP:
    store = SQLiteMemoryStore(db_path)
    mcp = FastMCP(
        "Agent Memory Fabric",
        instructions=(
            "Structured memory server for cross-session agent workflows. "
            "Use bounded project and repository scopes for all retrieval."
        ),
    )

    @mcp.tool(
        description="Search memory records within a bounded tenant, project, and repository scope."
    )
    def search_memory(payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("search-memory.request.schema.json")
        results = [record.to_dict() for record in store.search_memory(payload)]
        return {"results": results, "count": len(results)}

    @mcp.tool(description="Write a structured memory record.")
    def write_memory(payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("write-memory.request.schema.json")
        record = store.write_memory(payload)
        return {"memory": record.to_dict()}

    @mcp.tool(
        description="Get the most recent structured project context within explicit scopes."
    )
    def get_recent_project_context(payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("get-recent-project-context.request.schema.json")
        results = [record.to_dict() for record in store.get_recent_project_context(payload)]
        return {"results": results, "count": len(results)}

    @mcp.tool(description="Get recent decision records within explicit scopes.")
    def get_decisions(payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("get-decisions.request.schema.json")
        results = [record.to_dict() for record in store.get_decisions(payload)]
        return {"results": results, "count": len(results)}

    @mcp.tool(description="Get open questions and TODO-style records within explicit scopes.")
    def get_open_questions(payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("get-open-questions.request.schema.json")
        results = [record.to_dict() for record in store.get_open_questions(payload)]
        return {"results": results, "count": len(results)}

    return mcp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent Memory Fabric MCP server")
    parser.add_argument("--db-path", default="./tmp/agent-memory-fabric.db")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    mcp = build_mcp(args.db_path)
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
