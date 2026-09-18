# Demo

Start:
```bash
python server.py
```

Initialize:
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"demo","version":"1"}}}
```

Discover:
```json
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
```

Roadmap:
```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"nallar.roadmap","arguments":{}}}
```
