# WiFi Monitor

Aplicación de escritorio multiplataforma para monitorear tu red WiFi: fuerza de señal, dispositivos conectados, fabricante de cada dispositivo, velocidad de conexión y más — todo desde una interfaz nativa, sin depender de la terminal.

Autor: Omar López

## Descarga

| Sistema operativo | Dónde |
|---|---|
| **Windows 10 / 11** | **Microsoft Store** → https://apps.microsoft.com/detail/9p51j5mn0dgm |
| Linux | [Releases](../../releases/latest): `.AppImage` o `.deb` |
| macOS (Apple Silicon) | [Releases](../../releases/latest): `.dmg` |

En Windows se recomienda la Microsoft Store: la instalación y las actualizaciones las gestiona el sistema y la app va firmada. El instalador `.exe` y el paquete `.msix` se generan en cada compilación pero **no se publican como descarga**: el `.msix` es solo para subir a Partner Center.

## Características

- Monitoreo en tiempo real de la señal WiFi (dBm, calidad, canal, banda)
- Detección de dispositivos conectados con identificación de fabricante (base de datos IEEE OUI, más de 39.000 registros)
- Detector de intrusos con lista blanca: apruebas tus aparatos una vez y la app avisa cuando aparece uno fuera de esa lista
- Historial de tráfico de los últimos 7 días
- Alertas de escritorio (señal baja, latencia alta, pérdida de paquetes)
- Diagnóstico de video: compara tu conexión con lo que necesita cada calidad de streaming
- Test de velocidad integrado (descarga, subida, ping y jitter)
- Interfaz disponible en 6 idiomas (español, inglés, portugués, francés, alemán e italiano)
- Ventana nativa de escritorio (pywebview), sin necesidad de abrir el navegador

### Lo que la app no hace

- **No bloquea dispositivos por ti.** Identifica cuál es cada aparato —fabricante, IP y MAC— para que tú lo bloquees en las opciones de tu router o módem, que es donde se puede hacer.
- No modifica la configuración de tu router ni de tu red: solo lee lo que necesita para mostrar la información.

## Requisitos

**Sistema:** un PC con adaptador WiFi. En Windows, Windows 10 (1809 o superior) o Windows 11.

**Dependencias de Python** (solo si ejecutas desde el código): `streamlit`, `psutil`, `pandas`, `plotly`, `speedtest-cli`, `pywebview`.

**Herramientas del sistema** que la app usa según la plataforma:

| Plataforma | Herramientas | Para qué |
|---|---|---|
| Linux | `arp-scan`, `ping`, `iw`, `ip`, `notify-send` | Escaneo de la red, datos de la señal y notificaciones de escritorio |
| Windows | `ping`, `netsh`, `arp` | Escaneo de la red y datos de la interfaz WiFi |
| macOS | `ping`, `arp` | Escaneo de la red (con barrido por ping como respaldo) |

En Linux, el escaneo con `arp-scan` necesita permisos: la app te pide la contraseña desde su propia interfaz (no la guarda) y, si no la das, usa el método alternativo por barrido de ping.

## Instalación

**Windows (Microsoft Store)**

Busca **WiFi Monitor** en la Store o abre el enlace de la sección [Descarga](#descarga).

**Linux (.deb)**
```bash
sudo apt install arp-scan
sudo dpkg -i WiFiMonitor_amd64.deb
```

**Linux (AppImage)**
```bash
chmod +x WiFiMonitor-x86_64.AppImage
./WiFiMonitor-x86_64.AppImage
```

**macOS (.dmg)**

Abre el `.dmg` y arrastra la app a Aplicaciones.

**Desde el código (cualquier plataforma)**
```bash
git clone https://github.com/omarlopezg2-afk/wifi-monitor.git
cd wifi-monitor
pip install streamlit psutil pandas plotly speedtest-cli pywebview
python launcher.py
```

## Tecnología

Construido con Python, Streamlit y pywebview, empaquetado con PyInstaller. Compilado y distribuido automáticamente mediante GitHub Actions.

## Licencia

_(Pendiente de definir.)_ El repositorio es público para revisión, y eso no concede permiso de redistribución de los binarios. Antes de publicarlo como proyecto abierto hay que elegir explícitamente una licencia (por ejemplo MIT o Apache-2.0) o dejar por escrito que se reservan todos los derechos.

## Contribuir

¿Encontraste un fallo o quieres proponer una función? Abre un [issue](../../issues) con:

- Sistema operativo y versión
- Qué esperabas que pasara y qué pasó
- Si puedes, una captura de la pantalla donde ocurre
