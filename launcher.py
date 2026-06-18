"""
WiFi Monitor v2 — Launcher
Inicia Streamlit en background y abre el browser automáticamente.
Compatible con Linux, Windows y macOS.
"""

import subprocess
import sys
import time
import webbrowser
import os
import signal
import platform
from pathlib import Path

PORT = 8501
URL  = f"http://localhost:{PORT}"

# Localizar wifi_monitor.py junto al ejecutable o al script
BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
APP  = BASE / "wifi_monitor.py"


def find_streamlit():
    """Devuelve el ejecutable de streamlit disponible en el sistema."""
    # Dentro del bundle PyInstaller, streamlit queda como módulo
    streamlit_run = [sys.executable, "-m", "streamlit"]
    try:
        subprocess.run(
            streamlit_run + ["--version"],
            capture_output=True, check=True
        )
        return streamlit_run
    except Exception:
        pass
    # Búsqueda en PATH
    import shutil
    st = shutil.which("streamlit")
    if st:
        return [st]
    raise RuntimeError("streamlit no encontrado. Ejecuta: pip install streamlit")


def wait_for_server(timeout: int = 30) -> bool:
    """Espera hasta que el servidor Streamlit responda."""
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(URL, timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def main():
    streamlit_cmd = find_streamlit()

    cmd = streamlit_cmd + [
        "run", str(APP),
        "--server.port", str(PORT),
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--browser.gatherUsageStats", "false",
    ]

    # Ocultar ventana de consola en Windows
    kwargs = {}
    if platform.system() == "Windows":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(cmd, **kwargs)

    # Esperar a que el servidor arranque
    if wait_for_server(timeout=40):
        webbrowser.open(URL)
    else:
        print(f"[WiFi Monitor] El servidor tardó demasiado. Abre manualmente: {URL}")

    # Mantener vivo el launcher; al cerrarlo, terminar Streamlit
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    main()
