"""
WiFi Monitor v2 — Launcher
Inicia Streamlit en background y lo muestra en una ventana nativa
(pywebview) en vez de abrir el navegador del sistema.
Compatible con Linux, Windows y macOS.
"""

import subprocess
import sys
import time
import os
import signal
import platform
from pathlib import Path

import webview

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


def stop_streamlit(proc: subprocess.Popen):
    """Termina el proceso de Streamlit de forma ordenada."""
    if proc.poll() is not None:
        return  # ya terminó
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        proc.kill()


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

    # Esperar a que el servidor arranque ANTES de abrir la ventana
    server_ok = wait_for_server(timeout=40)

    if not server_ok:
        stop_streamlit(proc)
        # Ventana mínima de error en vez de fallar en silencio
        window = webview.create_window(
            "WiFi Monitor — Error",
            html="<body style='font-family:sans-serif;padding:2rem;'>"
                 "<h2>No se pudo iniciar WiFi Monitor</h2>"
                 "<p>El servidor interno tardó demasiado en responder. "
                 "Cierra esta ventana e intenta abrir la app de nuevo.</p>"
                 "</body>",
            width=480, height=260, resizable=False,
        )
        webview.start()
        return

    # Ventana nativa apuntando al servidor local de Streamlit
    window = webview.create_window(
        "WiFi Monitor",
        url=URL,
        width=1200,
        height=800,
        min_size=(900, 600),
    )

    # Al cerrar la ventana (closing event), terminar Streamlit
    window.events.closing += lambda: stop_streamlit(proc)

    try:
        # gui="edgechromium" usa WebView2 en Windows (ya viene en Win10/11 modernos)
        webview.start(gui="edgechromium" if platform.system() == "Windows" else None)
    finally:
        # Red de seguridad: asegurar que Streamlit no quede huérfano
        stop_streamlit(proc)


if __name__ == "__main__":
    main()
