# Office MCP Server Configurations

Tested MCP server configurations for document processing, added to ~/.hermes/config.yaml:

```yaml
mcp_servers:
  # Word document processing (2031⭐)
  word:
    command: "npx"
    args: ["-y", "@gongrzhe/office-word-mcp-server"]
    timeout: 60
  
  # Excel processing (3909⭐)
  excel:
    command: "npx"
    args: ["-y", "@haris-musa/excel-mcp-server"]
    timeout: 60
  
  # PDF processing (764⭐)
  pdf:
    command: "npx"
    args: ["-y", "@sylphx-ai/pdf-reader-mcp"]
    timeout: 60
  
  # Document intelligence - supports 97+ formats (8462⭐)
  kreuzberg:
    command: "npx"
    args: ["-y", "@kreuzberg-dev/kreuzberg"]
    timeout: 120
  
  # File system access
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/admin"]
    timeout: 30
  
  # Time server (Python-based)
  time:
    command: "uvx"
    args: ["mcp-server-time"]
    timeout: 30
```

## Notes

- `kreuzberg` has the longest timeout (120s) because it supports 97+ document formats and may need to process large files
- `filesystem` is scoped to `/home/admin` for security
- `time` uses `uvx` (Python) instead of `npx` (Node.js)
- All servers auto-install on first use via `-y` flag (npx) or uvx behavior
- Tool names are prefixed: `mcp_word_*`, `mcp_excel_*`, `mcp_pdf_*`, `mcp_kreuzberg_*`, `mcp_filesystem_*`, `mcp_time_*`
