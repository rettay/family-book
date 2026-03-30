import hashlib
import json
import logging
import os
import shutil
import subprocess
import uuid
from io import BytesIO

from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.media import Media, MediaSource, MediaType

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "video/mp4", "video/quicktime", "video/webm",
    "audio/opus", "audio/mp3", "audio/m4a", "audio/ogg",
    "audio/mpeg",
    "application/pdf",
}

IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
VIDEO_MIME_TYPES = {"video/mp4", "video/quicktime", "video/webm"}
AUDIO_MIME_TYPES = {"audio/opus", "audio/mp3", "audio/m4a", "audio/ogg", "audio/mpeg"}

MAX_SIZE_BY_CATEGORY = {
    "image": 10 * 1024 * 1024,      # 10 MB
    "video": 250 * 1024 * 1024,     # 250 MB
    "audio": 25 * 1024 * 1024,      # 25 MB
    "document": 50 * 1024 * 1024,   # 50 MB
}

THUMBNAIL_SIZE = (400, 400)
THUMB_SIZE = (200, 200)
MEDIUM_MAX = 800


def _category_for_mime(mime_type: str) -> str:
    if mime_type == "application/pdf":
        return "document"
    if mime_type.startswith("image/"):
        return "image"
    if mime_type.startswith("video/"):
        return "video"
    if mime_type.startswith("audio/"):
        return "audio"
    return "image"


def _media_type_for_mime(mime_type: str) -> str:
    if mime_type == "application/pdf":
        return MediaType.document.value
    if mime_type == "image/gif":
        return MediaType.gif.value
    if mime_type.startswith("image/"):
        return MediaType.image.value
    if mime_type.startswith("video/"):
        return MediaType.video.value
    if mime_type.startswith("audio/"):
        return MediaType.audio.value
    return MediaType.image.value


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_exif(data: bytes, mime_type: str) -> bytes:
    """Strip EXIF data from images for privacy."""
    if mime_type not in IMAGE_MIME_TYPES or mime_type == "image/gif":
        return data
    try:
        img = Image.open(BytesIO(data))
        clean = Image.new(img.mode, img.size)
        clean.paste(img)
        buf = BytesIO()
        fmt = "JPEG" if mime_type == "image/jpeg" else ("PNG" if mime_type == "image/png" else "WEBP")
        clean.save(buf, format=fmt, quality=90)
        return buf.getvalue()
    except Exception:
        return data


def generate_thumbnail(data: bytes, mime_type: str) -> bytes | None:
    """Generate a thumbnail for image files."""
    if mime_type not in IMAGE_MIME_TYPES:
        return None
    try:
        img = Image.open(BytesIO(data))
        img.thumbnail(THUMBNAIL_SIZE)
        # Strip EXIF from thumbnail too
        clean = Image.new(img.mode, img.size)
        clean.paste(img)
        buf = BytesIO()
        clean.save(buf, format="JPEG", quality=80)
        return buf.getvalue()
    except Exception:
        return None


def get_image_dimensions(data: bytes, mime_type: str) -> tuple[int | None, int | None]:
    if mime_type not in IMAGE_MIME_TYPES:
        return None, None
    try:
        img = Image.open(BytesIO(data))
        return img.width, img.height
    except Exception:
        return None, None


def generate_thumb_variant(data: bytes, mime_type: str) -> bytes | None:
    """Generate a 200x200 square center-crop thumbnail."""
    if mime_type not in IMAGE_MIME_TYPES:
        return None
    try:
        img = Image.open(BytesIO(data))
        # Center crop to square
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize(THUMB_SIZE, Image.LANCZOS)
        clean = Image.new(img.mode, img.size)
        clean.paste(img)
        buf = BytesIO()
        clean.save(buf, format="JPEG", quality=80)
        return buf.getvalue()
    except Exception:
        return None


def generate_medium_variant(data: bytes, mime_type: str) -> bytes | None:
    """Generate a medium variant (max 800px on longest side)."""
    if mime_type not in IMAGE_MIME_TYPES:
        return None
    try:
        img = Image.open(BytesIO(data))
        if max(img.size) <= MEDIUM_MAX:
            return None  # already small enough, no variant needed
        img.thumbnail((MEDIUM_MAX, MEDIUM_MAX), Image.LANCZOS)
        clean = Image.new(img.mode, img.size)
        clean.paste(img)
        buf = BytesIO()
        clean.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    except Exception:
        return None


def _save_variant(media_dir: str, media_id: str, variant_name: str, data: bytes) -> None:
    """Save a variant file to media/variants/{media_id}/{variant_name}.jpg."""
    variant_dir = os.path.join(media_dir, "variants", media_id)
    os.makedirs(variant_dir, exist_ok=True)
    path = os.path.join(variant_dir, f"{variant_name}.jpg")
    with open(path, "wb") as f:
        f.write(data)


def generate_image_variants(data: bytes, mime_type: str, media_dir: str, media_id: str) -> None:
    """Generate thumb and medium variants for an image."""
    thumb = generate_thumb_variant(data, mime_type)
    if thumb:
        _save_variant(media_dir, media_id, "thumb", thumb)
    medium = generate_medium_variant(data, mime_type)
    if medium:
        _save_variant(media_dir, media_id, "medium", medium)


def extract_audio_duration(file_path: str) -> float | None:
    """Extract audio duration in seconds using mutagen."""
    try:
        import mutagen
        audio = mutagen.File(file_path)
        if audio and audio.info and hasattr(audio.info, "length"):
            return round(audio.info.length, 2)
    except Exception:
        logger.debug("Could not extract audio duration from %s", file_path, exc_info=True)
    return None


def extract_video_metadata(file_path: str) -> tuple[float | None, int | None, int | None]:
    """Extract video duration, width, height using ffprobe. Returns (duration, width, height)."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", file_path,
            ],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None, None, None
        info = json.loads(result.stdout)
        duration = None
        width = None
        height = None
        if "format" in info and "duration" in info["format"]:
            duration = round(float(info["format"]["duration"]), 2)
        for stream in info.get("streams", []):
            if stream.get("codec_type") == "video":
                width = stream.get("width")
                height = stream.get("height")
                if not duration and "duration" in stream:
                    duration = round(float(stream["duration"]), 2)
                break
        return duration, width, height
    except Exception:
        logger.debug("Could not extract video metadata from %s", file_path, exc_info=True)
    return None, None, None


def generate_video_poster(file_path: str, media_dir: str, media_id: str) -> bool:
    """Extract first frame of video as poster image using ffmpeg. Returns True on success."""
    try:
        poster_path = os.path.join(media_dir, "variants", media_id, "poster.jpg")
        os.makedirs(os.path.dirname(poster_path), exist_ok=True)
        result = subprocess.run(
            [
                "ffmpeg", "-i", file_path, "-vframes", "1",
                "-vf", "scale='min(800,iw)':-2",
                "-q:v", "3", "-y", poster_path,
            ],
            capture_output=True, timeout=30,
        )
        return result.returncode == 0 and os.path.isfile(poster_path)
    except Exception:
        logger.debug("Could not generate video poster for %s", file_path, exc_info=True)
    return False


def get_variant_path(media_id: str, variant: str, data_dir: str | None = None) -> str | None:
    """Return the filesystem path for a variant, or None if it doesn't exist."""
    if data_dir is None:
        data_dir = get_settings().resolved_data_dir
    # Check new variants directory first
    path = os.path.join(data_dir, "media", "variants", media_id, f"{variant}.jpg")
    if os.path.isfile(path):
        return path
    # Backward compat: old thumbnails directory for "thumb" variant
    if variant == "thumb":
        legacy = os.path.join(data_dir, "media", "thumbnails", f"{media_id}.jpg")
        if os.path.isfile(legacy):
            return legacy
    return None


async def check_duplicate(db: AsyncSession, file_hash: str) -> Media | None:
    result = await db.execute(select(Media).where(Media.file_hash == file_hash))
    return result.scalar_one_or_none()


async def save_media_file(
    db: AsyncSession,
    file_data: bytes,
    filename: str,
    mime_type: str,
    person_id: str,
    uploaded_by: str,
    caption: str | None = None,
    title: str | None = None,
    description: str | None = None,
    taken_date: str | None = None,
    tagged_person_ids: list[str] | None = None,
    data_dir: str | None = None,
) -> tuple[Media, bool]:
    """
    Save a media file. Returns (media, is_duplicate).
    If duplicate, returns the existing media record.
    """
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Unsupported MIME type: {mime_type}")

    category = _category_for_mime(mime_type)
    max_size = MAX_SIZE_BY_CATEGORY[category]
    if len(file_data) > max_size:
        raise ValueError(f"File too large: {len(file_data)} bytes (max {max_size})")

    file_hash = compute_sha256(file_data)

    existing = await check_duplicate(db, file_hash)
    if existing:
        if tagged_person_ids:
            existing.tagged_person_ids = sorted(set(existing.tagged_person_ids) | set(tagged_person_ids))
        if caption and not existing.caption:
            existing.caption = caption
        if title and not existing.title:
            existing.title = title
        if description and not existing.description:
            existing.description = description
        if taken_date and not existing.taken_date:
            existing.taken_date = taken_date
        await db.flush()
        return existing, True

    # Strip EXIF from images
    clean_data = strip_exif(file_data, mime_type)

    if data_dir is None:
        data_dir = get_settings().resolved_data_dir

    media_id = str(uuid.uuid4())
    ext = os.path.splitext(filename)[1].lower() if filename else ""
    relative_path = f"{media_id}{ext}"

    media_dir = os.path.join(data_dir, "media")
    os.makedirs(media_dir, exist_ok=True)

    file_path = os.path.join(media_dir, relative_path)
    with open(file_path, "wb") as f:
        f.write(clean_data)

    # Generate thumbnail for images
    thumb_data = generate_thumbnail(clean_data, mime_type)
    if thumb_data:
        thumb_dir = os.path.join(media_dir, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)
        thumb_path = os.path.join(thumb_dir, f"{media_id}.jpg")
        with open(thumb_path, "wb") as f:
            f.write(thumb_data)

    width, height = get_image_dimensions(file_data, mime_type)

    media = Media(
        id=media_id,
        person_id=person_id,
        file_path=relative_path,
        original_filename=filename,
        media_type=_media_type_for_mime(mime_type),
        mime_type=mime_type,
        width=width,
        height=height,
        file_size_bytes=len(clean_data),
        file_hash=file_hash,
        caption=caption,
        title=title,
        description=description,
        taken_date=taken_date,
        source=MediaSource.manual.value,
        uploaded_by=uploaded_by,
    )
    media.tagged_person_ids = tagged_person_ids or []
    db.add(media)
    await db.flush()

    return media, False


async def save_media_temp_file(
    db: AsyncSession,
    temp_path: str,
    file_size: int,
    file_hash: str,
    filename: str,
    mime_type: str,
    person_id: str,
    uploaded_by: str,
    caption: str | None = None,
    title: str | None = None,
    description: str | None = None,
    taken_date: str | None = None,
    tagged_person_ids: list[str] | None = None,
    data_dir: str | None = None,
) -> tuple[Media, bool]:
    """Persist a streamed upload without buffering the entire file in route code."""
    _validate_media_upload(mime_type, file_size)

    existing = await check_duplicate(db, file_hash)
    if existing:
        return await _merge_duplicate_and_cleanup(
            db=db,
            existing=existing,
            temp_path=temp_path,
            caption=caption,
            title=title,
            description=description,
            taken_date=taken_date,
            tagged_person_ids=tagged_person_ids,
        )

    if data_dir is None:
        data_dir = get_settings().resolved_data_dir

    media_id, relative_path, media_dir, file_path = _allocate_media_paths(data_dir, filename)
    width, height, stored_size, duration = _persist_streamed_media(
        temp_path=temp_path,
        mime_type=mime_type,
        file_path=file_path,
        media_dir=media_dir,
        media_id=media_id,
    )
    media = _build_media_record(
        media_id=media_id,
        person_id=person_id,
        relative_path=relative_path,
        filename=filename,
        mime_type=mime_type,
        width=width,
        height=height,
        stored_size=stored_size,
        file_hash=file_hash,
        caption=caption,
        title=title,
        description=description,
        taken_date=taken_date,
        uploaded_by=uploaded_by,
        tagged_person_ids=tagged_person_ids,
        duration_seconds=duration,
    )
    db.add(media)
    await db.flush()

    return media, False


def _validate_media_upload(mime_type: str, file_size: int) -> None:
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Unsupported MIME type: {mime_type}")

    category = _category_for_mime(mime_type)
    max_size = MAX_SIZE_BY_CATEGORY[category]
    if file_size > max_size:
        raise ValueError(f"File too large: {file_size} bytes (max {max_size})")


async def _merge_duplicate_and_cleanup(
    db: AsyncSession,
    existing: Media,
    temp_path: str,
    caption: str | None,
    title: str | None,
    description: str | None,
    taken_date: str | None,
    tagged_person_ids: list[str] | None,
) -> tuple[Media, bool]:
    if tagged_person_ids:
        existing.tagged_person_ids = sorted(set(existing.tagged_person_ids) | set(tagged_person_ids))
    if caption and not existing.caption:
        existing.caption = caption
    if title and not existing.title:
        existing.title = title
    if description and not existing.description:
        existing.description = description
    if taken_date and not existing.taken_date:
        existing.taken_date = taken_date
    await db.flush()
    os.unlink(temp_path)
    return existing, True


def _allocate_media_paths(data_dir: str, filename: str) -> tuple[str, str, str, str]:
    media_id = str(uuid.uuid4())
    ext = os.path.splitext(filename)[1].lower() if filename else ""
    relative_path = f"{media_id}{ext}"
    media_dir = os.path.join(data_dir, "media")
    os.makedirs(media_dir, exist_ok=True)
    file_path = os.path.join(media_dir, relative_path)
    return media_id, relative_path, media_dir, file_path


def _persist_streamed_media(
    *,
    temp_path: str,
    mime_type: str,
    file_path: str,
    media_dir: str,
    media_id: str,
) -> tuple[int | None, int | None, int, float | None]:
    try:
        if mime_type.startswith("image/"):
            return _persist_temp_image(
                temp_path=temp_path,
                mime_type=mime_type,
                file_path=file_path,
                media_dir=media_dir,
                media_id=media_id,
            )
        shutil.move(temp_path, file_path)
        stored_size = os.path.getsize(file_path)
        width, height, duration = None, None, None

        if mime_type in VIDEO_MIME_TYPES:
            duration, width, height = extract_video_metadata(file_path)
            generate_video_poster(file_path, media_dir, media_id)
        elif mime_type in AUDIO_MIME_TYPES:
            duration = extract_audio_duration(file_path)

        return width, height, stored_size, duration
    except Exception:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def _build_media_record(
    *,
    media_id: str,
    person_id: str,
    relative_path: str,
    filename: str,
    mime_type: str,
    width: int | None,
    height: int | None,
    stored_size: int,
    file_hash: str,
    caption: str | None,
    title: str | None,
    description: str | None,
    taken_date: str | None,
    uploaded_by: str,
    tagged_person_ids: list[str] | None,
    duration_seconds: float | None = None,
) -> Media:
    media = Media(
        id=media_id,
        person_id=person_id,
        file_path=relative_path,
        original_filename=filename,
        media_type=_media_type_for_mime(mime_type),
        mime_type=mime_type,
        width=width,
        height=height,
        duration_seconds=duration_seconds,
        file_size_bytes=stored_size,
        file_hash=file_hash,
        caption=caption,
        title=title,
        description=description,
        taken_date=taken_date,
        source=MediaSource.manual.value,
        uploaded_by=uploaded_by,
    )
    media.tagged_person_ids = tagged_person_ids or []
    return media


def _persist_temp_image(
    *,
    temp_path: str,
    mime_type: str,
    file_path: str,
    media_dir: str,
    media_id: str,
) -> tuple[int | None, int | None, int, None]:
    with open(temp_path, "rb") as temp_file:
        original_data = temp_file.read()
    clean_data = strip_exif(original_data, mime_type)
    with open(file_path, "wb") as output_file:
        output_file.write(clean_data)

    # Legacy thumbnail (backward compat)
    thumb_data = generate_thumbnail(clean_data, mime_type)
    if thumb_data:
        thumb_dir = os.path.join(media_dir, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)
        thumb_path = os.path.join(thumb_dir, f"{media_id}.jpg")
        with open(thumb_path, "wb") as thumb_file:
            thumb_file.write(thumb_data)

    # New variants (thumb 200x200 crop + medium 800px)
    generate_image_variants(clean_data, mime_type, media_dir, media_id)

    width, height = get_image_dimensions(clean_data, mime_type)
    os.unlink(temp_path)
    return width, height, len(clean_data), None


def delete_media_files(media: Media, data_dir: str | None = None) -> None:
    if data_dir is None:
        data_dir = get_settings().resolved_data_dir

    if media.file_path:
        file_path = os.path.join(data_dir, "media", media.file_path)
        if os.path.isfile(file_path):
            os.unlink(file_path)

    # Legacy thumbnail
    thumb_path = os.path.join(data_dir, "media", "thumbnails", f"{media.id}.jpg")
    if os.path.isfile(thumb_path):
        os.unlink(thumb_path)

    # Variant directory
    variant_dir = os.path.join(data_dir, "media", "variants", media.id)
    if os.path.isdir(variant_dir):
        shutil.rmtree(variant_dir, ignore_errors=True)
