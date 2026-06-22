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
import webbrowser
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
            # Forzado explícito: si el usuario tiene un
            # ~/.streamlit/config.toml local con un valor distinto
            # para browser.serverPort, el mensaje impreso por
            # Streamlit ("Local URL: http://localhost:XXXX") puede
            # no coincidir con el puerto real donde escucha el
            # servidor (server.port). El bind real siempre respeta
            # server.port; esto solo corrige el texto impreso para
            # que no confunda.
            "browser.serverPort": PORT,
            # CRÍTICO dentro de un binario empaquetado con PyInstaller:
            # Streamlit decide automáticamente si está en "development
            # mode" mirando si la ruta de streamlit/__init__.py contiene
            # "site-packages" o "dist-packages". En un bundle de
            # PyInstaller las librerías viven bajo _internal/streamlit/...,
            # sin esos substrings en la ruta, así que Streamlit cree que
            # corre en modo desarrollo. En ese modo,
            # _get_browser_address_bar_port() ignora browser.serverPort
            # por completo y devuelve un puerto fijo de desarrollo
            # (3000), aunque el servidor real siga escuchando en
            # server.port (8501). Resultado: el "Local URL" impreso y la
            # URL que usa pywebview apuntan a un puerto donde no hay
            # nada escuchando -> ERR_CONNECTION_REFUSED / timeout.
            # Forzar este flag a False hace que el puerto mostrado y
            # usado sea siempre el real (server.port).
            "global.developmentMode": False,
            # Forzar tema oscuro: toda la UI (tarjetas, gráficas) está
            # diseñada en oscuro. Sin esto, en un sistema con tema claro
            # el fondo se vuelve blanco y algunos textos quedan ilegibles.
            "theme.base": "dark",
            "theme.primaryColor": "#3b82f6",
            "theme.backgroundColor": "#0e1117",
            "theme.secondaryBackgroundColor": "#1a2332",
            "theme.textColor": "#e5edff",
        }
        # CRÍTICO: bootstrap.run() NO aplica flag_options al estado
        # global de config. Esa aplicación (load_config_options)
        # solo ocurre en el flujo normal de "streamlit run" vía
        # cli.py, que launcher.py no usa (porque necesita correr
        # Streamlit en un hilo dentro del mismo proceso, no como
        # subproceso vía CLI). Sin esta llamada explícita, todo
        # flag_options anterior queda ignorado: el servidor puede
        # acabar escuchando en server.port igualmente (por otra vía
        # interna), pero global.developmentMode, browser.serverPort,
        # etc. quedan en sus valores automáticos/por defecto. Esto
        # es lo que causaba "Local URL: http://localhost:3000" con
        # el servidor real en 8501: developmentMode nunca se forzaba
        # a False de verdad, solo parecía que sí al inspeccionarlo
        # justo después de definir el diccionario.
        bootstrap.load_config_options(flag_options)
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


def run_in_browser_fallback():
    """
    Modo de respaldo: abre el navegador del sistema apuntando al
    servidor Streamlit, y mantiene el proceso vivo (el servidor
    corre en un hilo daemon; sin esto el proceso terminaría de
    inmediato y el navegador encontraría el puerto ya cerrado,
    como pasó al fallar la ventana nativa por una librería gráfica
    del sistema incompatible — GTK/WebKit en Linux, WebView2 en
    Windows, WebKit/Cocoa en macOS).
    """
    print()
    print("⚠️  No se pudo abrir la ventana nativa de la app.")
    print("   Abriendo WiFi Monitor en el navegador en su lugar...")
    print(f"   URL: {URL}")
    print("   (Cierra esta terminal o presiona Ctrl+C para salir)")
    print()
    try:
        webbrowser.open(URL)
    except Exception:
        pass  # el usuario puede abrir la URL a mano si esto falla

    # Mantener el proceso principal vivo mientras el hilo daemon de
    # Streamlit sigue sirviendo la app. Sin este loop, main() (y por
    # tanto el proceso) terminaría de inmediato.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def add_linux_window_controls(window):
    """
    En Linux la ventana la dibuja pywebview con un Gtk.ApplicationWindow
    cuyas decoraciones las pone el gestor de ventanas (WM). En GNOME, por
    defecto, el WM solo muestra el botón de cerrar (la «X»): minimizar y
    maximizar quedan ocultos por la política del escritorio.

    Para garantizar los tres botones (minimizar, maximizar/restaurar y
    cerrar) en CUALQUIER escritorio (GNOME, KDE, XFCE, etc.), le ponemos
    a la ventana una barra de título propia (Gtk.HeaderBar, decoración del
    lado del cliente). Al dibujarla la propia app, ya no depende de la
    política de botones del WM. GTK conecta solos los botones a las
    acciones de minimizar/maximizar/cerrar.

    Todo va envuelto en try/except: si algo falla, la ventana sigue
    funcionando con la decoración que ponga el WM (sin romper nada).
    """
    if platform.system() != "Linux":
        return

    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, GLib
    except Exception as exc:  # noqa: BLE001
        print(f"⚠️  No se pudieron cargar los controles de ventana GTK: {exc}")
        return

    def _install_headerbar():
        try:
            native = getattr(window, "native", None)
            if native is None:
                # La ventana nativa aún no está lista; reintentar luego.
                return True  # devuelve True => GLib vuelve a llamar

            # WM_CLASS determinista para que el .desktop (StartupWMClass)
            # agrupe la app en el dock y le ponga el ícono correcto.
            try:
                native.set_wmclass("WiFiMonitor", "WiFiMonitor")
            except Exception:
                pass

            headerbar = Gtk.HeaderBar()
            headerbar.set_show_close_button(True)
            headerbar.set_title("WiFi Monitor")
            # Layout con los tres botones estándar. GTK los dibuja y los
            # cablea solo: minimize -> iconify, maximize -> (un)maximize,
            # close -> cerrar la ventana.
            try:
                headerbar.set_decoration_layout(":minimize,maximize,close")
            except Exception:
                pass

            native.set_titlebar(headerbar)
            headerbar.show_all()
            native.set_resizable(True)
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  No se pudo instalar la barra de título personalizada: {exc}")
        return False  # False => no repetir

    # Las llamadas a GTK deben correr en el hilo del bucle principal de
    # GTK. Esta función la ejecuta pywebview en un hilo aparte, así que
    # programamos el trabajo con idle_add para que se ejecute en el hilo
    # correcto en cuanto el bucle esté libre.
    GLib.idle_add(_install_headerbar)


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
        # Si ni siquiera el servidor Streamlit pudo arrancar, no hay
        # nada que mostrar en el navegador tampoco: aquí sí mostramos
        # la ventana de error (o, si esa también falla, el except de
        # abajo ya lo cubre).
        try:
            show_error_window(detail + " Cierra esta ventana e intenta abrir la app de nuevo.")
        except Exception:
            print(f"❌ No se pudo iniciar WiFi Monitor: {detail}")
        return

    # Intentar la ventana nativa primero. Si el motor gráfico nativo
    # del sistema no está disponible o es incompatible (GTK/WebKit
    # faltante o desincronizado en Linux, WebView2 Runtime ausente
    # en Windows, frameworks de WebKit faltantes en macOS), caemos
    # al navegador del sistema en vez de mostrar un traceback.
    try:
        window = webview.create_window(
            "WiFi Monitor",
            url=URL,
            width=1200,
            height=800,
            min_size=(900, 600),
        )
        # En Linux añadimos una barra de título propia con los botones
        # minimizar / maximizar / cerrar (ver add_linux_window_controls).
        # webview.start(func, args) ejecuta func tras arrancar el bucle de
        # la GUI, momento en el que window.native ya existe.
        # gui="edgechromium" usa WebView2 en Windows (ya viene en Win10/11 modernos)
        if platform.system() == "Windows":
            webview.start(gui="edgechromium")
        else:
            webview.start(add_linux_window_controls, window)
    except Exception as exc:
        print(f"⚠️  Motor gráfico nativo no disponible: {exc}")
        run_in_browser_fallback()


if __name__ == "__main__":
    main()
