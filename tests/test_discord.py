import json
import pytest
from unittest.mock import MagicMock, patch
from updaters.discord import DiscordUpdater, _load_etags, _save_etag

# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def updater(tmp_path, monkeypatch):
    """Instância limpa do DiscordUpdater com etags.json isolado."""
    monkeypatch.setattr("updaters.discord.ETAG_FILE", tmp_path / "etags.json")
    return DiscordUpdater(
        app_name="discord",
        download_url="https://discord.com/api/download?platform=linux&format=deb",
        install_cmd="sudo dpkg -i {file}",
        dry_run=False,
        show_etag=True,
    )


# ─── _load_etags / _save_etag ─────────────────────────────────────────────────


def test_load_etags_empty(tmp_path, monkeypatch):
    """Sem etags.json deve retornar dict vazio."""
    monkeypatch.setattr("updaters.discord.ETAG_FILE", tmp_path / "etags.json")
    assert _load_etags() == {}


def test_save_and_load_etag(tmp_path, monkeypatch):
    """Salvar e carregar deve retornar o mesmo valor."""
    monkeypatch.setattr("updaters.discord.ETAG_FILE", tmp_path / "etags.json")
    _save_etag("discord", "abc123")
    assert _load_etags()["discord"] == "abc123"


def test_save_etag_preserves_others(tmp_path, monkeypatch):
    """Salvar um etag não deve apagar os outros."""
    monkeypatch.setattr("updaters.discord.ETAG_FILE", tmp_path / "etags.json")
    _save_etag("discord", "aaa")
    _save_etag("discord-ptb", "bbb")
    etags = _load_etags()
    assert etags["discord"] == "aaa"
    assert etags["discord-ptb"] == "bbb"


# ─── get_installed_version ────────────────────────────────────────────────────


def test_get_installed_version_none(updater):
    """Sem etag salvo deve retornar None."""
    assert updater.get_installed_version() is None


def test_get_installed_version_existing(updater, tmp_path, monkeypatch):
    """Com etag salvo deve retornar o valor correto."""
    etag_file = tmp_path / "etags.json"
    monkeypatch.setattr("updaters.discord.ETAG_FILE", etag_file)
    _save_etag("discord", "abc123")
    assert updater.get_installed_version() == "abc123"


# ─── get_latest_version ───────────────────────────────────────────────────────


def test_get_latest_version_success(updater):
    """HEAD request com etag válido deve retornar o etag."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"etag": '"abc123def456"'}

    with patch("updaters.discord.requests.head", return_value=mock_response):
        result = updater.get_latest_version()

    assert result == "abc123def456"


def test_get_latest_version_no_etag(updater):
    """HEAD request sem etag no header deve retornar None."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {}

    with patch("updaters.discord.requests.head", return_value=mock_response):
        result = updater.get_latest_version()

    assert result is None


def test_get_latest_version_timeout(updater):
    """Timeout em todas as tentativas deve retornar None."""
    import requests as req

    with patch("updaters.discord.requests.head", side_effect=req.Timeout):
        result = updater.get_latest_version()

    assert result is None


# ─── run() ────────────────────────────────────────────────────────────────────


def test_run_already_updated(updater, tmp_path, monkeypatch):
    """Etag local igual ao servidor deve retornar 'ok'."""
    etag_file = tmp_path / "etags.json"
    etag_file.write_text(json.dumps({"discord": "abc123"}))
    monkeypatch.setattr("updaters.discord.ETAG_FILE", etag_file)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"etag": '"abc123"'}

    with patch("updaters.discord.requests.head", return_value=mock_response):
        status = updater.run()

    assert status == "ok"


def test_run_dry_run(tmp_path, monkeypatch):
    """Dry-run com versão nova deve retornar 'dry-run' sem instalar."""
    etag_file = tmp_path / "etags.json"
    etag_file.write_text(json.dumps({"discord": "old_etag"}))
    monkeypatch.setattr("updaters.discord.ETAG_FILE", etag_file)

    updater = DiscordUpdater(
        app_name="discord",
        download_url="https://discord.com/api/download?platform=linux&format=deb",
        install_cmd="sudo dpkg -i {file}",
        dry_run=True,
        show_etag=True,
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"etag": '"new_etag"'}

    with patch("updaters.discord.requests.head", return_value=mock_response):
        status = updater.run()

    assert status == "dry-run"


def test_run_latest_unavailable(updater):
    """Sem etag do servidor deve retornar 'erro'."""
    import requests as req

    with patch("updaters.discord.requests.head", side_effect=req.Timeout):
        status = updater.run()

    assert status == "erro"
