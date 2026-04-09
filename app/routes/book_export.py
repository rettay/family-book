from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import can_view_media, get_accessible_person_ids, get_person_access
from app.auth import require_auth
from app.database import get_db
from app.models.book import BookProject
from app.models.media import Media
from app.models.person import Person, PersonLifecycleState
from app.models.story import Story
from app.routes.pages import _ctx, templates
from app.roles import is_staff_actor
from app.services.audit_service import log_audit
from app.services.book_export_service import build_book_export

router = APIRouter(tags=["book_export"])


@router.get("/books", response_class=HTMLResponse)
async def books_page(
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    accessible_ids = await get_accessible_person_ids(db, current_user)
    people_result = await db.execute(
        select(Person)
        .where(
            Person.id.in_(accessible_ids),
            Person.is_root.is_(False),
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
        .order_by(Person.last_name, Person.first_name)
    )
    people = people_result.scalars().all()

    story_result = await db.execute(
        select(Story).where(Story.person_id.in_(accessible_ids)).order_by(Story.created_at.desc()).limit(50)
    )
    stories = story_result.scalars().all()

    media_result = await db.execute(select(Media).order_by(Media.created_at.desc()).limit(50))
    media_items = []
    for media in media_result.scalars().all():
        if await can_view_media(db, current_user, media):
            media_items.append(media)

    project_result = await db.execute(
        select(BookProject).where(BookProject.created_by == current_user.id).order_by(BookProject.created_at.desc())
    )
    projects = project_result.scalars().all()

    return templates.TemplateResponse(
        "book_export.html",
        _ctx(
            request,
            current_user,
            active_page="books",
            people=people,
            stories=stories,
            media_items=media_items,
            projects=projects,
            can_create_books=is_staff_actor(current_user),
        ),
    )


@router.post("/books")
async def create_book_project(
    title: str = Form(...),
    subtitle: str | None = Form(None),
    introduction: str | None = Form(None),
    person_ids: list[str] = Form([]),
    story_ids: list[str] = Form([]),
    media_ids: list[str] = Form([]),
    include_timeline: str = Form("true"),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if not is_staff_actor(current_user):
        raise HTTPException(status_code=403, detail="Staff access required")

    validated_person_ids = []
    for person_id in person_ids:
        person = await db.get(Person, person_id)
        if person is None:
            continue
        access = await get_person_access(db, current_user, person)
        if access.can_view:
            validated_person_ids.append(person_id)

    validated_story_ids = []
    for story_id in story_ids:
        story = await db.get(Story, story_id)
        if story is None:
            continue
        person = await db.get(Person, story.person_id)
        if person is None:
            continue
        access = await get_person_access(db, current_user, person)
        if access.can_view:
            validated_story_ids.append(story_id)

    validated_media_ids = []
    for media_id in media_ids:
        media = await db.get(Media, media_id)
        if media is None:
            continue
        if await can_view_media(db, current_user, media):
            validated_media_ids.append(media_id)

    project = BookProject(
        created_by=current_user.id,
        title=title.strip(),
        subtitle=(subtitle or "").strip() or None,
        introduction=(introduction or "").strip() or None,
        include_timeline=include_timeline.strip().lower() in {"1", "true", "yes", "on"},
    )
    project.person_ids = validated_person_ids
    project.story_ids = validated_story_ids
    project.media_ids = validated_media_ids
    db.add(project)
    await db.flush()

    project.generated_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    await db.flush()

    await log_audit(
        db,
        current_user.id,
        "create",
        "book_project",
        project.id,
        new_value={
            "person_count": len(validated_person_ids),
            "story_count": len(validated_story_ids),
            "media_count": len(validated_media_ids),
        },
    )
    return RedirectResponse("/books", status_code=303)


@router.get("/books/{project_id}/download")
async def download_book_project(
    project_id: str,
    format: str = Query("markdown"),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(BookProject, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Book project not found")
    if project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    markdown, pdf_bytes = await build_book_export(db, project=project, actor=current_user)
    safe_title = "".join(char if char.isalnum() or char in {" ", "-", "_"} else "_" for char in project.title).strip()
    filename_base = safe_title or "family-book"

    if format == "markdown":
        return Response(
            markdown,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename_base}.md"',
            },
        )
    if format == "pdf":
        return Response(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename_base}.pdf"',
            },
        )
    raise HTTPException(status_code=400, detail="Unsupported export format")
