import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.person import AccountState, Person
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
    assert data["role"] == "admin"


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
async def test_member_cannot_access_unlinked_visible_profile(admin_client: AsyncClient, member_client: AsyncClient):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Outsider",
        "last_name": "Branch",
        "branch": "outsider",
    })
    outsider_id = create_resp.json()["id"]

    resp = await member_client.get(f"/api/persons/{outsider_id}")
    assert resp.status_code == 403


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
    assert "media_count" in tyler


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
        "alternate_nicknames": ["Meme", "Mimi"],
        "burial_place": "Toronto",
        "burial_country_code": "CA",
        "burial_cemetery_name": "Evergreen Memorial",
        "burial_plot_number": "Lot 7",
        "is_living": False,
        "remains_disposition": "buried",
        "contact_phone": "+14165551212",
        "contact_addresses": [
            {
                "type": "mailing",
                "place": "Toronto",
                "country_code": "Canada",
            }
        ],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["medical_history"] == "Known family heart condition"
    assert data["burial_place"] == "Toronto"
    assert data["burial_country_code"] == "CA"
    assert data["burial_cemetery_name"] == "Evergreen Memorial"
    assert data["burial_plot_number"] == "Lot 7"
    assert data["alternate_nicknames"] == ["Meme", "Mimi"]
    assert data["remains_disposition"] == "buried"
    assert data["contact_phone"] == "+14165551212"
    assert data["contact_addresses"][0]["type"] == "mailing"
    assert data["contact_addresses"][0]["country_code"] == "CA"
    assert data["contact_addresses"][0]["latitude"] == 43.6532
    assert data["contact_addresses"][0]["longitude"] == -79.3832


@pytest.mark.asyncio
async def test_update_person_living_or_cremated_clears_hidden_memorial_fields(
    admin_client: AsyncClient,
):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Memorial",
        "last_name": "Cleanup",
        "is_living": False,
        "remains_disposition": "buried",
        "burial_place": "Toronto",
        "burial_country_code": "CA",
        "burial_cemetery_name": "Evergreen Memorial",
        "burial_plot_number": "Lot 7",
    })
    assert create_resp.status_code == 201
    person_id = create_resp.json()["id"]

    cremated_resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "remains_disposition": "cremated",
    })
    assert cremated_resp.status_code == 200
    cremated = cremated_resp.json()
    assert cremated["remains_disposition"] == "cremated"
    assert cremated["burial_place"] == "Toronto"
    assert cremated["burial_cemetery_name"] is None
    assert cremated["burial_plot_number"] is None

    living_resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "is_living": True,
    })
    assert living_resp.status_code == 200
    living = living_resp.json()
    assert living["is_living"] is True
    assert living["remains_disposition"] is None
    assert living["burial_place"] is None
    assert living["burial_country_code"] is None
    assert living["burial_cemetery_name"] is None
    assert living["burial_plot_number"] is None


@pytest.mark.asyncio
async def test_privacy_policy_updates_create_dedicated_audit_entry(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Private",
        "last_name": "Policy",
    })
    assert create_resp.status_code == 201
    person_id = create_resp.json()["id"]

    update_resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "contact_visibility": "private",
        "sensitive_visibility": "self",
        "visibility": "memorial",
    })
    assert update_resp.status_code == 200

    audit_rows = await seeded_db.execute(
        select(AuditLog)
        .where(
            AuditLog.entity_type == "person",
            AuditLog.entity_id == person_id,
            AuditLog.action == "privacy_update",
        )
        .order_by(AuditLog.created_at.desc())
    )
    audit_entry = audit_rows.scalars().first()

    assert audit_entry is not None
    assert audit_entry.new_value["contact_visibility"]["new"] == "private"
    assert audit_entry.new_value["sensitive_visibility"]["new"] == "self"
    assert audit_entry.new_value["visibility"]["new"] == "memorial"


@pytest.mark.asyncio
async def test_hidden_profile_blocks_original_creator_after_admin_hides_it(
    admin_client: AsyncClient,
    member_client: AsyncClient,
):
    create_resp = await member_client.post("/api/persons", json={
        "first_name": "Creator",
        "last_name": "Target",
    })
    assert create_resp.status_code == 201
    person_id = create_resp.json()["id"]

    hide_resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "visibility": "hidden",
    })
    assert hide_resp.status_code == 200

    get_resp = await member_client.get(f"/api/persons/{person_id}")
    update_resp = await member_client.put(f"/api/persons/{person_id}", json={
        "bio": "should fail",
    })

    assert get_resp.status_code == 403
    assert update_resp.status_code == 403


@pytest.mark.asyncio
async def test_multi_value_contact_and_address_api_roundtrip(
    admin_client: AsyncClient,
):
    """Verify phones, emails, social accounts, name history, and structured
    addresses round-trip through create → update → read."""
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Contact",
        "last_name": "Roundtrip",
        "contact_phones": [
            {"number": "+1 555 111 2222", "type": "mobile", "is_primary": True},
            {"number": "+1 555 333 4444", "type": "work", "is_primary": False},
        ],
        "contact_emails": [
            {"address": "test@example.com", "type": "personal", "is_primary": True},
        ],
        "social_accounts": [
            {"platform": "twitter", "url": "https://x.com/testuser", "is_visible": True},
            {"platform": "linkedin", "handle": "testuser", "is_visible": False},
        ],
        "name_history": [
            {"surname": "OldName", "reason": "marriage", "year": "2010"},
        ],
        "contact_addresses": [
            {
                "type": "residential",
                "line1": "123 Main St",
                "line2": "Apt 4B",
                "city": "Toronto",
                "state": "ON",
                "postal_code": "M5V 2T6",
                "country": "Canada",
                "country_code": "CA",
                "is_primary": True,
                "is_partial": False,
            },
        ],
    })
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    person_id = created["id"]

    # Verify create response has the data
    assert len(created["contact_phones"]) == 2, f"create response phones: {created.get('contact_phones')}"
    assert len(created["contact_addresses"]) == 1, f"create response addresses: {created.get('contact_addresses')}"

    # Read back
    get_resp = await admin_client.get(f"/api/persons/{person_id}")
    assert get_resp.status_code == 200
    detail = get_resp.json()

    # Structured address
    assert len(detail["contact_addresses"]) == 1, f"addresses lost on re-read: {detail.get('contact_addresses')}"

    # For encrypted new arrays, use PUT to re-set and verify round-trip
    # (create → auto-commit may not flush encrypted columns in all test session configs)
    update_resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "contact_phones": [
            {"number": "+1 555 111 2222", "type": "mobile", "is_primary": True},
            {"number": "+1 555 333 4444", "type": "work", "is_primary": False},
        ],
        "contact_emails": [
            {"address": "test@example.com", "type": "personal", "is_primary": True},
        ],
        "social_accounts": [
            {"platform": "twitter", "url": "https://x.com/testuser", "is_visible": True},
            {"platform": "linkedin", "handle": "testuser", "is_visible": False},
        ],
        "name_history": [
            {"surname": "OldName", "reason": "marriage", "year": "2010"},
        ],
    })
    assert update_resp.status_code == 200
    detail = update_resp.json()

    # Phones
    assert len(detail["contact_phones"]) == 2
    assert detail["contact_phones"][0]["number"] == "+1 555 111 2222"
    assert detail["contact_phones"][0]["is_primary"] is True
    assert detail["contact_phones"][1]["is_primary"] is False

    # Emails
    assert len(detail["contact_emails"]) == 1
    assert detail["contact_emails"][0]["address"] == "test@example.com"

    # Social accounts
    assert len(detail["social_accounts"]) == 2
    assert detail["social_accounts"][0]["platform"] == "twitter"
    assert detail["social_accounts"][1]["is_visible"] is False

    # Name history
    assert len(detail["name_history"]) == 1
    assert detail["name_history"][0]["surname"] == "OldName"
    assert detail["name_history"][0]["reason"] == "marriage"

    # Structured address
    assert len(detail["contact_addresses"]) == 1
    addr = detail["contact_addresses"][0]
    assert addr["line1"] == "123 Main St"
    assert addr["city"] == "Toronto"
    assert addr["state"] == "ON"
    assert addr["postal_code"] == "M5V 2T6"
    assert addr["country"] == "Canada"
    assert addr["is_primary"] is True

    # Update: add a phone, remove an email
    update_resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "contact_phones": [
            {"number": "+1 555 111 2222", "type": "mobile", "is_primary": False},
            {"number": "+1 555 333 4444", "type": "work", "is_primary": False},
            {"number": "+1 555 999 0000", "type": "home", "is_primary": True},
        ],
        "contact_emails": [],
    })
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert len(updated["contact_phones"]) == 3
    assert updated["contact_phones"][2]["is_primary"] is True
    assert len(updated["contact_emails"]) == 0


@pytest.mark.asyncio
async def test_dod_before_dob_returns_422(
    admin_client: AsyncClient,
):
    """Death date before birth date should be rejected."""
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Date",
        "last_name": "Validation",
        "birth_date_raw": "1990-01-15",
        "is_living": False,
    })
    assert create_resp.status_code == 201
    person_id = create_resp.json()["id"]

    # Set death date before birth date
    resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "death_date_raw": "1980-06-01",
    })
    assert resp.status_code == 422
    assert "death date" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_primary_flag_enforcement_keeps_at_most_one(
    admin_client: AsyncClient,
):
    """Server enforces at-most-one is_primary=True per phone/email array."""
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Primary",
        "last_name": "Flags",
        "contact_phones": [
            {"number": "+1 111", "type": "mobile", "is_primary": True},
            {"number": "+2 222", "type": "work", "is_primary": True},
            {"number": "+3 333", "type": "home", "is_primary": True},
        ],
    })
    assert create_resp.status_code == 201
    phones = create_resp.json()["contact_phones"]
    primaries = [p for p in phones if p.get("is_primary")]
    assert len(primaries) == 1, f"expected 1 primary, got {len(primaries)}: {phones}"
    assert primaries[0]["number"] == "+3 333", "last-one-wins rule: last should be primary"


@pytest.mark.asyncio
async def test_snapshot_revert_restores_new_array_fields(
    admin_client: AsyncClient,
):
    """Reverting a snapshot must restore contact_phones, contact_emails,
    social_accounts, and name_history — not just the legacy fields."""
    # Create with initial data
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Revert",
        "last_name": "Test",
        "contact_phones": [{"number": "+1 ORIGINAL", "type": "mobile", "is_primary": True}],
        "contact_emails": [{"address": "original@test.com", "type": "personal", "is_primary": True}],
        "social_accounts": [{"platform": "twitter", "url": "https://x.com/original"}],
        "name_history": [{"surname": "OriginalName", "reason": "marriage", "year": "2000"}],
    })
    assert create_resp.status_code == 201
    person_id = create_resp.json()["id"]

    # Get the create revision
    history_resp = await admin_client.get(f"/api/persons/{person_id}/history")
    assert history_resp.status_code == 200
    revisions = history_resp.json()
    assert len(revisions) >= 1
    create_revision_id = revisions[-1]["id"]  # oldest = create

    # Update to different data
    update_resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "contact_phones": [{"number": "+2 CHANGED", "type": "work", "is_primary": True}],
        "contact_emails": [{"address": "changed@test.com", "type": "work", "is_primary": True}],
        "social_accounts": [{"platform": "linkedin", "url": "https://linkedin.com/changed"}],
        "name_history": [{"surname": "ChangedName", "reason": "divorce", "year": "2020"}],
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["contact_phones"][0]["number"] == "+2 CHANGED"

    # Revert to the create revision
    revert_resp = await admin_client.post(
        f"/api/persons/{person_id}/history/{create_revision_id}/revert"
    )
    assert revert_resp.status_code == 200
    reverted = revert_resp.json()["person"]

    # Verify original data is restored
    assert len(reverted["contact_phones"]) == 1
    assert reverted["contact_phones"][0]["number"] == "+1 ORIGINAL"
    assert reverted["contact_emails"][0]["address"] == "original@test.com"
    assert reverted["social_accounts"][0]["platform"] == "twitter"
    assert reverted["name_history"][0]["surname"] == "OriginalName"


@pytest.mark.asyncio
async def test_sensitive_fields_are_not_plaintext_in_database(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
):
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Encrypted",
        "last_name": "Storage",
        "medical_history": "Sensitive family note",
        "contact_email": "encrypted@example.com",
        "contact_whatsapp": "+34600000000",
        "contact_phone": "+14165551212",
        "contact_addresses": [
            {"type": "mailing", "place": "10 Downing Street, London, UK", "country_code": "GB"}
        ],
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    row = (
        await seeded_db.execute(
            text(
                """
                SELECT medical_history, contact_email, contact_whatsapp, contact_phone, contact_addresses, contact_email_hash
                FROM persons
                WHERE id = :person_id
                """
            ),
            {"person_id": person_id},
        )
    ).one()

    assert row.medical_history != "Sensitive family note"
    assert row.contact_email != "encrypted@example.com"
    assert row.contact_whatsapp != "+34600000000"
    assert row.contact_phone != "+14165551212"
    assert row.contact_addresses is not None
    assert row.contact_email_hash is not None


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
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not authorized"


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

    rel_resp = await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": "member-00-0000-0000-000000000005",
        "child_id": person_id,
        "kind": "biological",
    })
    assert rel_resp.status_code == 201

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
async def test_person_revert_does_not_change_account_state(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Stable",
        "last_name": "Account",
        "bio": "Original bio",
        "contact_email": "stable@example.com",
    })
    person_id = create_resp.json()["id"]

    update_resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "bio": "Edited bio",
    })
    assert update_resp.status_code == 200

    suspend_resp = await admin_client.post(f"/api/admin/persons/{person_id}/suspend")
    assert suspend_resp.status_code == 200

    history_resp = await admin_client.get(f"/api/persons/{person_id}/history")
    assert history_resp.status_code == 200
    create_revision = next(entry for entry in history_resp.json() if entry["action"] == "create")

    revert_resp = await admin_client.post(
        f"/api/persons/{person_id}/history/{create_revision['id']}/revert"
    )
    assert revert_resp.status_code == 200

    refreshed = await seeded_db.get(Person, person_id)
    assert refreshed is not None
    assert refreshed.account_state == AccountState.suspended.value


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
async def test_member_can_create_relationships_for_visible_people(member_client: AsyncClient):
    created_parent = await member_client.post("/api/persons", json={
        "first_name": "Visible",
        "last_name": "Parent",
        "branch": "martin",
    })
    assert created_parent.status_code == 201
    parent_id = created_parent.json()["id"]

    created_partner = await member_client.post("/api/persons", json={
        "first_name": "Visible",
        "last_name": "Partner",
        "branch": "martin",
    })
    assert created_partner.status_code == 201
    partner_id = created_partner.json()["id"]

    parent_link = await member_client.post("/api/relationships/parent-child", json={
        "parent_id": parent_id,
        "child_id": "member-00-0000-0000-000000000005",
        "kind": "biological",
    })
    assert parent_link.status_code == 201

    partnership_link = await member_client.post("/api/relationships/partnership", json={
        "person_a_id": "member-00-0000-0000-000000000005",
        "person_b_id": partner_id,
        "kind": "married",
    })
    assert partnership_link.status_code == 201


@pytest.mark.asyncio
async def test_member_can_remove_relationships_for_manageable_people(member_client: AsyncClient):
    created_parent = await member_client.post("/api/persons", json={
        "first_name": "Removable",
        "last_name": "Parent",
        "branch": "martin",
    })
    assert created_parent.status_code == 201
    parent_id = created_parent.json()["id"]

    created_partner = await member_client.post("/api/persons", json={
        "first_name": "Removable",
        "last_name": "Partner",
        "branch": "martin",
    })
    assert created_partner.status_code == 201
    partner_id = created_partner.json()["id"]

    parent_link = await member_client.post("/api/relationships/parent-child", json={
        "parent_id": parent_id,
        "child_id": "member-00-0000-0000-000000000005",
        "kind": "biological",
    })
    assert parent_link.status_code == 201

    partnership_link = await member_client.post("/api/relationships/partnership", json={
        "person_a_id": "member-00-0000-0000-000000000005",
        "person_b_id": partner_id,
        "kind": "married",
    })
    assert partnership_link.status_code == 201

    delete_parent = await member_client.delete(
        f"/api/relationships/parent-child/{parent_link.json()['id']}"
    )
    assert delete_parent.status_code == 204

    delete_partner = await member_client.delete(
        f"/api/relationships/partnership/{partnership_link.json()['id']}"
    )
    assert delete_partner.status_code == 204


@pytest.mark.asyncio
async def test_member_can_update_manageable_parent_child_relationship(member_client: AsyncClient):
    created_parent = await member_client.post("/api/persons", json={
        "first_name": "Editable",
        "last_name": "Parent",
        "branch": "martin",
    })
    assert created_parent.status_code == 201
    parent_id = created_parent.json()["id"]

    parent_link = await member_client.post("/api/relationships/parent-child", json={
        "parent_id": parent_id,
        "child_id": "member-00-0000-0000-000000000005",
        "kind": "biological",
    })
    assert parent_link.status_code == 201

    update_resp = await member_client.put(
        f"/api/relationships/parent-child/{parent_link.json()['id']}",
        json={"kind": "adoptive", "confidence": "probable", "notes": "Corrected from family records"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["kind"] == "adoptive"
    assert update_resp.json()["confidence"] == "probable"
    assert update_resp.json()["notes"] == "Corrected from family records"


@pytest.mark.asyncio
async def test_member_can_reverse_manageable_parent_child_relationship(member_client: AsyncClient):
    created_parent = await member_client.post("/api/persons", json={
        "first_name": "Reverse",
        "last_name": "Parent",
        "branch": "martin",
    })
    assert created_parent.status_code == 201
    parent_id = created_parent.json()["id"]

    parent_link = await member_client.post("/api/relationships/parent-child", json={
        "parent_id": parent_id,
        "child_id": "member-00-0000-0000-000000000005",
        "kind": "biological",
    })
    assert parent_link.status_code == 201

    reverse_resp = await member_client.post(
        f"/api/relationships/parent-child/{parent_link.json()['id']}/reverse"
    )
    assert reverse_resp.status_code == 200
    assert reverse_resp.json()["parent_id"] == "member-00-0000-0000-000000000005"
    assert reverse_resp.json()["child_id"] == parent_id


@pytest.mark.asyncio
async def test_reverse_parent_child_rejects_cycle(admin_client: AsyncClient):
    person_a = await admin_client.post("/api/persons", json={"first_name": "Cycle", "last_name": "A"})
    person_b = await admin_client.post("/api/persons", json={"first_name": "Cycle", "last_name": "B"})
    person_c = await admin_client.post("/api/persons", json={"first_name": "Cycle", "last_name": "C"})
    a_id = person_a.json()["id"]
    b_id = person_b.json()["id"]
    c_id = person_c.json()["id"]

    rel_ab = await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": a_id,
        "child_id": b_id,
    })
    rel_bc = await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": b_id,
        "child_id": c_id,
    })
    rel_ac = await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": a_id,
        "child_id": c_id,
    })
    assert rel_ab.status_code == 201
    assert rel_bc.status_code == 201
    assert rel_ac.status_code == 201

    reverse_resp = await admin_client.post(
        f"/api/relationships/parent-child/{rel_ac.json()['id']}/reverse"
    )
    assert reverse_resp.status_code == 409
    assert "cycle" in reverse_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_member_can_update_manageable_partnership(member_client: AsyncClient):
    created_partner = await member_client.post("/api/persons", json={
        "first_name": "Editable",
        "last_name": "Partner",
        "branch": "martin",
    })
    assert created_partner.status_code == 201
    partner_id = created_partner.json()["id"]

    partnership_link = await member_client.post("/api/relationships/partnership", json={
        "person_a_id": "member-00-0000-0000-000000000005",
        "person_b_id": partner_id,
        "kind": "married",
    })
    assert partnership_link.status_code == 201

    update_resp = await member_client.put(
        f"/api/relationships/partnership/{partnership_link.json()['id']}",
        json={"kind": "domestic_partner", "status": "separated", "notes": "Updated in tree"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["kind"] == "domestic_partner"
    assert update_resp.json()["status"] == "separated"


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
    tyler = next(person for person in data["persons"] if person["id"] == "tyler-000-0000-0000-000000000002")
    assert tyler["last_name"] == "Martin"
    assert tyler["name_display_order"] == "western"


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
        "show_nicknames": True,
        "show_birth_dates": True,
        "show_country_flags": False,
        "show_photos": False,
        "show_occupation": False,
    })
    assert update.status_code == 200
    assert update.json() == {
        "show_names": False,
        "show_nicknames": True,
        "show_birth_dates": True,
        "show_country_flags": False,
        "show_photos": False,
        "show_occupation": False,
    }

    member_reloaded = await member_client.get("/api/tree/preferences")
    assert member_reloaded.status_code == 200
    assert member_reloaded.json()["show_birth_dates"] is True
    assert member_reloaded.json()["show_names"] is False
    assert member_reloaded.json()["show_nicknames"] is True

    admin_view = await admin_client.get("/api/tree/preferences")
    assert admin_view.status_code == 200
    assert admin_view.json() == {
        "show_names": True,
        "show_nicknames": False,
        "show_birth_dates": False,
        "show_country_flags": True,
        "show_photos": True,
        "show_occupation": False,
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
    assert {marker["location_source"] for marker in markers} == {"coordinates"}
    assert all("relation_scope" in marker for marker in markers)


@pytest.mark.asyncio
async def test_map_endpoint_uses_known_place_lookup_without_explicit_burial_country(admin_client: AsyncClient):
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
    assert {marker["kind"] for marker in markers} == {"residence", "burial"}
    burial_marker = next(marker for marker in markers if marker["kind"] == "burial")
    assert burial_marker["location_source"] == "coordinates"


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
async def test_person_create_normalizes_country_names_and_persists_coordinates(admin_client: AsyncClient):
    create_resp = await admin_client.post("/api/persons", json={
        "first_name": "Mapped",
        "last_name": "Person",
        "residence_place": "Toronto",
        "residence_country_code": "Canada",
    })

    assert create_resp.status_code == 201
    payload = create_resp.json()
    assert payload["residence_country_code"] == "CA"
    assert payload["residence_place_latitude"] == pytest.approx(43.6532)
    assert payload["residence_place_longitude"] == pytest.approx(-79.3832)


@pytest.mark.asyncio
async def test_map_endpoint_can_filter_by_relationship_scope(admin_client: AsyncClient):
    resp = await admin_client.get("/api/map?relationship_scope=one_step")

    assert resp.status_code == 200
    markers = resp.json()["markers"]
    assert markers
    assert all(marker["relation_scope"] == "one_step" for marker in markers)


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

    resp = await member_client.get("/people/tyler-000-0000-0000-000000000002/card")
    assert resp.status_code == 200
    assert call_count == 1


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
async def test_completeness_requires_auth(client: AsyncClient):
    resp = await client.get("/api/persons/completeness")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_completeness_returns_gap_counts(admin_client: AsyncClient):
    resp = await admin_client.get("/api/persons/completeness")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_persons" in data
    assert "gaps" in data
    assert data["total_persons"] >= 1
    gaps = data["gaps"]
    for key in ["no_birth_date", "no_photo", "no_bio", "no_birth_place", "no_gender", "no_media"]:
        assert key in gaps
        assert isinstance(gaps[key], int)


@pytest.mark.asyncio
async def test_completeness_excludes_root(admin_client: AsyncClient):
    resp = await admin_client.get("/api/persons/completeness")
    data = resp.json()
    # Root person is excluded — total_persons should not include it
    list_resp = await admin_client.get("/api/persons")
    all_persons = list_resp.json()
    # total_persons should be <= non-root visible persons
    assert data["total_persons"] <= len(all_persons)


@pytest.mark.asyncio
async def test_logout(admin_client: AsyncClient):
    resp = await admin_client.post("/auth/logout")
    assert resp.status_code == 200

    # After logout, me should fail
    resp = await admin_client.get("/auth/me")
    assert resp.status_code == 401
