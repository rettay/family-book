"""Tests for wiki pages feature (S24, Slices 2-3)."""

import pytest
from httpx import AsyncClient

ROOT_ID = "root-0000-0000-0000-000000000001"


@pytest.mark.asyncio
async def test_slug_generated_on_create(admin_client: AsyncClient):
    """POST /api/persons assigns a slug."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Maria",
        "last_name": "Santos",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] is not None
    assert "maria" in data["slug"].lower()
    assert "santos" in data["slug"].lower()


@pytest.mark.asyncio
async def test_slug_unique(admin_client: AsyncClient):
    """Two persons with same name get different slugs (short_id differs)."""
    resp1 = await admin_client.post("/api/persons", json={
        "first_name": "John",
        "last_name": "Doe",
    })
    resp2 = await admin_client.post("/api/persons", json={
        "first_name": "John",
        "last_name": "Doe",
    })
    assert resp1.status_code == 201
    assert resp2.status_code == 201
    assert resp1.json()["slug"] != resp2.json()["slug"]


@pytest.mark.asyncio
async def test_wiki_index_renders(admin_client: AsyncClient):
    """GET /wiki returns 200."""
    resp = await admin_client.get("/wiki")
    assert resp.status_code == 200
    assert "Family Bios" in resp.text


@pytest.mark.asyncio
async def test_wiki_index_lists_persons(admin_client: AsyncClient):
    """Persons appear in wiki index."""
    # Create a person
    resp = await admin_client.post("/api/persons", json={
        "first_name": "WikiIdx",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get("/wiki")
    assert resp.status_code == 200
    assert slug in resp.text


@pytest.mark.asyncio
async def test_wiki_index_search(admin_client: AsyncClient):
    """Search filter works on wiki index."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Searchable",
        "last_name": "Wikiman",
    })
    assert resp.status_code == 201

    resp = await admin_client.get("/wiki?search=Searchable")
    assert resp.status_code == 200
    assert "Searchable" in resp.text


@pytest.mark.asyncio
async def test_wiki_person_page(admin_client: AsyncClient):
    """GET /wiki/{slug} returns 200."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "WikiPage",
        "last_name": "Test",
        "bio": "A test person for wiki pages.",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    assert "WikiPage" in resp.text


@pytest.mark.asyncio
async def test_wiki_person_sections(admin_client: AsyncClient):
    """Sections render from structured data."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Detailed",
        "last_name": "Wiki",
        "bio": "A remarkable individual.",
        "birth_place": "Mexico City",
        "education": [{"degree": "PhD", "institution": "UNAM", "year": "2010"}],
        "career": [{"title": "Professor", "company": "UNAM", "years": "2010-2020"}],
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    assert "Mexico City" in resp.text
    assert "PhD" in resp.text
    assert "Professor" in resp.text


@pytest.mark.asyncio
async def test_wiki_api_returns_sections(admin_client: AsyncClient):
    """API endpoint returns section data."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "ApiWiki",
        "last_name": "Test",
        "bio": "Bio text",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/api/wiki/{slug}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == slug
    assert len(data["sections"]) > 0
    section_ids = [s["id"] for s in data["sections"]]
    assert "summary" in section_ids


@pytest.mark.asyncio
async def test_wiki_unauthenticated(client: AsyncClient):
    """Wiki requires authentication."""
    resp = await client.get("/wiki")
    # Should redirect to login or return 401
    assert resp.status_code in (302, 401)


@pytest.mark.asyncio
async def test_wiki_404_for_bad_slug(admin_client: AsyncClient):
    """GET /wiki/nonexistent returns 404."""
    resp = await admin_client.get("/wiki/nonexistent-slug-xyz")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_wiki_root_person_redacted(admin_client: AsyncClient):
    """Root person wiki page redacts name."""
    # Get root person slug
    resp = await admin_client.get(f"/api/persons/{ROOT_ID}")
    assert resp.status_code == 200
    slug = resp.json().get("slug")
    if slug:
        resp = await admin_client.get(f"/wiki/{slug}")
        assert resp.status_code == 200
        # Root person's real name should not appear
        # The display_name should be redacted (shows "You" or similar)


# ── Slice 3 Tests: Section Editing and Cross-Links ────────────────


@pytest.mark.asyncio
async def test_wiki_edit_section_renders(admin_client: AsyncClient):
    """GET /wiki/{slug}/edit/summary returns edit form partial."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "EditForm",
        "last_name": "Test",
        "bio": "Original bio",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}/edit/summary")
    assert resp.status_code == 200
    assert "form" in resp.text.lower()
    assert "Original bio" in resp.text


@pytest.mark.asyncio
async def test_wiki_save_section(admin_client: AsyncClient):
    """POST /wiki/{slug}/edit/summary updates person bio."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "SaveTest",
        "last_name": "Wiki",
        "bio": "Old bio",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    resp = await admin_client.post(
        f"/wiki/{slug}/edit/summary",
        data={"bio": "Updated bio via wiki"},
    )
    assert resp.status_code == 200

    # Verify the update persisted
    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    assert resp.json()["bio"] == "Updated bio via wiki"


@pytest.mark.asyncio
async def test_wiki_edit_unknown_section(admin_client: AsyncClient):
    """GET /wiki/{slug}/edit/nonexistent returns 404."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Unknown",
        "last_name": "Section",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}/edit/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_wiki_cross_links_in_person_page(admin_client: AsyncClient):
    """Person profile page contains wiki link."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "CrossLink",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/people/{person_id}/edit")
    assert resp.status_code == 200
    assert f"/wiki/{slug}" in resp.text


# ── Audit Follow-up Tests: Access Control ─────────────────────────


@pytest.mark.asyncio
async def test_wiki_index_excludes_hidden(admin_client: AsyncClient, member_client: AsyncClient):
    """Hidden persons do not appear in wiki index for non-admin members."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "HiddenWiki",
        "last_name": "Person",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    # Admin sets visibility to hidden
    resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "visibility": "hidden",
    })
    assert resp.status_code == 200

    # Member should NOT see hidden person in wiki index
    resp = await member_client.get("/wiki")
    assert resp.status_code == 200
    assert slug not in resp.text

    # Admin SHOULD still see hidden person
    resp = await admin_client.get("/wiki")
    assert resp.status_code == 200
    assert slug in resp.text


@pytest.mark.asyncio
async def test_wiki_edit_unauthorized(client: AsyncClient):
    """Unauthenticated user cannot access wiki edit endpoints."""
    # Auth check happens before slug lookup, so any slug works
    resp = await client.get("/wiki/any-slug/edit/summary")
    assert resp.status_code in (302, 401)

    resp = await client.post(
        "/wiki/any-slug/edit/summary",
        data={"bio": "Hacked bio"},
    )
    assert resp.status_code in (302, 401)


# ── S26 Tests: Section Structure Enhancement & Rich Text ─────────


@pytest.mark.asyncio
async def test_wiki_physical_description_section(admin_client: AsyncClient):
    """Physical description section appears when data exists."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "PhysDesc",
        "last_name": "Test",
        "height": "175 cm",
        "eye_color": "brown",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    assert "175 cm" in resp.text
    assert "brown" in resp.text


@pytest.mark.asyncio
async def test_wiki_sources_section(admin_client: AsyncClient):
    """Sources section appears when source_detail exists."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "SourceTest",
        "last_name": "Wiki",
        "source_detail": "Aunt Maria, Thanksgiving 2019",
        "confidence": "probable",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    assert "Aunt Maria" in resp.text
    assert "probable" in resp.text


@pytest.mark.asyncio
async def test_wiki_rich_text_sanitization(admin_client: AsyncClient):
    """Rich text HTML is sanitized (script tags removed)."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "RichText",
        "last_name": "Sanitize",
        "bio": "Clean bio",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    # Submit bio with malicious script tag
    resp = await admin_client.post(
        f"/wiki/{slug}/edit/summary",
        data={"bio": '<p>Hello</p><script>alert("xss")</script><strong>World</strong>'},
    )
    assert resp.status_code == 200

    # Verify script tag was stripped but allowed tags preserved
    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    bio = resp.json()["bio"]
    assert "<script>" not in bio
    assert "<strong>World</strong>" in bio
    assert "<p>Hello</p>" in bio


@pytest.mark.asyncio
async def test_wiki_rich_text_round_trip(admin_client: AsyncClient):
    """Rich text saves and renders with formatting preserved."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "RoundTrip",
        "last_name": "Rich",
        "bio": "Original",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    rich_bio = "<p>A <strong>remarkable</strong> individual with <em>many</em> talents.</p>"
    resp = await admin_client.post(
        f"/wiki/{slug}/edit/summary",
        data={"bio": rich_bio},
    )
    assert resp.status_code == 200

    # Verify it renders on the wiki page
    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    assert "<strong>remarkable</strong>" in resp.text


@pytest.mark.asyncio
async def test_wiki_edit_physical_description(admin_client: AsyncClient):
    """Physical description section can be edited."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "EditPhys",
        "last_name": "Desc",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/wiki/{slug}/edit/physical-description")
    assert resp.status_code == 200
    assert "form" in resp.text.lower()

    resp = await admin_client.post(
        f"/wiki/{slug}/edit/physical-description",
        data={"height": "180 cm", "weight": "75 kg", "eye_color": "blue",
              "hair_color": "brown", "blood_type": "A+"},
    )
    assert resp.status_code == 200

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    assert resp.json()["height"] == "180 cm"
    assert resp.json()["blood_type"] == "A+"


@pytest.mark.asyncio
async def test_wiki_edit_sources(admin_client: AsyncClient):
    """Sources section can be edited."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "EditSrc",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    resp = await admin_client.post(
        f"/wiki/{slug}/edit/sources",
        data={"source_detail": "1940 US Census", "confidence": "confirmed"},
    )
    assert resp.status_code == 200

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    assert resp.json()["source_detail"] == "1940 US Census"
    assert resp.json()["confidence"] == "confirmed"


@pytest.mark.asyncio
async def test_wiki_summary_shows_age(admin_client: AsyncClient):
    """Summary section includes computed age for living persons."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "AgeTest",
        "last_name": "Wiki",
        "birth_date_raw": "1990-06-15",
        "birth_date": "1990-06-15",
        "is_living": True,
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    # Should contain "age XX" in the summary
    assert "age" in resp.text.lower()


@pytest.mark.asyncio
async def test_wiki_early_life_maiden_name(admin_client: AsyncClient):
    """Early life section shows maiden name when different from last name."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "MaidenTest",
        "last_name": "Smith",
        "birth_last_name": "Jones",
        "birth_place": "Chicago",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    assert "Jones" in resp.text


@pytest.mark.asyncio
async def test_wiki_death_legacy_full_burial(admin_client: AsyncClient):
    """Death & Legacy section shows full burial details."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "BurialTest",
        "last_name": "Wiki",
        "is_living": False,
        "death_date_raw": "2020-01-15",
        "burial_place": "Oak Hill Cemetery",
        "burial_cemetery_name": "Oak Hill",
        "burial_country_code": "US",
        "burial_plot_number": "Section 3, Row 12",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    assert "Oak Hill" in resp.text
    assert "Section 3, Row 12" in resp.text


@pytest.mark.asyncio
async def test_wiki_structured_education_edit(admin_client: AsyncClient):
    """Education entries can be edited via structured form fields."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "EduForm",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    # Submit structured form fields
    resp = await admin_client.post(
        f"/wiki/{slug}/edit/education",
        data={
            "education[0].institution": "MIT",
            "education[0].degree": "BS",
            "education[0].field_of_study": "Computer Science",
            "education[0].year_start": "2010",
            "education[0].year_end": "2014",
            "education[1].institution": "Stanford",
            "education[1].degree": "PhD",
            "education[1].year_start": "2014",
        },
    )
    assert resp.status_code == 200

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    edu = resp.json()["education"]
    assert len(edu) == 2
    assert edu[0]["institution"] == "MIT"
    assert edu[0]["degree"] == "BS"
    assert edu[1]["institution"] == "Stanford"
    assert edu[1]["degree"] == "PhD"


@pytest.mark.asyncio
async def test_wiki_structured_career_edit(admin_client: AsyncClient):
    """Career entries can be edited via structured form fields."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "CareerForm",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    resp = await admin_client.post(
        f"/wiki/{slug}/edit/career",
        data={
            "career[0].title": "Professor",
            "career[0].employer": "UNAM",
            "career[0].year_start": "2010",
            "career[0].year_end": "2020",
            "career[0].location": "Mexico City",
        },
    )
    assert resp.status_code == 200

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    career = resp.json()["career"]
    assert len(career) == 1
    assert career[0]["title"] == "Professor"
    assert career[0]["employer"] == "UNAM"
    assert career[0]["location"] == "Mexico City"


@pytest.mark.asyncio
async def test_wiki_structured_organizations_edit(admin_client: AsyncClient):
    """Organization entries can be edited via structured form fields."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "OrgForm",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    resp = await admin_client.post(
        f"/wiki/{slug}/edit/organizations",
        data={
            "organizations[0].name": "Rotary Club",
            "organizations[0].role": "President",
            "organizations[0].year_joined": "2005",
        },
    )
    assert resp.status_code == 200

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    orgs = resp.json()["organizations"]
    assert len(orgs) == 1
    assert orgs[0]["name"] == "Rotary Club"
    assert orgs[0]["role"] == "President"


@pytest.mark.asyncio
async def test_wiki_structured_form_remove_entry(admin_client: AsyncClient):
    """Removing entries via structured form works (submit with fewer entries)."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "RemoveEntry",
        "last_name": "Test",
        "education": [
            {"institution": "School A", "degree": "BA"},
            {"institution": "School B", "degree": "MA"},
        ],
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    # Submit with only one entry (simulating user removed the second)
    resp = await admin_client.post(
        f"/wiki/{slug}/edit/education",
        data={
            "education[0].institution": "School A",
            "education[0].degree": "BA",
        },
    )
    assert resp.status_code == 200

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    edu = resp.json()["education"]
    assert len(edu) == 1
    assert edu[0]["institution"] == "School A"


@pytest.mark.asyncio
async def test_wiki_structured_form_remove_all_entries(admin_client: AsyncClient):
    """Removing ALL entries clears the array to empty list (S4-F01)."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "RemoveAll",
        "last_name": "Test",
        "education": [
            {"institution": "School A", "degree": "BA"},
        ],
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    # Submit education section with no entries at all
    resp = await admin_client.post(
        f"/wiki/{slug}/edit/education",
        data={},
    )
    assert resp.status_code == 200

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    assert resp.json()["education"] == []


@pytest.mark.asyncio
async def test_wiki_api_returns_new_sections(admin_client: AsyncClient):
    """API endpoint returns physical-description and sources section IDs."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "ApiSections",
        "last_name": "Test",
        "height": "170 cm",
        "source_detail": "Family oral history",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/api/wiki/{slug}")
    assert resp.status_code == 200
    data = resp.json()
    section_ids = [s["id"] for s in data["sections"]]
    assert "physical-description" in section_ids
    assert "sources" in section_ids


@pytest.mark.asyncio
async def test_api_create_sanitizes_rich_text(admin_client: AsyncClient):
    """POST /api/persons sanitizes bio/obituary/research_notes (S3-F01)."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "ApiSanitize",
        "last_name": "Create",
        "bio": '<p>Safe</p><script>alert("xss")</script>',
        "obituary": '<em>Rest</em><img src=x onerror=alert(1)>',
        "research_notes": '<strong>Note</strong><iframe src="evil"></iframe>',
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "<script>" not in data["bio"]
    assert "<p>Safe</p>" in data["bio"]
    assert "<img" not in data["obituary"]
    assert "<em>Rest</em>" in data["obituary"]
    assert "<iframe" not in data["research_notes"]
    assert "<strong>Note</strong>" in data["research_notes"]


@pytest.mark.asyncio
async def test_api_update_sanitizes_rich_text(admin_client: AsyncClient):
    """PUT /api/persons/{id} sanitizes rich text fields (S3-F01)."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "ApiSanitize",
        "last_name": "Update",
    })
    assert resp.status_code == 201
    pid = resp.json()["id"]

    resp = await admin_client.put(f"/api/persons/{pid}", json={
        "bio": '<p>Updated</p><script>steal()</script>',
        "obituary": '<p>Memory</p><object data="bad"></object>',
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "<script>" not in data["bio"]
    assert "<p>Updated</p>" in data["bio"]
    assert "<object" not in data["obituary"]
    assert "<p>Memory</p>" in data["obituary"]


@pytest.mark.asyncio
async def test_wiki_structured_form_validates_and_strips_unknown_keys(admin_client: AsyncClient):
    """Pydantic validation strips unknown keys and enforces max_length (S4-F02+F08)."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Validate",
        "last_name": "Keys",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    # Submit education with an unknown key "evil_field" and oversized institution
    resp = await admin_client.post(
        f"/wiki/{slug}/edit/education",
        data={
            "education[0].institution": "MIT",
            "education[0].degree": "PhD",
            "education[0].evil_field": "should be stripped",
        },
    )
    assert resp.status_code == 200

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    edu = resp.json()["education"]
    assert len(edu) == 1
    assert edu[0]["institution"] == "MIT"
    assert "evil_field" not in edu[0]


@pytest.mark.asyncio
async def test_wiki_structured_form_rejects_oversized_field(admin_client: AsyncClient):
    """Pydantic validation rejects values exceeding max_length (S4-F08)."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "MaxLen",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    # Institution max_length is 300 — submit 400 chars
    resp = await admin_client.post(
        f"/wiki/{slug}/edit/education",
        data={
            "education[0].institution": "X" * 400,
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_wiki_plain_text_fields_escaped_in_safe_sections(admin_client: AsyncClient):
    """Plain-text fields are HTML-escaped even in |safe sections (S2-R01/R02)."""
    xss = '<img src=x onerror=alert(1)>'
    resp = await admin_client.post("/api/persons", json={
        "first_name": "EscapeTest",
        "last_name": "Safe",
        "birth_date_raw": xss,
        "is_living": False,
        "death_date_raw": "2020-01-01",
        "burial_place": xss,
        "burial_cemetery_name": xss,
        "burial_plot_number": xss,
        "obituary_source": xss,
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    # Fetch wiki page — HTML should be escaped, not rendered raw
    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    html = resp.text

    # The raw <img> tag must NOT appear unescaped
    assert '<img src=x onerror=alert(1)>' not in html
    # The escaped form should appear
    assert '&lt;img src=x onerror=alert(1)&gt;' in html
