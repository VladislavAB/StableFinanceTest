import hashlib
import hmac
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
