from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# --- Life story entry sub-models ---

class EducationEntry(BaseModel):
    institution: str | None = Field(None, max_length=300)
    degree: str | None = Field(None, max_length=200)
    field_of_study: str | None = Field(None, max_length=200)
    year_start: str | None = Field(None, max_length=10)
    year_end: str | None = Field(None, max_length=10)
    notes: str | None = Field(None, max_length=1000)


class CareerEntry(BaseModel):
    employer: str | None = Field(None, max_length=300)
    title: str | None = Field(None, max_length=200)
    year_start: str | None = Field(None, max_length=10)
    year_end: str | None = Field(None, max_length=10)
    location: str | None = Field(None, max_length=300)
    notes: str | None = Field(None, max_length=1000)


class OrganizationEntry(BaseModel):
    name: str | None = Field(None, max_length=300)
    role: str | None = Field(None, max_length=200)
    year_joined: str | None = Field(None, max_length=10)
    year_left: str | None = Field(None, max_length=10)
    notes: str | None = Field(None, max_length=1000)


class AdmixtureEntry(BaseModel):
    ethnicity: str | None = Field(None, max_length=200)
    percentage: str | None = Field(None, max_length=10)
    source: str | None = Field(None, max_length=200)


class MedicalConditionEntry(BaseModel):
    condition: str | None = Field(None, max_length=300)
    onset_age: str | None = Field(None, max_length=20)
    status: str | None = Field(None, max_length=20)
    severity: str | None = Field(None, max_length=50)
    treatment: str | None = Field(None, max_length=500)
    is_inherited: bool | None = None
    hereditary_line: str | None = Field(None, max_length=100)
    notes: str | None = Field(None, max_length=1000)


class AddressEntry(BaseModel):
    type: str = Field(min_length=1, max_length=40)
    label: str | None = Field(None, max_length=100)
    place: str | None = Field(None, max_length=300)  # legacy/display string
    line1: str | None = Field(None, max_length=300)
    line2: str | None = Field(None, max_length=300)
    city: str | None = Field(None, max_length=200)
    state: str | None = Field(None, max_length=200)
    postal_code: str | None = Field(None, max_length=20)
    country: str | None = Field(None, max_length=100)
    country_code: str | None = Field(None, max_length=80)
    place_id: str | None = Field(None, max_length=300)
    latitude: float | None = None
    longitude: float | None = None
    is_primary: bool = False
    is_partial: bool = False


class PhoneEntry(BaseModel):
    number: str = Field(min_length=1, max_length=50)
    type: str | None = Field(None, max_length=20)
    label: str | None = Field(None, max_length=100)
    is_primary: bool = False


class EmailEntry(BaseModel):
    address: str = Field(min_length=1, max_length=320)
    type: str | None = Field(None, max_length=20)
    is_primary: bool = False


class SocialAccountEntry(BaseModel):
    platform: str = Field(min_length=1, max_length=50)
    handle: str | None = Field(None, max_length=300)
    url: str | None = Field(None, max_length=1000)
    is_visible: bool = True


class NameHistoryEntry(BaseModel):
    surname: str | None = Field(None, max_length=200)
    reason: str | None = Field(None, max_length=100)
    year: str | None = Field(None, max_length=10)
    notes: str | None = Field(None, max_length=500)


class PlaceHistoryEntry(BaseModel):
    place: str | None = Field(None, max_length=300)
    country_code: str | None = Field(None, max_length=80)
    from_year: str | None = Field(None, max_length=10)
    to_year: str | None = Field(None, max_length=10)
    description: str | None = Field(None, max_length=1000)
    place_latitude: float | None = None
    place_longitude: float | None = None
    place_id: str | None = Field(None, max_length=300)
    is_current: bool | None = None


# --- Person ---

class PersonCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=200)
    last_name: str = Field(min_length=1, max_length=200)
    patronymic: str | None = Field(None, max_length=200)
    birth_last_name: str | None = Field(None, max_length=200)
    nickname: str | None = Field(None, max_length=100)
    alternate_nicknames: list[str] = []
    name_display_order: str = "western"
    gender: str | None = None
    birth_date_raw: str | None = Field(None, max_length=50)
    birth_date: str | None = Field(None, max_length=10)
    birth_date_precision: str | None = None
    death_date_raw: str | None = Field(None, max_length=50)
    death_date: str | None = Field(None, max_length=10)
    death_date_precision: str | None = None
    is_living: bool = True
    birth_place: str | None = Field(None, max_length=300)
    birth_country_code: str | None = Field(None, max_length=80)
    birth_place_latitude: float | None = None
    birth_place_longitude: float | None = None
    residence_place: str | None = Field(None, max_length=300)
    residence_country_code: str | None = Field(None, max_length=80)
    residence_place_latitude: float | None = None
    residence_place_longitude: float | None = None
    burial_place: str | None = Field(None, max_length=300)
    burial_country_code: str | None = Field(None, max_length=80)
    burial_place_latitude: float | None = None
    burial_place_longitude: float | None = None
    burial_cemetery_name: str | None = Field(None, max_length=300)
    burial_plot_number: str | None = Field(None, max_length=100)
    remains_disposition: str | None = Field(None, max_length=20)
    languages: list[str] = []
    bio: str | None = Field(None, max_length=2000)
    research_notes: str | None = Field(None, max_length=5000)
    medical_history: str | None = None
    obituary: str | None = Field(None, max_length=10000)
    obituary_source: str | None = Field(None, max_length=500)
    obituary_url: str | None = Field(None, max_length=1000)
    education: list[EducationEntry] = []
    career: list[CareerEntry] = []
    organizations: list[OrganizationEntry] = []
    height: str | None = Field(None, max_length=50)
    weight: str | None = Field(None, max_length=50)
    eye_color: str | None = Field(None, max_length=50)
    hair_color: str | None = Field(None, max_length=50)
    blood_type: str | None = Field(None, max_length=10)
    maternal_haplogroup: str | None = Field(None, max_length=100)
    paternal_haplogroup: str | None = Field(None, max_length=100)
    dna_test_provider: str | None = Field(None, max_length=200)
    admixture: list[AdmixtureEntry] = []
    medical_conditions: list[MedicalConditionEntry] = []
    source_detail: str | None = Field(None, max_length=500)
    confidence: str | None = Field(None, max_length=20)
    contact_whatsapp: str | None = None
    contact_telegram: str | None = None
    contact_signal: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    contact_addresses: list[AddressEntry] = []
    contact_phones: list[PhoneEntry] = []
    contact_emails: list[EmailEntry] = []
    social_accounts: list[SocialAccountEntry] = []
    name_history: list[NameHistoryEntry] = []
    place_history: list[PlaceHistoryEntry] = []
    social_instagram: str | None = Field(None, max_length=300)
    social_facebook: str | None = Field(None, max_length=300)
    social_twitter: str | None = Field(None, max_length=300)
    social_linkedin: str | None = Field(None, max_length=300)
    social_tiktok: str | None = Field(None, max_length=300)
    social_youtube: str | None = Field(None, max_length=300)
    branch: str | None = Field(None, max_length=100)
    source: str = "manual"

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v):
        if v is not None and v not in ("confirmed", "probable", "uncertain", "unknown"):
            raise ValueError("confidence must be one of: confirmed, probable, uncertain, unknown")
        return v

    @field_validator("remains_disposition")
    @classmethod
    def validate_remains_disposition(cls, v):
        if v is not None and v not in ("buried", "cremated", "unknown"):
            raise ValueError("remains_disposition must be one of: buried, cremated, unknown")
        return v

    @field_validator("obituary_url")
    @classmethod
    def validate_obituary_url(cls, v):
        if v is not None and v.strip() and not v.strip().startswith(("http://", "https://")):
            raise ValueError("obituary_url must start with http:// or https://")
        return v


class PersonUpdate(BaseModel):
    first_name: str | None = Field(None, max_length=200)
    last_name: str | None = Field(None, max_length=200)
    patronymic: str | None = Field(None, max_length=200)
    birth_last_name: str | None = Field(None, max_length=200)
    nickname: str | None = Field(None, max_length=100)
    alternate_nicknames: list[str] | None = None
    name_display_order: str | None = None
    gender: str | None = None
    birth_date_raw: str | None = Field(None, max_length=50)
    birth_date: str | None = Field(None, max_length=10)
    birth_date_precision: str | None = None
    death_date_raw: str | None = Field(None, max_length=50)
    death_date: str | None = Field(None, max_length=10)
    death_date_precision: str | None = None
    is_living: bool | None = None
    birth_place: str | None = Field(None, max_length=300)
    birth_country_code: str | None = Field(None, max_length=80)
    birth_place_latitude: float | None = None
    birth_place_longitude: float | None = None
    residence_place: str | None = Field(None, max_length=300)
    residence_country_code: str | None = Field(None, max_length=80)
    residence_place_latitude: float | None = None
    residence_place_longitude: float | None = None
    burial_place: str | None = Field(None, max_length=300)
    burial_country_code: str | None = Field(None, max_length=80)
    burial_place_latitude: float | None = None
    burial_place_longitude: float | None = None
    burial_cemetery_name: str | None = Field(None, max_length=300)
    burial_plot_number: str | None = Field(None, max_length=100)
    remains_disposition: str | None = Field(None, max_length=20)
    languages: list[str] | None = None
    bio: str | None = Field(None, max_length=2000)
    research_notes: str | None = Field(None, max_length=5000)
    medical_history: str | None = None
    obituary: str | None = Field(None, max_length=10000)
    obituary_source: str | None = Field(None, max_length=500)
    obituary_url: str | None = Field(None, max_length=1000)
    education: list[EducationEntry] | None = None
    career: list[CareerEntry] | None = None
    organizations: list[OrganizationEntry] | None = None
    height: str | None = Field(None, max_length=50)
    weight: str | None = Field(None, max_length=50)
    eye_color: str | None = Field(None, max_length=50)
    hair_color: str | None = Field(None, max_length=50)
    blood_type: str | None = Field(None, max_length=10)
    maternal_haplogroup: str | None = Field(None, max_length=100)
    paternal_haplogroup: str | None = Field(None, max_length=100)
    dna_test_provider: str | None = Field(None, max_length=200)
    admixture: list[AdmixtureEntry] | None = None
    medical_conditions: list[MedicalConditionEntry] | None = None
    source_detail: str | None = Field(None, max_length=500)
    confidence: str | None = Field(None, max_length=20)
    photo_url: str | None = Field(None, max_length=500)
    contact_whatsapp: str | None = None
    contact_telegram: str | None = None
    contact_signal: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    contact_addresses: list[AddressEntry] | None = None
    contact_phones: list[PhoneEntry] | None = None
    contact_emails: list[EmailEntry] | None = None
    social_accounts: list[SocialAccountEntry] | None = None
    name_history: list[NameHistoryEntry] | None = None
    place_history: list[PlaceHistoryEntry] | None = None
    social_instagram: str | None = Field(None, max_length=300)
    social_facebook: str | None = Field(None, max_length=300)
    social_twitter: str | None = Field(None, max_length=300)
    social_linkedin: str | None = Field(None, max_length=300)
    social_tiktok: str | None = Field(None, max_length=300)
    social_youtube: str | None = Field(None, max_length=300)
    branch: str | None = Field(None, max_length=100)
    visibility: str | None = None

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v):
        if v is not None and v not in ("confirmed", "probable", "uncertain", "unknown"):
            raise ValueError("confidence must be one of: confirmed, probable, uncertain, unknown")
        return v

    @field_validator("remains_disposition")
    @classmethod
    def validate_remains_disposition(cls, v):
        if v is not None and v not in ("buried", "cremated", "unknown"):
            raise ValueError("remains_disposition must be one of: buried, cremated, unknown")
        return v

    @field_validator("obituary_url")
    @classmethod
    def validate_obituary_url(cls, v):
        if v is not None and v.strip() and not v.strip().startswith(("http://", "https://")):
            raise ValueError("obituary_url must start with http:// or https://")
        return v


class PersonSummary(BaseModel):
    id: str
    display_name: str
    nickname: str | None
    last_name: str | None = None
    patronymic: str | None = None
    name_display_order: str | None = None
    photo_url: str | None
    birth_date_raw: str | None = None
    residence_country_code: str | None
    branch: str | None
    is_living: bool
    visibility: str
    slug: str | None = None
    media_count: int = 0
    current_occupation: str | None = None

    model_config = {"from_attributes": True}


class PersonDetail(PersonSummary):
    first_name: str | None = None  # None for root person
    birth_last_name: str | None = None
    gender: str | None = None
    alternate_nicknames: list[str] = []
    birth_date_raw: str | None = None
    birth_date: str | None = None
    birth_date_precision: str | None = None
    death_date_raw: str | None = None
    death_date: str | None = None
    death_date_precision: str | None = None
    birth_place: str | None = None
    birth_country_code: str | None = None
    birth_place_latitude: float | None = None
    birth_place_longitude: float | None = None
    residence_place: str | None = None
    residence_place_latitude: float | None = None
    residence_place_longitude: float | None = None
    burial_place: str | None = None
    burial_country_code: str | None = None
    burial_place_latitude: float | None = None
    burial_place_longitude: float | None = None
    burial_cemetery_name: str | None = None
    burial_plot_number: str | None = None
    remains_disposition: str | None = None
    languages: list[str] = []
    bio: str | None = None
    research_notes: str | None = None
    medical_history: str | None = None
    obituary: str | None = None
    obituary_source: str | None = None
    obituary_url: str | None = None
    education: list[dict] = []
    career: list[dict] = []
    organizations: list[dict] = []
    height: str | None = None
    weight: str | None = None
    eye_color: str | None = None
    hair_color: str | None = None
    blood_type: str | None = None
    maternal_haplogroup: str | None = None
    paternal_haplogroup: str | None = None
    dna_test_provider: str | None = None
    admixture: list[dict] = []
    medical_conditions: list[dict] = []
    source_detail: str | None = None
    confidence: str | None = None
    slug: str | None = None
    current_age: int | None = None
    age_at_death: int | None = None
    contact_whatsapp: str | None = None
    contact_telegram: str | None = None
    contact_signal: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    contact_addresses: list[dict] = []
    contact_phones: list[dict] = []
    contact_emails: list[dict] = []
    social_accounts: list[dict] = []
    name_history: list[dict] = []
    place_history: list[dict] = []
    social_instagram: str | None = None
    social_facebook: str | None = None
    social_twitter: str | None = None
    social_linkedin: str | None = None
    social_tiktok: str | None = None
    social_youtube: str | None = None
    is_admin: bool = False
    is_root: bool = False
    source: str = "manual"
    created_at: datetime | None = None


def person_to_summary(person) -> PersonSummary:
    """Convert a Person ORM object to PersonSummary, respecting root redaction."""
    return PersonSummary(
        id=person.id,
        display_name=person.display_name,
        nickname=person.nickname if not person.is_root else None,
        last_name=None if person.is_root else person.last_name,
        patronymic=None if person.is_root else person.patronymic,
        name_display_order=None if person.is_root else person.name_display_order,
        photo_url=person.photo_url,
        birth_date_raw=person.birth_date_raw,
        residence_country_code=person.residence_country_code,
        branch=person.branch,
        is_living=person.is_living,
        visibility=person.visibility,
        media_count=getattr(person, "media_count", 0) or 0,
    )


def person_to_detail(person) -> PersonDetail:
    """Convert a Person ORM object to PersonDetail, respecting root redaction."""
    if person.is_root:
        return PersonDetail(
            id=person.id,
            display_name=person.display_name,
            nickname=None,
            photo_url=person.photo_url,
            residence_country_code=person.residence_country_code,
            branch=person.branch,
            is_living=person.is_living,
            visibility=person.visibility,
            media_count=getattr(person, "media_count", 0) or 0,
            first_name=None,
            last_name=None,
            patronymic=None,
            name_display_order=None,
            slug=person.slug,
            is_root=True,
            source=person.source,
            created_at=person.created_at,
        )
    return PersonDetail(
        id=person.id,
        display_name=person.display_name,
        nickname=person.nickname,
        photo_url=person.photo_url,
        residence_country_code=person.residence_country_code,
        branch=person.branch,
        is_living=person.is_living,
        visibility=person.visibility,
        media_count=getattr(person, "media_count", 0) or 0,
        first_name=person.first_name,
        last_name=person.last_name,
        patronymic=person.patronymic,
        name_display_order=person.name_display_order,
        birth_last_name=person.birth_last_name,
        alternate_nicknames=person.alternate_nicknames,
        gender=person.gender,
        birth_date_raw=person.birth_date_raw,
        birth_date=person.birth_date,
        birth_date_precision=person.birth_date_precision,
        death_date_raw=person.death_date_raw,
        death_date=person.death_date,
        death_date_precision=person.death_date_precision,
        birth_place=person.birth_place,
        birth_country_code=person.birth_country_code,
        birth_place_latitude=person.birth_place_latitude,
        birth_place_longitude=person.birth_place_longitude,
        residence_place=person.residence_place,
        residence_place_latitude=person.residence_place_latitude,
        residence_place_longitude=person.residence_place_longitude,
        burial_place=person.burial_place,
        burial_country_code=person.burial_country_code,
        burial_place_latitude=person.burial_place_latitude,
        burial_place_longitude=person.burial_place_longitude,
        burial_cemetery_name=person.burial_cemetery_name,
        burial_plot_number=person.burial_plot_number,
        remains_disposition=person.remains_disposition,
        languages=person.languages,
        bio=person.bio,
        research_notes=person.research_notes,
        medical_history=person.medical_history,
        obituary=person.obituary,
        obituary_source=person.obituary_source,
        obituary_url=person.obituary_url,
        education=person.education,
        career=person.career,
        organizations=person.organizations,
        height=person.height,
        weight=person.weight,
        eye_color=person.eye_color,
        hair_color=person.hair_color,
        blood_type=person.blood_type,
        maternal_haplogroup=person.maternal_haplogroup,
        paternal_haplogroup=person.paternal_haplogroup,
        dna_test_provider=person.dna_test_provider,
        admixture=person.admixture,
        medical_conditions=person.medical_conditions,
        source_detail=person.source_detail,
        confidence=person.confidence,
        slug=person.slug,
        contact_whatsapp=person.contact_whatsapp,
        contact_telegram=person.contact_telegram,
        contact_signal=person.contact_signal,
        contact_phone=person.contact_phone,
        contact_email=person.contact_email,
        contact_addresses=person.contact_addresses,
        contact_phones=person.contact_phones,
        contact_emails=person.contact_emails,
        social_accounts=person.social_accounts,
        name_history=person.name_history,
        place_history=person.place_history,
        social_instagram=person.social_instagram,
        social_facebook=person.social_facebook,
        social_twitter=person.social_twitter,
        social_linkedin=person.social_linkedin,
        social_tiktok=person.social_tiktok,
        social_youtube=person.social_youtube,
        is_admin=person.is_admin,
        is_root=person.is_root,
        source=person.source,
        created_at=person.created_at,
    )


# --- ParentChild ---

class ParentChildCreate(BaseModel):
    parent_id: str
    child_id: str
    kind: str = "biological"
    confidence: str | None = "confirmed"
    source: str = "manual"
    source_detail: str | None = None
    notes: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class ParentChildUpdate(BaseModel):
    parent_id: str | None = None
    child_id: str | None = None
    kind: str | None = None
    confidence: str | None = None
    source: str | None = None
    source_detail: str | None = None
    notes: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class ParentChildResponse(BaseModel):
    id: str
    parent_id: str
    child_id: str
    kind: str
    confidence: str | None
    source: str
    source_detail: str | None = None
    notes: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Partnership ---

class PartnershipCreate(BaseModel):
    person_a_id: str
    person_b_id: str
    kind: str = "married"
    status: str = "active"
    start_date: str | None = None
    start_date_precision: str | None = None
    end_date: str | None = None
    end_date_precision: str | None = None
    source: str = "manual"
    notes: str | None = None


class PartnershipUpdate(BaseModel):
    kind: str | None = None
    status: str | None = None
    start_date: str | None = None
    start_date_precision: str | None = None
    end_date: str | None = None
    end_date_precision: str | None = None
    source: str | None = None
    notes: str | None = None


class PartnershipResponse(BaseModel):
    id: str
    person_a_id: str
    person_b_id: str
    kind: str
    status: str
    start_date: str | None = None
    end_date: str | None = None
    source: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- External Calendar Sources ---

class ExternalCalendarSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    url: str = Field(min_length=1, max_length=1000)
    source_type: str = Field(default="holiday", max_length=30)
    enabled: bool = True


class ExternalCalendarSourceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    url: str | None = Field(None, min_length=1, max_length=1000)
    source_type: str | None = Field(None, max_length=30)
    enabled: bool | None = None


class ExternalCalendarSourceResponse(BaseModel):
    id: str
    name: str
    url: str
    source_type: str
    enabled: bool
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Tree ---

class TreeResponse(BaseModel):
    root_id: str
    persons: list[PersonSummary]
    parent_child: list[ParentChildResponse]
    partnerships: list[PartnershipResponse]
