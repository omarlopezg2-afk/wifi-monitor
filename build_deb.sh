#!/bin/bash
# ─────────────────────────────────────────────────────────────────
#  build_deb.sh — Genera WiFiMonitor_<version>_amd64.deb
#
#  Empaqueta la app como un paquete Debian/Ubuntu instalable con
#  doble clic (o `sudo apt install ./WiFiMonitor_*.deb`). Tras
#  instalarlo, "WiFi Monitor" aparece en el menú de aplicaciones y
#  en el escritorio, con su ícono, igual que cualquier app nativa.
#
#  Reutiliza el mismo bundle de PyInstaller que el AppImage
#  (WiFiMonitor.linux.spec). Por eso el .deb depende de que el
#  sistema tenga GTK3 + WebKit2GTK instalados (el spec excluye a
#  propósito las librerías de sistema del bundle; ver el .spec).
#
#  Uso: bash build_deb.sh
# ─────────────────────────────────────────────────────────────────
set -e

APP_NAME="WiFiMonitor"
# Versión tomada automáticamente del tag de git (ej. tag v5.0 -> 5.0),
# para que coincida siempre con el Release y no haya que editarla a mano
# en cada versión. Orden de prioridad:
#   1) variable de entorno VERSION (si se define al llamar al script)
#   2) GITHUB_REF_NAME en CI cuando el disparador es un tag (ej. v5.0)
#   3) último tag de git visible en el repo
#   4) respaldo fijo "5.0"
VERSION="${VERSION:-${GITHUB_REF_NAME:-}}"
if [ -z "${VERSION}" ]; then
    VERSION="$(git describe --tags --abbrev=0 2>/dev/null || true)"
fi
VERSION="${VERSION#v}"          # quitar la 'v' inicial: v5.0 -> 5.0
VERSION="${VERSION:-5.0}"       # respaldo si no hay tag
ARCH="amd64"
# Carpeta donde se instalan los archivos de la app dentro del sistema.
INSTALL_DIR="/opt/${APP_NAME}"
PKGROOT="${APP_NAME}_${VERSION}_${ARCH}"   # árbol temporal del paquete
OUTFILE="${APP_NAME}_${VERSION}_${ARCH}.deb"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   WiFi Monitor — Build paquete .deb (Linux)  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── 1. Compilar el bundle con PyInstaller (si no existe ya) ──────
# Si dist/WiFiMonitor ya fue generado (por build_appimage.sh en el
# mismo job de CI), lo reutilizamos para no compilar dos veces.
if [ ! -d "dist/${APP_NAME}" ]; then
    echo "▶ Compilando binario con PyInstaller (WiFiMonitor.linux.spec)..."
    pyinstaller --noconfirm WiFiMonitor.linux.spec
else
    echo "▶ Reutilizando bundle existente en dist/${APP_NAME}/"
fi

# ── 2. Construir el árbol del paquete ────────────────────────────
echo ""
echo "▶ Construyendo árbol del paquete .deb..."
rm -rf "${PKGROOT}"
mkdir -p "${PKGROOT}/DEBIAN"
mkdir -p "${PKGROOT}${INSTALL_DIR}"
mkdir -p "${PKGROOT}/usr/bin"
mkdir -p "${PKGROOT}/usr/share/applications"
mkdir -p "${PKGROOT}/usr/share/icons/hicolor/256x256/apps"

# Copiar todo el bundle de PyInstaller a /opt/WiFiMonitor
cp -r "dist/${APP_NAME}/." "${PKGROOT}${INSTALL_DIR}/"

# ── 3. Lanzador en /usr/bin ──────────────────────────────────────
# Pequeño wrapper para poder ejecutar "wifimonitor" desde cualquier
# terminal, y para que el .desktop tenga un Exec estable.
cat > "${PKGROOT}/usr/bin/wifimonitor" << EOF
#!/bin/bash
exec "${INSTALL_DIR}/${APP_NAME}" "\$@"
EOF
chmod 755 "${PKGROOT}/usr/bin/wifimonitor"

# ── 4. Ícono ─────────────────────────────────────────────────────
if [ -f "wifi_monitor.png" ]; then
    cp wifi_monitor.png "${PKGROOT}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
else
    python3 - <<'PYEOF'
try:
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (256, 256), (13, 33, 55, 255))
    draw = ImageDraw.Draw(img)
    draw.text((64, 80), "WiFi", fill=(126, 179, 255, 255))
    draw.text((40, 150), "Monitor", fill=(255, 255, 255, 255))
    img.save("WiFiMonitor.png")
except Exception:
    import struct, zlib
    def chunk(name, data):
        c = zlib.crc32(name + data) & 0xffffffff
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", c)
    with open("WiFiMonitor.png", "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff")))
        f.write(chunk(b"IEND", b""))
PYEOF
    cp WiFiMonitor.png "${PKGROOT}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
fi

# ── 5. Entrada de menú (.desktop) ────────────────────────────────
# StartupWMClass=WiFiMonitor coincide con el WM_CLASS que fija
# launcher.py (native.set_wmclass), para que el dock agrupe la
# ventana con su ícono correctamente.
cat > "${PKGROOT}/usr/share/applications/wifimonitor.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=WiFi Monitor
GenericName=Network Monitor
Comment=Monitor de red WiFi en tiempo real
Comment[en]=Real-time WiFi network monitor
Exec=wifimonitor
Icon=${APP_NAME}
Terminal=false
Categories=Network;Monitor;System;
Keywords=wifi;network;monitor;red;
StartupNotify=true
StartupWMClass=${APP_NAME}
EOF

# ── 6. Archivo de control del paquete ────────────────────────────
# Calcular tamaño instalado (en KB) para el campo Installed-Size.
INSTALLED_KB=$(du -sk "${PKGROOT}${INSTALL_DIR}" | cut -f1)

cat > "${PKGROOT}/DEBIAN/control" << EOF
Package: wifimonitor
Version: ${VERSION}
Section: net
Priority: optional
Architecture: ${ARCH}
Maintainer: Omar Lopez <omarlopezg2@users.noreply.github.com>
Installed-Size: ${INSTALLED_KB}
Depends: libgtk-3-0, libwebkit2gtk-4.1-0 | libwebkit2gtk-4.0-37, libnotify4, iproute2
Recommends: arp-scan, nmap, net-tools, iw, iputils-ping, wireless-tools
Description: Monitor de red WiFi en tiempo real
 WiFi Monitor muestra calidad de señal, latencia, dispositivos
 conectados, alertas e historial de tráfico de tu red local en
 una ventana de escritorio.
 .
 Incluye detector de intrusos con lista blanca aprendida y test
 de velocidad. Funciona sobre GTK3 + WebKit2GTK.
EOF

# ── 7. postinst / postrm: refrescar caché de íconos y menú ───────
cat > "${PKGROOT}/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 755 "${PKGROOT}/DEBIAN/postinst"

cat > "${PKGROOT}/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
exit 0
EOF
chmod 755 "${PKGROOT}/DEBIAN/postrm"

# Permisos correctos del binario principal
chmod 755 "${PKGROOT}${INSTALL_DIR}/${APP_NAME}" || true

# ── 8. Empaquetar ────────────────────────────────────────────────
echo ""
echo "▶ Empaquetando con dpkg-deb..."
# --root-owner-group: todo queda como root:root (evita warnings de
# ownership al construir como usuario normal en CI).
dpkg-deb --root-owner-group --build "${PKGROOT}" "${OUTFILE}"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ✅  Paquete .deb generado correctamente     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "   📦 Archivo: ${OUTFILE}"
echo "   📏 Tamaño:  $(du -sh "${OUTFILE}" | cut -f1)"
echo ""
echo "   Instalar:"
echo "     sudo apt install ./${OUTFILE}"
echo "   (o doble clic en el archivo)"
echo ""
echo "   Después aparece 'WiFi Monitor' en el menú de aplicaciones."
echo "   Desinstalar:  sudo apt remove wifimonitor"
echo ""
