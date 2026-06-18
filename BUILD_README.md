# WiFi Monitor v2 — Build Multiplataforma

Sistema de empaquetado para distribuir WiFi Monitor como aplicación nativa
en Linux, Windows y macOS. El usuario final **nunca ve una terminal**.

---

## Arquitectura del launcher

```
Ícono de escritorio / AppImage / .exe / .app
           ↓
      launcher.py           ← proceso invisible
           ↓
  streamlit run wifi_monitor.py  (background)
           ↓
  Abre browser → localhost:8501
           ↓
  Usuario ve la app como una web
```

---

## Archivos del sistema de build

| Archivo | Propósito |
|---------|-----------|
| `launcher.py` | Lanzador invisible multiplataforma |
| `build_appimage.sh` | Genera `.AppImage` para Linux |
| `build_windows_prep.py` | Prepara bundle PyInstaller en Windows |
| `WiFiMonitor-Setup.iss` | Script Inno Setup → `WiFiMonitor-Setup.exe` |
| `build_mac.sh` | Genera `.dmg` para macOS |
| `build_all.py` | Orquestador: detecta SO y compila el correcto |
| `.github/workflows/build.yml` | CI/CD automático con GitHub Actions |

---

## 🐧 Linux — AppImage

**Experiencia del usuario:** Descarga → doble clic → la app abre en el browser.

### Compilar

```bash
# En una máquina Ubuntu 22.04 o 24.04:
bash build_appimage.sh

# Resultado:
# WiFiMonitor-2.0-x86_64.AppImage  (~150-200 MB)
```

### Requisitos de la máquina de build
- Ubuntu 22.04+
- Python 3.10+
- libfuse2 (`sudo apt install libfuse2`)
- Conexión a internet (descarga appimagetool automáticamente)

### Ejecutar en la máquina del usuario
```bash
chmod +x WiFiMonitor-2.0-x86_64.AppImage
./WiFiMonitor-2.0-x86_64.AppImage
# → abre http://localhost:8501 automáticamente
```

---

## 🪟 Windows — Instalador .exe

**Experiencia del usuario:** Doble clic → Siguiente → Siguiente → Instalar → ícono en escritorio.

### Compilar (requiere Windows)

```powershell
# Paso 1: generar bundle PyInstaller
python build_windows_prep.py

# Paso 2: instalar Inno Setup 6
# Descargar: https://jrsoftware.org/isdl.php

# Paso 3: compilar el instalador
iscc WiFiMonitor-Setup.iss

# Resultado:
# installer_output\WiFiMonitor-Setup.exe  (~120-160 MB)
```

### Opcional: ícono personalizado
Coloca `wifi_monitor.ico` en la carpeta del proyecto antes de compilar.
Conversor online: https://convertio.co/png-ico/

---

## 🍎 macOS — DMG

**Experiencia del usuario:** Descarga → monta el DMG → arrastra a Aplicaciones.

### Compilar (requiere macOS 12+)

```bash
# Instalar prerrequisitos
brew install python create-dmg
pip3 install pyinstaller streamlit plotly pandas psutil speedtest-cli

# Compilar
bash build_mac.sh

# Resultado:
# WiFiMonitor-2.0-macOS.dmg  (~130-170 MB)
```

### ⚠️ Gatekeeper (importante)
Sin firma Apple Developer ($99/año), macOS bloqueará la app la primera vez.
El usuario debe ir a:
**Ajustes del Sistema → Privacidad y seguridad → "Abrir de todas formas"**

Para distribución comercial seria, se recomienda obtener un Apple Developer ID.

---

## 🤖 CI/CD automático con GitHub Actions

El workflow `.github/workflows/build.yml` genera los **tres paquetes en paralelo**
cada vez que creas un tag de versión:

```bash
git tag v2.0
git push origin v2.0
```

Esto dispara:
1. Build Linux en `ubuntu-22.04`
2. Build Windows en `windows-latest`
3. Build macOS en `macos-14` (Apple Silicon, universal2)
4. Crea un Release de GitHub con los tres archivos adjuntos

### Configurar en tu repo
```
tu-repo/
├── wifi_monitor.py
├── launcher.py
├── build_appimage.sh
├── build_windows_prep.py
├── WiFiMonitor-Setup.iss
├── build_mac.sh
├── build_all.py
└── .github/
    └── workflows/
        └── build.yml    ← copiar aquí
```

---

## Tamaños esperados de los distribuidores

| Paquete | Tamaño aprox. | Motivo |
|---------|---------------|--------|
| AppImage | ~180 MB | Python + Streamlit + todas las deps |
| Setup.exe | ~150 MB | Igual, empaquetado con NSIS/Inno |
| .dmg | ~160 MB | Igual, .app bundle de macOS |

> El tamaño grande es inherente a empaquetar Python completo.
> Es el precio de la portabilidad total (sin instalar nada).

---

## Solución de problemas

### "El AppImage no arranca en mi distro"
```bash
# Instalar FUSE si falta:
sudo apt install libfuse2       # Ubuntu/Debian
sudo dnf install fuse           # Fedora
```

### "Windows Defender bloquea el .exe"
Normal para ejecutables sin firma. El usuario puede hacer clic en
"Más información → Ejecutar de todas formas".
Para distribución seria: adquirir un Code Signing Certificate (~$50-300/año).

### "Streamlit tarda en arrancar la primera vez"
Es normal. El launcher espera hasta 40 segundos antes de abrir el browser.
En hardware lento puede tardar hasta 15-20 segundos la primera vez.
