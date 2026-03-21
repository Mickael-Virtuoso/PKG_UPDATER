import json
from pathlib import Path

from config import BASE_DIR
from logger import logger

PREFERENCES_FILE = Path(BASE_DIR) / "preferences.json"

DEFAULTS = {
    "show_etag": None,  # None = nunca foi perguntado
}


def load_preferences() -> dict:
    logger.trace("Carregando preferences.json...")
    if PREFERENCES_FILE.exists():
        with open(PREFERENCES_FILE, "r") as f:
            data = json.load(f)
            logger.debug(f"Preferências carregadas: {data}")
            return data
    logger.debug("preferences.json não encontrado — usando defaults.")
    return DEFAULTS.copy()


def save_preferences(prefs: dict):
    logger.trace(f"Salvando preferências: {prefs}")
    with open(PREFERENCES_FILE, "w") as f:
        json.dump(prefs, f, indent=2)
    logger.debug("preferences.json salvo com sucesso.")


def ask_etag_preference() -> bool:
    """Pergunta ao usuário e salva a preferência. Retorna True se quer ver ETag completo."""
    print("\n┌─────────────────────────────────────────────┐")
    print("│           PREFERÊNCIA DE EXIBIÇÃO           │")
    print("├─────────────────────────────────────────────┤")
    print("│  Deseja exibir o ETag completo nos logs?    │")
    print("│                                             │")
    print("│  ETag completo:   6d612f1e6542a8538549d5e8  │")
    print("│  ETag mascarado:  6d61...d5e8               │")
    print("└─────────────────────────────────────────────┘")

    while True:
        answer = input("  Sua escolha [sim/não]: ").strip().lower()
        if answer in ("sim", "s", "yes", "y"):
            show = True
            break
        elif answer in ("não", "nao", "n", "no"):
            show = False
            break
        else:
            print("  ❌ Resposta inválida. Digite 'sim' ou 'não'.")

    prefs = load_preferences()
    prefs["show_etag"] = show
    save_preferences(prefs)

    label = "completo ✔" if show else "mascarado ✔"
    print(f"  Preferência salva: ETag {label}\n")
    logger.debug(f"Preferência de ETag definida pelo usuário: show_etag={show}")
    return show