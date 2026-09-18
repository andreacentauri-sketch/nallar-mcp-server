# Security Boundary

- Tools are read-only.
- Package lookup is confined below `NALLAR_MCP_PORTFOLIO_ROOT`.
- No shell execution by the server.
- No model download, training, fine-tuning, or production promotion.
- No raw private evaluation payload exposure.
- `nallar://evidence` exposes metadata rather than the entire evidence document.
