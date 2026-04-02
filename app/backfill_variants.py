from __future__ import annotations

import argparse
import asyncio
import logging
import os
from dataclasses import dataclass

from sqlalchemy import select

from app.database import async_session_factory
from app.models.media import Media
from app.services.media_service import (
    generate_image_variants,
    generate_medium_variant,
    generate_video_poster,
    get_variant_path,
)

logger = logging.getLogger(__name__)


@dataclass
class BackfillStats:
    processed: int = 0
    created: int = 0
    skipped: int = 0
    failed: int = 0


async def backfill_variants(*, dry_run: bool = False) -> BackfillStats:
    stats = BackfillStats()
    async with async_session_factory() as session:
        result = await session.execute(select(Media).order_by(Media.created_at.asc()))
        media_items = result.scalars().all()

        from app.config import get_settings

        settings = get_settings()
        data_dir = getattr(settings, "resolved_data_dir", settings.DATA_DIR)
        media_dir = os.path.join(data_dir, "media")

        for media in media_items:
            stats.processed += 1
            try:
                changed = await _backfill_one_media(media, media_dir=media_dir, dry_run=dry_run)
            except Exception:
                stats.failed += 1
                logger.warning("Variant backfill failed for %s", media.id, exc_info=True)
                continue
            if changed:
                stats.created += 1
            else:
                stats.skipped += 1
        await session.commit()
    return stats


async def _backfill_one_media(media: Media, *, media_dir: str, dry_run: bool) -> bool:
    if not media.file_path:
        logger.info("Skipping %s: no file_path", media.id)
        return False

    file_path = os.path.join(media_dir, media.file_path)
    if not os.path.isfile(file_path):
        logger.info("Skipping %s: missing file", media.id)
        return False

    if media.media_type in ("image", "gif"):
        thumb_exists = get_variant_path(media.id, "thumb") is not None
        medium_exists = get_variant_path(media.id, "medium") is not None
        with open(file_path, "rb") as fh:
            data = fh.read()
        medium_needed = generate_medium_variant(data, media.mime_type or "image/jpeg") is not None
        if thumb_exists and (medium_exists or not medium_needed):
            return False
        if dry_run:
            logger.info("[dry-run] would backfill image variants for %s", media.id)
            return True
        generate_image_variants(data, media.mime_type or "image/jpeg", media_dir, media.id)
        return True

    if media.media_type == "video":
        poster_exists = get_variant_path(media.id, "poster") is not None
        if poster_exists:
            return False
        if dry_run:
            logger.info("[dry-run] would generate poster variant for %s", media.id)
            return True
        return generate_video_poster(file_path, media_dir, media.id)

    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill media variants for existing records.")
    parser.add_argument("--dry-run", action="store_true", help="Report work without writing files.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    stats = asyncio.run(backfill_variants(dry_run=args.dry_run))
    logger.info(
        "processed=%s created=%s skipped=%s failed=%s",
        stats.processed,
        stats.created,
        stats.skipped,
        stats.failed,
    )


if __name__ == "__main__":
    main()
