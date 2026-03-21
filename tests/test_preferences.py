import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from preferences import load_preferences, save_preferences, DEFAULTS
from updaters.discord import _format_etag


# ─── _format_etag ─────────────────────────────────────────────────────────────

def test_format_etag_show_full():
    etag = "6d612f1e6542a8538549d5e8"
    assert _format_etag(etag, show_full=True) == etag


def test_format_etag_masked():
    etag = "6d612f1e6542a8538549d5e8"
    assert _format_etag(etag, show_full=False) == "6d61...d5e8"


def test_format_etag_none_show_full():
    """show_full=None deve mascarar — comportamento padrão seguro."""
    etag = "6d612f1e6542a8538549d5e8"
    assert _format_etag(etag, show_full=None) == "6d61...d5e8"


def test_format_etag_empty():
    assert _format_etag("", show_full=True) == "N/A"


def test_format_etag_none_value():
    assert _format_etag(None, show_full=True) == "N/A"


# ─── load_preferences ─────────────────────────────────────────────────────────

def test_load_preferences_file_not_found(tmp_path, monkeypatch):
    """Sem preferences.json deve retornar DEFAULTS."""
    monkeypatch.setattr("preferences.PREFERENCES_FILE", tmp_path / "preferences.json")
    prefs = load_preferences()
    assert prefs == DEFAULTS


def test_load_preferences_existing_file(tmp_path, monkeypatch):
    """Com preferences.json deve retornar os valores salvos."""
    prefs_file = tmp_path / "preferences.json"
    prefs_file.write_text(json.dumps({"show_etag": True}))
    monkeypatch.setattr("preferences.PREFERENCES_FILE", prefs_file)
    prefs = load_preferences()
    assert prefs["show_etag"] is True


# ─── save_preferences ─────────────────────────────────────────────────────────

def test_save_preferences(tmp_path, monkeypatch):
    """Deve salvar corretamente em disco."""
    prefs_file = tmp_path / "preferences.json"
    monkeypatch.setattr("preferences.PREFERENCES_FILE", prefs_file)
    save_preferences({"show_etag": False})
    saved = json.loads(prefs_file.read_text())
    assert saved["show_etag"] is False