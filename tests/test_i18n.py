import json
from pathlib import Path

LOCALE_DIR = Path(__file__).parent.parent / "locales"
LOCALES = ["en", "es", "ru"]
# Keys intentionally left blank (admin-configurable branding fields)
ALLOWED_EMPTY_KEYS = {"app.tagline"}


def _flatten_keys(data, prefix=""):
    """Flatten nested dict keys into dot-separated paths."""
    keys = set()
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            keys |= _flatten_keys(value, full_key)
        else:
            keys.add(full_key)
    return keys


def test_all_locales_have_same_keys():
    """All locale files must have identical key sets."""
    key_sets = {}
    for locale in LOCALES:
        with open(LOCALE_DIR / f"{locale}.json") as f:
            data = json.load(f)
        key_sets[locale] = _flatten_keys(data)

    reference = key_sets["en"]
    for locale in LOCALES[1:]:
        missing = reference - key_sets[locale]
        extra = key_sets[locale] - reference
        assert not missing, f"{locale} missing keys: {missing}"
        assert not extra, f"{locale} extra keys: {extra}"


def test_locale_files_are_valid_json():
    """Each locale file parses without error."""
    for locale in LOCALES:
        with open(LOCALE_DIR / f"{locale}.json") as f:
            data = json.load(f)
        assert isinstance(data, dict)


def test_no_empty_translations():
    """No key should have an empty string value."""
    for locale in LOCALES:
        with open(LOCALE_DIR / f"{locale}.json") as f:
            data = json.load(f)

        def _check_empty(d, prefix=""):
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    _check_empty(value, full_key)
                else:
                    assert value != "" or full_key in ALLOWED_EMPTY_KEYS, (
                        f"{locale}: empty value for key '{full_key}'"
                    )

        _check_empty(data)
