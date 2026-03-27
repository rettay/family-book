import pytest

from app.models.person import Person
from app.services.revision_service import apply_person_snapshot, serialize_person_snapshot


def test_person_snapshot_encrypts_sensitive_fields():
    person = Person(
        first_name="Protected",
        last_name="History",
        medical_history="Sensitive family note",
        contact_email="history@example.com",
        contact_signal="+15551234567",
    )

    snapshot = serialize_person_snapshot(person)

    assert snapshot["medical_history"].startswith("enc::")
    assert snapshot["contact_email"].startswith("enc::")
    assert snapshot["contact_signal"].startswith("enc::")
    assert "Sensitive family note" not in snapshot["medical_history"]


def test_apply_person_snapshot_restores_sensitive_fields():
    source = Person(
        first_name="Source",
        last_name="Person",
        medical_history="Sensitive family note",
        contact_email="history@example.com",
        contact_signal="+15551234567",
    )
    snapshot = serialize_person_snapshot(source)

    target = Person(first_name="Blank", last_name="Person")
    apply_person_snapshot(target, snapshot)

    assert target.medical_history == "Sensitive family note"
    assert target.contact_email == "history@example.com"
    assert target.contact_signal == "+15551234567"


def test_apply_person_snapshot_sanitizes_rich_text():
    """Revert path sanitizes bio/obituary/research_notes (S3-R01)."""
    source = Person(
        first_name="XSS",
        last_name="Revert",
        bio='<p>Safe</p><script>alert("xss")</script>',
        obituary='<em>Rest</em><iframe src="evil"></iframe>',
        research_notes='<strong>Note</strong><img src=x onerror=alert(1)>',
    )
    snapshot = serialize_person_snapshot(source)

    target = Person(first_name="Blank", last_name="Person")
    apply_person_snapshot(target, snapshot)

    assert "<script>" not in target.bio
    assert "<p>Safe</p>" in target.bio
    assert "<iframe" not in target.obituary
    assert "<em>Rest</em>" in target.obituary
    assert "<img" not in target.research_notes
    assert "<strong>Note</strong>" in target.research_notes
