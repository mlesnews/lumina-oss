#!/usr/bin/env python3
"""Debug proxy to log Kilo Code requests to Ollama."""

import json
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

TARGET = "http://localhost:11434"


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()

    def do_POST(self):
        self.proxy_request()

    def do_HEAD(self):
        self.proxy_request()

    def proxy_request(self):
        # Log the request
        print(f"\n{'=' * 60}")
        print(f"[REQUEST] {self.command} {self.path}")
        print("[HEADERS]")
        for h, v in self.headers.items():
            print(f"  {h}: {v}")

        # Read body if present
        content_length = self.headers.get("Content-Length")
        body = None
        if content_length:
            body = self.rfile.read(int(content_length))
            try:
                body_json = json.loads(body)
                print("[BODY]")
                print(json.dumps(body_json, indent=2)[:1000])
            except:
                print(f"[BODY] (raw) {body[:500]}")

        # Forward to Ollama
        target_url = TARGET + self.path
        print(f"\n[FORWARDING TO] {target_url}")

        try:
            req = urllib.request.Request(
                target_url,
                data=body,
                headers={
                    k: v
                    for k, v in self.headers.items()
                    if k.lower() not in ["host", "content-length"]
                },
                method=self.command,
            )
            req.add_header("Content-Length", len(body) if body else 0)

            with urllib.request.urlopen(req, timeout=60) as response:
                response_body = response.read()
                print(f"\n[RESPONSE] {response.status}")
                print("[RESPONSE HEADERS]")
                for h, v in response.headers.items():
                    print(f"  {h}: {v}")
                print("[RESPONSE BODY] (first 500 chars)")
                print(response_body[:500].decode("utf-8", errors="replace"))

                self.send_response(response.status)
                for h, v in response.headers.items():
                    if h.lower() not in ["transfer-encoding", "content-length"]:
                        self.send_header(h, v)
                self.send_header("Content-Length", len(response_body))
                self.end_headers()
                self.wfile.write(response_body)
        except urllib.error.HTTPError as e:
            print(f"\n[ERROR] HTTP {e.code}: {e.reason}")
            self.send_error(e.code, e.reason)
        except Exception as e:
            print(f"\n[ERROR] {e}")
            self.send_error(500, str(e))


if __name__ == "__main__":
    port = 18080  # Different port to avoid conflict
    print(f"Starting debug proxy on port {port}")
    print(f"Forwarding to {TARGET}")
    print(f"\nSet Kilo Code ollamaBaseUrl to: http://localhost:{port}")
    print("Press Ctrl+C to stop\n")

    server = HTTPServer(("127.0.0.1", port), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
