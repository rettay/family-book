from sqlalchemy import select

from app.models.book import BookProject
from app.models.media import Media
from app.models.person import Person, PersonRole
from app.models.story import Story


async def test_staff_can_create_book_project_and_download_exports(admin_client, seeded_db, tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    story = Story(
        person_id="member-00-0000-0000-000000000005",
        title="A family recipe",
        body="The dough rested overnight.",
        author_person_id="tyler-000-0000-0000-000000000002",
        source="Recipe card",
    )
    media = Media(
        person_id="member-00-0000-0000-000000000005",
        file_path="recipe.jpg",
        original_filename="recipe.jpg",
        media_type="image",
        mime_type="image/jpeg",
        title="Recipe photo",
        source="manual",
        uploaded_by="tyler-000-0000-0000-000000000002",
    )
    seeded_db.add_all([story, media])
    await seeded_db.commit()

    resp = await admin_client.post(
        "/books",
        data={
            "title": "Martin Family Book",
            "subtitle": "Kitchen and stories",
            "introduction": "A first printable draft.",
            "person_ids": ["member-00-0000-0000-000000000005"],
            "story_ids": [story.id],
            "media_ids": [media.id],
            "include_timeline": "true",
        },
        follow_redirects=False,
    )

    assert resp.status_code == 303
    project = (await seeded_db.execute(select(BookProject))).scalar_one()
    assert project.markdown_path is None
    assert project.pdf_path is None

    markdown_resp = await admin_client.get(f"/books/{project.id}/download?format=markdown")
    assert markdown_resp.status_code == 200
    assert "# Martin Family Book" in markdown_resp.text
    assert "A family recipe" in markdown_resp.text
    assert "Source: Recipe card" in markdown_resp.text
    assert "Recipe photo" in markdown_resp.text
    assert not (tmp_path / "exports" / "books").exists()

    pdf_resp = await admin_client.get(f"/books/{project.id}/download?format=pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"].startswith("application/pdf")
    assert pdf_resp.content.startswith(b"%PDF-1.4")


async def test_non_staff_cannot_create_book_project(member_client):
    resp = await member_client.post(
        "/books",
        data={"title": "Unauthorized book"},
    )

    assert resp.status_code == 403


async def test_book_project_excludes_invisible_private_media_for_steward(
    member_client,
    seeded_db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    steward = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    steward.role = PersonRole.steward.value

    private_media = Media(
        person_id="tyler-000-0000-0000-000000000002",
        file_path="private.jpg",
        original_filename="private.jpg",
        media_type="image",
        mime_type="image/jpeg",
        title="Private upload",
        source="manual",
        uploaded_by="tyler-000-0000-0000-000000000002",
        visibility="private",
    )
    seeded_db.add(private_media)
    await seeded_db.commit()

    resp = await member_client.post(
        "/books",
        data={
            "title": "Steward draft",
            "media_ids": [private_media.id],
        },
        follow_redirects=False,
    )

    assert resp.status_code == 303
    project = (await seeded_db.execute(select(BookProject).order_by(BookProject.created_at.desc()))).scalars().first()
    markdown_resp = await member_client.get(f"/books/{project.id}/download?format=markdown")
    assert markdown_resp.status_code == 200
    assert "Private upload" not in markdown_resp.text


async def test_staff_cannot_download_another_staff_members_book_project(
    admin_client,
    member_client,
    seeded_db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    steward = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    steward.role = PersonRole.steward.value
    await seeded_db.commit()

    resp = await admin_client.post(
        "/books",
        data={
            "title": "Private draft",
            "person_ids": ["tyler-000-0000-0000-000000000002"],
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    project = (
        await seeded_db.execute(select(BookProject).order_by(BookProject.created_at.desc()))
    ).scalars().first()

    other_staff_resp = await member_client.get(f"/books/{project.id}/download?format=markdown")
    assert other_staff_resp.status_code == 403
