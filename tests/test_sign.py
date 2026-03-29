import json
from unittest.mock import MagicMock
from app.sign import verify_signature, make_signature


def test_valid_signature():
    payload = {"amount": "100", "external_invoice_id": "abc"}
    body = json.dumps(payload, separators=(",", ":")).encode()
    signature = make_signature(payload)

    request = MagicMock()
    request.headers = {"X-Signature": signature}

    assert verify_signature(request, body) is True


def test_invalid_signature():
    payload = {"amount": "100", "external_invoice_id": "abc"}
    body = json.dumps(payload, separators=(",", ":")).encode()

    request = MagicMock()
    request.headers = {"X-Signature": "wrong signatuge"}

    assert verify_signature(request, body) is False
