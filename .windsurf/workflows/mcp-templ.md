---
description: Add MCP server to Claude Code or Windsurf
---

# MCP Server Template

## Config Locations

- **Claude Code:** `C:\Users\bolaf\.claude\settings.json`
- **Windsurf:** Project `.windsurf/mcp.json` or global settings

## Basic Template

```json
{
  "mcpServers": {
    "SERVER_NAME": {
      "command": "npx",
      "args": ["-y", "@org/package-name@latest"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

## Common Servers

### 21st.dev Magic (UI Components)
```json
"21st-dev-magic": {
  "command": "npx",
  "args": ["-y", "@21st-dev/magic@latest"],
  "env": { "TWENTY_FIRST_API_KEY": "xxx" }
}
```

### GitHub
```json
"github": {
  "command": "npx",
  "args": ["-y", "@anthropic-ai/mcp-server-github"],
  "env": { "GITHUB_TOKEN": "ghp_xxx" }
}
```

### Filesystem
```json
"filesystem": {
  "command": "npx",
  "args": ["-y", "@anthropic-ai/mcp-server-filesystem", "C:/Users/bolaf"]
}
```

### Brave Search
```json
"brave-search": {
  "command": "npx",
  "args": ["-y", "@anthropic-ai/mcp-server-brave-search"],
  "env": { "BRAVE_API_KEY": "xxx" }
}
```

### Postgres
```json
"postgres": {
  "command": "npx",
  "args": ["-y", "@anthropic-ai/mcp-server-postgres"],
  "env": { "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost:5432/db" }
}
```

### Slack
```json
"slack": {
  "command": "npx",
  "args": ["-y", "@anthropic-ai/mcp-server-slack"],
  "env": { "SLACK_BOT_TOKEN": "xoxb-xxx", "SLACK_TEAM_ID": "Txxx" }
}
```

### Memory
```json
"memory": {
  "command": "npx",
  "args": ["-y", "@anthropic-ai/mcp-server-memory"]
}
```

### Puppeteer
```json
"puppeteer": {
  "command": "npx",
  "args": ["-y", "@anthropic-ai/mcp-server-puppeteer"]
}
```

## Server Types

### NPX (Node packages)
```json
"command": "npx",
"args": ["-y", "@org/package"]
```

### Python
```json
"command": "python",
"args": ["-m", "package_name"]
```

### Node Script
```json
"command": "node",
"args": ["C:/path/to/server.js"]
```

### Docker
```json
"command": "docker",
"args": ["run", "-i", "--rm", "image-name"]
```

## CLI Commands (Claude Code)

```powershell
# Add server globally
claude mcp add SERVER_NAME --global

# List servers
claude mcp list

# Remove server
claude mcp remove SERVER_NAME --global
```
