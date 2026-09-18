# MCP Compatibility Note

This package implements the MCP-facing local JSON-RPC stdio surface exercised by its tests: initialize, initialized notification, ping, tools, resources, and prompts.

It is self-contained rather than SDK-dependent. Evidence supports this documented local protocol surface; it does not claim exhaustive compatibility with every future MCP revision or third-party host.
