"""Tests for the secret scanner."""

import tempfile
from pathlib import Path

from lumina.safety.secret_scanner import SecretScanner


def test_detects_aws_key():
    scanner = SecretScanner()
    findings = scanner.scan("export AWS_KEY=AKIAIOSFODNN7EXAMPLE")
    assert len(findings) >= 1
    assert any(f["pattern_name"] == "aws_access_key" for f in findings)


def test_detects_openai_key():
    scanner = SecretScanner()
    findings = scanner.scan("OPENAI_KEY=sk-abc123def456ghi789jkl012mno345pqr678")
    assert any(f["pattern_name"] == "openai_key" for f in findings)


def test_detects_github_pat():
    scanner = SecretScanner()
    findings = scanner.scan("token: ghp_1234567890abcdefghijklmnopqrstuv")
    assert any(f["pattern_name"] == "github_pat" for f in findings)


def test_detects_private_key():
    scanner = SecretScanner()
    findings = scanner.scan("-----BEGIN RSA PRIVATE KEY-----\nblah\n-----END RSA PRIVATE KEY-----")
    assert any(f["pattern_name"] == "private_key" for f in findings)


def test_detects_jwt():
    scanner = SecretScanner()
    findings = scanner.scan("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0")
    assert any(f["pattern_name"] == "jwt_token" for f in findings)


def test_detects_huggingface_token():
    scanner = SecretScanner()
    findings = scanner.scan("HF_TOKEN=hf_abcdefghijklmnopqrstuvwxyz1234567890")
    assert any(f["pattern_name"] == "huggingface_token" for f in findings)


def test_no_false_positive_on_clean_text():
    scanner = SecretScanner()
    findings = scanner.scan("Hello world, this is clean text with no secrets.")
    assert len(findings) == 0


def test_has_secrets():
    scanner = SecretScanner()
    assert scanner.has_secrets("key: AKIAIOSFODNN7EXAMPLE") is True
    assert scanner.has_secrets("just a normal string") is False


def test_redaction():
    scanner = SecretScanner()
    findings = scanner.scan("AKIAIOSFODNN7EXAMPLE")
    assert findings[0]["match"].endswith("***")
    assert len(findings[0]["match"]) < 20  # Redacted, not full key


def test_scan_file():
    scanner = SecretScanner()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("api_key: sk-abc123def456ghi789jkl012\n")
        f.write("normal line\n")
        tmp_path = Path(f.name)

    try:
        findings = scanner.scan_file(tmp_path)
        assert len(findings) >= 1
        assert findings[0]["file"] == str(tmp_path)
    finally:
        tmp_path.unlink()


def test_extra_patterns():
    scanner = SecretScanner(extra_patterns=[
        ("custom_key", r"CUSTOM_[A-Z]{20}", "Custom API Key"),
    ])
    findings = scanner.scan("CUSTOM_ABCDEFGHIJKLMNOPQRST")
    assert any(f["pattern_name"] == "custom_key" for f in findings)
