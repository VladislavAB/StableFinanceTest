import hashlib
import hmac
import json
import os
from fastapi import HTTPException, Request
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


def verify_signature(request: Request, body: bytes) -> bool:
    signature = request.headers.get("X-Signature")
    if not signature:
        return False

    expected_signature = hmac.new(SECRET_KEY.encode('utf-8'), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


async def verify_request_signature(request: Request):
    body = await request.body()
    if not verify_signature(request, body):
        raise HTTPException(status_code=404, detail="Неправильная подпись")


def make_signature(payload: dict) -> str:
    body = json.dumps(payload, separators=(",", ":")).encode()
    return hmac.new(SECRET_KEY.encode(), body, hashlib.sha256).hexdigest()
