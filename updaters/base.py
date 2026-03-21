from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
import requests
import shlex

from config import DOWNLOAD_DIR, REQUEST_TIMEOUT,DOWNLOAD_TIMEOUT, MAX_RETRIES
from logger import logger


class BaseUpdater(ABC):

    def __init__(self, app_name: str, download_url: str, install_cmd: str, dry_run: bool = False):
        self.app_name     = app_name
        self.download_url = download_url
        self.install_cmd  = install_cmd
        self.download_dir = Path(DOWNLOAD_DIR)
        self.dry_run      = dry_run
        logger.trace(f"[{self.app_name}] BaseUpdater instanciado. dry_run={self.dry_run}")

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
        logger.trace(f"[{self.app_name}] Destino do download: {dest}")
        logger.debug(f"[{self.app_name}] Timeouts: connect={REQUEST_TIMEOUT}s, read={DOWNLOAD_TIMEOUT}s")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"[{self.app_name}] Baixando ({attempt}/{MAX_RETRIES}): {self.download_url}")
                response = requests.get(
                    self.download_url, 
                    stream=True, 
                    timeout=(REQUEST_TIMEOUT, DOWNLOAD_TIMEOUT)
                    )
                response.raise_for_status()

                logger.debug(f"[{self.app_name}] HTTP {response.status_code} — Content-Length: {response.headers.get('content-length', 'desconhecido')} bytes")

                total = 0
                with open(dest, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        total += len(chunk)

                logger.debug(f"[{self.app_name}] Total escrito em disco: {total / 1024 / 1024:.2f} MB")
                logger.info(f"[{self.app_name}] Download concluído: {dest}")
                return dest

            except requests.Timeout:
                logger.warning(f"[{self.app_name}] Tentativa {attempt} — timeout após {DOWNLOAD_TIMEOUT}s.")
            except requests.RequestException as e:
                logger.warning(f"[{self.app_name}] Tentativa {attempt} falhou: {e}")

        logger.error(f"[{self.app_name}] Todas as tentativas de download falharam.")
        return None

    def install(self, file: Path) -> bool:
        """Executa o comando de instalação. Retorna True se bem-sucedido."""
        cmd = self.install_cmd.format(file=shlex.quote(str(file)))
        logger.trace(f"[{self.app_name}] Comando de instalação montado: {cmd}")
        logger.info(f"[{self.app_name}] Instalando: {cmd}")

        result = subprocess.run(cmd, shell=True)
        logger.debug(f"[{self.app_name}] subprocess returncode: {result.returncode}")

        if result.returncode == 0:
            logger.info(f"[{self.app_name}] Instalação concluída com sucesso.")
            return True
        else:
            logger.error(f"[{self.app_name}] Falha na instalação. Código: {result.returncode}")
            return False

    def run(self) -> None:
        ###Orquestra too o fluxo — deve ser sobrescrito pelas subclasses.###
        logger.trace(f"[{self.app_name}] BaseUpdater.run() chamado — deve ser sobrescrito.")