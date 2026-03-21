# ─── Controle central de níveis de log ───────────────────────────────────────
# Ative/desative cada nível de forma independente.
# Logs desativados aqui não aparecem no terminal nem no arquivo em disco.

LOG_LEVELS = {
    "TRACE":    False,   # rastreamento detalhado de fluxo interno
    "DEBUG":    False,   # diagnóstico e inspeção de valores
    "INFO":     True,    # fluxo normal de execução
    "WARNING":  True,    # situações inesperadas mas recuperáveis
    "ERROR":    True,    # falhas que impedem uma operação
    "CRITICAL": True,    # falhas que impedem o sistema inteiro
}