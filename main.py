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
    "ok":           "✔",
    "atualizado":   "🆙",
    "dry-run":      "🔍",
    "erro":         "✗",
    "desabilitado": "⏭",
}

def main():
    parser = argparse.ArgumentParser(description="Packages Updater")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula verificação sem baixar nem instalar"
    )
    args = parser.parse_args()

    logger.trace("Argumentos parsed — dry_run=%s", args.dry_run)

    if args.dry_run:
        logger.info("🔍 Modo DRY-RUN ativo — nenhuma alteração será feita.")

    logger.info("=" * 50)
    logger.info("  PACKAGES UPDATER — Iniciando...")
    logger.info("=" * 50)

    logger.debug(f"Apps configurados: {list(APPS.keys())}")

    results = []

    for app_name, app_config in APPS.items():
        logger.trace(f"[{app_name}] Processando entrada do config...")

        if not app_config.get("enabled", False):
            logger.warning(f"[{app_name}] Desabilitado, pulando...")
            results.append((app_name, "desabilitado"))
            continue

        updater_class = UPDATER_MAP.get(app_name)

        if not updater_class:
            logger.warning(f"[{app_name}] Nenhum handler encontrado, pulando...")
            logger.debug(f"[{app_name}] Handlers disponíveis: {list(UPDATER_MAP.keys())}")
            results.append((app_name, "erro"))
            continue

        logger.trace(f"[{app_name}] Handler encontrado: {updater_class.__name__}")

        try:
            updater = updater_class(
                app_name     = app_name,
                download_url = app_config["download_url"],
                install_cmd  = app_config["install_cmd"],
                dry_run      = args.dry_run,
            )
            logger.trace(f"[{app_name}] Instância criada, chamando run()...")
            status = updater.run()
            logger.debug(f"[{app_name}] run() retornou: '{status}'")
            results.append((app_name, status))

        except Exception as e:
            logger.error(f"[{app_name}] Erro inesperado: {e}")
            logger.debug(f"[{app_name}] Traceback completo:", exc_info=True)
            results.append((app_name, "erro"))

    # ─── Resumo final ─────────────────────────────────────────────────────────
    logger.trace(f"Resultados coletados: {results}")
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