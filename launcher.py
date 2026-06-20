"""
WiFi Monitor v2 — Launcher
Inicia Streamlit en un hilo dentro del mismo proceso (en vez de un
subproceso aparte) y lo muestra en una ventana nativa (pywebview)
en vez de abrir el navegador del sistema.
Compatible con Linux, Windows y macOS.

IMPORTANTE — por qué Streamlit corre en un hilo y no en subprocess:
Dentro de un ejecutable empaquetado con PyInstaller, sys.executable
apunta al propio binario de la app, no a un intérprete de Python
normal. Lanzar `subprocess.Popen([sys.executable, "-m", "streamlit", ...])`
en ese contexto relanza el ejecutable completo desde cero (vuelve a
ejecutar este mismo launcher), que a su vez intenta relanzarse otra
vez, y así sucesivamente: una bomba fork recursiva que agota CPU y
RAM en segundos. Por eso Streamlit se arranca aquí con su API en
proceso (streamlit.web.bootstrap.run) dentro de un hilo, sin crear
ningún subproceso nuevo.
"""

import sys
import time
import threading
import platform
from pathlib import Path
from typing import Optional

import webview

PORT = 8501
URL  = f"http://localhost:{PORT}"

# Localizar wifi_monitor.py junto al ejecutable o al script
BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
APP  = BASE / "wifi_monitor.py"

_server_error: Optional[Exception] = None


def run_streamlit_in_thread():
    """Arranca el servidor Streamlit en el hilo actual (bloqueante)."""
    global _server_error
    try:
        import streamlit.web.bootstrap as bootstrap

        # Streamlit intenta instalar manejadores de señal (SIGTERM,
        # SIGINT...) al arrancar, pero eso solo funciona en el hilo
        # principal del intérprete. Como este servidor corre en un
        # hilo secundario (pywebview necesita el hilo principal para
        # la ventana), desactivamos ese paso: nosotros controlamos el
        # ciclo de vida completo del proceso desde main().
        bootstrap._set_up_signal_handler = lambda server: None

        flag_options = {
            "server.port": PORT,
            "server.headless": True,
            "server.enableCORS": False,
            "server.enableXsrfProtection": False,
            "browser.gatherUsageStats": False,
        }
        bootstrap.run(str(APP), False, [], flag_options)
    except Exception as exc:  # noqa: BLE001 - queremos capturar cualquier fallo
        _server_error = exc


def wait_for_server(timeout: int = 40) -> bool:
    """Espera hasta que el servidor Streamlit responda."""
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _server_error is not None:
            return False
        try:
            urllib.request.urlopen(URL, timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def show_error_window(message: str):
    """Ventana mínima de error en vez de fallar en silencio."""
    webview.create_window(
        "WiFi Monitor — Error",
        html="<body style='font-family:sans-serif;padding:2rem;'>"
             "<h2>No se pudo iniciar WiFi Monitor</h2>"
             f"<p>{message}</p>"
             "</body>",
        width=480, height=260, resizable=False,
    )
    webview.start()


def main():
    # Streamlit corre en un hilo daemon: si el proceso principal
    # termina (p. ej. el usuario cierra la ventana), el hilo no
    # impide que el programa salga.
    server_thread = threading.Thread(
        target=run_streamlit_in_thread,
        daemon=True,
        name="streamlit-server",
    )
    server_thread.start()

    server_ok = wait_for_server(timeout=40)

    if not server_ok:
        detail = (
            f"Detalle: {_server_error}" if _server_error is not None
            else "El servidor interno tardó demasiado en responder."
        )
        show_error_window(detail + " Cierra esta ventana e intenta abrir la app de nuevo.")
        return

    # Ventana nativa apuntando al servidor local de Streamlit
    window = webview.create_window(
        "WiFi Monitor",
        url=URL,
        width=1200,
        height=800,
        min_size=(900, 600),
    )

    try:
        # gui="edgechromium" usa WebView2 en Windows (ya viene en Win10/11 modernos)
        webview.start(gui="edgechromium" if platform.system() == "Windows" else None)
    finally:
        # Streamlit corre en hilo daemon: al salir el proceso principal
        # (aquí), el hilo se termina automáticamente con el programa.
        pass


if __name__ == "__main__":
    main()
