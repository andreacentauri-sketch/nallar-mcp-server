# Architecture

```text
MCP client
   |
   | newline-delimited JSON-RPC 2.0 over stdio
   v
server.py
   |-- initialize / ping
   |-- tools/list + tools/call
   |-- resources/list + resources/read
   `-- prompts/list + prompts/get
           |
           v
      read-only adapters
       /           \
rolling evidence   package manifests
```

The MCP package is isolated from canonical NALLAR source.
