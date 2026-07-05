# WiFi Monitor

Aplicación de escritorio multiplataforma para monitorear tu red WiFi: fuerza de señal, dispositivos conectados, fabricante de cada dispositivo, velocidad de conexión y más — todo desde una interfaz nativa, sin depender de la terminal.

## Descarga (v6.10)

Descarga la última versión desde la sección [Releases](../../releases/latest):

| Sistema operativo | Archivo |
|---|---|
| Linux | `.AppImage` o `.deb` |
| Windows | `.exe` |
| macOS (Apple Silicon) | `.dmg` |

## Características

- Monitoreo en tiempo real de la señal WiFi
- Detección de dispositivos conectados con identificación de fabricante (base de datos IEEE OUI)
- Test de velocidad integrado
- Interfaz disponible en 6 idiomas (Español, Inglés, Portugués, Francés, Alemán, Italiano)
- Ventana nativa de escritorio (sin necesidad de abrir el navegador)

## Instalación

**Linux (.deb)**
```bash
sudo dpkg -i wifi-monitor_6.10_amd64.deb
```

**Linux (AppImage)**
```bash
chmod +x WiFiMonitor-6.10.AppImage
./WiFiMonitor-6.10.AppImage
```

**Windows**
Ejecuta el instalador `.exe` y sigue el asistente.

**macOS**
Abre el `.dmg` y arrastra la app a Aplicaciones.

## Tecnología

Construido con Python, Streamlit y pywebview, empaquetado con PyInstaller. Compilado y distribuido automáticamente mediante GitHub Actions.

## Licencia

_(agrega aquí la licencia si aplica, ej. MIT)_
