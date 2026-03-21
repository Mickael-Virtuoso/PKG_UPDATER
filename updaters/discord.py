import json
import requests
from pathlib import Path

from config import REQUEST_TIMEOUT, BASE_DIR, MAX_RETRIES
from logger import logger
from updaters.base import BaseUpdater

# Arquivo que persiste os etags entre execuções
ETAG_FILE = Path(BASE_DIR) / "etags.json"


def _load_etags() -> dict:
    logger.trace("Carregando etags.json do disco...")
    if ETAG_FILE.exists():
        with open(ETAG_FILE, "r") as f:
            data = json.load(f)
            logger.trace(f"etags.json carregado: {list(data.keys())}")
            return data
    logger.debug("etags.json não encontrado — retornando dict vazio.")
    return {}


def _save_etag(app_name: str, etag: str):
    logger.trace(f"Salvando etag para '{app_name}'")
    etags = _load_etags()
    etags[app_name] = etag
    with open(ETAG_FILE, "w") as f:
        json.dump(etags, f, indent=2)
    logger.debug(f"etags.json atualizado com sucesso para '{app_name}'.")


def _format_etag(etag: str, show_full: bool | None) -> str:
    """Formata o ETag conforme preferência do usuário."""
    if not etag:
        return "N/A"
    if show_full:
        return etag
    return f"{etag[:4]}...{etag[-4:]}"


class DiscordUpdater(BaseUpdater):

    def __init__(self, app_name: str, download_url: str, install_cmd: str, dry_run: bool = False, show_etag: bool | None = None):
        super().__init__(app_name, download_url, install_cmd, dry_run)
        self.show_etag = show_etag
        logger.trace(f"[{self.app_name}] show_etag={self.show_etag}")

    def get_installed_version(self) -> str | None:
        """Retorna o etag salvo localmente — representa a versão instalada."""
        logger.trace(f"[{self.app_name}] Buscando etag local...")
        etags = _load_etags()
        version = etags.get(self.app_name)
        if version:
            logger.debug(f"[{self.app_name}] Etag local encontrado: {_format_etag(version, self.show_etag)}")
        else:
            logger.debug(f"[{self.app_name}] Nenhum etag local — app não instalado ainda.")
        return version

    def get_latest_version(self) -> str | None:
        """Retorna o etag atual do servidor com retry em caso de timeout."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.trace(f"[{self.app_name}] HEAD request tentativa {attempt}/{MAX_RETRIES}: {self.download_url}")
                response = requests.head(
                    self.download_url,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()

                logger.debug(f"[{self.app_name}] HTTP {response.status_code} recebido.")
                logger.trace(f"[{self.app_name}] Headers completos: {dict(response.headers)}")

                etag = response.headers.get("etag", "").strip('"')
                if etag:
                    logger.debug(f"[{self.app_name}] ETag do servidor: {_format_etag(etag, self.show_etag)}")
                    return etag

                logger.warning(f"[{self.app_name}] ETag não encontrado nos headers.")
                return None

            except requests.Timeout:
                logger.warning(f"[{self.app_name}] Tentativa {attempt}/{MAX_RETRIES} — timeout no HEAD request.")
            except requests.RequestException as e:
                logger.error(f"[{self.app_name}] Erro ao checar versão mais recente: {e}")
                return None

        logger.error(f"[{self.app_name}] Todas as {MAX_RETRIES} tentativas de HEAD falharam.")
        return None

    def run(self) -> str:
        """Retorna: 'atualizado', 'ok', 'dry-run' ou 'erro'."""
        logger.trace(f"[{self.app_name}] DiscordUpdater.run() iniciado.")
        logger.info(f"[{self.app_name}] Iniciando verificação...")

        installed = self.get_installed_version()
        latest    = self.get_latest_version()

        logger.debug(f"[{self.app_name}] Comparando — local: {_format_etag(installed, self.show_etag)} | servidor: {_format_etag(latest, self.show_etag)}")

        if not latest:
            logger.error(f"[{self.app_name}] Não foi possível obter a versão mais recente.")
            return "erro"

        if installed == latest:
            logger.info(f"[{self.app_name}] Já está na versão mais recente. Nada a fazer.")
            return "ok"

        if not installed:
            logger.info(f"[{self.app_name}] Não instalado. Baixando...")
        else:
            logger.info(f"[{self.app_name}] Nova versão detectada! Atualizando...")

        # ─── Dry-run — simula sem baixar nem instalar ─────────────────────────
        if self.dry_run:
            logger.info(f"[{self.app_name}] [DRY-RUN] Pulando download e instalação.")
            logger.debug(f"[{self.app_name}] [DRY-RUN] Etag NÃO será salvo.")
            return "dry-run"

        filename = f"{self.app_name}-latest.deb"
        logger.trace(f"[{self.app_name}] Nome do arquivo definido: {filename}")
        file = self.download(filename)

        if file:
            success = super().install(file)
            if success:
                logger.trace(f"[{self.app_name}] Salvando novo etag após instalação bem-sucedida.")
                _save_etag(self.app_name, latest)
                return "atualizado"

        logger.error(f"[{self.app_name}] Falha no fluxo de atualização.")
        return "erro"