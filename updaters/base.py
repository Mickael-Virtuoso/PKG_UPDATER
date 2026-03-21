from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
import requests
import shlex

from config import DOWNLOAD_DIR, REQUEST_TIMEOUT, MAX_RETRIES
from logger import logger


class BaseUpdater(ABC):

    def __init__(self, app_name: str, download_url: str, install_cmd: str):
        self.app_name     = app_name
        self.download_url = download_url
        self.install_cmd  = install_cmd
        self.download_dir = Path(DOWNLOAD_DIR)

    # ─── Métodos abstratos — cada app implementa o seu ────────────────────────

    @abstractmethod
    def get_installed_version(self) -> str | None:
        """Retorna a versão instalada no sistema ou None se não instalado."""
        pass

    @abstractmethod
    def get_latest_version(self) -> str | None:
        """Retorna a versão mais recente disponível para download."""
        pass

    # ─── Métodos concretos — comportamento padrão para todos ──────────────────

    def download(self, filename: str) -> Path | None:
        """Baixa o arquivo e salva em downloads/. Retorna o Path ou None."""
        dest = self.download_dir / filename

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"[{self.app_name}] Baixando ({attempt}/{MAX_RETRIES}): {self.download_url}")
                response = requests.get(self.download_url, stream=True, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                with open(dest, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                logger.info(f"[{self.app_name}] Download concluído: {dest}")
                return dest

            except requests.RequestException as e:
                logger.warning(f"[{self.app_name}] Tentativa {attempt} falhou: {e}")

        logger.error(f"[{self.app_name}] Todas as tentativas de download falharam.")
        return None

    def install(self, file: Path) -> bool:
        """Executa o comando de instalação. Retorna True se bem-sucedido."""
        cmd = self.install_cmd.format(file=shlex.quote(str(file)))
        logger.info(f"[{self.app_name}] Instalando: {cmd}")

        result = subprocess.run(cmd, shell=True)

        if result.returncode == 0:
            logger.info(f"[{self.app_name}] Instalação concluída com sucesso.")
            return True
        else:
            logger.error(f"[{self.app_name}] Falha na instalação. Código: {result.returncode}")
            return False

    def run(self) -> None:
        """Orquestra todo o fluxo de verificação, download e instalação."""
        logger.info(f"[{self.app_name}] Iniciando verificação...")

        installed = self.get_installed_version()
        latest    = self.get_latest_version()

        if not latest:
            logger.error(f"[{self.app_name}] Não foi possível obter a versão mais recente.")
            return

        if not installed:
            logger.info(f"[{self.app_name}] Não instalado. Instalando versão {latest}...")
        else:
            logger.info(f"[{self.app_name}] Instalado: {installed} | Disponível: {latest}")

            from packaging.version import Version
            if Version(installed) >= Version(latest):
                logger.info(f"[{self.app_name}] Já está na versão mais recente. Nada a fazer.")
                return

        filename = f"{self.app_name}_{latest}.deb"
        file     = self.download(filename)

        if file:
            self.install(file)