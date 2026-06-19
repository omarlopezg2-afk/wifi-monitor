"""
build_windows_prep.py
─────────────────────
Prepara el bundle PyInstaller en Windows.
Ejecutar ANTES de compilar WiFiMonitor-Setup.iss con Inno Setup.

Uso (desde cmd o PowerShell, en la carpeta del proyecto):
    python build_windows_prep.py
"""

import subprocess
import sys
import shutil
from pathlib import Path

# ── Fix encoding para Windows (cp1252 no soporta emojis/cajas Unicode) ──
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

APP_NAME = "WiFiMonitor"


def run(cmd: list, **kwargs):
    print(f"   $ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, **kwargs)


def main():
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   WiFi Monitor — Build Windows (PyInstaller) ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    # 1. Instalar dependencias Python
    print("▶ Instalando dependencias Python...")
    run([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade",
         "pyinstaller", "streamlit", "plotly", "pandas", "psutil", "speedtest-cli", "pillow"])

    # 1b. Generar ícono si no existe
    icon_path = Path("wifi_monitor.ico")
    if icon_path.exists():
        print("   ✅ Usando wifi_monitor.ico existente")
    else:
        print("▶ wifi_monitor.ico no encontrado, generando placeholder...")
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (256, 256), (13, 33, 55, 255))
        draw = ImageDraw.Draw(img)
        draw.ellipse((53, 53, 203, 203), outline=(126, 179, 255, 255), width=10)
        draw.ellipse((90, 90, 166, 166), outline=(126, 179, 255, 255), width=8)
        draw.ellipse((115, 115, 141, 141), fill=(126, 179, 255, 255))
        img.save(icon_path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print("   ✅ Ícono placeholder generado: wifi_monitor.ico")

    # 2. Limpiar builds anteriores
    for d in ("dist", "build", f"{APP_NAME}.spec"):
        p = Path(d)
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
    print("   ✅ Limpieza completada")

    # 3. Compilar con PyInstaller
    print()
    print("▶ Compilando con PyInstaller (esto tarda unos minutos)...")

    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",              # carpeta, no onefile: más rápido de arrancar
        "--windowed",            # sin ventana de consola
        "--name", APP_NAME,
        "--icon", "wifi_monitor.ico",
        "--add-data", "wifi_monitor.py;.",   # Windows usa ; como separador
        "--hidden-import", "streamlit",
        "--hidden-import", "streamlit.web.cli",
        "--hidden-import", "streamlit.runtime.scriptrunner",
        "--hidden-import", "streamlit.runtime.caching",
        "--hidden-import", "altair",
        "--hidden-import", "plotly",
        "--hidden-import", "pandas",
        "--hidden-import", "psutil",
        "--hidden-import", "packaging",
        "--collect-all", "streamlit",
        "--collect-all", "altair",
        "--collect-all", "plotly",
        "launcher.py",
    ]
    run(pyinstaller_args)

    dist_path = Path("dist") / APP_NAME
    if dist_path.exists():
        print()
        print(f"   ✅ Bundle generado en: {dist_path}")
        size_mb = sum(f.stat().st_size for f in dist_path.rglob("*") if f.is_file()) / 1e6
        print(f"   📏 Tamaño total: {size_mb:.1f} MB")
        print()
        print("─" * 50)
        print("Siguiente paso: compilar el instalador con Inno Setup")
        print("  iscc WiFiMonitor-Setup.iss")
        print("─" * 50)
    else:
        print("❌ ERROR: PyInstaller no generó la carpeta dist/")
        sys.exit(1)


if __name__ == "__main__":
    main()
