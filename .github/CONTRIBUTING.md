# Contributing to pkg_updater

Thank you for your interest in contributing to **pkg_updater**!
This document outlines the process for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Adding a New App](#adding-a-new-app)

---

## Code of Conduct

Be respectful and constructive. This is an open source project built for the
Linux community — everyone is welcome regardless of experience level.

---

## How to Contribute

- 🐛 **Bug reports** — open an issue using the Bug Report template
- 💡 **Feature requests** — open an issue using the Feature Request template
- 🔧 **Code contributions** — fork, branch, and open a Pull Request
- 📖 **Documentation** — improvements to README, docstrings, or comments

---

## Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/your-username/pkg_updater.git
cd pkg_updater

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install pre-commit hooks
pre-commit install

# 5. Run tests to verify setup
pytest tests/ -v
```

---

## Code Standards

This project enforces code quality automatically via pre-commit hooks:

| Tool     | Purpose         |
| -------- | --------------- |
| `black`  | Code formatting |
| `flake8` | Code linting    |
| `pytest` | Test suite      |

Before every commit, the hooks run automatically. You can also run manually:

```bash
black .
flake8 .
pytest tests/ -v
```

---

## Submitting a Pull Request

1. Fork the repository
2. Create a branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Ensure all checks pass: `pre-commit run --all-files && pytest tests/ -v`
5. Commit: `git commit -m "feat: description of change"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request against `main`

---

## Adding a New App

pkg_updater is designed to be modular. To add support for a new application:

1. Create `updaters/your_app.py` extending `BaseUpdater`
2. Implement `get_installed_version()` and `get_latest_version()`
3. Register in `config.py` under `APPS`
4. Register the handler in `main.py` under `UPDATER_MAP`
5. Add tests in `tests/test_your_app.py`
6. Open a Pull Request

---

## Commit Message Convention

This project follows a simple convention:

| Prefix      | Use for                    |
| ----------- | -------------------------- |
| `feat:`     | New feature or app support |
| `fix:`      | Bug fix                    |
| `chore:`    | Maintenance, dependencies  |
| `docs:`     | Documentation only         |
| `test:`     | Tests only                 |
| `refactor:` | Code restructuring         |

---

> Built with ❤️ for the Linux community.
