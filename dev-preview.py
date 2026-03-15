#!/usr/bin/env python3
"""
EphItUpStudio local frontend preview server.

Assembles the dashboard HTML from static files exactly like webchat.rs does,
serves it on localhost:3333, and auto-reloads when you edit any file.

Usage:
    python3 dev-preview.py

Then open http://localhost:3333 in your browser.
Edit any file in crates/openfang-api/static/ and refresh to see changes instantly.
No Rust rebuild needed.
"""

import http.server
import os
import sys

PORT = 3333
STATIC = os.path.join(os.path.dirname(__file__), "crates", "openfang-api", "static")

def read(path):
    with open(os.path.join(STATIC, path), "r") as f:
        return f.read()

def read_bytes(path):
    with open(os.path.join(STATIC, path), "rb") as f:
        return f.read()

def build_html():
    css_files = ["css/theme.css", "css/layout.css", "css/components.css", "vendor/github-dark.min.css"]
    js_vendor = ["vendor/marked.min.js", "vendor/highlight.min.js", "vendor/chart.umd.min.js"]
    js_app = [
        "js/api.js", "js/app.js",
        "js/pages/overview.js", "js/pages/chat.js", "js/pages/agents.js",
        "js/pages/workflows.js", "js/pages/workflow-builder.js",
        "js/pages/channels.js", "js/pages/skills.js", "js/pages/hands.js",
        "js/pages/scheduler.js", "js/pages/settings.js", "js/pages/usage.js",
        "js/pages/sessions.js", "js/pages/logs.js", "js/pages/wizard.js",
        "js/pages/approvals.js", "js/pages/comms.js", "js/pages/runtime.js",
    ]

    html = read("index_head.html")
    html += "<style>\n"
    for f in css_files:
        html += read(f) + "\n"
    html += "</style>\n"
    html += read("index_body.html")
    html += "<style>.auth-overlay { display: none !important; }</style>\n"
    for f in js_vendor:
        html += f"<script>\n{read(f)}\n</script>\n"
    html += "<script>\n"
    for f in js_app:
        html += read(f) + "\n"
    html += "</script>\n"
    html += f"<script>\n{read('vendor/alpine.min.js')}\n</script>\n"

    html += "</body></html>"
    return html

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/logo.png":
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            self.wfile.write(read_bytes("logo.png"))
        elif self.path == "/favicon.ico":
            self.send_response(200)
            self.send_header("Content-Type", "image/x-icon")
            self.end_headers()
            self.wfile.write(read_bytes("favicon.ico"))
        elif self.path == "/" or self.path.startswith("/#") or self.path.startswith("/?"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(build_html().encode())
        elif self.path.startswith("/api/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            import json
            mock = {
                "/api/tools": {"tools": []},
                "/api/agents": {"agents": []},
                "/api/status": {"agent_count": 2, "uptime_seconds": 86400, "version": "dev-preview", "model": "preview/mock", "ws_connected": False, "total_tokens": 142000, "total_cost": 3.42, "memory_mb": 128, "cpu_percent": 4.2},
                "/api/sessions": {"sessions": []},
                "/api/skills": {"skills": []},
                "/api/hands": {"hands": []},
                "/api/workflows": {"workflows": []},
                "/api/scheduler/jobs": {"jobs": []},
                "/api/channels": {"channels": []},
                "/api/logs": [],
                "/api/auth/check": {"mode": "none", "authenticated": True},
                "/api/usage/summary": {"total_tokens": 142000, "total_cost": 3.42, "providers": {}},
            }
            path = self.path.split("?")[0]
            self.wfile.write(json.dumps(mock.get(path, {})).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        if args and "favicon" not in str(args[0]):
            print(f"  {args[0]}")

if __name__ == "__main__":
    print(f"\n  EphItUpStudio Dev Preview")
    print(f"  http://localhost:{PORT}")
    print(f"  Edit files in crates/openfang-api/static/ and refresh browser.\n")
    server = http.server.HTTPServer(("", PORT), Handler)
    server.socket.setsockopt(__import__('socket').SOL_SOCKET, __import__('socket').SO_REUSEADDR, 1)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
