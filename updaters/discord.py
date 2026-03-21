import json
import subprocess
import requests
from pathlib import Path

from config import REQUEST_TIMEOUT, BASE_DIR
from logger import logger
from updaters.base import BaseUpdater

# Arquivo que persiste os etags entre execuções
ETAG_FILE = Path(BASE_DIR) / "etags.json"


def _load_etags() -> dict:
    if ETAG_FILE.exists():
        with open(ETAG_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_etag(app_name: str, etag: str):
    etags = _load_etags()
    etags[app_name] = etag
    with open(ETAG_FILE, "w") as f:
        json.dump(etags, f, indent=2)


class DiscordUpdater(BaseUpdater):

    def get_installed_version(self) -> str | None:
        """Retorna o etag salvo localmente — representa a versão instalada."""
        etags = _load_etags()
        return etags.get(self.app_name)

    def get_latest_version(self) -> str | None:
        """Retorna o etag atual do servidor — representa a versão disponível."""
        try:
            response = requests.head(
                self.download_url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()

            etag = response.headers.get("etag", "").strip('"')
            if etag:
                return etag

            logger.warning(f"[{self.app_name}] ETag não encontrado nos headers.")

        except requests.RequestException as e:
            logger.error(f"[{self.app_name}] Erro ao checar versão mais recente: {e}")

        return None

    def run(self) -> str:
        """Retorna: 'Atualizado', 'ok', ou 'erro'."""
        logger.info(f"[{self.app_name}] Iniciando verificação...")

        installed = self.get_installed_version()
        latest    = self.get_latest_version()

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

        # ─── Dry-run — simula sem baixar nem instalar ─────────────────────────────
        if self.dry_run:
            logger.info(f"[{self.app_name}] [DRY-RUN] Pulando download e instalação.")
            return "dry-run"

        filename = f"{self.app_name}-latest.deb"
        file     = self.download(filename)

        if file:
            success = super().install(file)
            if success:
                _save_etag(self.app_name, latest)
                return "atualizado"
                
        return "erro"