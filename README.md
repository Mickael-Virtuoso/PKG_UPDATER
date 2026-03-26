<div align="center">

# 📦 pkg_updater

**Automatic updater for Linux applications without native auto-update support.**
**Atualizador automático para aplicativos Linux sem suporte a auto-atualização nativa.**

[![CI](https://github.com/Mickael-Virtuoso/PKG_UPDATER/actions/workflows/ci.yml/badge.svg)](https://github.com/Mickael-Virtuoso/PKG_UPDATER/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

---

## 🇧🇷 Português

### O que é?

O **pkg_updater** é um script Python para Linux que verifica e atualiza automaticamente aplicativos que não possuem chave GPG de auto-atualização — como o Discord — usando comparação de ETag para detectar novas versões sem baixar o arquivo desnecessariamente.

### Apps suportados

| App            | Canal            | Formato |
| -------------- | ---------------- | ------- |
| Discord        | Stable           | `.deb`  |
| Discord PTB    | Public Test Beta | `.deb`  |
| Discord Canary | Canary           | `.deb`  |

### Pré-requisitos

- Linux (Debian/Ubuntu/Mint ou derivados)
- Python 3.12+
- `dpkg` instalado no sistema

### Instalação

```bash
# Clone o repositório
git clone https://github.com/Mickael-Virtuoso/PKG_UPDATER.git
cd PKG_UPDATER

# Crie o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Instale os hooks de qualidade
pre-commit install
```

### Uso

```bash
# Verificar e atualizar todos os apps
python3 main.py

# Simular sem baixar nem instalar
python3 main.py --dry-run

# Controlar exibição do ETag nos logs (requer DEBUG ativo)
python3 main.py --show-etag
python3 main.py --hide-etag

# Combinações
python3 main.py --dry-run --show-etag
python3 main.py --dry-run --hide-etag
```

### Output do terminal

```
[2026-03-21 03:48:19] [INFO] ==================================================
[2026-03-21 03:48:19] [INFO]   PACKAGES UPDATER — Iniciando...
[2026-03-21 03:48:19] [INFO] ==================================================
[2026-03-21 03:48:19] [INFO] [discord] Iniciando verificação...
[2026-03-21 03:48:19] [INFO] [discord] Já está na versão mais recente. Nada a fazer.
[2026-03-21 03:48:19] [INFO] [discord-ptb] Iniciando verificação...
[2026-03-21 03:48:19] [INFO] [discord-ptb] Já está na versão mais recente. Nada a fazer.
[2026-03-21 03:48:19] [INFO] [discord-canary] Iniciando verificação...
[2026-03-21 03:48:19] [INFO] [discord-canary] Já está na versão mais recente. Nada a fazer.
[2026-03-21 03:48:20] [INFO] ==================================================
[2026-03-21 03:48:20] [INFO]   RESUMO
[2026-03-21 03:48:20] [INFO] ==================================================
[2026-03-21 03:48:20] [INFO]   ✔  discord              ok
[2026-03-21 03:48:20] [INFO]   ✔  discord-ptb          ok
[2026-03-21 03:48:20] [INFO]   ✔  discord-canary       ok
[2026-03-21 03:48:20] [INFO] ==================================================
```

### Configuração de logs

Edite o `log_config.py` para ativar/desativar níveis de log:

```python
LOG_LEVELS = {
    "TRACE":    False,  # rastreamento detalhado
    "DEBUG":    False,  # diagnóstico de valores
    "INFO":     True,   # fluxo normal
    "WARNING":  True,   # situações recuperáveis
    "ERROR":    True,   # falhas de operação
    "CRITICAL": True,   # falhas críticas
}
```

### Adicionando um novo app

Veja o [CONTRIBUTING.md](.github/CONTRIBUTING.md) para instruções detalhadas.

---

## 🇺🇸 English

### What is it?

**pkg_updater** is a Python script for Linux that automatically checks and updates applications that lack native GPG auto-update keys — such as Discord — using ETag comparison to detect new versions without unnecessarily downloading files.

### Supported Apps

| App            | Channel          | Format |
| -------------- | ---------------- | ------ |
| Discord        | Stable           | `.deb` |
| Discord PTB    | Public Test Beta | `.deb` |
| Discord Canary | Canary           | `.deb` |

### Requirements

- Linux (Debian/Ubuntu/Mint or derivatives)
- Python 3.12+
- `dpkg` installed on the system

### Installation

```bash
# Clone the repository
git clone https://github.com/Mickael-Virtuoso/PKG_UPDATER.git
cd PKG_UPDATER

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install quality hooks
pre-commit install
```

### Usage

```bash
# Check and update all apps
python3 main.py

# Simulate without downloading or installing
python3 main.py --dry-run

# Control ETag display in logs (requires DEBUG enabled)
python3 main.py --show-etag
python3 main.py --hide-etag

# Combinations
python3 main.py --dry-run --show-etag
python3 main.py --dry-run --hide-etag
```

### Log Configuration

Edit `log_config.py` to enable/disable log levels:

```python
LOG_LEVELS = {
    "TRACE":    False,  # detailed flow tracing
    "DEBUG":    False,  # value inspection
    "INFO":     True,   # normal execution flow
    "WARNING":  True,   # recoverable situations
    "ERROR":    True,   # operation failures
    "CRITICAL": True,   # critical failures
}
```

### Adding a New App

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for detailed instructions.

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](.github/CONTRIBUTING.md) first.

## 🔒 Security

Found a vulnerability? Please read [SECURITY.md](.github/SECURITY.md) before opening an issue.

## 📄 License

This project is licensed under the [GPL-3.0 License](LICENSE).

---

<div align="center">

Made with ❤️ for the Linux community by [Mickael Virtuoso](https://github.com/Mickael-Virtuoso)

[![Sponsor](https://img.shields.io/badge/Sponsor-❤️-ea4aaa)](https://github.com/sponsors/Mickael-Virtuoso)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-mickaelvirtuoso-FF5E5B)](https://ko-fi.com/mickaelvirtuoso)

</div>
