import argparse
from config import APPS
from logger import logger
from updaters import DiscordUpdater

UPDATER_MAP = {
    "discord":        DiscordUpdater,
    "discord-ptb":    DiscordUpdater,
    "discord-canary": DiscordUpdater,
}

STATUS_ICON = {
    "ok":         "✔",
    "atualizado": "🆙",
    "dry-run":    "🔍",
    "erro":       "✗",
}

def main():
    parser = argparse.ArgumentParser(description="Packages Updater")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula verificação sem baixar nem instalar"
    )
    args = parser.parse_args()

    if args.dry_run:
        logger.info("🔍 Modo DRY-RUN ativo — nenhuma alteração será feita.")

    logger.info("=" * 50)
    logger.info("  PACKAGES UPDATER — Iniciando...")
    logger.info("=" * 50)

    results = []

    for app_name, app_config in APPS.items():

        if not app_config.get("enabled", False):
            logger.warning(f"[{app_name}] Desabilitado, pulando...")
            results.append((app_name, "desabilitado"))
            continue

        updater_class = UPDATER_MAP.get(app_name)

        if not updater_class:
            logger.warning(f"[{app_name}] Nenhum handler encontrado, pulando...")
            results.append((app_name, "erro"))
            continue

        try:
            updater = updater_class(
                app_name     = app_name,
                download_url = app_config["download_url"],
                install_cmd  = app_config["install_cmd"],
                dry_run      = args.dry_run,  # ← passa o flag
            )
            status = updater.run()
            results.append((app_name, status))

        except Exception as e:
            logger.error(f"[{app_name}] Erro inesperado: {e}")
            results.append((app_name, "erro"))

    # ─── Resumo final ─────────────────────────────────────────────────────────
    logger.info("=" * 50)
    logger.info("  RESUMO")
    logger.info("=" * 50)
    for app_name, status in results:
        icon = STATUS_ICON.get(status, "?")
        logger.info(f"  {icon}  {app_name:<20} {status}")
    logger.info("=" * 50)
    logger.info("  PACKAGES UPDATER — Concluído!")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()