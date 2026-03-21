import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

from updaters.discord import DiscordUpdater


# ─── Fixture ──────────────────────────────────────────────────────────────────

@pytest.fixture
def updater(tmp_path, monkeypatch):
    """Instância limpa com diretório de download isolado."""
    monkeypatch.setattr("updaters.discord.ETAG_FILE", tmp_path / "etags.json")
    instance = DiscordUpdater(
        app_name="discord",
        download_url="https://discord.com/api/download?platform=linux&format=deb",
        install_cmd="sudo dpkg -i {file}",
        dry_run=False,
        show_etag=True,
    )
    instance.download_dir = tmp_path
    return instance


# ─── download() ───────────────────────────────────────────────────────────────

def test_download_success(updater, tmp_path):
    """Download bem-sucedido deve retornar o Path do arquivo."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-length": "1024"}
    mock_response.iter_content = MagicMock(return_value=[b"chunk1", b"chunk2"])

    with patch("updaters.base.requests.get", return_value=mock_response):
        result = updater.download("discord-latest.deb")

    assert result == tmp_path / "discord-latest.deb"
    assert result.exists()


def test_download_retries_on_failure(updater):
    """Falha em todas as tentativas deve retornar None."""
    import requests as req

    with patch("updaters.base.requests.get", side_effect=req.RequestException("erro")):
        result = updater.download("discord-latest.deb")

    assert result is None


def test_download_timeout(updater):
    """Timeout em todas as tentativas deve retornar None."""
    import requests as req

    with patch("updaters.base.requests.get", side_effect=req.Timeout):
        result = updater.download("discord-latest.deb")

    assert result is None


def test_download_creates_file_with_content(updater, tmp_path):
    """Arquivo baixado deve conter o conteúdo dos chunks."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-length": "12"}
    mock_response.iter_content = MagicMock(return_value=[b"hello", b"world"])

    with patch("updaters.base.requests.get", return_value=mock_response):
        result = updater.download("discord-latest.deb")

    assert result.read_bytes() == b"helloworld"


# ─── install() ────────────────────────────────────────────────────────────────

def test_install_success(updater, tmp_path):
    """Comando com returncode 0 deve retornar True."""
    fake_file = tmp_path / "discord-latest.deb"
    fake_file.write_bytes(b"fake")

    mock_result = MagicMock()
    mock_result.returncode = 0

    with patch("updaters.base.subprocess.run", return_value=mock_result):
        assert updater.install(fake_file) is True


def test_install_failure(updater, tmp_path):
    """Comando com returncode != 0 deve retornar False."""
    fake_file = tmp_path / "discord-latest.deb"
    fake_file.write_bytes(b"fake")

    mock_result = MagicMock()
    mock_result.returncode = 1

    with patch("updaters.base.subprocess.run", return_value=mock_result):
        assert updater.install(fake_file) is False


def test_install_quotes_path_with_spaces(updater, tmp_path):
    """Path com espaços deve ser escapado corretamente no comando."""
    spaced_dir = tmp_path / "Área de trabalho"
    spaced_dir.mkdir()
    fake_file = spaced_dir / "discord-latest.deb"
    fake_file.write_bytes(b"fake")

    mock_result = MagicMock()
    mock_result.returncode = 0

    with patch("updaters.base.subprocess.run", return_value=mock_result) as mock_run:
        updater.install(fake_file)
        cmd = mock_run.call_args[0][0]
        assert "'" in cmd  # shlex.quote usa aspas simples