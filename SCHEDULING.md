# ⏰ Automatic Scheduling — pkg_updater

This document covers how to configure **pkg_updater** to run automatically
using **systemd timers** on Linux (Debian/Ubuntu/Mint or derivatives).

---

## Table of Contents

- [Why systemd?](#why-systemd)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Managing the timer](#managing-the-timer)
- [Logs](#logs)
- [Moving the project](#moving-the-project)

---

## Why systemd?

| Feature                              | systemd timer         | cron               |
| ------------------------------------ | --------------------- | ------------------ |
| Runs if PC was off at scheduled time | ✅ `Persistent=true`  | ❌ Missed          |
| Integrated logs                      | ✅ `journalctl`       | ❌ None by default |
| Status monitoring                    | ✅ `systemctl status` | ❌ Limited         |
| Retry on failure                     | ✅ Configurable       | ❌ No              |

---

## Prerequisites

- Linux with systemd (Debian/Ubuntu/Mint or derivatives)
- pkg_updater installed and working — see [README](README.md)
- A dedicated execution path without spaces (e.g. `~/.local/bin/pkg_updater`)

---

## Setup

### 1. Create the execution directory

```bash
mkdir -p ~/.local/bin/pkg_updater
```

### 2. Copy the project (excluding dev files)

```bash
rsync -av \
  --exclude='.venv' \
  --exclude='downloads' \
  --exclude='logs' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='etags.json' \
  --exclude='preferences.json' \
  /path/to/your/pkg_updater/ \
  ~/.local/bin/pkg_updater/
```

### 3. Create the virtual environment

```bash
cd ~/.local/bin/pkg_updater
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure sudoers for passwordless dpkg

```bash
sudo visudo -f /etc/sudoers.d/pkg-updater
```

Add the following line (replace `your_user` with your username):

```
your_user ALL=(ALL) NOPASSWD: /usr/bin/dpkg -i *
```

### 5. Create the service unit

```bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/pkg-updater.service
```

```ini
[Unit]
Description=pkg_updater — Automatic Linux package updater
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/home/your_user/.local/bin/pkg_updater
ExecStart=/home/your_user/.local/bin/pkg_updater/.venv/bin/python3 main.py --hide-etag
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

> ⚠️ Replace `your_user` with your actual username.  
> 💡 `--hide-etag` is required — systemd has no interactive terminal.

### 6. Create the timer unit

```bash
nano ~/.config/systemd/user/pkg-updater.timer
```

```ini
[Unit]
Description=pkg_updater timer — runs daily
Requires=pkg-updater.service

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=10min

[Install]
WantedBy=timers.target
```

### 7. Enable and start

```bash
# Reload units
systemctl --user daemon-reload

# Enable timer on system startup
systemctl --user enable pkg-updater.timer

# Start timer now
systemctl --user start pkg-updater.timer

# Verify status
systemctl --user status pkg-updater.timer
```

---

## Managing the timer

```bash
# Check next scheduled run
systemctl --user list-timers pkg-updater.timer

# Run manually right now
systemctl --user start pkg-updater.service

# Stop the timer
systemctl --user stop pkg-updater.timer

# Disable the timer
systemctl --user disable pkg-updater.timer

# Restart after changes
systemctl --user daemon-reload
systemctl --user restart pkg-updater.timer
```

---

## Logs

```bash
# Follow logs in real time
journalctl --user -u pkg-updater.service -f

# Last 7 days
journalctl --user -u pkg-updater.service --since "7 days ago"

# Last run only
journalctl --user -u pkg-updater.service -n 50
```

---

## Moving the project

If you move or rename the project directory, update the two paths in the
service unit and reload:

```bash
nano ~/.config/systemd/user/pkg-updater.service
# Update WorkingDirectory and ExecStart

systemctl --user daemon-reload
systemctl --user restart pkg-updater.timer
```

---

> Built with ❤️ for the Linux community.
