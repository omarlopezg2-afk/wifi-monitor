#!/bin/bash
# ─────────────────────────────────────────────────────────────────
#  build_mac.sh — Genera WiFiMonitor.dmg para macOS
#
#  Requisitos (macOS 12+):
#    - Python 3.9+ (Homebrew recomendado: brew install python)
#    - pip install pyinstaller streamlit plotly pandas psutil speedtest-cli
#    - create-dmg: brew install create-dmg
#    - Xcode Command Line Tools: xcode-select --install
#
#  Uso: bash build_mac.sh
#
#  NOTA SOBRE ARQUITECTURA:
#    Este build genera un binario para la arquitectura NATIVA de la máquina
#    donde se compila (arm64 en Apple Silicon, x86_64 en Intel).
#    NO es universal2 — varias dependencias (Pillow, numpy, etc.) no
#    distribuyen wheels "fat" completos, lo que rompe PyInstaller con
#    IncompatibleBinaryArchError. Si necesitas soporte para ambas
#    arquitecturas, compila dos veces: una en runner macos-14 (arm64)
#    y otra en macos-13 (Intel x86_64), y distribuye ambos .dmg.
#
#  NOTA SOBRE FIRMA (notarización):
#    Sin firma Apple, macOS Gatekeeper bloqueará la app la primera vez.
#    El usuario debe ir a: Ajustes → Privacidad y seguridad → Abrir igualmente
#    Para distribución comercial, se necesita Apple Developer ID ($99/año).
# ─────────────────────────────────────────────────────────────────
set -e

APP_NAME="WiFiMonitor"
VERSION="2.0"
BUNDLE_ID="com.omarlopez.wifimonitor"
ARCH_NAME="$(uname -m)"
DMG_OUT="${APP_NAME}-${VERSION}-macOS-${ARCH_NAME}.dmg"
APP_BUNDLE="dist/${APP_NAME}.app"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   WiFi Monitor — Build macOS (.dmg)          ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── 1. Verificar sistema ─────────────────────────────────────────
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ Este script solo corre en macOS"
    exit 1
fi

# ── 2. Instalar dependencias ─────────────────────────────────────
echo "▶ Instalando dependencias Python..."
pip3 install --quiet --upgrade \
    pyinstaller streamlit plotly pandas psutil speedtest-cli

if ! command -v create-dmg &> /dev/null; then
    echo "▶ Instalando create-dmg..."
    brew install create-dmg
fi

# ── 3. Compilar con PyInstaller ──────────────────────────────────
echo ""
echo "▶ Compilando .app con PyInstaller..."

rm -rf dist build "${APP_NAME}.spec"

pyinstaller \
    --noconfirm \
    --onedir \
    --windowed \
    --name "${APP_NAME}" \
    --icon "wifi_monitor.icns" \
    --osx-bundle-identifier "${BUNDLE_ID}" \
    --add-data "wifi_monitor.py:." \
    --hidden-import "streamlit" \
    --hidden-import "streamlit.web.cli" \
    --hidden-import "streamlit.runtime.scriptrunner" \
    --hidden-import "altair" \
    --hidden-import "plotly" \
    --hidden-import "pandas" \
    --hidden-import "psutil" \
    --collect-all streamlit \
    --collect-all altair \
    launcher.py

echo "   ✅ .app generado en: ${APP_BUNDLE}"

# ── 4. Info.plist extra ──────────────────────────────────────────
# Agregar permisos de red y descriptor legible
PLIST="${APP_BUNDLE}/Contents/Info.plist"
if [ -f "$PLIST" ]; then
    /usr/libexec/PlistBuddy -c \
        "Set :NSHumanReadableCopyright 'Copyright © 2024 Omar Lopez'" \
        "$PLIST" 2>/dev/null || true
    /usr/libexec/PlistBuddy -c \
        "Add :NSLocalNetworkUsageDescription string 'WiFi Monitor necesita acceso a la red local para detectar dispositivos.'" \
        "$PLIST" 2>/dev/null || true
fi

# ── 5. Empaquetar en DMG ─────────────────────────────────────────
echo ""
echo "▶ Creando DMG con ventana de instalación..."

rm -f "${DMG_OUT}"

create-dmg \
    --volname "${APP_NAME} ${VERSION}" \
    --volicon "wifi_monitor.icns" \
    --window-pos  200 150 \
    --window-size 540 380 \
    --icon-size   100 \
    --icon "${APP_NAME}.app" 130 180 \
    --hide-extension "${APP_NAME}.app" \
    --app-drop-link 410 180 \
    --no-internet-enable \
    "${DMG_OUT}" \
    "${APP_BUNDLE}"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ✅  DMG generado correctamente              ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "   📦 Archivo: ${DMG_OUT}"
echo "   📏 Tamaño:  $(du -sh "${DMG_OUT}" | cut -f1)"
echo ""
echo "   ⚠️  IMPORTANTE — Gatekeeper:"
echo "   Sin firma Apple, el usuario debe abrir:"
echo "   Ajustes del Sistema → Privacidad y seguridad"
echo "   → 'Abrir de todas formas' la primera vez."
echo ""
echo "   Para notarización comercial:"
echo "   https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution"
echo ""
