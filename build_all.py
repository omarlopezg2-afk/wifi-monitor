"""
build_all.py — Orquestador de builds multiplataforma
─────────────────────────────────────────────────────
Genera el paquete correcto según el SO actual, o todos si se pide.

Uso:
    python build_all.py              # Detecta el SO y compila para él
    python build_all.py --linux      # Solo AppImage
    python build_all.py --windows    # Solo instalador .exe  (requiere Windows)
    python build_all.py --mac        # Solo .dmg             (requiere macOS)
    python build_all.py --all        # Los tres (requiere CI multiplaforma)
"""

import argparse
import platform
import subprocess
import sys
from pathlib import Path


def run_shell(script: str, description: str):
    print(f"\n{'='*55}")
    print(f"  {description}")
    print(f"{'='*55}\n")
    if script.endswith(".sh"):
        subprocess.run(["bash", script], check=True)
    elif script.endswith(".py"):
        subprocess.run([sys.executable, script], check=True)
    else:
        subprocess.run(script, shell=True, check=True)


def build_linux():
    run_shell("build_appimage.sh", "🐧  Build Linux → AppImage")


def build_windows():
    if platform.system() != "Windows":
        print("⚠️  El build de Windows requiere ejecutar en Windows.")
        print("   Opciones:")
        print("   1. GitHub Actions con windows-latest runner")
        print("   2. Una VM Windows con Python + Inno Setup")
        return
    run_shell("build_windows_prep.py", "🪟  Build Windows → PyInstaller bundle")
    iscc = r"C:\Program Files (x86)\Inno Setup 6\iscc.exe"
    if Path(iscc).exists():
        subprocess.run([iscc, "WiFiMonitor-Setup.iss"], check=True)
        print("\n✅  Instalador generado en installer_output\\WiFiMonitor-Setup.exe")
    else:
        print("\n⚠️  Inno Setup no encontrado.")
        print(f"    Descárgalo en: https://jrsoftware.org/isdl.php")
        print(f"    Luego compila: iscc WiFiMonitor-Setup.iss")


def build_mac():
    if platform.system() != "Darwin":
        print("⚠️  El build de macOS requiere ejecutar en macOS.")
        print("   Opción: GitHub Actions con macos-latest runner")
        return
    run_shell("build_mac.sh", "🍎  Build macOS → DMG")


def main():
    parser = argparse.ArgumentParser(description="WiFi Monitor — Build multiplataforma")
    parser.add_argument("--linux",   action="store_true", help="Generar AppImage (Linux)")
    parser.add_argument("--windows", action="store_true", help="Generar instalador .exe (Windows)")
    parser.add_argument("--mac",     action="store_true", help="Generar .dmg (macOS)")
    parser.add_argument("--all",     action="store_true", help="Intentar los tres")
    args = parser.parse_args()

    # Sin flags → detectar plataforma actual
    if not any([args.linux, args.windows, args.mac, args.all]):
        sys = platform.system()
        print(f"\nPlataforma detectada: {sys}")
        if sys == "Linux":
            args.linux = True
        elif sys == "Windows":
            args.windows = True
        elif sys == "Darwin":
            args.mac = True
        else:
            print("Sistema operativo no reconocido. Usa --linux, --windows o --mac.")
            raise SystemExit(1)

    if args.all or args.linux:
        build_linux()
    if args.all or args.windows:
        build_windows()
    if args.all or args.mac:
        build_mac()

    print("\n✅  Build finalizado.\n")


if __name__ == "__main__":
    main()
