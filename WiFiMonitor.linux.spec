# WiFiMonitor.linux.spec
# ─────────────────────────────────────────────────────────────────
#  Spec file de PyInstaller para el build de Linux (AppImage).
#
#  POR QUÉ EXISTE ESTE ARCHIVO:
#  El build anterior usaba pyinstaller directo en línea de comandos
#  con --collect-all webview / streamlit / altair. Eso empaqueta
#  también las librerías de sistema GTK/GLib/WebKit/GObject que el
#  runner de CI (ubuntu-22.04) tiene instaladas.
#
#  Esas librerías empaquetadas chocan en distros más nuevas que
#  ubuntu-22.04 (por ejemplo Ubuntu 26.04), porque el sistema del
#  usuario tiene versiones más nuevas de libstdc++, libgcc_s, glib,
#  gtk, webkit2gtk, etc., y mezclar las del bundle (viejas) con las
#  del sistema (nuevas) produce errores de símbolo indefinido como:
#    - libstdc++.so.6: version `CXXABI_1.3.15' not found
#    - libgcc_s.so.1: version `GCC_13.0.0' not found
#    - libgudev-1.0.so.0: undefined symbol: g_once_init_enter_pointer
#
#  La solución correcta (documentada por PyInstaller) es excluir del
#  bundle las librerías de sistema no-Python con
#  exclude_system_libraries(), para que el binario use SIEMPRE las
#  librerías del sistema operativo donde se ejecuta, en vez de una
#  mezcla parcial de las del runner de CI + las del usuario.
#
#  Uso (dentro de build_appimage.sh, en vez de pyinstaller con flags):
#    pyinstaller --noconfirm WiFiMonitor.linux.spec
# ─────────────────────────────────────────────────────────────────

from PyInstaller.utils.hooks import collect_all, copy_metadata

# ── Replicar --collect-all de la línea de comandos original ──────
# El spec file no hereda --collect-all automáticamente; hay que
# llamar collect_all() por cada paquete y fusionar sus resultados
# en datas/binaries/hiddenimports. Sin esto, faltan archivos
# estáticos de Streamlit/Altair (HTML, JS, JSON) y, sobre todo, la
# metadata de distribución (dist-info), que Streamlit consulta en
# runtime vía importlib.metadata.version("streamlit"). Si falta,
# la app falla con "No package metadata was found for streamlit".
datas = [('wifi_monitor.py', '.'), ('i18n.py', '.'), ('oui_db.json', '.')]
binaries = []
hiddenimports = [
    'streamlit.web.cli',
    'streamlit.web.bootstrap',
    'streamlit.runtime.scriptrunner',
    'webview.platforms.gtk',
    'i18n',
    'speedtest',
]

for pkg in ('streamlit', 'altair', 'webview'):
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports

# copy_metadata explícito como red de seguridad adicional: algunos
# paquetes (streamlit, pandas, plotly, psutil) o sus dependencias
# transitivas consultan su propia metadata en tiempo de ejecución
# (version-checks, plugin discovery), aunque no se haya detectado
# en el análisis estático de imports.
for pkg in ('streamlit', 'pandas', 'plotly', 'psutil', 'altair', 'pywebview'):
    try:
        datas += copy_metadata(pkg)
    except Exception:
        pass  # si el paquete no tiene dist-info instalable, lo ignoramos

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# ── Punto clave del fix ──────────────────────────────────────────
# Excluye del bundle TODAS las librerías de sistema no-Python
# (cualquier .so que venga de /lib* o /usr/lib*), para forzar que en
# tiempo de ejecución se usen siempre las del sistema operativo del
# usuario. Esto evita la mezcla de versiones bundle/sistema que
# causaba los errores de símbolo indefinido.
#
# Excepciones: dejamos pasar ffi/libffi porque algunas distros viejas
# no la tienen, y es una librería muy estable que rara vez causa
# conflictos de versión.
a.exclude_system_libraries(list_of_exceptions=['libffi*'])

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WiFiMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='WiFiMonitor',
)
