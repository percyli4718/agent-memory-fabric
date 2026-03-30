# MCP Client Integration Guide

Configure Agent Memory Fabric in your preferred agent platform.

---

## Quick Start

```bash
# Install
pip install -e ".[dev]" asyncpg

# Run MCP server
amf-mcp-server --db-path ~/.amf/memory.db
```

---

## Claude Code Integration

### Option 1: MCP Settings (Recommended)

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "agent-memory-fabric": {
      "command": "python",
      "args": [
        "-m",
        "agent_memory_fabric.mcp_server",
        "--db-path",
        "/Users/you/.amf/memory.db"
      ],
      "env": {}
    }
  }
}
```

### Option 2: Project-Level Configuration

Add to your project's `.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "agent-memory-fabric": {
      "command": "amf-mcp-server",
      "args": ["--db-path", "./.amf/memory.db"]
    }
  }
}
```

### Option 3: Claude Desktop App

Add to Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "agent-memory-fabric": {
      "command": "python3",
      "args": ["-c", "from agent_memory_fabric.mcp_server import main; main()"],
      "cwd": "/path/to/agent-memory-fabric"
    }
  }
}
```

### Usage Example

Once configured, Claude will have access to these tools:

```
/search_memory - Search memory records
/write_memory - Write structured memory
/get_recent_project_context - Get recent context
/get_decisions - Get decisions
/get_open_questions - Get open questions
/upsert_fact - Create/update facts
/list_memories_by_repo - List repository memories
/redact_memory - Redact sensitive content
```

**Example conversation:**
```
User: Write a memory about our API design decision

Claude: I'll record that decision for you.
*uses write_memory tool*

User: What decisions did we make about authentication?

Claude: Let me search our memory...
*uses search_memory tool*
```

---

## Codex Integration (VS Code)

### Step 1: Install MCP Extension

1. Open VS Code
2. Go to Extensions
3. Search for "MCP" or "Model Context Protocol"
4. Install the MCP extension

### Step 2: Configure MCP

Create or edit `.vscode/mcp.json`:

```json
{
  "servers": {
    "agent-memory-fabric": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m",
        "agent_memory_fabric.mcp_server",
        "--db-path",
        "${workspaceFolder}/.amf/memory.db"
      ]
    }
  }
}
```

### Step 3: Enable Codex Integration

In VS Code Settings (`settings.json`):

```json
{
  "github.copilot.chat.mcp.enabled": true,
  "copilot.mcp.servers": ["agent-memory-fabric"]
}
```

### Usage in Copilot Chat

In Copilot Chat panel:
```
@workspace Search memory for our deployment decisions
```

---

## Gemini CLI Integration

### Step 1: Create MCP Config

Create `~/.gemini/mcp_config.json`:

```json
{
  "mcp": {
    "servers": {
      "agent-memory-fabric": {
        "command": "python3",
        "args": [
          "-m",
          "agent_memory_fabric.mcp_server",
          "--db-path",
          "/Users/you/.amf/memory.db"
        ],
        "env": {}
      }
    }
  }
}
```

### Step 2: Enable MCP in Gemini

Add to `~/.gemini/settings.json`:

```json
{
  "mcp": {
    "enabled": true,
    "servers": ["agent-memory-fabric"]
  }
}
```

### Usage Example

```
Gemini, search memory for our API decisions
Gemini, write a memory about the authentication flow we designed
```

---

## Cursor Integration

### Step 1: Configure MCP

Open Cursor Settings → Features → MCP

Add server configuration:

```json
{
  "mcpServers": {
    "agent-memory-fabric": {
      "command": "python",
      "args": ["-m", "agent_memory_fabric.mcp_server"],
      "env": {
        "AMF_DB_PATH": "~/.amf/memory.db"
      }
    }
  }
}
```

### Step 2: Restart Cursor

Restart Cursor to load the MCP server.

### Usage

In Cursor chat:
```
@memory What did we decide about the database schema?
```

---

## Shared AGENTS.md Pattern

Add to your repository's `AGENTS.md`:

```markdown
# Project Memory

This project uses Agent Memory Fabric for cross-session memory.

## Memory Scope

- `tenant`: default
- `project`: <your-project-name>
- `repository`: <repo-name>

## Available Tools

- `search_memory` - Search by query
- `write_memory` - Write structured records
- `get_decisions` - Get architecture decisions
- `get_open_questions` - Get unresolved questions
- `upsert_fact` - Update durable facts

## Example

```json
{
  "tenant": "default",
  "project": "my-project",
  "repository": "my-repo",
  "scope": "repo",
  "visibility": "team",
  "type": "decision",
  "summary": "Use PostgreSQL for production",
  "details": "SQLite for dev, PostgreSQL for prod",
  "tags": ["database", "architecture"]
}
```
```

---

## Verification

Test your configuration:

```bash
# Run verification script
python examples/v0.1-verification.py

# Or test manually with pytest
pytest tests/ -v
```

---

## Troubleshooting

### MCP Server Not Starting

```bash
# Test manually
amf-mcp-server --db-path ./test.db

# Check Python path
which python
which amf-mcp-server
```

### Permission Errors

```bash
# Ensure database directory exists
mkdir -p ~/.amf
chmod 755 ~/.amf
```

### Module Not Found

```bash
# Reinstall in editable mode
pip install -e ".[dev]"
```

### Connection Timeout

Increase timeout in your MCP client config:
```json
{
  "timeout": 30000
}
```

---

## Database Location Best Practices

| Environment | Path |
|-------------|------|
| Local dev | `~/.amf/memory.db` |
| Project-level | `./.amf/memory.db` |
| Team/shared | PostgreSQL connection string |

---

## PostgreSQL Configuration

For team deployments:

```json
{
  "mcpServers": {
    "agent-memory-fabric": {
      "command": "python",
      "args": [
        "-c",
        "from agent_memory_fabric.mcp_server import main; import os; os.environ['DATABASE_URL']='postgresql://user:pass@host:5432/amf'; main()"
      ]
    }
  }
}
```

Or set environment variable:
```bash
export AMF_DATABASE_URL="postgresql://user:pass@host:5432/amf"
```

---

## Next Steps

1. Configure MCP in your preferred client
2. Test with `amf-mcp-server --help`
3. Write your first memory record
4. Share `AGENTS.md` with your team
