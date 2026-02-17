#!/usr/bin/env python3
import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:11437"


def post(path, payload):
    url = BASE + path
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return (
            f"HTTPError: {e.code} {e.reason} {e.read().decode('utf-8') if e.fp else ''}"
        )
    except Exception as e:
        return f"Error: {e}"


def get(path):
    url = BASE + path
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    print("POST /triage ->")
    print(
        post(
            "/triage",
            {"text": "Service failure observed: disk full", "severity": "urgent"},
        )
    )
    print("\nPOST /aiq ->")
    print(
        post(
            "/aiq",
            {
                "candidates": [
                    {"id": "a", "content": "short"},
                    {"id": "b", "content": "a much longer content sample text"},
                ],
                "quorum": 1,
            },
        )
    )
    print("\nPOST /r5 ->")
    print(post("/r5", {"decision": "scale_up", "reason": "high_load"}))
    print("\nGET /telemetry/traces ->")
    print(get("/telemetry/traces"))
    print("\nGET /telemetry/evaluations ->")
    print(get("/telemetry/evaluations"))
    print("\nGET /telemetry/ssot ->")
    print(get("/telemetry/ssot"))
