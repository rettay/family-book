import os
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, Response
from starlette.requests import Request

import app.middleware.security as security_middleware
import app.services.io_limits as io_limits
from app.middleware.security import (
    BodySizeLimitMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    add_security_middleware,
)
from app.services.io_limits import (
    SizeLimitExceeded,
    read_response_limited,
    read_upload_limited,
    stream_upload_to_temp,
)


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
    assert security_middleware.MB == 1024 * 1024

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


@pytest.mark.asyncio
async def test_body_size_limit_allows_in_range_request():
    middleware = BodySizeLimitMiddleware(FastAPI())
    request = _request("POST", "/api/share", headers=[(b"content-length", b"64")])

    async def call_next(_request):
        return Response("ok", status_code=202)

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 202


@pytest.mark.asyncio
async def test_body_size_limit_rejects_oversized_request():
    middleware = BodySizeLimitMiddleware(FastAPI())
    request = _request("POST", "/api/share", headers=[(b"content-length", str(12 * 1024 * 1024).encode())])

    async def call_next(_request):
        return Response("ok")

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 413


@pytest.mark.asyncio
async def test_security_headers_add_hsts_and_no_store(monkeypatch):
    middleware = SecurityHeadersMiddleware(FastAPI())
    request = _request("GET", "/api/people")
    request._cookies = {"session": "abc"}  # type: ignore[attr-defined]

    monkeypatch.setattr(
        "app.middleware.security.get_settings",
        lambda: SimpleNamespace(BASE_URL="https://family.example.com"),
    )

    async def call_next(_request):
        return Response("ok")

    response = await middleware.dispatch(request, call_next)

    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Pragma"] == "no-cache"
    assert "Content-Security-Policy" in response.headers
    csp = response.headers["Content-Security-Policy"]
    assert "https://maps.googleapis.com" in csp
    assert "https://maps.gstatic.com" in csp


def test_rate_limit_resolve_key_prefers_session_cookie():
    middleware = RateLimitMiddleware(FastAPI())
    request = SimpleNamespace(cookies={"session": "session-token"}, client=SimpleNamespace(host="1.2.3.4"))

    assert middleware._resolve_key(request, "cookie") == "session-token"
    assert middleware._resolve_key(request, "ip") == "1.2.3.4"
    assert middleware._get_limit("/api/admin/backup") == (2, 3600, "ip")


@pytest.mark.asyncio
async def test_rate_limit_dispatch_blocks_after_threshold():
    middleware = RateLimitMiddleware(FastAPI())
    request = _request("GET", "/api/people")
    request._cookies = {"session": "session-token"}  # type: ignore[attr-defined]

    async def call_next(_request):
        return Response("ok")

    responses = []
    for _ in range(121):
        responses.append(await middleware.dispatch(request, call_next))

    assert responses[-1].status_code == 429
    assert responses[-1].headers["Retry-After"] == "60"


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
async def test_read_upload_limited_returns_payload():
    class Upload:
        def __init__(self):
            self._chunks = [b"abc", b"def"]

        async def read(self, _size):
            return self._chunks.pop(0) if self._chunks else b""

    assert await read_upload_limited(Upload(), 6) == b"abcdef"
    assert io_limits.READ_CHUNK_SIZE == 1024 * 1024


@pytest.mark.asyncio
async def test_read_response_limited_raises_for_oversized_payload():
    class FakeResponse:
        async def aiter_bytes(self, _chunk_size):
            yield b"abc"
            yield b"def"

    with pytest.raises(SizeLimitExceeded):
        await read_response_limited(FakeResponse(), 5)


@pytest.mark.asyncio
async def test_read_response_limited_returns_payload():
    class FakeResponse:
        async def aiter_bytes(self, _chunk_size):
            yield b"abc"
            yield b"def"

    assert await read_response_limited(FakeResponse(), 6) == b"abcdef"


@pytest.mark.asyncio
async def test_stream_upload_to_temp_persists_file(tmp_path, monkeypatch):
    class Upload:
        def __init__(self):
            self._chunks = [b"abc", b"def"]

        async def read(self, _size):
            return self._chunks.pop(0) if self._chunks else b""

    temp_path = tmp_path / "upload.tmp"

    def fake_mkstemp(prefix):
        fd = os.open(temp_path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o600)
        return fd, str(temp_path)

    monkeypatch.setattr("tempfile.mkstemp", fake_mkstemp)

    streamed = await stream_upload_to_temp(Upload(), 6)

    assert streamed.size == 6
    assert len(streamed.sha256) == 64
    with open(streamed.path, "rb") as handle:
        assert handle.read() == b"abcdef"


@pytest.mark.asyncio
async def test_stream_upload_to_temp_cleans_up_on_overflow(tmp_path, monkeypatch):
    temp_path = tmp_path / "overflow.tmp"

    class Upload:
        def __init__(self):
            self._chunks = [b"abc", b"def"]

        async def read(self, _size):
            return self._chunks.pop(0) if self._chunks else b""

    def fake_mkstemp(prefix):
        fd = os.open(temp_path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o600)
        return fd, str(temp_path)

    monkeypatch.setattr("tempfile.mkstemp", fake_mkstemp)

    with pytest.raises(SizeLimitExceeded):
        await stream_upload_to_temp(Upload(), 5)

    assert not temp_path.exists()
