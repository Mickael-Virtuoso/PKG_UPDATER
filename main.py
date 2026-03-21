from config import APPS
from logger import logger
from updaters import DiscordUpdater

# ─── Mapa de handlers disponíveis ─────────────────────────────────────────────
UPDATER_MAP = {
    "discord":        DiscordUpdater,
    "discord-ptb":    DiscordUpdater,
    "discord-canary": DiscordUpdater,
}

def main():
    logger.info("=" * 50)
    logger.info("  PACKAGES UPDATER — Iniciando...")
    logger.info("=" * 50)

    for app_name, app_config in APPS.items():

        if not app_config.get("enabled", False):
            logger.warning(f"[{app_name}] Desabilitado, pulando...")
            continue

        updater_class = UPDATER_MAP.get(app_name)

        if not updater_class:
            logger.warning(f"[{app_name}] Nenhum handler encontrado, pulando...")
            continue

        try:
            updater = updater_class(
                app_name     = app_name,
                download_url = app_config["download_url"],
                install_cmd  = app_config["install_cmd"],
            )
            updater.run()

        except Exception as e:
            logger.error(f"[{app_name}] Erro inesperado: {e}")

    logger.info("=" * 50)
    logger.info("  PACKAGES UPDATER — Concluído!")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()