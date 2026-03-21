import os

# ─── Caminhos base ────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

# Garante que a pasta downloads existe ao importar o config
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ─── Configurações gerais ─────────────────────────────────────────────────────
REQUEST_TIMEOUT = 15        # segundos para requisições HTTP
DOWNLOAD_TIMEOUT = 120       # segundos para transferêcia completa
MAX_RETRIES     = 3         # tentativas em caso de falha de download

# ─── Apps configurados ────────────────────────────────────────────────────────
APPS = {
    "discord": {
        "enabled": True,
        "download_url": "https://discord.com/api/download?platform=linux&format=deb",
        "install_cmd":  "sudo dpkg -i {file}",
    },
    "discord-ptb": {
        "enabled": True,
        "download_url": "https://discord.com/api/download/ptb?platform=linux&format=deb",
        "install_cmd":  "sudo dpkg -i {file}",
    },
    "discord-canary": {
        "enabled": True,
        "download_url": "https://discord.com/api/download/canary?platform=linux&format=deb",
        "install_cmd":  "sudo dpkg -i {file}",
    },
}