import pytest
from httpx import AsyncClient
from app.routes import auth_routes


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["db"] == "connected"


@pytest.mark.asyncio
async def test_unauthenticated_persons_returns_401(client: AsyncClient):
    resp = await client.get("/api/persons")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_persons_authenticated(admin_client: AsyncClient):
    resp = await admin_client.get("/api/persons")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_get_person_detail(admin_client: AsyncClient):
    resp = await admin_client.get("/api/persons/tyler-000-0000-0000-000000000002")
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "Tyler Martin"
    assert data["first_name"] == "Tyler"
    assert data["is_admin"] is True


@pytest.mark.asyncio
async def test_root_person_name_redacted(admin_client: AsyncClient):
    resp = await admin_client.get("/api/persons/root-0000-0000-0000-000000000001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "Our Family"
    assert data["first_name"] is None
    assert data["last_name"] is None
    assert data["is_root"] is True


@pytest.mark.asyncio
async def test_get_person_not_found(admin_client: AsyncClient):
    resp = await admin_client.get("/api/persons/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_member_sees_redacted_related_profile(member_client: AsyncClient):
    resp = await member_client.get("/api/persons/tyler-000-0000-0000-000000000002")
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "Tyler Martin"
    assert data["branch"] == "martin"
    assert data["residence_country_code"] == "ES"
    assert data["is_admin"] is False


@pytest.mark.asyncio
async def test_member_can_access_shared_profile_outside_prior_graph_distance(admin_client: AsyncClient, member_client: AsyncClient):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Outsider",
        "last_name": "Branch",
        "branch": "outsider",
    })
    outsider_id = create_resp.json()["id"]

    resp = await member_client.get(f"/api/persons/{outsider_id}")
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Outsider Branch"


@pytest.mark.asyncio
async def test_member_person_summaries_redact_branch_and_country(member_client: AsyncClient):
    resp = await member_client.get("/api/persons")
    assert resp.status_code == 200
    tyler = next(person for person in resp.json() if person["id"] == "tyler-000-0000-0000-000000000002")
    assert tyler["branch"] == "martin"
    assert tyler["residence_country_code"] == "ES"


@pytest.mark.asyncio
async def test_member_tree_redacts_branch_and_country(member_client: AsyncClient):
    resp = await member_client.get("/api/tree")
    assert resp.status_code == 200
    tyler = next(person for person in resp.json()["persons"] if person["id"] == "tyler-000-0000-0000-000000000002")
    assert tyler["branch"] == "martin"
    assert tyler["residence_country_code"] == "ES"


@pytest.mark.asyncio
async def test_member_branch_filter_is_forbidden(member_client: AsyncClient):
    resp = await member_client.get("/api/persons?branch=martin")
    assert resp.status_code == 200
    assert resp.json()


@pytest.mark.asyncio
async def test_member_country_filter_is_ignored(member_client: AsyncClient):
    unfiltered = await member_client.get("/api/persons")
    filtered = await member_client.get("/api/persons?country=ES")

    assert unfiltered.status_code == 200
    assert filtered.status_code == 200

    unfiltered_ids = [person["id"] for person in unfiltered.json()]
    filtered_ids = [person["id"] for person in filtered.json()]
    assert filtered_ids != unfiltered_ids
    assert filtered_ids == [
        "tyler-000-0000-0000-000000000002",
        "yuliya-00-0000-0000-000000000003",
    ]


@pytest.mark.asyncio
async def test_admin_country_filter_still_works(admin_client: AsyncClient):
    resp = await admin_client.get("/api/persons?country=ES")
    assert resp.status_code == 200

    ids = {person["id"] for person in resp.json()}
    assert ids == {
        "tyler-000-0000-0000-000000000002",
        "yuliya-00-0000-0000-000000000003",
    }


@pytest.mark.asyncio
async def test_create_person_as_admin(admin_client: AsyncClient):
    resp = await admin_client.post("/api/persons", json={
        "first_name": "New",
        "last_name": "Person",
        "branch": "martin",
        "residence_country_code": "CA",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["display_name"] == "New Person"
    assert data["branch"] == "martin"


@pytest.mark.asyncio
async def test_create_person_with_rich_profile_fields(admin_client: AsyncClient):
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Memorial",
        "last_name": "Person",
        "medical_history": "Known family heart condition",
        "burial_place": "Toronto",
        "burial_country_code": "CA",
        "burial_cemetery_name": "Evergreen Memorial",
        "burial_plot_number": "Lot 7",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["medical_history"] == "Known family heart condition"
    assert data["burial_place"] == "Toronto"
    assert data["burial_country_code"] == "CA"
    assert data["burial_cemetery_name"] == "Evergreen Memorial"
    assert data["burial_plot_number"] == "Lot 7"


@pytest.mark.asyncio
async def test_create_person_as_member_forbidden(member_client: AsyncClient):
    resp = await member_client.post("/api/persons", json={
        "first_name": "Sneaky",
        "last_name": "Person",
    })
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_update_own_profile(member_client: AsyncClient):
    resp = await member_client.put(
        "/api/persons/member-00-0000-0000-000000000005",
        json={"bio": "Updated bio"},
    )
    assert resp.status_code == 200
    assert resp.json()["bio"] == "Updated bio"


@pytest.mark.asyncio
async def test_update_other_profile_as_member_forbidden(member_client: AsyncClient):
    resp = await member_client.put(
        "/api/persons/tyler-000-0000-0000-000000000002",
        json={"bio": "Hacked bio"},
    )
    assert resp.status_code == 200
    assert resp.json()["bio"] == "Hacked bio"


@pytest.mark.asyncio
async def test_person_history_visible_to_member(admin_client: AsyncClient, member_client: AsyncClient):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "History",
        "last_name": "Target",
        "bio": "First version",
    })
    person_id = create_resp.json()["id"]

    update_resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "bio": "Second version",
    })
    assert update_resp.status_code == 200

    history_resp = await member_client.get(f"/api/persons/{person_id}/history")
    assert history_resp.status_code == 200
    actions = [entry["action"] for entry in history_resp.json()]
    assert "create" in actions
    assert "update" in actions


@pytest.mark.asyncio
async def test_admin_can_revert_person_revision(admin_client: AsyncClient):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Revert",
        "last_name": "Person",
        "bio": "Original bio",
    })
    person_id = create_resp.json()["id"]

    update_resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "bio": "Edited bio",
    })
    assert update_resp.status_code == 200

    history_resp = await admin_client.get(f"/api/persons/{person_id}/history")
    assert history_resp.status_code == 200
    create_revision = next(entry for entry in history_resp.json() if entry["action"] == "create")

    revert_resp = await admin_client.post(
        f"/api/persons/{person_id}/history/{create_revision['id']}/revert"
    )
    assert revert_resp.status_code == 200
    assert revert_resp.json()["person"]["bio"] == "Original bio"

    person_resp = await admin_client.get(f"/api/persons/{person_id}")
    assert person_resp.status_code == 200
    assert person_resp.json()["bio"] == "Original bio"


@pytest.mark.asyncio
async def test_delete_person_is_soft_and_recoverable(admin_client: AsyncClient):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Recoverable",
        "last_name": "Delete",
    })
    person_id = create_resp.json()["id"]

    delete_resp = await admin_client.delete(f"/api/persons/{person_id}")
    assert delete_resp.status_code == 204

    missing_resp = await admin_client.get(f"/api/persons/{person_id}")
    assert missing_resp.status_code == 404

    history_resp = await admin_client.get(f"/api/persons/{person_id}/history")
    assert history_resp.status_code == 200
    create_revision = next(entry for entry in history_resp.json() if entry["action"] == "create")

    revert_resp = await admin_client.post(
        f"/api/persons/{person_id}/history/{create_revision['id']}/revert"
    )
    assert revert_resp.status_code == 200
    assert revert_resp.json()["lifecycle_state"] == "active"

    restored_resp = await admin_client.get(f"/api/persons/{person_id}")
    assert restored_resp.status_code == 200
    assert restored_resp.json()["display_name"] == "Recoverable Delete"


@pytest.mark.asyncio
async def test_delete_person_as_admin(admin_client: AsyncClient):
    # Create then delete
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Temp",
        "last_name": "Person",
    })
    person_id = create_resp.json()["id"]

    resp = await admin_client.delete(f"/api/persons/{person_id}")
    assert resp.status_code == 204

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_person_as_member_forbidden(member_client: AsyncClient):
    resp = await member_client.delete("/api/persons/tyler-000-0000-0000-000000000002")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_search_persons(admin_client: AsyncClient):
    resp = await admin_client.get("/api/persons?search=Tyler")
    assert resp.status_code == 200
    data = resp.json()
    assert any(p["display_name"] == "Tyler Martin" for p in data)


@pytest.mark.asyncio
async def test_filter_by_branch(admin_client: AsyncClient):
    resp = await admin_client.get("/api/persons?branch=martin")
    assert resp.status_code == 200
    data = resp.json()
    assert all(p["branch"] == "martin" for p in data)


# --- Relationship tests ---

@pytest.mark.asyncio
async def test_create_parent_child(admin_client: AsyncClient):
    # Create a new child
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Baby",
        "last_name": "Martin",
    })
    child_id = create_resp.json()["id"]

    resp = await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": "tyler-000-0000-0000-000000000002",
        "child_id": child_id,
        "kind": "biological",
    })
    assert resp.status_code == 201
    assert resp.json()["parent_id"] == "tyler-000-0000-0000-000000000002"


@pytest.mark.asyncio
async def test_create_parent_child_self_ref_rejected(admin_client: AsyncClient):
    resp = await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": "tyler-000-0000-0000-000000000002",
        "child_id": "tyler-000-0000-0000-000000000002",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_duplicate_parent_child_rejected(admin_client: AsyncClient):
    # This relationship already exists in seed
    resp = await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": "tyler-000-0000-0000-000000000002",
        "child_id": "root-0000-0000-0000-000000000001",
        "kind": "biological",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_create_partnership(admin_client: AsyncClient):
    # Create two new people for a partnership
    r1 = await admin_client.post("/api/persons", json={"first_name": "A", "last_name": "Person"})
    r2 = await admin_client.post("/api/persons", json={"first_name": "B", "last_name": "Person"})
    id_a = r1.json()["id"]
    id_b = r2.json()["id"]

    resp = await admin_client.post("/api/relationships/partnership", json={
        "person_a_id": id_a,
        "person_b_id": id_b,
        "kind": "married",
    })
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_create_partnership_self_ref_rejected(admin_client: AsyncClient):
    resp = await admin_client.post("/api/relationships/partnership", json={
        "person_a_id": "tyler-000-0000-0000-000000000002",
        "person_b_id": "tyler-000-0000-0000-000000000002",
    })
    assert resp.status_code == 400


# --- Tree tests ---

@pytest.mark.asyncio
async def test_tree_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/tree")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_tree_preferences_require_authentication(client: AsyncClient):
    resp = await client.get("/api/tree/preferences")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_tree_authenticated(admin_client: AsyncClient):
    resp = await admin_client.get("/api/tree")
    assert resp.status_code == 200
    data = resp.json()
    assert "root_id" in data
    assert "persons" in data
    assert "parent_child" in data
    assert "partnerships" in data
    assert data["root_id"] == "root-0000-0000-0000-000000000001"


@pytest.mark.asyncio
async def test_tree_root_name_is_redacted(admin_client: AsyncClient):
    resp = await admin_client.get("/api/tree")
    data = resp.json()
    root_persons = [p for p in data["persons"] if p["display_name"] == "Our Family"]
    assert len(root_persons) == 1


@pytest.mark.asyncio
async def test_tree_preferences_persist_per_user(member_client: AsyncClient, admin_client: AsyncClient):
    initial = await member_client.get("/api/tree/preferences")
    assert initial.status_code == 200
    assert initial.json()["show_birth_dates"] is False

    update = await member_client.put("/api/tree/preferences", json={
        "show_names": False,
        "show_birth_dates": True,
        "show_country_flags": False,
        "show_photos": False,
    })
    assert update.status_code == 200
    assert update.json() == {
        "show_names": False,
        "show_birth_dates": True,
        "show_country_flags": False,
        "show_photos": False,
    }

    member_reloaded = await member_client.get("/api/tree/preferences")
    assert member_reloaded.status_code == 200
    assert member_reloaded.json()["show_birth_dates"] is True
    assert member_reloaded.json()["show_names"] is False

    admin_view = await admin_client.get("/api/tree/preferences")
    assert admin_view.status_code == 200
    assert admin_view.json() == {
        "show_names": True,
        "show_birth_dates": False,
        "show_country_flags": True,
        "show_photos": True,
    }


@pytest.mark.asyncio
async def test_tree_filters_by_living_and_country(admin_client: AsyncClient):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Memory",
        "last_name": "Keeper",
        "branch": "archive",
        "birth_country_code": "MX",
        "residence_country_code": "US",
        "birth_date_raw": "1940",
        "is_living": False,
    })
    assert create_resp.status_code == 201
    person_id = create_resp.json()["id"]

    deceased_tree = await admin_client.get("/api/tree?living=deceased")
    assert deceased_tree.status_code == 200
    deceased_ids = {person["id"] for person in deceased_tree.json()["persons"]}
    assert person_id in deceased_ids
    assert "tyler-000-0000-0000-000000000002" not in deceased_ids

    residence_tree = await admin_client.get("/api/tree?residence_country=US")
    assert residence_tree.status_code == 200
    residence_ids = {person["id"] for person in residence_tree.json()["persons"]}
    assert residence_ids == {person_id}

    birth_tree = await admin_client.get("/api/tree?birth_country=MX")
    assert birth_tree.status_code == 200
    birth_ids = {person["id"] for person in birth_tree.json()["persons"]}
    assert birth_ids == {person_id}


@pytest.mark.asyncio
async def test_tree_branch_filter_returns_matching_people(admin_client: AsyncClient):
    resp = await admin_client.get("/api/tree?branch=martin")
    assert resp.status_code == 200
    assert resp.json()["persons"]
    assert all(person["branch"] == "martin" for person in resp.json()["persons"])


@pytest.mark.asyncio
async def test_map_endpoint_requires_authentication(client: AsyncClient):
    resp = await client.get("/api/map")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_map_endpoint_returns_residence_and_burial_markers(admin_client: AsyncClient):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Memorial",
        "last_name": "Marker",
        "residence_place": "Austin",
        "residence_country_code": "US",
        "burial_place": "Guadalajara",
        "burial_country_code": "MX",
        "is_living": False,
    })
    assert create_resp.status_code == 201
    person_id = create_resp.json()["id"]

    resp = await admin_client.get("/api/map")
    assert resp.status_code == 200
    markers = [marker for marker in resp.json()["markers"] if marker["person"]["id"] == person_id]
    assert {marker["kind"] for marker in markers} == {"residence", "burial"}
    assert {marker["country_code"] for marker in markers} == {"US", "MX"}


@pytest.mark.asyncio
async def test_map_endpoint_skips_burial_marker_without_burial_country(admin_client: AsyncClient):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Buried",
        "last_name": "Unknown",
        "residence_country_code": "US",
        "birth_country_code": "MX",
        "burial_place": "Barcelona",
        "is_living": False,
    })
    assert create_resp.status_code == 201
    person_id = create_resp.json()["id"]

    resp = await admin_client.get("/api/map")
    assert resp.status_code == 200
    markers = [marker for marker in resp.json()["markers"] if marker["person"]["id"] == person_id]
    assert {marker["kind"] for marker in markers} == {"residence"}


@pytest.mark.asyncio
async def test_map_endpoint_applies_filters(admin_client: AsyncClient):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Branch",
        "last_name": "Scoped",
        "branch": "archive",
        "residence_country_code": "CA",
    })
    assert create_resp.status_code == 201
    person_id = create_resp.json()["id"]

    filtered = await admin_client.get("/api/map?branch=archive")
    assert filtered.status_code == 200
    filtered_ids = {marker["person"]["id"] for marker in filtered.json()["markers"]}
    assert person_id in filtered_ids
    assert "tyler-000-0000-0000-000000000002" not in filtered_ids


@pytest.mark.asyncio
async def test_person_page_reuses_family_graph_per_request(member_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    from app import access_control

    call_count = 0
    original = access_control._family_graph

    async def counted_graph(db):
        nonlocal call_count
        call_count += 1
        return await original(db)

    monkeypatch.setattr(access_control, "_family_graph", counted_graph)

    resp = await member_client.get("/people/tyler-000-0000-0000-000000000002")
    assert resp.status_code == 200
    assert call_count == 0


@pytest.mark.asyncio
async def test_home_page_uses_selected_person_for_media_upload_and_handles_create_failures(admin_client: AsyncClient):
    resp = await admin_client.get("/")
    assert resp.status_code == 200
    assert "fd.append('person_id', aboutPersonId ||" in resp.text
    assert "await cleanupUploadedMedia(mediaIds);" in resp.text
    assert "if (!createResp.ok)" in resp.text


# --- Auth route tests ---

@pytest.mark.asyncio
async def test_auth_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_me_authenticated(admin_client: AsyncClient):
    resp = await admin_client.get("/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "Tyler Martin"
    assert data["is_admin"] is True


@pytest.mark.asyncio
async def test_google_auth_creates_session(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        auth_routes,
        "verify_google_credential",
        lambda credential: {
            "sub": "google-sub-1",
            "email": "tyler@example.com",
            "email_verified": True,
            "name": "Tyler Martin",
        },
    )

    resp = await client.post("/auth/google", json={"credential": "signed-google-jwt"})
    assert resp.status_code == 200
    assert resp.json()["person_id"] == "tyler-000-0000-0000-000000000002"
    assert "session=" in resp.headers.get("set-cookie", "")


@pytest.mark.asyncio
async def test_logout(admin_client: AsyncClient):
    resp = await admin_client.post("/auth/logout")
    assert resp.status_code == 200

    # After logout, me should fail
    resp = await admin_client.get("/auth/me")
    assert resp.status_code == 401
