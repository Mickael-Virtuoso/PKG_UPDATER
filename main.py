import argparse
from config import APPS
from logger import logger
from log_config import LOG_LEVELS
from updaters import DiscordUpdater
from preferences import load_preferences, ask_etag_preference

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


def resolve_etag_preference(args) -> bool | None:
    """
    Resolve a preferência de exibição do ETag.
    Retorna True (completo), False (mascarado) ou None (DEBUG inativo).
    """
    if not LOG_LEVELS.get("DEBUG", False):
        logger.trace("DEBUG inativo — preferência de ETag ignorada.")
        return None

    # ─── Flags explícitos — bypassa tudo ──────────────────────────────────────
    if args.show_etag:
        logger.debug("Flag --show-etag detectado — exibindo ETag completo.")
        return True
    if args.hide_etag:
        logger.debug("Flag --hide-etag detectado — exibindo ETag mascarado.")
        return False

    # ─── Preferência salva ────────────────────────────────────────────────────
    prefs = load_preferences()
    if prefs.get("show_etag") is not None:
        logger.debug(f"Preferência carregada do preferences.json: show_etag={prefs['show_etag']}")
        return prefs["show_etag"]

    # ─── Pergunta interativa ──────────────────────────────────────────────────
    return ask_etag_preference()


def main():
    parser = argparse.ArgumentParser(description="Packages Updater")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula verificação sem baixar nem instalar"
    )

    etag_group = parser.add_mutually_exclusive_group()
    etag_group.add_argument(
        "--show-etag",
        action="store_true",
        help="Exibe o ETag completo nos logs (requer DEBUG ativo)"
    )
    etag_group.add_argument(
        "--hide-etag",
        action="store_true",
        help="Exibe o ETag mascarado nos logs (requer DEBUG ativo)"
    )

    args = parser.parse_args()
    logger.trace(f"Argumentos parsed — dry_run={args.dry_run}, show_etag={args.show_etag}, hide_etag={args.hide_etag}")

    show_etag = resolve_etag_preference(args)

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
                show_etag    = show_etag,  # ← novo
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