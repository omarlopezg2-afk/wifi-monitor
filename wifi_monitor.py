"""
WiFi Network Monitor v2.0 - Streamlit App
Para Ubuntu 24.04 / Anaconda (base)
Autor: Omar Lopez

Nuevas funciones v2:
  ✅ Alertas (escritorio Ubuntu + banner en app)
  ✅ Historial de tráfico CSV (7 días)
  ✅ Test de velocidad real (speedtest-cli)
  ✅ Detector de intrusos con lista blanca aprendida
"""

import streamlit as st
import subprocess
import re
import time
import socket
import platform
import psutil
import json
import csv
import os
import threading
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─────────────────────────────────────────────
# RUTAS DE DATOS PERSISTENTES
# ─────────────────────────────────────────────
DATA_DIR        = Path.home() / ".wifi_monitor"
TRAFFIC_CSV     = DATA_DIR / "traffic_history.csv"
KNOWN_MACS_JSON = DATA_DIR / "known_devices.json"
ALERTS_LOG      = DATA_DIR / "alerts.log"
DATA_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="WiFi Monitor v2 — Omar Desktop",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #0d2137);
        border: 1px solid #2a5298;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
        color: white;
    }
    .metric-card h3 { font-size: 0.85rem; color: #7eb3ff; margin: 0 0 4px 0; }
    .metric-card .value { font-size: 1.9rem; font-weight: 700; margin: 0; }

    .intruder-card {
        background: #2d1515;
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .known-card {
        background: #111827;
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .status-ok   { color: #10b981; font-weight: 700; }
    .status-warn { color: #f59e0b; font-weight: 700; }
    .status-bad  { color: #ef4444; font-weight: 700; }

    div[data-testid="stMetric"] {
        background: #111827;
        border-radius: 10px;
        padding: 12px;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #7eb3ff !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #d1d5db !important;
    }
    .stButton>button { width: 100%; border-radius: 8px; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  FUNCIONES BASE DE RED
# ══════════════════════════════════════════════

@st.cache_data(ttl=5)
def get_wifi_interface() -> str:
    try:
        result = subprocess.run(
            ["ip", "route", "get", "8.8.8.8"],
            capture_output=True, text=True, timeout=5
        )
        match = re.search(r"dev\s+(\S+)", result.stdout)
        if match:
            return match.group(1)
    except Exception:
        pass
    for iface in psutil.net_if_addrs():
        if iface.startswith(("wlan", "wlp", "wlx", "wifi")):
            return iface
    return "wlan0"


@st.cache_data(ttl=5)
def get_wifi_info() -> dict:
    info = {"ssid": "N/A", "signal": "N/A", "channel": "N/A",
            "freq": "N/A", "bssid": "N/A", "bitrate": "N/A"}
    iface = get_wifi_interface()
    try:
        r = subprocess.run(["iw", "dev", iface, "link"],
                           capture_output=True, text=True, timeout=5)
        out = r.stdout
        m = re.search(r"SSID:\s*(.+)", out)
        if m:
            raw = m.group(1).strip()
            try:
                info["ssid"] = bytes(raw, "utf-8").decode("unicode_escape").strip()
            except Exception:
                info["ssid"] = raw
        m = re.search(r"Connected to\s+([\da-fA-F:]+)", out)
        if m:
            info["bssid"] = m.group(1)
        m = re.search(r"signal:\s*(-?\d+)\s*dBm", out)
        if m:
            info["signal"] = int(m.group(1))
        m = re.search(r"tx bitrate:\s*([\d.]+\s*\S+)", out)
        if m:
            info["bitrate"] = m.group(1)
    except Exception:
        pass
    try:
        r2 = subprocess.run(["iw", "dev", iface, "info"],
                            capture_output=True, text=True, timeout=5)
        m = re.search(r"channel\s+(\d+)\s+\((\d+)\s*MHz\)", r2.stdout)
        if m:
            info["channel"] = m.group(1)
            info["freq"] = f"{int(m.group(2)) / 1000:.3f} GHz"
    except Exception:
        pass
    return info


@st.cache_data(ttl=3)
def get_network_stats() -> dict:
    iface = get_wifi_interface()
    counters = psutil.net_io_counters(pernic=True)
    if iface in counters:
        c = counters[iface]
        return {
            "bytes_sent": c.bytes_sent, "bytes_recv": c.bytes_recv,
            "packets_sent": c.packets_sent, "packets_recv": c.packets_recv,
            "errin": c.errin, "errout": c.errout,
            "dropin": c.dropin, "dropout": c.dropout,
        }
    return {}


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_network_prefix() -> str:
    return ".".join(get_local_ip().split(".")[:3])


def bytes_to_human(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def ping_host(ip: str, timeout: float = 0.5) -> tuple:
    try:
        start = time.time()
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            capture_output=True, text=True, timeout=timeout + 1
        )
        elapsed = (time.time() - start) * 1000
        return ip, result.returncode == 0, round(elapsed, 1)
    except Exception:
        return ip, False, 0.0


def resolve_hostname(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "N/A"


def guess_vendor(mac: str) -> str:
    if mac in ("N/A", "(incomplete)", ""):
        return "Desconocido"
    oui = mac.upper().replace("-", ":")[0:8]
    known = {
        "B8:27:EB": "Raspberry Pi", "DC:A6:32": "Raspberry Pi",
        "00:1A:79": "Apple",    "A4:C3:F0": "Apple",
        "3C:22:FB": "Apple",    "F0:18:98": "Apple",
        "70:85:C2": "Apple",    "AC:BC:32": "Apple",
        "18:65:90": "Apple",    "8C:85:90": "Apple",
        "00:26:BB": "Apple",    "28:CF:E9": "Apple",
        "F8:1E:DF": "Apple",    "04:0C:CE": "Cisco",
        "00:1E:E5": "Cisco",    "E8:40:F2": "Motorola",
        "F0:9F:C2": "Ubiquiti", "24:A4:3C": "Ubiquiti",
        "DC:9F:DB": "TP-Link",  "50:C7:BF": "TP-Link",
        "C4:E9:84": "TP-Link",  "EC:08:6B": "TP-Link",
        "00:1D:AA": "D-Link",   "1C:7E:E5": "D-Link",
        "00:26:5A": "Netgear",  "A0:21:B7": "Netgear",
        "2C:D0:5A": "Samsung",  "8C:C8:CD": "Samsung",
        "00:16:32": "Samsung",  "94:35:0A": "Samsung",
        "00:50:56": "VMware",   "00:0C:29": "VMware",
        "00:1B:21": "Intel",    "14:EB:B6": "Realtek (USB WiFi)",
    }
    return known.get(oui, "Desconocido")


@st.cache_data(ttl=60)
def scan_network(sudo_password: str = "") -> list:
    devices = []
    my_ip = get_local_ip()
    iface = get_wifi_interface()

    # Intento 1: arp-scan (con contraseña desde la UI si se proporcionó)
    try:
        if sudo_password:
            r = subprocess.run(
                ["sudo", "-S", "arp-scan", "--interface", iface, "--localnet"],
                input=sudo_password + "\n",
                capture_output=True, text=True, timeout=30
            )
        else:
            r = subprocess.run(
                ["sudo", "arp-scan", "--interface", iface, "--localnet"],
                capture_output=True, text=True, timeout=30
            )
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                parts = line.split("\t")
                if len(parts) >= 2:
                    ip = parts[0].strip()
                    mac = parts[1].strip() if len(parts) > 1 else "N/A"
                    vendor = parts[2].strip() if len(parts) > 2 else guess_vendor(mac)
                    if re.match(r"\d+\.\d+\.\d+\.\d+", ip):
                        devices.append({
                            "ip": ip, "mac": mac, "vendor": vendor,
                            "hostname": resolve_hostname(ip),
                            "is_this_pc": ip == my_ip, "latency": 0,
                        })
            if devices:
                return devices
    except Exception:
        pass

    # Fallback: ping sweep + arp cache
    arp_cache = {}
    try:
        r = subprocess.run(["arp", "-n"], capture_output=True, text=True, timeout=5)
        for line in r.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3 and re.match(r"\d+\.\d+\.\d+\.\d+", parts[0]):
                arp_cache[parts[0]] = parts[2] if parts[2] != "(incomplete)" else "N/A"
    except Exception:
        pass

    prefix = get_network_prefix()
    ips = [f"{prefix}.{i}" for i in range(1, 255)]
    active = {}
    with ThreadPoolExecutor(max_workers=100) as ex:
        futures = {ex.submit(ping_host, ip, 0.4): ip for ip in ips}
        for f in as_completed(futures):
            ip, alive, lat = f.result()
            if alive:
                active[ip] = lat

    for ip, lat in sorted(active.items(), key=lambda x: int(x[0].split(".")[-1])):
        mac = arp_cache.get(ip, "N/A")
        devices.append({
            "ip": ip, "mac": mac, "vendor": guess_vendor(mac),
            "hostname": resolve_hostname(ip),
            "is_this_pc": ip == my_ip, "latency": lat,
        })
    return devices


def measure_latency(host: str = "8.8.8.8", count: int = 5) -> dict:
    try:
        r = subprocess.run(
            ["ping", "-c", str(count), "-W", "2", host],
            capture_output=True, text=True, timeout=30
        )
        out = r.stdout
        loss_m = re.search(r"(\d+)%\s+packet loss", out)
        rtt_m  = re.search(r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)", out)
        return {
            "host": host,
            "packet_loss": int(loss_m.group(1)) if loss_m else 100,
            "min_ms":    float(rtt_m.group(1)) if rtt_m else None,
            "avg_ms":    float(rtt_m.group(2)) if rtt_m else None,
            "max_ms":    float(rtt_m.group(3)) if rtt_m else None,
            "jitter_ms": float(rtt_m.group(4)) if rtt_m else None,
        }
    except Exception as e:
        return {"host": host, "packet_loss": 100, "min_ms": None,
                "avg_ms": None, "max_ms": None, "jitter_ms": None}


def diagnose_streaming(latency_data: dict) -> dict:
    issues = []
    loss   = latency_data.get("packet_loss", 0)
    avg    = latency_data.get("avg_ms")
    jitter = latency_data.get("jitter_ms")

    if avg is None:
        return {"verdict": "Sin datos", "cause": "Sin conexión",
                "color": "bad", "issues": ["No se pudo alcanzar el servidor"],
                "recommendations": ["Verifica tu conexión WiFi"]}

    if loss > 5:
        issues.append(f"⚠️ Pérdida de paquetes alta: {loss}%")
    if avg > 150:
        issues.append(f"⚠️ Latencia alta: {avg:.1f} ms")
    if jitter and jitter > 30:
        issues.append(f"⚠️ Jitter elevado: {jitter:.1f} ms")

    if not issues:
        return {"verdict": "🟢 La red está bien — el problema es externo",
                "cause": "otro", "color": "ok", "issues": ["Sin problemas detectados"],
                "recommendations": [
                    "Tu conexión tiene buena latencia y sin pérdidas.",
                    "Revisa: servidor saturado, plan de internet, CPU/RAM del dispositivo, VPN activa.",
                ]}
    elif loss > 10 or avg > 200:
        return {"verdict": "🔴 Problema de RED confirmado",
                "cause": "red", "color": "bad", "issues": issues,
                "recommendations": [
                    "Reinicia el router (desenchufa 30 seg).",
                    "Acércate al router o usa cable Ethernet.",
                    "Verifica si muchos dispositivos consumen ancho de banda.",
                    "Contacta a tu ISP si persiste.",
                ]}
    else:
        return {"verdict": "🟡 Red con leve degradación",
                "cause": "red", "color": "warn", "issues": issues,
                "recommendations": [
                    "Prueba cambiar al canal 5 GHz si tu router lo soporta.",
                    "Cierra aplicaciones que usen internet en segundo plano.",
                ]}


# ══════════════════════════════════════════════
#  NUEVA: ALERTAS
# ══════════════════════════════════════════════

ALERT_DEFAULTS = {
    "signal_threshold": -75,   # dBm mínimo aceptable
    "latency_threshold": 150,  # ms máxima aceptable
    "loss_threshold": 5,       # % pérdida máxima
    "enabled": True,
}

def load_alert_config() -> dict:
    cfg_path = DATA_DIR / "alert_config.json"
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text())
        except Exception:
            pass
    return ALERT_DEFAULTS.copy()


def save_alert_config(cfg: dict):
    (DATA_DIR / "alert_config.json").write_text(json.dumps(cfg, indent=2))


def send_desktop_notification(title: str, body: str, urgency: str = "critical"):
    """Envía notificación de escritorio Ubuntu via notify-send."""
    try:
        subprocess.Popen(
            ["notify-send", "-u", urgency, "-a", "WiFi Monitor", title, body],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception:
        pass


def log_alert(msg: str):
    with open(ALERTS_LOG, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {msg}\n")


def check_and_fire_alerts(wifi_info: dict, lat_data: dict | None = None) -> list:
    """Evalúa umbrales y dispara alertas si se superan. Retorna lista de alertas activas."""
    cfg = load_alert_config()
    if not cfg.get("enabled"):
        return []

    fired = []
    sig = wifi_info.get("signal")

    # Alerta de señal baja
    if isinstance(sig, int) and sig < cfg["signal_threshold"]:
        msg = f"Señal WiFi baja: {sig} dBm (umbral {cfg['signal_threshold']} dBm)"
        fired.append(("🔴 Señal baja", msg))
        send_desktop_notification("📡 WiFi Monitor — Señal Baja", msg)
        log_alert(msg)

    # Alertas de latencia
    if lat_data and lat_data.get("avg_ms"):
        if lat_data["avg_ms"] > cfg["latency_threshold"]:
            msg = f"Latencia alta: {lat_data['avg_ms']:.0f} ms (umbral {cfg['latency_threshold']} ms)"
            fired.append(("🟡 Latencia alta", msg))
            send_desktop_notification("📡 WiFi Monitor — Latencia Alta", msg, "normal")
            log_alert(msg)
        if lat_data["packet_loss"] > cfg["loss_threshold"]:
            msg = f"Pérdida de paquetes: {lat_data['packet_loss']}% (umbral {cfg['loss_threshold']}%)"
            fired.append(("🔴 Pérdida paquetes", msg))
            send_desktop_notification("📡 WiFi Monitor — Paquetes Perdidos", msg)
            log_alert(msg)

    return fired


# ══════════════════════════════════════════════
#  NUEVA: HISTORIAL CSV (7 DÍAS)
# ══════════════════════════════════════════════

CSV_FIELDS = ["timestamp", "ssid", "signal_dbm", "channel", "freq_ghz",
              "bytes_sent", "bytes_recv", "upload_kb_s", "download_kb_s"]


def append_traffic_record(wifi: dict, stats: dict, upload_kb: float, download_kb: float):
    """Agrega una fila al CSV y purga registros > 7 días."""
    row = {
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ssid":         wifi.get("ssid", ""),
        "signal_dbm":   wifi.get("signal", ""),
        "channel":      wifi.get("channel", ""),
        "freq_ghz":     wifi.get("freq", ""),
        "bytes_sent":   stats.get("bytes_sent", 0),
        "bytes_recv":   stats.get("bytes_recv", 0),
        "upload_kb_s":  round(upload_kb, 2),
        "download_kb_s": round(download_kb, 2),
    }
    file_exists = TRAFFIC_CSV.exists()
    with open(TRAFFIC_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
    purge_old_records()


def purge_old_records():
    """Elimina filas con más de 7 días del CSV."""
    if not TRAFFIC_CSV.exists():
        return
    try:
        df = pd.read_csv(TRAFFIC_CSV, parse_dates=["timestamp"])
        cutoff = datetime.now() - timedelta(days=7)
        df = df[df["timestamp"] >= cutoff]
        df.to_csv(TRAFFIC_CSV, index=False)
    except Exception:
        pass


def load_traffic_history() -> pd.DataFrame:
    if not TRAFFIC_CSV.exists():
        return pd.DataFrame(columns=CSV_FIELDS)
    try:
        df = pd.read_csv(TRAFFIC_CSV, parse_dates=["timestamp"])
        return df.sort_values("timestamp")
    except Exception:
        return pd.DataFrame(columns=CSV_FIELDS)


# ══════════════════════════════════════════════
#  NUEVA: TEST DE VELOCIDAD REAL
# ══════════════════════════════════════════════

def run_speedtest() -> dict:
    """
    Ejecuta speedtest-cli como subproceso para no bloquear Streamlit.
    Retorna dict con download_mbps, upload_mbps, ping_ms, server.
    """
    try:
        r = subprocess.run(
            ["speedtest-cli", "--simple", "--secure"],
            capture_output=True, text=True, timeout=90
        )
        out = r.stdout
        result = {}
        m = re.search(r"Ping:\s*([\d.]+)\s*ms", out)
        if m:
            result["ping_ms"] = float(m.group(1))
        m = re.search(r"Download:\s*([\d.]+)\s*Mbit/s", out)
        if m:
            result["download_mbps"] = float(m.group(1))
        m = re.search(r"Upload:\s*([\d.]+)\s*Mbit/s", out)
        if m:
            result["upload_mbps"] = float(m.group(1))
        result["timestamp"] = datetime.now().strftime("%H:%M:%S")
        result["success"] = bool(result.get("download_mbps"))
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ══════════════════════════════════════════════
#  NUEVA: DETECTOR DE INTRUSOS
# ══════════════════════════════════════════════

def load_known_devices() -> dict:
    """Carga la lista blanca de MACs conocidas."""
    if KNOWN_MACS_JSON.exists():
        try:
            return json.loads(KNOWN_MACS_JSON.read_text())
        except Exception:
            pass
    return {}


def save_known_devices(devices: dict):
    KNOWN_MACS_JSON.write_text(json.dumps(devices, indent=2, ensure_ascii=False))


def approve_device(mac: str, label: str):
    known = load_known_devices()
    known[mac.upper()] = {"label": label, "approved_at": datetime.now().strftime("%Y-%m-%d %H:%M")}
    save_known_devices(known)


def remove_device(mac: str):
    known = load_known_devices()
    known.pop(mac.upper(), None)
    save_known_devices(known)


def classify_devices(scanned: list) -> tuple:
    """Separa dispositivos en conocidos e intrusos."""
    known = load_known_devices()
    trusted, intruders = [], []
    for d in scanned:
        mac = d.get("mac", "N/A").upper()
        if d.get("is_this_pc") or mac in known:
            label = known.get(mac, {}).get("label", "Este PC" if d.get("is_this_pc") else "")
            trusted.append({**d, "label": label})
        else:
            intruders.append(d)
    return trusted, intruders


# ══════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════

with st.sidebar:
    st.title("📡 WiFi Monitor v2")
    st.caption(f"Host: **{platform.node()}** | {platform.system()} {platform.release()}")
    st.divider()

    page = st.radio(
        "Sección",
        ["🏠 Resumen", "📱 Dispositivos", "🔐 Intrusos",
         "🎬 Diagnóstico Video", "⚡ Velocidad", "📊 Historial", "🔔 Alertas"],
        label_visibility="collapsed"
    )
    st.divider()

    # ── Contraseña sudo (para arp-scan) ──────────────────────────────────
    with st.expander("🔑 Contraseña sudo", expanded=False):
        st.caption(
            "Necesaria para escanear dispositivos con **arp-scan**. "
            "No se almacena en disco."
        )
        sudo_pwd = st.text_input(
            "Contraseña del sistema",
            type="password",
            key="sudo_password",
            placeholder="Tu contraseña de Ubuntu",
        )
        if sudo_pwd:
            st.success("✅ Contraseña lista")
        else:
            st.warning("Sin contraseña — se usará fallback (ping sweep)")
    st.divider()

    auto_refresh = st.toggle("Auto-refresh (15s)", value=False)
    if auto_refresh:
        time.sleep(15)
        st.rerun()

    # Mini-estado en sidebar
    wifi_sb = get_wifi_info()
    sig_sb  = wifi_sb.get("signal")
    if isinstance(sig_sb, int):
        icon = "🟢" if sig_sb > -60 else ("🟡" if sig_sb > -75 else "🔴")
        st.caption(f"{icon} {wifi_sb.get('ssid', 'N/A')}  {sig_sb} dBm")
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")


# ══════════════════════════════════════════════
#  PÁGINA: RESUMEN
# ══════════════════════════════════════════════
if page == "🏠 Resumen":
    st.title("🏠 Resumen de Red")

    wifi  = get_wifi_info()
    iface = get_wifi_interface()
    my_ip = get_local_ip()
    stats = get_network_stats()

    sig = wifi.get("signal", "N/A")
    if isinstance(sig, int):
        sig_pct  = max(0, min(100, 2 * (sig + 100)))
        sig_text = f"{sig} dBm ({sig_pct}%)"
        sig_icon = "🟢" if sig > -60 else ("🟡" if sig > -75 else "🔴")
    else:
        sig_pct, sig_text, sig_icon = 0, "N/A", "⚪"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📶 Red (SSID)", wifi.get("ssid", "N/A"))
    c2.metric(f"{sig_icon} Señal", sig_text)
    c3.metric("📍 Tu IP", my_ip)
    c4.metric("🔌 Interfaz", iface)

    st.divider()
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("📺 Frecuencia", wifi.get("freq", "N/A"))
    c6.metric("📡 Canal", wifi.get("channel", "N/A"))
    c7.metric("⬆️ Enviado", bytes_to_human(stats.get("bytes_sent", 0)))
    c8.metric("⬇️ Recibido", bytes_to_human(stats.get("bytes_recv", 0)))

    # Alertas automáticas en resumen
    cfg = load_alert_config()
    if cfg.get("enabled"):
        fired = check_and_fire_alerts(wifi)
        for title, msg in fired:
            st.error(f"**{title}** — {msg}")

    st.divider()
    col_lat, col_gauge = st.columns([1, 1])

    with col_lat:
        st.subheader("⚡ Test de Latencia Rápido")
        if st.button("Medir latencia (8.8.8.8)"):
            with st.spinner("Midiendo…"):
                result = measure_latency("8.8.8.8", count=5)
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Promedio", f"{result['avg_ms']:.1f} ms" if result["avg_ms"] else "Error")
            r2.metric("Mínimo",   f"{result['min_ms']:.1f} ms" if result["min_ms"] else "—")
            r3.metric("Máximo",   f"{result['max_ms']:.1f} ms" if result["max_ms"] else "—")
            r4.metric("Pérdida",  f"{result['packet_loss']}%")
            # Alertas de latencia
            alerts = check_and_fire_alerts(wifi, result)
            for t, m in alerts:
                st.warning(f"**{t}**: {m}")

    with col_gauge:
        if isinstance(sig, int):
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sig_pct,
                title={"text": "Calidad de señal WiFi"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar":  {"color": "#3b82f6"},
                    "steps": [
                        {"range": [0,  30],  "color": "#ef4444"},
                        {"range": [30, 60],  "color": "#f59e0b"},
                        {"range": [60, 100], "color": "#10b981"},
                    ],
                },
                number={"suffix": "%"},
            ))
            fig.update_layout(
                height=250, paper_bgcolor="rgba(0,0,0,0)",
                font={"color": "white"}, margin=dict(t=40, b=10, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════
#  PÁGINA: DISPOSITIVOS
# ══════════════════════════════════════════════
elif page == "📱 Dispositivos":
    st.title("📱 Dispositivos Conectados")

    col_btn, col_note = st.columns([1, 3])
    scan_btn = col_btn.button("🔍 Escanear red ahora", type="primary")
    col_note.info("El primer escaneo puede tardar ~15–30 s.")

    if scan_btn or "devices" in st.session_state:
        if scan_btn:
            scan_network.clear()
            with st.spinner("Escaneando red…"):
                devices = scan_network(st.session_state.get("sudo_password", ""))
            st.session_state["devices"] = devices
        else:
            devices = st.session_state["devices"]

        st.success(f"✅ {len(devices)} dispositivo(s) encontrado(s)")

        if devices:
            df = pd.DataFrame(devices)
            df["Este PC"]    = df["is_this_pc"].map({True: "⭐", False: ""})
            df["latency_str"] = df["latency"].apply(lambda x: f"{x:.0f} ms" if x else "—")
            show = df[["ip", "mac", "vendor", "hostname", "latency_str", "Este PC"]].copy()
            show.columns = ["IP", "MAC", "Fabricante", "Hostname", "Latencia", "Este PC"]
            st.dataframe(show, use_container_width=True, hide_index=True)

            vc = df["vendor"].value_counts().reset_index()
            vc.columns = ["Fabricante", "Cantidad"]
            fig = px.pie(vc, names="Fabricante", values="Cantidad",
                         title="Dispositivos por fabricante",
                         color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"},
                              height=300, margin=dict(t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Presiona **Escanear red ahora** para ver los dispositivos.")


# ══════════════════════════════════════════════
#  PÁGINA: INTRUSOS
# ══════════════════════════════════════════════
elif page == "🔐 Intrusos":
    st.title("🔐 Detector de Intrusos")
    st.markdown(
        "La app **aprende** cuáles son tus dispositivos. "
        "Los que no estén aprobados aparecen como **intrusos**."
    )

    col_scan, col_info = st.columns([1, 3])
    do_scan = col_scan.button("🔍 Escanear ahora", type="primary")
    col_info.info(
        "La primera vez todos aparecerán como desconocidos. "
        "Apruébalos con un nombre y la próxima vez serán reconocidos."
    )

    if do_scan or "devices" in st.session_state:
        if do_scan:
            scan_network.clear()
            with st.spinner("Escaneando…"):
                devices = scan_network(st.session_state.get("sudo_password", ""))
            st.session_state["devices"] = devices
        else:
            devices = st.session_state["devices"]

        trusted, intruders = classify_devices(devices)

        # ── Intrusos ─────────────────────────────────────────────────────
        st.subheader(f"🚨 Dispositivos desconocidos ({len(intruders)})")
        if not intruders:
            st.success("✅ No hay dispositivos desconocidos en tu red.")
        else:
            st.error(f"Se encontraron **{len(intruders)}** dispositivo(s) no reconocidos.")
            for d in intruders:
                with st.expander(f"❓ {d['ip']}  —  {d['mac']}  ({d['vendor']})"):
                    st.write(f"**Hostname:** {d['hostname']}")
                    st.write(f"**Latencia:** {d['latency']:.0f} ms" if d['latency'] else "")
                    label = st.text_input(
                        "Nombre para este dispositivo",
                        placeholder="ej: Celular Omar, Smart TV, Laptop Invitado",
                        key=f"label_{d['mac']}"
                    )
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Aprobar y guardar", key=f"approve_{d['mac']}"):
                        approve_device(d["mac"], label or d["vendor"])
                        send_desktop_notification(
                            "📡 WiFi Monitor — Dispositivo Aprobado",
                            f"{label or d['mac']} agregado a la lista blanca"
                        )
                        st.rerun()
                    if c2.button("🚫 Ignorar por ahora", key=f"ignore_{d['mac']}"):
                        st.info("Ignorado. Aparecerá de nuevo en el próximo escaneo.")

        st.divider()

        # ── Dispositivos conocidos ────────────────────────────────────────
        st.subheader(f"✅ Dispositivos conocidos ({len(trusted)})")
        known_db = load_known_devices()
        for d in trusted:
            mac = d["mac"].upper()
            label = d.get("label") or ("Este PC" if d.get("is_this_pc") else mac)
            approved_at = known_db.get(mac, {}).get("approved_at", "—")
            with st.expander(f"✅ {label}  —  {d['ip']}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**MAC:** {d['mac']}")
                col_a.write(f"**Fabricante:** {d['vendor']}")
                col_b.write(f"**Hostname:** {d['hostname']}")
                col_b.write(f"**Aprobado:** {approved_at}")
                if not d.get("is_this_pc"):
                    new_label = st.text_input("Renombrar", value=label, key=f"rename_{mac}")
                    cc1, cc2 = st.columns(2)
                    if cc1.button("💾 Guardar nombre", key=f"save_{mac}"):
                        approve_device(mac, new_label)
                        st.rerun()
                    if cc2.button("🗑️ Eliminar de lista blanca", key=f"del_{mac}"):
                        remove_device(mac)
                        st.rerun()

        # ── Log de alertas recientes ──────────────────────────────────────
        if ALERTS_LOG.exists():
            st.divider()
            with st.expander("📋 Log de alertas recientes"):
                lines = ALERTS_LOG.read_text().strip().splitlines()[-20:]
                for line in reversed(lines):
                    st.caption(line)


# ══════════════════════════════════════════════
#  PÁGINA: DIAGNÓSTICO VIDEO
# ══════════════════════════════════════════════
elif page == "🎬 Diagnóstico Video":
    st.title("🎬 ¿Por qué va lento mi video?")

    with st.expander("⚙️ Opciones"):
        test_host  = st.selectbox("Servidor de prueba",
            ["8.8.8.8 (Google DNS)", "1.1.1.1 (Cloudflare)", "208.67.222.222 (OpenDNS)"])
        ping_count = st.slider("Número de pings", 5, 20, 10)

    host_ip = test_host.split()[0]

    if st.button("🔬 Diagnosticar ahora", type="primary"):
        with st.spinner(f"Midiendo hacia {host_ip}…"):
            lat_data = measure_latency(host_ip, count=ping_count)

        diag = diagnose_streaming(lat_data)
        color_map = {"ok": "success", "warn": "warning", "bad": "error"}
        getattr(st, color_map[diag["color"]])(diag["verdict"])

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Diagnóstico")
            for issue in diag["issues"]:
                st.write(issue)
            if lat_data.get("avg_ms"):
                st.divider()
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Promedio",  f"{lat_data['avg_ms']:.1f} ms")
                m2.metric("Mínimo",    f"{lat_data['min_ms']:.1f} ms")
                m3.metric("Jitter",    f"{lat_data['jitter_ms']:.1f} ms")
                m4.metric("Pérdida",   f"{lat_data['packet_loss']}%")

        with col2:
            st.subheader("💡 Recomendaciones")
            for rec in diag["recommendations"]:
                st.info(rec)

        st.divider()
        st.subheader("📖 Referencia para streaming")
        ref = {
            "Métrica": ["Latencia", "Jitter", "Pérdida"],
            "✅ Excelente":    ["< 20 ms",  "< 5 ms",  "0%"],
            "🟡 Aceptable":    ["20–80 ms", "5–20 ms", "< 1%"],
            "🔴 Problemático": ["> 150 ms", "> 30 ms", "> 2%"],
        }
        st.table(pd.DataFrame(ref))

        with st.expander("📚 Si la red está bien, revisa también"):
            st.markdown("""
- 🌐 **Servidor saturado** — intenta en horario no pico
- 📊 **Plan de internet**: HD requiere ~8 Mbps, 4K ~25 Mbps
- 💻 **CPU/RAM** ocupado — cierra otras apps
- 🔄 **Actualizaciones en segundo plano**
- 🔒 **VPN activa** que añade latencia
            """)


# ══════════════════════════════════════════════
#  PÁGINA: TEST DE VELOCIDAD
# ══════════════════════════════════════════════
elif page == "⚡ Velocidad":
    st.title("⚡ Test de Velocidad Real")
    st.markdown(
        "Mide el ancho de banda real de tu conexión a internet "
        "usando servidores de **Speedtest.net**."
    )

    st.warning(
        "⏱️ El test tarda entre **30 y 60 segundos**. "
        "No cierres la página mientras corre."
    )

    if "speedtest_history" not in st.session_state:
        st.session_state.speedtest_history = []

    if st.button("🚀 Iniciar test de velocidad", type="primary"):
        progress = st.progress(0, text="Iniciando speedtest…")
        for i in range(1, 4):
            time.sleep(0.3)
            progress.progress(i * 10, text="Conectando al servidor más cercano…")

        with st.spinner("Midiendo descarga y subida…"):
            result = run_speedtest()
        progress.progress(100, text="¡Listo!")

        if result.get("success"):
            st.session_state.speedtest_history.append(result)

            dl = result["download_mbps"]
            ul = result["upload_mbps"]
            pi = result["ping_ms"]

            # Clasificación de velocidad
            def speed_label(mbps):
                if mbps >= 100: return "🟢 Excelente"
                if mbps >= 25:  return "🟡 Buena"
                if mbps >= 10:  return "🟠 Aceptable"
                return "🔴 Lenta"

            c1, c2, c3 = st.columns(3)
            c1.metric("⬇️ Descarga", f"{dl:.1f} Mbps", speed_label(dl))
            c2.metric("⬆️ Subida",   f"{ul:.1f} Mbps", speed_label(ul))
            c3.metric("🏓 Ping",     f"{pi:.0f} ms")

            # Referencia por uso
            st.divider()
            st.subheader("¿Para qué alcanza tu velocidad?")
            usos = [
                ("📧 Email / Navegación básica", 1,   dl >= 1),
                ("📺 Video HD (1080p)",           8,   dl >= 8),
                ("🎮 Gaming online",              15,  dl >= 15),
                ("🎬 4K Streaming",               25,  dl >= 25),
                ("👨‍👩‍👧 4K + varios usuarios",     50,  dl >= 50),
                ("☁️  Videollamadas 4K",          25,  dl >= 25),
            ]
            for label, req, ok in usos:
                icon = "✅" if ok else "❌"
                st.write(f"{icon} {label} (requiere {req} Mbps)")

        else:
            st.error(f"Error al correr el test: {result.get('error', 'Desconocido')}")
            st.info("Verifica que `speedtest-cli` esté instalado: `pip install speedtest-cli`")

    # Historial de tests en sesión
    if st.session_state.speedtest_history:
        st.divider()
        st.subheader("📈 Historial de tests (esta sesión)")
        hist_df = pd.DataFrame(st.session_state.speedtest_history)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=hist_df["timestamp"], y=hist_df["download_mbps"],
                             name="⬇️ Descarga", marker_color="#3b82f6"))
        fig.add_trace(go.Bar(x=hist_df["timestamp"], y=hist_df["upload_mbps"],
                             name="⬆️ Subida", marker_color="#10b981"))
        fig.update_layout(
            barmode="group", yaxis_title="Mbps",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.8)",
            font={"color": "white"}, height=300,
            margin=dict(t=20, b=30, l=50, r=20),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════
#  PÁGINA: HISTORIAL CSV
# ══════════════════════════════════════════════
elif page == "📊 Historial":
    st.title("📊 Historial de Red (7 días)")

    # Registrar muestra actual
    wifi  = get_wifi_info()
    stats = get_network_stats()
    prev  = st.session_state.get("prev_stats_hist")
    upload_kb = download_kb = 0.0
    if prev:
        upload_kb   = max(0, stats.get("bytes_sent", 0) - prev.get("bytes_sent", 0)) / 1024
        download_kb = max(0, stats.get("bytes_recv", 0) - prev.get("bytes_recv", 0)) / 1024
        append_traffic_record(wifi, stats, upload_kb, download_kb)
    st.session_state["prev_stats_hist"] = stats

    # También mantener historial en sesión para la gráfica en tiempo real
    if "traffic_history" not in st.session_state:
        st.session_state.traffic_history = []
    if prev:
        st.session_state.traffic_history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "upload_kb": round(upload_kb, 2),
            "download_kb": round(download_kb, 2),
        })
        if len(st.session_state.traffic_history) > 60:
            st.session_state.traffic_history.pop(0)

    # Métricas actuales
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⬇️ Total recibido", bytes_to_human(stats.get("bytes_recv", 0)))
    c2.metric("⬆️ Total enviado",  bytes_to_human(stats.get("bytes_sent", 0)))
    c3.metric("❌ Errores",         stats.get("errin", 0))
    c4.metric("📦 Paquetes perdidos", stats.get("dropin", 0))

    st.divider()

    # Gráfica en tiempo real (sesión)
    if st.session_state.traffic_history:
        df_rt = pd.DataFrame(st.session_state.traffic_history)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_rt["time"], y=df_rt["download_kb"],
                                 name="⬇️ Descarga (KB/s)", fill="tozeroy",
                                 line=dict(color="#3b82f6", width=2)))
        fig.add_trace(go.Scatter(x=df_rt["time"], y=df_rt["upload_kb"],
                                 name="⬆️ Subida (KB/s)", fill="tozeroy",
                                 line=dict(color="#10b981", width=2)))
        fig.update_layout(
            title="Tráfico en tiempo real (sesión actual)",
            xaxis_title="Hora", yaxis_title="KB/s",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.8)",
            font={"color": "white"}, height=300,
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=50, b=30, l=50, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Gráfica histórica CSV (7 días)
    df_hist = load_traffic_history()
    if not df_hist.empty and len(df_hist) > 1:
        st.subheader("📅 Últimos 7 días — tráfico acumulado")

        # Filtro de rango
        days = st.slider("Mostrar últimos N días", 1, 7, 7)
        cutoff = datetime.now() - timedelta(days=days)
        df_f = df_hist[df_hist["timestamp"] >= cutoff].copy()

        if not df_f.empty:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df_f["timestamp"], y=df_f["download_kb_s"],
                                      name="⬇️ Descarga KB/s", fill="tozeroy",
                                      line=dict(color="#3b82f6")))
            fig2.add_trace(go.Scatter(x=df_f["timestamp"], y=df_f["upload_kb_s"],
                                      name="⬆️ Subida KB/s", fill="tozeroy",
                                      line=dict(color="#10b981")))

            # Señal
            df_sig = df_f.dropna(subset=["signal_dbm"])
            if not df_sig.empty:
                fig2.add_trace(go.Scatter(
                    x=df_sig["timestamp"], y=df_sig["signal_dbm"],
                    name="📶 Señal dBm", yaxis="y2",
                    line=dict(color="#f59e0b", dash="dot")
                ))

            fig2.update_layout(
                xaxis_title="Fecha/Hora", yaxis_title="KB/s",
                yaxis2=dict(title="dBm", overlaying="y", side="right",
                            range=[-100, -20]),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.8)",
                font={"color": "white"}, height=380,
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=30, b=30, l=60, r=60),
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Tabla resumen
            st.subheader("📋 Resumen estadístico")
            summary = df_f[["download_kb_s", "upload_kb_s", "signal_dbm"]].describe().round(2)
            st.dataframe(summary, use_container_width=True)

            # Descargar CSV
            st.download_button(
                "⬇️ Descargar historial CSV",
                data=df_f.to_csv(index=False),
                file_name=f"wifi_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info(
            "El historial se construye automáticamente mientras la app está abierta. "
            f"Los datos se guardan en `{TRAFFIC_CSV}`"
        )

    if st.button("🔄 Actualizar"):
        st.rerun()


# ══════════════════════════════════════════════
#  PÁGINA: ALERTAS
# ══════════════════════════════════════════════
elif page == "🔔 Alertas":
    st.title("🔔 Configuración de Alertas")
    st.markdown(
        "Las alertas se envían como **notificación de escritorio Ubuntu** "
        "y como **banner rojo en la app**. También quedan registradas en el log."
    )

    cfg = load_alert_config()

    with st.form("alert_form"):
        st.subheader("⚙️ Umbrales")
        enabled = st.toggle("Alertas activadas", value=cfg.get("enabled", True))

        c1, c2, c3 = st.columns(3)
        sig_thr  = c1.slider("Señal mínima (dBm)",   -90, -50, cfg["signal_threshold"])
        lat_thr  = c2.slider("Latencia máxima (ms)",  50, 500, cfg["latency_threshold"])
        loss_thr = c3.slider("Pérdida máx (%)",         1,  50, cfg["loss_threshold"])

        submitted = st.form_submit_button("💾 Guardar configuración", type="primary")
        if submitted:
            new_cfg = {
                "enabled": enabled,
                "signal_threshold": sig_thr,
                "latency_threshold": lat_thr,
                "loss_threshold": loss_thr,
            }
            save_alert_config(new_cfg)
            st.success("✅ Configuración guardada.")

    st.divider()

    # Test manual de alertas
    st.subheader("🧪 Probar alertas")
    if st.button("Enviar notificación de prueba al escritorio"):
        send_desktop_notification(
            "📡 WiFi Monitor — Prueba",
            "Las notificaciones de escritorio funcionan correctamente ✅"
        )
        st.success("Notificación enviada. Revisa el área de notificaciones de Ubuntu.")

    st.divider()

    # Log de alertas
    st.subheader("📋 Log de alertas")
    if ALERTS_LOG.exists():
        lines = ALERTS_LOG.read_text().strip().splitlines()
        if lines:
            df_log = pd.DataFrame(
                [l.split(" | ", 1) for l in lines if " | " in l],
                columns=["Fecha/Hora", "Mensaje"]
            )
            st.dataframe(df_log.iloc[::-1], use_container_width=True, hide_index=True)
            if st.button("🗑️ Limpiar log"):
                ALERTS_LOG.write_text("")
                st.rerun()
        else:
            st.info("Sin alertas registradas aún.")
    else:
        st.info("Sin alertas registradas aún.")

    st.divider()
    st.subheader("ℹ️ ¿Cómo funcionan las notificaciones de escritorio?")
    st.markdown("""
La app usa `notify-send` (incluido en Ubuntu por defecto).

Si no ves las notificaciones, ejecuta en terminal:
```bash
sudo apt install libnotify-bin
```
Y asegúrate de que la app corra en la **misma sesión gráfica** (no por SSH sin `-X`).
    """)
