#!/bin/bash
set -e

# ─── Configurações ────────────────────────────────────────────────────────────
PKG_NAME="pkg-updater"
PKG_VERSION="${1:-0.9.0}"  # Aceita versão como argumento: ./build_deb.sh 0.9.0
PKG_ARCH="amd64"
PKG_MAINTAINER="Mickael Virtuoso <mickaelitppositron@gmail.com>"
PKG_DESCRIPTION="Automatic updater for Linux applications without native auto-update support"
PKG_URL="https://github.com/Mickael-Virtuoso/PKG_UPDATER"

BUILD_DIR="$(pwd)/build"
OUTPUT_DIR="$(pwd)/dist"
INSTALL_DIR="$BUILD_DIR/usr/lib/pkg-updater"

echo "🔨 Building $PKG_NAME v$PKG_VERSION..."

# ─── Limpa build anterior ─────────────────────────────────────────────────────
rm -rf "$BUILD_DIR" "$OUTPUT_DIR"
mkdir -p "$INSTALL_DIR" "$OUTPUT_DIR"

# ─── Copia o código fonte ─────────────────────────────────────────────────────
echo "  → Copiando arquivos..."
rsync -av \
  --exclude='.venv' \
  --exclude='.git' \
  --exclude='.github' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='downloads' \
  --exclude='logs' \
  --exclude='etags.json' \
  --exclude='preferences.json' \
  --exclude='build' \
  --exclude='dist' \
  ./ "$INSTALL_DIR/"

# ─── Cria o comando pkg-updater em /usr/bin ───────────────────────────────────
echo "  → Criando comando pkg-updater..."
mkdir -p "$BUILD_DIR/usr/bin"
cat > "$BUILD_DIR/usr/bin/pkg-updater" << 'EOF'
#!/bin/bash
exec /usr/lib/pkg-updater/.venv/bin/python3 /usr/lib/pkg-updater/main.py "$@"
EOF
chmod +x "$BUILD_DIR/usr/bin/pkg-updater"

# ─── Copia units do systemd ───────────────────────────────────────────────────
echo "  → Copiando units do systemd..."
mkdir -p "$BUILD_DIR/lib/systemd/user"
cat > "$BUILD_DIR/lib/systemd/user/pkg-updater.service" << EOF
[Unit]
Description=pkg_updater — Automatic Linux package updater
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/usr/lib/pkg-updater
ExecStart=/usr/lib/pkg-updater/.venv/bin/python3 /usr/lib/pkg-updater/main.py --hide-etag
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

cat > "$BUILD_DIR/lib/systemd/user/pkg-updater.timer" << EOF
[Unit]
Description=pkg_updater timer — runs daily
Requires=pkg-updater.service

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=10min

[Install]
WantedBy=timers.target
EOF

# ─── Gera o .deb com fpm ──────────────────────────────────────────────────────
echo "  → Gerando .deb..."
fpm \
  --input-type dir \
  --output-type deb \
  --name "$PKG_NAME" \
  --version "$PKG_VERSION" \
  --architecture "$PKG_ARCH" \
  --maintainer "$PKG_MAINTAINER" \
  --description "$PKG_DESCRIPTION" \
  --url "$PKG_URL" \
  --license "GPL-3.0" \
  --depends "python3 (>= 3.12)" \
  --depends "python3-venv" \
  --after-install "packaging/postinst" \
  --before-remove "packaging/prerm" \
  --package "$OUTPUT_DIR/${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}.deb" \
  "$BUILD_DIR/=/"

echo ""
echo "✅ Pacote gerado com sucesso!"
echo "   → $OUTPUT_DIR/${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}.deb"
echo ""
echo "Para instalar:"
echo "  sudo dpkg -i $OUTPUT_DIR/${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}.deb"