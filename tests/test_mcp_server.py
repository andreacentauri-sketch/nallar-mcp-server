from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server.py"


class MCPProc:
    def __init__(self, extra_env=None):
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)

        self.p = subprocess.Popen(
            [sys.executable, str(SERVER)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        self.n = 0

    def request(self, method, params=None):
        self.n += 1
        msg = {"jsonrpc": "2.0", "id": self.n, "method": method}
        if params is not None:
            msg["params"] = params

        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()

        line = self.p.stdout.readline()
        if not line:
            raise AssertionError("no response: " + self.p.stderr.read())

        return json.loads(line)

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params

        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()

    def close(self):
        try:
            if self.p.stdin:
                self.p.stdin.close()
        except Exception:
            pass

        if self.p.poll() is None:
            self.p.terminate()

        try:
            self.p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.p.kill()
            self.p.wait(timeout=3)

        for stream in (self.p.stdout, self.p.stderr):
            try:
                if stream:
                    stream.close()
            except Exception:
                pass


class T(unittest.TestCase):
    def setUp(self):
        # Hermetic test fixture: do not depend on a developer's ~/Downloads tree.
        self.tmp = tempfile.TemporaryDirectory()
        portfolio_root = Path(self.tmp.name)

        package_dir = portfolio_root / "01_OFFLINE_LLM_APP"
        package_dir.mkdir(parents=True)

        manifest = {
            "file_count": 1,
            "package_content_sha256": "test-fixture",
        }

        (package_dir / "PACKAGE_MANIFEST.json").write_text(
            json.dumps(manifest, sort_keys=True),
            encoding="utf-8",
        )

        self.s = MCPProc(
            {"NALLAR_MCP_PORTFOLIO_ROOT": str(portfolio_root)}
        )

    def tearDown(self):
        self.s.close()
        self.tmp.cleanup()

    def init(self):
        r = self.s.request(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"},
            },
        )
        self.assertEqual(
            r["result"]["serverInfo"]["name"],
            "nallar-portfolio-mcp",
        )
        self.s.notify("notifications/initialized")
        return r

    def test_01_initialize(self):
        r = self.init()
        self.assertEqual(
            r["result"]["protocolVersion"],
            "2025-06-18",
        )

    def test_02_ping(self):
        self.init()
        self.assertEqual(
            self.s.request("ping")["result"],
            {},
        )

    def test_03_tools_list(self):
        self.init()
        names = {
            x["name"]
            for x in self.s.request("tools/list")["result"]["tools"]
        }
        self.assertEqual(
            names,
            {
                "nallar.health",
                "nallar.roadmap",
                "nallar.package_manifest",
            },
        )

    def test_04_health(self):
        self.init()
        r = self.s.request(
            "tools/call",
            {
                "name": "nallar.health",
                "arguments": {},
            },
        )
        self.assertFalse(r["result"]["isError"])
        self.assertTrue(
            json.loads(
                r["result"]["content"][0]["text"]
            )["read_only"]
        )

    def test_05_roadmap(self):
        self.init()
        r = self.s.request(
            "tools/call",
            {
                "name": "nallar.roadmap",
                "arguments": {},
            },
        )
        p = json.loads(
            r["result"]["content"][0]["text"]
        )
        self.assertEqual(p["milestones_complete"], 32)
        self.assertEqual(p["offline_llm_app"], "4/4")

    def test_06_manifest(self):
        self.init()
        r = self.s.request(
            "tools/call",
            {
                "name": "nallar.package_manifest",
                "arguments": {
                    "package_name": "01_OFFLINE_LLM_APP"
                },
            },
        )

        self.assertFalse(r["result"]["isError"])

        payload = json.loads(
            r["result"]["content"][0]["text"]
        )

        self.assertGreater(payload["file_count"], 0)

    def test_07_resources(self):
        self.init()

        r = self.s.request("resources/list")
        self.assertIn(
            "nallar://roadmap",
            {x["uri"] for x in r["result"]["resources"]},
        )

        rr = self.s.request(
            "resources/read",
            {"uri": "nallar://roadmap"},
        )

        self.assertEqual(
            json.loads(
                rr["result"]["contents"][0]["text"]
            )["milestones_complete"],
            32,
        )

    def test_08_prompts(self):
        self.init()

        self.assertIn(
            "nallar_engineering_review",
            {
                x["name"]
                for x in self.s.request(
                    "prompts/list"
                )["result"]["prompts"]
            },
        )

        rr = self.s.request(
            "prompts/get",
            {
                "name": "nallar_engineering_review",
                "arguments": {"focus": "MCP"},
            },
        )

        self.assertIn(
            "ClaimStrength <= EvidenceStrength",
            rr["result"]["messages"][0]["content"]["text"],
        )

    def test_09_unknown_method(self):
        self.init()
        self.assertEqual(
            self.s.request("bad/method")["error"]["code"],
            -32601,
        )

    def test_10_invalid_params(self):
        self.s.n += 1

        self.s.p.stdin.write(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": self.s.n,
                    "method": "ping",
                    "params": [],
                }
            )
            + "\n"
        )
        self.s.p.stdin.flush()

        self.assertEqual(
            json.loads(
                self.s.p.stdout.readline()
            )["error"]["code"],
            -32602,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
