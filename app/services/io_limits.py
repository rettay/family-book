from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass

from httpx import Response


READ_CHUNK_SIZE = 1024 * 1024


class SizeLimitExceeded(ValueError):
    pass


@dataclass(frozen=True)
class StreamedTempFile:
    path: str
    size: int
    sha256: str


async def read_upload_limited(upload, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0

    while True:
        chunk = await upload.read(READ_CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise SizeLimitExceeded(f"Payload exceeds {max_bytes} bytes")
        chunks.append(chunk)

    return b"".join(chunks)


async def stream_upload_to_temp(upload, max_bytes: int) -> StreamedTempFile:
    total = 0
    digest = hashlib.sha256()
    fd, temp_path = tempfile.mkstemp(prefix="family-book-upload-")
    os.close(fd)

    try:
        with open(temp_path, "wb") as temp_file:
            while True:
                chunk = await upload.read(READ_CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise SizeLimitExceeded(f"Payload exceeds {max_bytes} bytes")
                digest.update(chunk)
                temp_file.write(chunk)
    except Exception:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise

    return StreamedTempFile(
        path=temp_path,
        size=total,
        sha256=digest.hexdigest(),
    )


async def read_response_limited(response: Response, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0

    async for chunk in response.aiter_bytes(READ_CHUNK_SIZE):
        total += len(chunk)
        if total > max_bytes:
            raise SizeLimitExceeded(f"Payload exceeds {max_bytes} bytes")
        chunks.append(chunk)

    return b"".join(chunks)
