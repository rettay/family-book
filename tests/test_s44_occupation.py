"""Tests for S44 Occupation History: data model, API, wiki UI, tree payload, i18n."""
import pytest
from httpx import AsyncClient

ADMIN_ID = "tyler-000-0000-0000-000000000002"
MEMBER_ID = "member-00-0000-0000-000000000005"


async def _create_person(client: AsyncClient, first: str = "Test", last: str = "Person") -> dict:
    resp = await client.post("/api/persons", json={"first_name": first, "last_name": last})
    assert resp.status_code == 201
    return resp.json()


# ── FB-098: REST API ──────────────────────────────────────────────────────────


class TestOccupationListAPI:
    async def test_list_empty(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        resp = await admin_client.get(f"/api/persons/{person['id']}/occupations")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/persons/nonexistent/occupations")
        assert resp.status_code == 401

    async def test_list_current_role_first(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        pid = person["id"]
        # Add a past role first
        await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Past Role", "start_date": "1990", "end_date": "2000"},
        )
        # Then a current role
        await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Current Role", "currently_in_role": "1"},
        )
        resp = await admin_client.get(f"/api/persons/{pid}/occupations")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 2
        assert items[0]["title"] == "Current Role"
        assert items[0]["end_date"] is None
        assert items[1]["title"] == "Past Role"


class TestOccupationCreateAPI:
    async def test_create_basic(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        resp = await admin_client.post(
            f"/api/persons/{person['id']}/occupations",
            data={"title": "Farmer", "employer": "Self", "start_date": "1920"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Farmer"
        assert body["employer"] == "Self"
        assert body["start_date"] == "1920"
        assert body["end_date"] is None  # currently_in_role not submitted → null

    async def test_create_requires_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/persons/x/occupations",
            data={"title": "Teacher"},
        )
        assert resp.status_code == 401

    async def test_create_fuzzy_dates(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        resp = await admin_client.post(
            f"/api/persons/{person['id']}/occupations",
            data={"title": "Seamstress", "start_date": "circa 1895", "end_date": "early 1920s"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["start_date"] == "circa 1895"
        assert body["end_date"] == "early 1920s"

    async def test_create_with_currently_in_role_sets_end_date_null(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        resp = await admin_client.post(
            f"/api/persons/{person['id']}/occupations",
            data={"title": "Engineer", "currently_in_role": "1"},
        )
        assert resp.status_code == 201
        assert resp.json()["end_date"] is None

    async def test_create_second_current_returns_conflict_flag(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        pid = person["id"]
        # First current role
        await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "First Current", "currently_in_role": "1"},
        )
        # Second current role — should get conflict flag
        resp = await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Second Current", "currently_in_role": "1"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["conflict"] is True
        assert "conflict_message" in body

    async def test_create_second_current_does_not_auto_close_first(self, admin_client: AsyncClient):
        """Warn, don't auto-close: the first current role must remain unchanged."""
        person = await _create_person(admin_client)
        pid = person["id"]
        await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "First Current", "currently_in_role": "1"},
        )
        await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Second Current", "currently_in_role": "1"},
        )
        items = (await admin_client.get(f"/api/persons/{pid}/occupations")).json()
        current_items = [i for i in items if i["end_date"] is None]
        assert len(current_items) == 2  # both remain current

    async def test_create_past_role_no_conflict(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        pid = person["id"]
        await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Current", "currently_in_role": "1"},
        )
        resp = await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Past", "start_date": "1990", "end_date": "2000"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body.get("conflict") is None or body.get("conflict") is False


class TestOccupationUpdateAPI:
    async def test_update_fields(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        pid = person["id"]
        create_resp = await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Old Title", "employer": "Old Employer"},
        )
        occ_id = create_resp.json()["id"]
        resp = await admin_client.put(
            f"/api/persons/{pid}/occupations/{occ_id}",
            data={"title": "New Title", "employer": "New Employer", "start_date": "2005"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["title"] == "New Title"
        assert body["employer"] == "New Employer"
        assert body["start_date"] == "2005"

    async def test_update_404_for_wrong_person(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        person2 = await _create_person(admin_client, first="Other")
        create_resp = await admin_client.post(
            f"/api/persons/{person['id']}/occupations",
            data={"title": "Role"},
        )
        occ_id = create_resp.json()["id"]
        resp = await admin_client.put(
            f"/api/persons/{person2['id']}/occupations/{occ_id}",
            data={"title": "Hijacked"},
        )
        assert resp.status_code == 404


class TestOccupationDeleteAPI:
    async def test_admin_can_delete_any(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        pid = person["id"]
        create_resp = await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Doomed Role"},
        )
        occ_id = create_resp.json()["id"]
        resp = await admin_client.delete(f"/api/persons/{pid}/occupations/{occ_id}")
        assert resp.status_code == 204
        items = (await admin_client.get(f"/api/persons/{pid}/occupations")).json()
        assert items == []

    async def test_non_adder_member_cannot_delete(self, admin_client: AsyncClient, member_client: AsyncClient):
        """A member who did not add the role cannot delete it."""
        # Admin adds a role
        person = await _create_person(admin_client)
        pid = person["id"]
        create_resp = await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Admin-added Role"},
        )
        occ_id = create_resp.json()["id"]
        # Member (not the adder) tries to delete — should get 403
        resp = await member_client.delete(f"/api/persons/{pid}/occupations/{occ_id}")
        assert resp.status_code == 403

    async def test_delete_requires_auth(self, client: AsyncClient):
        resp = await client.delete("/api/persons/x/occupations/y")
        assert resp.status_code == 401

    async def test_delete_404_wrong_person(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        person2 = await _create_person(admin_client, first="Other2")
        create_resp = await admin_client.post(
            f"/api/persons/{person['id']}/occupations",
            data={"title": "Role"},
        )
        occ_id = create_resp.json()["id"]
        resp = await admin_client.delete(f"/api/persons/{person2['id']}/occupations/{occ_id}")
        assert resp.status_code == 404

    async def test_adder_member_can_delete_own_role(
        self, admin_client: AsyncClient, member_client: AsyncClient
    ):
        """P2-1: The member who added a role can delete it (adder-or-admin pattern)."""
        person = await _create_person(admin_client)
        pid = person["id"]
        # Member adds the role
        create_resp = await member_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Member-added Role"},
        )
        assert create_resp.status_code == 201
        occ_id = create_resp.json()["id"]
        # Same member deletes it — should succeed
        resp = await member_client.delete(f"/api/persons/{pid}/occupations/{occ_id}")
        assert resp.status_code == 204
        items = (await admin_client.get(f"/api/persons/{pid}/occupations")).json()
        assert items == []

    async def test_cascade_delete_removes_occupations(
        self, admin_client: AsyncClient, seeded_db
    ):
        """P2-2: Hard-deleting a Person row cascades to occupation rows (CASCADE FK).

        The API uses soft-delete (lifecycle_state change), so we bypass it and issue
        a raw DELETE on the Person row to exercise the SQLite CASCADE constraint.
        """
        from sqlalchemy import delete, select as sa_select
        from app.models.person import Person
        from app.models.occupation import PersonOccupation

        person = await _create_person(admin_client)
        pid = person["id"]
        await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Role A", "start_date": "1990", "end_date": "2000"},
        )
        await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Role B", "currently_in_role": "1"},
        )
        items_before = (await admin_client.get(f"/api/persons/{pid}/occupations")).json()
        assert len(items_before) == 2

        # Hard-delete the person row directly to fire the FK CASCADE
        await seeded_db.execute(delete(Person).where(Person.id == pid))
        await seeded_db.flush()

        # Occupation rows must be gone
        result = await seeded_db.execute(
            sa_select(PersonOccupation).where(PersonOccupation.person_id == pid)
        )
        assert result.scalars().all() == []


# ── FB-099: HTMX wiki partials ────────────────────────────────────────────────


class TestOccupationWikiHTMX:
    async def test_new_form_renders(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        resp = await admin_client.get(f"/api/wiki/{person['slug']}/occupations/new-form")
        assert resp.status_code == 200
        assert b"wiki-occupation-form" in resp.content

    async def test_post_returns_card_html(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        resp = await admin_client.post(
            f"/api/wiki/{person['slug']}/occupations",
            data={"title": "Postal Worker", "employer": "Post Office", "start_date": "1955"},
        )
        assert resp.status_code == 200
        assert b"Postal Worker" in resp.content
        assert b"wiki-occupation-card" in resp.content

    async def test_post_conflict_shows_warning(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        slug = person["slug"]
        await admin_client.post(
            f"/api/wiki/{slug}/occupations",
            data={"title": "First Current", "currently_in_role": "1"},
        )
        resp = await admin_client.post(
            f"/api/wiki/{slug}/occupations",
            data={"title": "Second Current", "currently_in_role": "1"},
        )
        assert resp.status_code == 200
        assert b"wiki-occupation-card__conflict" in resp.content

    async def test_edit_form_prefills(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        slug = person["slug"]
        pid = person["id"]
        create_resp = await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Lumberjack", "employer": "Forest Co"},
        )
        occ_id = create_resp.json()["id"]
        resp = await admin_client.get(f"/api/wiki/{slug}/occupations/{occ_id}/edit")
        assert resp.status_code == 200
        assert b"Lumberjack" in resp.content
        assert b"Forest Co" in resp.content

    async def test_put_returns_updated_card(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        slug = person["slug"]
        pid = person["id"]
        create_resp = await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Old"},
        )
        occ_id = create_resp.json()["id"]
        resp = await admin_client.put(
            f"/api/wiki/{slug}/occupations/{occ_id}",
            data={"title": "Updated"},
        )
        assert resp.status_code == 200
        assert b"Updated" in resp.content

    async def test_card_endpoint_renders(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        slug = person["slug"]
        pid = person["id"]
        create_resp = await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Mechanic"},
        )
        occ_id = create_resp.json()["id"]
        resp = await admin_client.get(f"/api/wiki/{slug}/occupations/{occ_id}/card")
        assert resp.status_code == 200
        assert b"Mechanic" in resp.content

    async def test_confirm_delete_renders_for_adder(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        slug = person["slug"]
        pid = person["id"]
        create_resp = await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Welder"},
        )
        occ_id = create_resp.json()["id"]
        resp = await admin_client.get(f"/api/wiki/{slug}/occupations/{occ_id}/confirm-delete")
        assert resp.status_code == 200
        assert b"hx-delete" in resp.content

    async def test_confirm_delete_403_for_non_adder_member(
        self, admin_client: AsyncClient, member_client: AsyncClient
    ):
        person = await _create_person(admin_client)
        slug = person["slug"]
        pid = person["id"]
        create_resp = await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Role To Guard"},
        )
        occ_id = create_resp.json()["id"]
        resp = await member_client.get(f"/api/wiki/{slug}/occupations/{occ_id}/confirm-delete")
        assert resp.status_code == 403

    async def test_delete_htmx_removes_record(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        slug = person["slug"]
        pid = person["id"]
        create_resp = await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Deleted Role"},
        )
        occ_id = create_resp.json()["id"]
        resp = await admin_client.delete(f"/api/wiki/{slug}/occupations/{occ_id}")
        assert resp.status_code == 204
        items = (await admin_client.get(f"/api/persons/{pid}/occupations")).json()
        assert items == []

    async def test_wiki_page_includes_occupation_section(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        resp = await admin_client.get(f"/wiki/{person['slug']}")
        assert resp.status_code == 200
        assert b"wiki-occupation-section" in resp.content

    async def test_wiki_page_shows_occupation_card(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        await admin_client.post(
            f"/api/persons/{person['id']}/occupations",
            data={"title": "Blacksmith", "employer": "Village Forge"},
        )
        resp = await admin_client.get(f"/wiki/{person['slug']}")
        assert resp.status_code == 200
        assert b"Blacksmith" in resp.content


# ── FB-100: Tree payload ──────────────────────────────────────────────────────


class TestTreeCurrentOccupation:
    async def test_tree_includes_current_occupation(self, admin_client: AsyncClient):
        """Tree payload for a person with a current occupation includes current_occupation field."""
        person = await _create_person(admin_client)
        await admin_client.post(
            f"/api/persons/{person['id']}/occupations",
            data={"title": "Tree Node Title", "currently_in_role": "1"},
        )
        resp = await admin_client.get("/api/tree")
        assert resp.status_code == 200
        persons = resp.json()["persons"]
        match = next((p for p in persons if p["id"] == person["id"]), None)
        assert match is not None
        assert match["current_occupation"] == "Tree Node Title"

    async def test_tree_current_occupation_null_for_no_occupation(self, admin_client: AsyncClient):
        resp = await admin_client.get("/api/tree")
        assert resp.status_code == 200
        persons = resp.json()["persons"]
        # Persons with no occupation should have null current_occupation
        for p in persons:
            assert "current_occupation" in p

    async def test_tree_uses_current_role_not_past(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        pid = person["id"]
        # Past role only
        await admin_client.post(
            f"/api/persons/{pid}/occupations",
            data={"title": "Old Job", "start_date": "1980", "end_date": "1990"},
        )
        resp = await admin_client.get("/api/tree")
        persons = resp.json()["persons"]
        match = next((p for p in persons if p["id"] == pid), None)
        assert match is not None
        assert match["current_occupation"] is None


# ── Tree preferences ──────────────────────────────────────────────────────────


class TestTreePreferencesOccupation:
    async def test_preferences_include_show_occupation(self, admin_client: AsyncClient):
        resp = await admin_client.get("/api/tree/preferences")
        assert resp.status_code == 200
        body = resp.json()
        assert "show_occupation" in body
        assert body["show_occupation"] is False  # default off

    async def test_save_show_occupation_preference(self, admin_client: AsyncClient):
        resp = await admin_client.put(
            "/api/tree/preferences",
            json={"show_names": True, "show_nicknames": False, "show_birth_dates": False,
                  "show_country_flags": True, "show_photos": True, "show_occupation": True},
        )
        assert resp.status_code == 200
        assert resp.json()["show_occupation"] is True


# ── i18n parity ───────────────────────────────────────────────────────────────


class TestOccupationI18n:
    OCCUPATION_KEYS = [
        "occupation.section_title",
        "occupation.add_occupation",
        "occupation.edit_occupation",
        "occupation.delete_occupation",
        "occupation.title_label",
        "occupation.employer_label",
        "occupation.start_date_label",
        "occupation.end_date_label",
        "occupation.currently_in_role",
        "occupation.save",
        "occupation.cancel",
        "occupation.delete_confirm",
        "occupation.empty",
        "occupation.present",
        "occupation.conflict_warning",
        "tree.show_occupation",
    ]

    @pytest.mark.parametrize("locale", ["en", "es", "it", "ru", "zh"])
    def test_locale_has_all_occupation_keys(self, locale):
        import json, os
        locale_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "locales", f"{locale}.json"
        )
        with open(locale_path) as f:
            data = json.load(f)

        def get_nested(d, key):
            parts = key.split(".", 1)
            if len(parts) == 1:
                return d.get(parts[0])
            section = d.get(parts[0], {})
            return section.get(parts[1]) if isinstance(section, dict) else None

        missing = [k for k in self.OCCUPATION_KEYS if get_nested(data, k) is None]
        assert missing == [], f"Locale '{locale}' missing keys: {missing}"
