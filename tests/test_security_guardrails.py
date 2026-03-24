from types import SimpleNamespace

import pytest
from fastapi import FastAPI, Response
from starlette.requests import Request

from app.middleware.security import (
    BodySizeLimitMiddleware,
    RateLimitMiddleware,
    add_security_middleware,
)
from app.services.io_limits import SizeLimitExceeded, read_response_limited, read_upload_limited


def _request(method: str, path: str, headers: list[tuple[bytes, bytes]] | None = None) -> Request:
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": method,
        "path": path,
        "raw_path": path.encode(),
        "headers": headers or [],
        "query_string": b"",
        "scheme": "http",
        "client": ("127.0.0.1", 1234),
        "server": ("test", 80),
    }
    return Request(scope)


def test_add_security_middleware_registers_expected_stack():
    app = FastAPI()
    add_security_middleware(app)
    middleware_names = {entry.cls.__name__ for entry in app.user_middleware}

    assert "CORSMiddleware" in middleware_names
    assert "TrustedHostMiddleware" in middleware_names
    assert "SecurityHeadersMiddleware" in middleware_names
    assert "BodySizeLimitMiddleware" in middleware_names
    assert "RateLimitMiddleware" in middleware_names


@pytest.mark.asyncio
async def test_body_size_limit_rejects_invalid_content_length():
    middleware = BodySizeLimitMiddleware(FastAPI())
    request = _request("POST", "/api/share", headers=[(b"content-length", b"nope")])
    async def call_next(_request):
        return Response("ok")

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 400


def test_rate_limit_resolve_key_prefers_session_cookie():
    middleware = RateLimitMiddleware(FastAPI())
    request = SimpleNamespace(cookies={"session": "session-token"}, client=SimpleNamespace(host="1.2.3.4"))

    assert middleware._resolve_key(request, "cookie") == "session-token"
    assert middleware._resolve_key(request, "ip") == "1.2.3.4"
    assert middleware._get_limit("/api/admin/backup") == (2, 3600, "ip")


@pytest.mark.asyncio
async def test_read_upload_limited_raises_for_oversized_payload():
    class Upload:
        def __init__(self):
            self._chunks = [b"abc", b"def"]

        async def read(self, _size):
            return self._chunks.pop(0) if self._chunks else b""

    with pytest.raises(SizeLimitExceeded):
        await read_upload_limited(Upload(), 5)


@pytest.mark.asyncio
async def test_read_response_limited_raises_for_oversized_payload():
    class FakeResponse:
        async def aiter_bytes(self, _chunk_size):
            yield b"abc"
            yield b"def"

    with pytest.raises(SizeLimitExceeded):
        await read_response_limited(FakeResponse(), 5)
