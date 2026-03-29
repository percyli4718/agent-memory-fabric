from __future__ import annotations

import argparse
from typing import Any

from mcp.server.fastmcp import FastMCP

from agent_memory_fabric.handlers import ToolHandlers
from agent_memory_fabric.storage.sqlite import SQLiteMemoryStore


def build_mcp(db_path: str) -> FastMCP:
    store = SQLiteMemoryStore(db_path)
    handlers = ToolHandlers(store)
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
        return handlers.search_memory(payload)

    @mcp.tool(description="Write a structured memory record.")
    def write_memory(payload: dict[str, Any]) -> dict[str, Any]:
        return handlers.write_memory(payload)

    @mcp.tool(
        description="Get the most recent structured project context within explicit scopes."
    )
    def get_recent_project_context(payload: dict[str, Any]) -> dict[str, Any]:
        return handlers.get_recent_project_context(payload)

    @mcp.tool(description="Get recent decision records within explicit scopes.")
    def get_decisions(payload: dict[str, Any]) -> dict[str, Any]:
        return handlers.get_decisions(payload)

    @mcp.tool(description="Get open questions and TODO-style records within explicit scopes.")
    def get_open_questions(payload: dict[str, Any]) -> dict[str, Any]:
        return handlers.get_open_questions(payload)

    @mcp.tool(description="Redact a memory record and append an audit event.")
    def redact_memory(payload: dict[str, Any]) -> dict[str, Any]:
        return handlers.redact_memory(payload)

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
