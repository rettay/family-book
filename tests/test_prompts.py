from sqlalchemy import select

import app.routes.prompts as prompts_routes
from app.models.notifications import NotificationPreference, PushChannel, PushFrequency
from app.models.person import Person, PersonRole, Visibility
from app.models.prompts import PromptCampaign, PromptCampaignRecipient
from app.models.story import Story


async def test_staff_can_create_prompt_campaign(admin_client, seeded_db):
    recipient = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    recipient.contact_email = "jane@example.com"
    await seeded_db.commit()

    resp = await admin_client.post(
        "/prompts/campaigns",
        data={
            "title": "Ask grandma about summer holidays",
            "prompt_body": "What summer memory should we save?",
            "recipient_ids": [recipient.id],
            "response_kind": "story",
        },
        follow_redirects=False,
    )

    assert resp.status_code == 303
    campaign = (await seeded_db.execute(select(PromptCampaign))).scalar_one()
    recipient_row = (await seeded_db.execute(select(PromptCampaignRecipient))).scalar_one()
    assert campaign.title == "Ask grandma about summer holidays"
    assert recipient_row.recipient_person_id == recipient.id


async def test_member_can_respond_to_prompt_with_story(member_client, seeded_db):
    campaign = PromptCampaign(
        created_by="tyler-000-0000-0000-000000000002",
        title="Tell us about the old neighborhood",
        prompt_body="What do you remember most?",
        response_kind="story",
    )
    seeded_db.add(campaign)
    await seeded_db.flush()
    recipient = PromptCampaignRecipient(
        campaign_id=campaign.id,
        recipient_person_id="member-00-0000-0000-000000000005",
    )
    seeded_db.add(recipient)
    await seeded_db.commit()

    resp = await member_client.post(
        f"/prompts/recipients/{recipient.id}/respond",
        data={
            "title": "Old neighborhood story",
            "body": "We played outside until the streetlights came on.",
        },
        follow_redirects=False,
    )

    assert resp.status_code == 303
    await seeded_db.refresh(recipient)
    story = await seeded_db.get(Story, recipient.response_story_id)
    assert recipient.status == "responded"
    assert story is not None
    assert "streetlights" in story.body
    assert story.source == "Prompt response: Tell us about the old neighborhood"


async def test_prompt_campaign_rejects_hidden_subject_for_ineligible_recipient(admin_client, seeded_db):
    hidden = Person(
        id="hidden-00-0000-0000-000000000071",
        first_name="Hidden",
        last_name="Relative",
        role=PersonRole.member.value,
        visibility=Visibility.hidden.value,
    )
    seeded_db.add(hidden)
    await seeded_db.commit()

    resp = await admin_client.post(
        "/prompts/campaigns",
        data={
            "title": "Tell us about Hidden",
            "prompt_body": "Share what you remember.",
            "recipient_ids": ["member-00-0000-0000-000000000005"],
            "response_kind": "story",
            "target_person_id": hidden.id,
        },
        follow_redirects=False,
    )

    assert resp.status_code == 403
    assert resp.json()["detail"] == "Recipient cannot view the selected subject person"


async def test_hidden_prompt_target_is_suppressed_and_cannot_be_answered(member_client, seeded_db):
    hidden = Person(
        id="hidden-00-0000-0000-000000000072",
        first_name="Private",
        last_name="Subject",
        role=PersonRole.member.value,
        visibility=Visibility.hidden.value,
    )
    campaign = PromptCampaign(
        created_by="tyler-000-0000-0000-000000000002",
        target_person_id=hidden.id,
        title="Tell us about the private subject",
        prompt_body="Share a memory.",
        response_kind="story",
    )
    seeded_db.add_all([hidden, campaign])
    await seeded_db.flush()
    seeded_db.add(
        PromptCampaignRecipient(
            campaign_id=campaign.id,
            recipient_person_id="member-00-0000-0000-000000000005",
        )
    )
    await seeded_db.commit()

    page = await member_client.get("/prompts")
    assert page.status_code == 200
    assert "For Private Subject" not in page.text

    recipient_row = (
        await seeded_db.execute(
            select(PromptCampaignRecipient).where(
                PromptCampaignRecipient.campaign_id == campaign.id
            )
        )
    ).scalar_one()
    resp = await member_client.post(
        f"/prompts/recipients/{recipient_row.id}/respond",
        data={"title": "Nope", "body": "Should fail"},
        follow_redirects=False,
    )

    assert resp.status_code == 403
    assert resp.json()["detail"] == "Prompt target is not visible"


async def test_weekly_digest_respects_visibility_filtering(admin_client, seeded_db, monkeypatch):
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    member.contact_email = "jane@example.com"
    seeded_db.add(
        NotificationPreference(
            person_id=member.id,
            push_channel=PushChannel.email.value,
            push_email="jane@example.com",
            push_frequency=PushFrequency.weekly_digest.value,
        )
    )
    hidden = Person(
        id="hidden-00-0000-0000-000000000099",
        first_name="Hidden",
        last_name="Relative",
        role=PersonRole.member.value,
        visibility=Visibility.hidden.value,
    )
    seeded_db.add(hidden)
    await seeded_db.flush()
    seeded_db.add_all(
        [
            Story(
                person_id="tyler-000-0000-0000-000000000002",
                title="Visible story",
                body="Visible body",
                author_person_id="tyler-000-0000-0000-000000000002",
            ),
            Story(
                person_id=hidden.id,
                title="Hidden story",
                body="Should not leak",
                author_person_id="tyler-000-0000-0000-000000000002",
            ),
        ]
    )
    await seeded_db.commit()

    sent = {}

    async def fake_send_weekly_digest_email(**kwargs):
        sent["digest"] = kwargs["digest"]
        return type("Result", (), {"status": "sent"})()

    monkeypatch.setattr(prompts_routes, "send_weekly_digest_email", fake_send_weekly_digest_email)

    resp = await admin_client.post("/prompts/digest/send", data={"recipient_id": member.id})

    assert resp.status_code == 200
    assert resp.json()["sent_count"] == 1
    titles = [item["title"] for item in sent["digest"]["stories"]]
    assert "Visible story" in titles
    assert "Hidden story" not in titles


async def test_digest_preferences_can_disable_email(admin_client, seeded_db, monkeypatch):
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    member.contact_email = "jane@example.com"
    seeded_db.add(
        NotificationPreference(
            person_id=member.id,
            push_channel=PushChannel.none.value,
            push_email="jane@example.com",
            push_frequency=PushFrequency.weekly_digest.value,
        )
    )
    await seeded_db.commit()

    called = {"count": 0}

    async def fake_send_weekly_digest_email(**kwargs):
        called["count"] += 1
        return type("Result", (), {"status": "sent"})()

    monkeypatch.setattr(prompts_routes, "send_weekly_digest_email", fake_send_weekly_digest_email)

    resp = await admin_client.post("/prompts/digest/send", data={"recipient_id": member.id})

    assert resp.status_code == 200
    assert resp.json()["sent_count"] == 0
    assert resp.json()["skipped_count"] == 1
    assert called["count"] == 0
