import re
import subprocess
import requests

from config import REQUEST_TIMEOUT
from logger import logger
from updaters.base import BaseUpdater


class DiscordUpdater(BaseUpdater):

    def get_installed_version(self) -> str | None:
        """Consulta o dpkg para saber a versão instalada."""
        try:
            result = subprocess.run(
                ["dpkg", "-l", self.app_name],
                capture_output=True,
                text=True
            )

            for line in result.stdout.splitlines():
                if line.startswith("ii") and self.app_name in line:
                    # linha: "ii  discord  0.0.45  amd64  ..."
                    parts = line.split()
                    return parts[2]  # índice da versão

        except Exception as e:
            logger.error(f"[{self.app_name}] Erro ao checar versão instalada: {e}")

        return None

    def get_latest_version(self) -> str | None:
        """
        Faz um HEAD na URL de download e extrai a versão
        pelo header Content-Disposition.
        Ex: attachment; filename=discord-0.0.45.deb
        """
        try:
            response = requests.head(
                self.download_url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()

            disposition = response.headers.get("Content-Disposition", "")
            match = re.search(r"filename=\S+?-([\d.]+)\.deb", disposition)

            if match:
                return match.group(1)

            logger.warning(f"[{self.app_name}] Não foi possível extrair versão do header.")

        except requests.RequestException as e:
            logger.error(f"[{self.app_name}] Erro ao checar versão mais recente: {e}")

        return None
```

---

## Como funciona a detecção de versão
```
HEAD https://discord.com/api/download?platform=linux&format=deb
        ↓
Content-Disposition: attachment; filename=discord-0.0.45.deb
        ↓
regex extrai → "0.0.45"