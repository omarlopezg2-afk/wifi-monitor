#!/bin/bash
# ─────────────────────────────────────────────────────────────────
#  build_appimage.sh — Genera WiFiMonitor-x86_64.AppImage
#  Requisitos: python3, pip, fuse (o libfuse2), wget
#  Uso: bash build_appimage.sh
# ─────────────────────────────────────────────────────────────────
set -e

APP_NAME="WiFiMonitor"
# Versión tomada del tag de git (v5.0 -> 5.0) para que el nombre del
# AppImage coincida con el Release. Mismo criterio que build_deb.sh.
VERSION="${VERSION:-${GITHUB_REF_NAME:-}}"
if [ -z "${VERSION}" ]; then
    VERSION="$(git describe --tags --abbrev=0 2>/dev/null || true)"
fi
VERSION="${VERSION#v}"
VERSION="${VERSION:-5.0}"
ARCH="x86_64"
APPDIR="${APP_NAME}.AppDir"
OUTFILE="${APP_NAME}-${VERSION}-${ARCH}.AppImage"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   WiFi Monitor — Build AppImage Linux        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── 1. Herramientas base ─────────────────────────────────────────
echo "▶ Instalando herramientas del sistema..."
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    libfuse2 wget patchelf \
    iproute2 net-tools arp-scan nmap \
    iputils-ping libnotify-bin \
    gir1.2-gtk-3.0 gir1.2-webkit2-4.1 python3-gi python3-gi-cairo \
    libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev

# ── 2. PyInstaller + dependencias Python ─────────────────────────
echo ""
echo "▶ Instalando dependencias Python..."
# NOTA: PyGObject se fija a <3.51 a propósito. Desde la versión 3.51
# PyGObject requiere la librería girepository-2.0, cuyo paquete -dev
# todavía no existe en los repos de Ubuntu 22.04/24.04 (solo en 24.10+).
# Con el pin <3.51, pip compila PyGObject usando girepository-1.0,
# cubierto por libgirepository1.0-dev instalado arriba. Esto es
# necesario incluso si el runner ya trae python3-gi por apt, porque
# actions/setup-python usa un Python aislado del sistema que no ve
# los paquetes de /usr/lib/python3/dist-packages.
pip install --quiet --upgrade \
    pyinstaller streamlit plotly pandas psutil speedtest-cli pywebview "PyGObject<3.51"

# ── 3. Compilar con PyInstaller ──────────────────────────────────
echo ""
echo "▶ Compilando binario con PyInstaller..."
# NOTA: usamos WiFiMonitor.linux.spec en vez de pasar flags directo
# por línea de comandos. El spec file excluye del bundle las
# librerías de sistema no-Python (libstdc++, libgcc_s, glib, gtk,
# webkit2gtk, etc.) vía exclude_system_libraries(), para que el
# binario siempre use las librerías del sistema operativo donde se
# ejecuta en vez de las del runner de CI (ubuntu-22.04). Sin esto,
# en distros más nuevas que el runner (ej. Ubuntu 24.04+) aparecen
# errores de símbolo indefinido como CXXABI_1.3.15 not found o
# g_once_init_enter_pointer al intentar abrir la ventana nativa.
pyinstaller --noconfirm WiFiMonitor.linux.spec

echo "   ✅ Binario generado en dist/${APP_NAME}/"

# ── 4. Construir estructura AppDir ───────────────────────────────
echo ""
echo "▶ Construyendo AppDir..."
rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

# Copiar binario PyInstaller
cp -r "dist/${APP_NAME}/." "${APPDIR}/usr/bin/"

# Ícono (usando el emoji como PNG con Python si no existe wifi_monitor.png)
if [ -f "wifi_monitor.png" ]; then
    cp wifi_monitor.png "${APPDIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
    cp wifi_monitor.png "${APPDIR}/${APP_NAME}.png"
else
    # Crear ícono placeholder si no existe
    python3 - <<'PYEOF'
try:
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (256, 256), (13, 33, 55, 255))
    draw = ImageDraw.Draw(img)
    draw.text((64, 80), "📡", fill=(126, 179, 255, 255))
    draw.text((40, 160), "WiFi Mon", fill=(255, 255, 255, 255))
    img.save("wifi_monitor.png")
    print("   Ícono generado con PIL")
except ImportError:
    # Crear un PNG mínimo vacío (1x1) si PIL no está disponible
    import struct, zlib
    def png_chunk(name, data):
        c = zlib.crc32(name + data) & 0xffffffff
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", c)
    with open("wifi_monitor.png", "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(png_chunk(b"IHDR", struct.pack(">IIBBBBB", 1,1,8,2,0,0,0)))
        f.write(png_chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff")))
        f.write(png_chunk(b"IEND", b""))
    print("   Ícono placeholder creado")
PYEOF
    cp wifi_monitor.png "${APPDIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
    cp wifi_monitor.png "${APPDIR}/${APP_NAME}.png"
fi

# ── 5. AppRun ────────────────────────────────────────────────────
# NOTA: desde que el .spec excluye las librerías de sistema del
# bundle (exclude_system_libraries), el AppImage depende de que el
# sistema del usuario tenga GTK3 + WebKit2GTK 4.1 instalados. AppRun
# verifica esto primero y muestra un mensaje claro si falta algo,
# en vez de dejar que el binario truene con un traceback de Python.
cat > "${APPDIR}/AppRun" << 'EOF'
#!/bin/bash
SELF="$(readlink -f "$0")"
HERE="${SELF%/*}"
export PATH="${HERE}/usr/bin:${PATH}"

# Verificar que las librerías del sistema necesarias existen antes
# de arrancar. ldconfig -p busca en la caché de librerías del sistema.
MISSING=""
ldconfig -p 2>/dev/null | grep -q "libwebkit2gtk-4.1.so.0" || MISSING="${MISSING}  - libwebkit2gtk-4.1-0 (o libwebkit2gtk-4.0-37)\n"
ldconfig -p 2>/dev/null | grep -q "libgtk-3.so.0" || MISSING="${MISSING}  - libgtk-3-0\n"

if [ -n "$MISSING" ]; then
    echo ""
    echo "❌ Faltan librerías del sistema necesarias para la ventana de WiFi Monitor:"
    echo -e "$MISSING"
    echo "Instálalas con:"
    echo "  sudo apt update && sudo apt install -y gir1.2-webkit2-4.1 gir1.2-gtk-3.0"
    echo ""
    exit 1
fi

exec "${HERE}/usr/bin/WiFiMonitor" "$@"
EOF
chmod +x "${APPDIR}/AppRun"

# ── 6. .desktop file ─────────────────────────────────────────────
cat > "${APPDIR}/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Name=WiFi Monitor
Comment=Monitor de red WiFi en tiempo real
Exec=WiFiMonitor
Icon=${APP_NAME}
Type=Application
Categories=Network;Monitor;
Terminal=false
StartupNotify=true
EOF

# ── 7. Descargar appimagetool ────────────────────────────────────
echo ""
echo "▶ Descargando appimagetool..."
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    wget -q --show-progress \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# ── 8. Empaquetar ────────────────────────────────────────────────
echo ""
echo "▶ Empaquetando AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage "${APPDIR}" "${OUTFILE}"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ✅  AppImage generado correctamente         ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "   📦 Archivo: ${OUTFILE}"
echo "   📏 Tamaño:  $(du -sh "${OUTFILE}" | cut -f1)"
echo ""
echo "   Para ejecutar:"
echo "   chmod +x ${OUTFILE} && ./${OUTFILE}"
echo ""
