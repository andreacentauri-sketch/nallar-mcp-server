#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, sys
from pathlib import Path
from typing import Any, Dict

SERVER_NAME = "nallar-portfolio-mcp"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2025-06-18"

def evidence_path() -> Path:
    raw = os.environ.get("NALLAR_MCP_EVIDENCE")
    if raw:
        return Path(raw).expanduser()
    return Path(__file__).resolve().parent / "data" / "NALLAR_COMPACT_EVIDENCE_V51R4D9F3E9L4CY1B8R9R1.json"

def portfolio_root() -> Path:
    raw = os.environ.get("NALLAR_MCP_PORTFOLIO_ROOT")
    return Path(raw).expanduser() if raw else Path.home() / "Downloads" / "NALLAR_AI_ENGINEERING_PORTFOLIO"

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def roadmap_summary() -> Dict[str, Any]:
    obj = read_json(evidence_path())
    suite = obj.get("roadmap_monitor", {}).get("portfolio_suite", {})
    return {
        "milestones_complete": suite.get("milestones_complete"),
        "milestones_total": suite.get("milestones_total"),
        "percent": suite.get("percent"),
        "offline_llm_app": suite.get("offline_llm_app"),
        "mcp_server": suite.get("mcp_server"),
        "rag_telemetry_evals": suite.get("rag_telemetry_evals"),
        "multi_agent_system": suite.get("multi_agent_system"),
        "voice_ai_study_coach": suite.get("voice_ai_study_coach"),
        "model_tuning": suite.get("model_tuning"),
        "integrated_flagship": suite.get("integrated_flagship"),
        "cv_linkedin_career_pack": suite.get("cv_linkedin_career_pack"),
    }

def package_manifest(package_name: str) -> Dict[str, Any]:
    root = portfolio_root().resolve()
    requested = (root / package_name).resolve()
    requested.relative_to(root)
    manifest = requested / "PACKAGE_MANIFEST.json"
    obj = read_json(manifest)
    return {
        "package_name": package_name,
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "file_count": obj.get("file_count"),
        "package_content_sha256": obj.get("package_content_sha256"),
    }

TOOLS = [
    {"name":"nallar.health","description":"Return server health/read-only status.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}},
    {"name":"nallar.roadmap","description":"Return current NALLAR portfolio roadmap summary.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}},
    {"name":"nallar.package_manifest","description":"Read package manifest metadata.","inputSchema":{"type":"object","properties":{"package_name":{"type":"string"}},"required":["package_name"],"additionalProperties":False}},
]
RESOURCES = [
    {"uri":"nallar://roadmap","name":"NALLAR Roadmap","mimeType":"application/json"},
    {"uri":"nallar://evidence","name":"NALLAR Evidence Metadata","mimeType":"application/json"},
]
PROMPTS = [{
    "name":"nallar_engineering_review",
    "description":"Evidence-bounded NALLAR engineering review.",
    "arguments":[{"name":"focus","description":"Optional review focus","required":False}],
}]

def tool_result(obj: Any, is_error: bool=False) -> Dict[str, Any]:
    return {"content":[{"type":"text","text":json.dumps(obj, sort_keys=True)}],"isError":is_error}

def handle(method: str, params: Dict[str, Any]) -> Any:
    if method == "initialize":
        return {
            "protocolVersion": params.get("protocolVersion") or PROTOCOL_VERSION,
            "capabilities":{"tools":{},"resources":{},"prompts":{}},
            "serverInfo":{"name":SERVER_NAME,"version":SERVER_VERSION},
        }
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools":TOOLS}
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            if name == "nallar.health":
                return tool_result({"status":"ok","server":SERVER_NAME,"version":SERVER_VERSION,"read_only":True})
            if name == "nallar.roadmap":
                return tool_result(roadmap_summary())
            if name == "nallar.package_manifest":
                pn = args.get("package_name")
                if not isinstance(pn, str) or not pn:
                    return tool_result({"error":"package_name is required"}, True)
                return tool_result(package_manifest(pn))
            return tool_result({"error":"unknown tool"}, True)
        except Exception as e:
            return tool_result({"error":type(e).__name__}, True)
    if method == "resources/list":
        return {"resources":RESOURCES}
    if method == "resources/read":
        uri = params.get("uri")
        if uri == "nallar://roadmap":
            obj = roadmap_summary()
        elif uri == "nallar://evidence":
            p = evidence_path()
            data = p.read_bytes()
            obj = {"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"plaintext_exposed":False}
        else:
            raise KeyError
        return {"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(obj, sort_keys=True)}]}
    if method == "prompts/list":
        return {"prompts":PROMPTS}
    if method == "prompts/get":
        if params.get("name") != "nallar_engineering_review":
            raise KeyError
        focus = ((params.get("arguments") or {}).get("focus") or "current portfolio evidence")
        return {
            "description":"Evidence-bounded NALLAR engineering review",
            "messages":[{"role":"user","content":{"type":"text","text":
                "Review " + str(focus) + ". Preserve ClaimStrength <= EvidenceStrength. "
                "Distinguish architecture, implementation, execution, verification, and production promotion."
            }}],
        }
    raise KeyError

def ok(req_id: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc":"2.0","id":req_id,"result":result}

def err(req_id: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc":"2.0","id":req_id,"error":{"code":code,"message":message}}

def process(msg: Dict[str, Any]) -> Dict[str, Any] | None:
    if msg.get("jsonrpc") != "2.0" or "method" not in msg:
        return err(msg.get("id"), -32600, "Invalid Request")
    if "params" in msg and not isinstance(msg["params"], dict):
        return err(msg.get("id"), -32602, "Invalid params")
    notification = "id" not in msg
    try:
        result = handle(msg["method"], msg.get("params") or {})
        return None if notification else ok(msg.get("id"), result)
    except KeyError:
        return None if notification else err(msg.get("id"), -32601, "Method not found")
    except Exception:
        return None if notification else err(msg.get("id"), -32603, "Internal error")

def main() -> int:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
            out = process(msg) if isinstance(msg, dict) else err(None, -32600, "Invalid Request")
        except json.JSONDecodeError:
            out = err(None, -32700, "Parse error")
        if out is not None:
            sys.stdout.write(json.dumps(out, separators=(",",":")) + "\n")
            sys.stdout.flush()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
