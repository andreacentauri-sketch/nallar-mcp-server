# Evaluation

The same giantstep executes ten tests: initialize, ping, tools discovery, health, roadmap, package manifest, resources, prompts, unknown-method failure, and invalid-params failure.

A gate is awarded only if the generated suite exits successfully.

Passing establishes the documented local stdio JSON-RPC/MCP-facing surface. It does not establish production deployment, exhaustive external-host interoperability, O6 correctness closure, or production promotion.
