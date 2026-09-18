# MCP Server

> Recruiter-facing public presentation generated from the verified local NALLAR portfolio package.

## 30-second summary

This project is presented around four questions: **what was built, how it was tested, what was measured, and what is not being claimed**.

## Evidence model

- Runnable implementation or portfolio artifact.
- Executable tests and/or quantitative evaluation.
- Reproducible local commands.
- Explicit limitations.

## Proof points

- Read-only stdio / JSON-RPC MCP-facing server.
- Tools, resources, prompts, initialize/ping, and negative-path handling.
- **10/10 protocol/integration tests passed.**

## Recruiter demo

Run the server and show `initialize`, `tools/list`, then one negative-path request.

## Evidence boundary

Protocol tests prove the documented local server behavior; they do not prove exhaustive compatibility with every MCP host or production deployment.

---

## Reproduce locally

See the project files and original run notes below. Use the repository's own test/evaluation commands and inspect the generated evidence artifacts rather than relying on screenshots alone.


### Original run notes

# NALLAR MCP Server

Read-only MCP portfolio server for NALLAR engineering evidence.

## Run
```bash
cd ~/Downloads/NALLAR_AI_ENGINEERING_PORTFOLIO/02_MCP_SERVER
python server.py
```

Each stdio request/response is one JSON-RPC 2.0 object per line.

## Test
```bash
python -m unittest discover -s tests -v
```

Environment variables:
- `NALLAR_MCP_EVIDENCE`
- `NALLAR_MCP_PORTFOLIO_ROOT`

The server exposes tools, resources, and prompts while leaving canonical NALLAR source unchanged.


## Public claim boundary

This repository is published as an evidence-backed portfolio artifact. Test and evaluation results apply to the documented local/bundled scope. No production deployment, foundation-model training, or other unverified capability is implied.
