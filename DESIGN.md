# MCP Server Design

## Goal
Expose selected NALLAR engineering evidence through a small read-only MCP server for portfolio demonstration and later agent integration.

## Contracts
Tools: `nallar.health`, `nallar.roadmap`, `nallar.package_manifest`.
Resources: `nallar://roadmap`, `nallar://evidence`.
Prompt: `nallar_engineering_review`.

## Constraints
No canonical source mutation, no production promotion, no HOLDOUT80/Q1 private reads, read-only tool behavior, explicit JSON-RPC errors.

## Gate
DESIGN passes only when tool/resource/prompt contracts and security boundaries are documented and match the generated implementation.
