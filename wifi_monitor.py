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
import sys
import threading
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from i18n import t, LANGUAGES, DEFAULT_LANG

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
# IDIOMA (i18n)
# ─────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state["lang"] = DEFAULT_LANG
lang = st.session_state["lang"]

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
        return t("na", lang)


# Respaldo mínimo embebido por si faltara el archivo oui_db.json.
# El nombre del fabricante es un nombre propio: NO se traduce.
_FALLBACK_OUI = {
    "B8:27:EB": "Raspberry Pi", "DC:A6:32": "Raspberry Pi",
    "3C:22:FB": "Apple",    "F0:18:98": "Apple",
    "70:85:C2": "Apple",    "AC:BC:32": "Apple",
    "F0:9F:C2": "Ubiquiti", "24:A4:3C": "Ubiquiti",
    "DC:9F:DB": "TP-Link",  "50:C7:BF": "TP-Link",
    "00:50:56": "VMware",   "00:0C:29": "VMware",
}


def _oui_db_path() -> Path:
    """Ubica oui_db.json tanto en ejecución normal como dentro del bundle PyInstaller."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        p = Path(base) / "oui_db.json"
        if p.exists():
            return p
    return Path(__file__).resolve().parent / "oui_db.json"


@st.cache_resource
def _load_oui_db() -> dict:
    """Carga la base de datos IEEE (prefijo OUI -> fabricante) una sola vez."""
    try:
        return json.loads(_oui_db_path().read_text(encoding="utf-8"))
    except Exception:
        return {}


def guess_vendor(mac: str) -> str:
    # El nombre del fabricante NO depende del idioma; sólo el texto
    # "Desconocido" (cuando no se identifica) se traduce.
    if not mac or mac in ("N/A", "(incomplete)", ""):
        return t("unknown", lang)
    oui = mac.upper().replace("-", ":")[0:8]
    db = _load_oui_db()
    name = db.get(oui) or _FALLBACK_OUI.get(oui)
    return name if name else t("unknown", lang)


def best_vendor(mac: str, arp_vendor: str = "") -> str:
    """
    Elige el mejor nombre de fabricante. Nuestra base IEEE (oui_db.json)
    es autoritativa; el valor que entrega arp-scan se usa SOLO como
    respaldo, y nunca cuando dice "(Unknown)" (su base local suele estar
    vacía o desactualizada en el runner/sistema del usuario).
    """
    v = guess_vendor(mac)
    if v != t("unknown", lang):
        return v
    arp_vendor = (arp_vendor or "").strip()
    if arp_vendor and "unknown" not in arp_vendor.lower() and arp_vendor != "(incomplete)":
        return arp_vendor
    return t("unknown", lang)


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
                    vendor = best_vendor(mac, parts[2] if len(parts) > 2 else "")
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
        return {"verdict": t("diag_no_data_verdict", lang), "cause": "Sin conexión",
                "color": "bad", "issues": [t("diag_no_connection_issue", lang)],
                "recommendations": [t("diag_check_wifi_rec", lang)]}

    if loss > 5:
        issues.append(t("diag_high_loss_issue", lang, loss=loss))
    if avg > 150:
        issues.append(t("diag_high_latency_issue", lang, avg=avg))
    if jitter and jitter > 30:
        issues.append(t("diag_high_jitter_issue", lang, jitter=jitter))

    if not issues:
        return {"verdict": t("diag_ok_verdict", lang),
                "cause": "otro", "color": "ok", "issues": [t("diag_no_issues_label", lang)],
                "recommendations": [
                    t("diag_ok_rec_1", lang),
                    t("diag_ok_rec_2", lang),
                ]}
    elif loss > 10 or avg > 200:
        return {"verdict": t("diag_bad_verdict", lang),
                "cause": "red", "color": "bad", "issues": issues,
                "recommendations": [
                    t("diag_bad_rec_1", lang),
                    t("diag_bad_rec_2", lang),
                    t("diag_bad_rec_3", lang),
                    t("diag_bad_rec_4", lang),
                ]}
    else:
        return {"verdict": t("diag_warn_verdict", lang),
                "cause": "red", "color": "warn", "issues": issues,
                "recommendations": [
                    t("diag_warn_rec_1", lang),
                    t("diag_warn_rec_2", lang),
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
        msg = t("alert_low_signal_msg", lang, sig=sig, threshold=cfg["signal_threshold"])
        fired.append((t("alert_low_signal_title", lang), msg))
        send_desktop_notification(t("alert_desktop_low_signal_title", lang), msg)
        log_alert(msg)

    # Alertas de latencia
    if lat_data and lat_data.get("avg_ms"):
        if lat_data["avg_ms"] > cfg["latency_threshold"]:
            msg = t("alert_high_latency_msg", lang, lat=lat_data["avg_ms"], threshold=cfg["latency_threshold"])
            fired.append((t("alert_high_latency_title", lang), msg))
            send_desktop_notification(t("alert_desktop_high_latency_title", lang), msg, "normal")
            log_alert(msg)
        if lat_data["packet_loss"] > cfg["loss_threshold"]:
            msg = t("alert_packet_loss_msg", lang, loss=lat_data["packet_loss"], threshold=cfg["loss_threshold"])
            fired.append((t("alert_packet_loss_title", lang), msg))
            send_desktop_notification(t("alert_desktop_packet_loss_title", lang), msg)
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
    Ejecuta el test de velocidad usando la librería 'speedtest' (speedtest-cli)
    como módulo de Python, en lugar de invocar el ejecutable 'speedtest-cli'
    por PATH (que no existe dentro del bundle de PyInstaller y provoca
    'No existe el archivo o directorio: speedtest-cli').
    Retorna dict con download_mbps, upload_mbps, ping_ms, server.
    """
    try:
        import speedtest  # del paquete speedtest-cli
        s = speedtest.Speedtest(secure=True)
        s.get_best_server()
        download = s.download() / 1_000_000   # bits/s -> Mbit/s
        upload   = s.upload() / 1_000_000
        res = s.results.dict()
        return {
            "success": True,
            "ping_ms": round(res.get("ping", 0.0), 1),
            "download_mbps": round(download, 2),
            "upload_mbps": round(upload, 2),
            "server": (res.get("server") or {}).get("sponsor", ""),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
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
            label = known.get(mac, {}).get("label", t("this_pc", lang) if d.get("is_this_pc") else "")
            trusted.append({**d, "label": label})
        else:
            intruders.append(d)
    return trusted, intruders


# ══════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════

with st.sidebar:
    st.title(t("app_title", lang))
    st.caption(t("host_caption", lang, host=platform.node(), system=platform.system(), release=platform.release()))
    st.divider()

    lang_codes = list(LANGUAGES.keys())
    selected_lang = st.selectbox(
        t("language_label", lang),
        options=lang_codes,
        format_func=lambda code: LANGUAGES[code],
        index=lang_codes.index(st.session_state["lang"]),
    )
    if selected_lang != st.session_state["lang"]:
        st.session_state["lang"] = selected_lang
        st.rerun()

    st.divider()

    page = st.radio(
        t("section_label", lang),
        [t("nav_summary", lang), t("nav_devices", lang), t("nav_intruders", lang),
         t("nav_video", lang), t("nav_speed", lang), t("nav_history", lang), t("nav_alerts", lang)],
        label_visibility="collapsed"
    )
    st.divider()

    # ── Contraseña sudo (para arp-scan) ──────────────────────────────────
    with st.expander(t("sudo_password_expander", lang), expanded=False):
        st.caption(t("sudo_password_help", lang))
        sudo_pwd = st.text_input(
            t("sudo_password_input", lang),
            type="password",
            key="sudo_password",
            placeholder=t("sudo_password_placeholder", lang),
        )
        if sudo_pwd:
            st.success(t("sudo_password_ready", lang))
        else:
            st.warning(t("sudo_password_missing", lang))
    st.divider()

    auto_refresh = st.toggle(t("auto_refresh", lang), value=False)
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
if page == t("nav_summary", lang):
    st.title(t("summary_title", lang))

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
        sig_pct, sig_text, sig_icon = 0, t("na", lang), "⚪"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("metric_ssid", lang), wifi.get("ssid", "N/A"))
    c2.metric(f"{sig_icon} {t('metric_signal', lang)}", sig_text)
    c3.metric(t("metric_your_ip", lang), my_ip)
    c4.metric(t("metric_interface", lang), iface)

    st.divider()
    c5, c6, c7, c8 = st.columns(4)
    c5.metric(t("metric_frequency", lang), wifi.get("freq", "N/A"))
    c6.metric(t("metric_channel", lang), wifi.get("channel", "N/A"))
    c7.metric(t("metric_sent", lang), bytes_to_human(stats.get("bytes_sent", 0)))
    c8.metric(t("metric_received", lang), bytes_to_human(stats.get("bytes_recv", 0)))

    # Alertas automáticas en resumen
    cfg = load_alert_config()
    if cfg.get("enabled"):
        fired = check_and_fire_alerts(wifi)
        for title, msg in fired:
            st.error(f"**{title}** — {msg}")

    st.divider()
    col_lat, col_gauge = st.columns([1, 1])

    with col_lat:
        st.subheader(t("latency_test_subheader", lang))
        if st.button(t("measure_latency_btn", lang)):
            with st.spinner(t("measuring", lang)):
                result = measure_latency("8.8.8.8", count=5)
            r1, r2, r3, r4 = st.columns(4)
            r1.metric(t("metric_average", lang), f"{result['avg_ms']:.1f} ms" if result["avg_ms"] else t("error_word", lang))
            r2.metric(t("metric_minimum", lang),   f"{result['min_ms']:.1f} ms" if result["min_ms"] else "—")
            r3.metric(t("metric_maximum", lang),   f"{result['max_ms']:.1f} ms" if result["max_ms"] else "—")
            r4.metric(t("metric_loss", lang),  f"{result['packet_loss']}%")
            # Alertas de latencia
            alerts = check_and_fire_alerts(wifi, result)
            for tt, m in alerts:
                st.warning(f"**{tt}**: {m}")

    with col_gauge:
        if isinstance(sig, int):
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sig_pct,
                title={"text": t("signal_gauge_title", lang),
                       "font": {"color": "#e5edff", "size": 16}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#cbd5e1",
                             "tickfont": {"color": "#cbd5e1"}},
                    "bar":  {"color": "#3b82f6"},
                    "bgcolor": "#0d2137",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0,  30],  "color": "#ef4444"},
                        {"range": [30, 60],  "color": "#f59e0b"},
                        {"range": [60, 100], "color": "#10b981"},
                    ],
                },
                # Color del número (porcentaje) explícito y siempre legible
                # sobre el panel oscuro, sin depender del tema del sistema.
                number={"suffix": "%", "font": {"color": "#ffffff", "size": 40}},
            ))
            # paper_bgcolor con un color sólido oscuro (no transparente) para
            # que el porcentaje en blanco SIEMPRE se vea, aunque el sistema
            # del usuario tenga el tema claro y el fondo de la página sea blanco.
            fig.update_layout(
                height=250, paper_bgcolor="#0d2137",
                font={"color": "#ffffff"}, margin=dict(t=50, b=10, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════
#  PÁGINA: DISPOSITIVOS
# ══════════════════════════════════════════════
elif page == t("nav_devices", lang):
    st.title(t("devices_title", lang))

    col_btn, col_note = st.columns([1, 3])
    scan_btn = col_btn.button(t("scan_now_btn", lang), type="primary")
    col_note.info(t("scan_first_time_note", lang))

    if scan_btn or "devices" in st.session_state:
        if scan_btn:
            scan_network.clear()
            with st.spinner(t("scanning_network", lang)):
                devices = scan_network(st.session_state.get("sudo_password", ""))
            st.session_state["devices"] = devices
        else:
            devices = st.session_state["devices"]

        st.success(t("devices_found", lang, count=len(devices)))

        if devices:
            df = pd.DataFrame(devices)
            df["Este PC"]    = df["is_this_pc"].map({True: "⭐", False: ""})
            df["latency_str"] = df["latency"].apply(lambda x: f"{x:.0f} ms" if x else "—")
            show = df[["ip", "mac", "vendor", "hostname", "latency_str", "Este PC"]].copy()
            show.columns = [t("col_ip", lang), t("col_mac", lang), t("col_vendor", lang),
                             t("col_hostname", lang), t("col_latency", lang), t("col_this_pc", lang)]
            st.dataframe(show, use_container_width=True, hide_index=True)

            vc = df["vendor"].value_counts().reset_index()
            vc.columns = [t("col_vendor", lang), t("col_count", lang)]
            fig = px.pie(vc, names=t("col_vendor", lang), values=t("col_count", lang),
                         title=t("devices_by_vendor_chart", lang),
                         color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"},
                              height=300, margin=dict(t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(t("press_scan_hint", lang))


# ══════════════════════════════════════════════
#  PÁGINA: INTRUSOS
# ══════════════════════════════════════════════
elif page == t("nav_intruders", lang):
    st.title(t("intruders_title", lang))
    st.markdown(t("intruders_intro", lang))

    col_scan, col_info = st.columns([1, 3])
    do_scan = col_scan.button(t("scan_now_short_btn", lang), type="primary")
    col_info.info(t("intruders_first_scan_note", lang))

    if do_scan or "devices" in st.session_state:
        if do_scan:
            scan_network.clear()
            with st.spinner(t("scanning", lang)):
                devices = scan_network(st.session_state.get("sudo_password", ""))
            st.session_state["devices"] = devices
        else:
            devices = st.session_state["devices"]

        trusted, intruders = classify_devices(devices)

        # ── Intrusos ─────────────────────────────────────────────────────
        st.subheader(t("unknown_devices_subheader", lang, count=len(intruders)))
        if not intruders:
            st.success(t("no_unknown_devices", lang))
        else:
            st.error(t("unknown_devices_found", lang, count=len(intruders)))
            for d in intruders:
                with st.expander(f"❓ {d['ip']}  —  {d['mac']}  ({d['vendor']})"):
                    st.write(f"{t('hostname_label', lang)} {d['hostname']}")
                    st.write(f"{t('latency_label', lang)} {d['latency']:.0f} ms" if d['latency'] else "")
                    label = st.text_input(
                        t("device_name_input", lang),
                        placeholder=t("device_name_placeholder", lang),
                        key=f"label_{d['mac']}"
                    )
                    c1, c2 = st.columns(2)
                    if c1.button(t("approve_save_btn", lang), key=f"approve_{d['mac']}"):
                        approve_device(d["mac"], label or d["vendor"])
                        send_desktop_notification(
                            t("alert_device_approved_title", lang),
                            t("alert_device_approved_msg", lang, label=label or d["mac"])
                        )
                        st.rerun()
                    if c2.button(t("ignore_for_now_btn", lang), key=f"ignore_{d['mac']}"):
                        st.info(t("ignored_will_reappear", lang))

        st.divider()

        # ── Dispositivos conocidos ────────────────────────────────────────
        st.subheader(t("known_devices_subheader", lang, count=len(trusted)))
        known_db = load_known_devices()
        for d in trusted:
            mac = d["mac"].upper()
            label = d.get("label") or (t("this_pc", lang) if d.get("is_this_pc") else mac)
            approved_at = known_db.get(mac, {}).get("approved_at", "—")
            with st.expander(f"✅ {label}  —  {d['ip']}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**MAC:** {d['mac']}")
                col_a.write(f"{t('vendor_label', lang)} {d['vendor']}")
                col_b.write(f"{t('hostname_label', lang)} {d['hostname']}")
                col_b.write(f"{t('approved_at_label', lang)} {approved_at}")
                if not d.get("is_this_pc"):
                    new_label = st.text_input(t("rename_input", lang), value=label, key=f"rename_{mac}")
                    cc1, cc2 = st.columns(2)
                    if cc1.button(t("save_name_btn", lang), key=f"save_{mac}"):
                        approve_device(mac, new_label)
                        st.rerun()
                    if cc2.button(t("remove_from_list_btn", lang), key=f"del_{mac}"):
                        remove_device(mac)
                        st.rerun()

        # ── Log de alertas recientes ──────────────────────────────────────
        if ALERTS_LOG.exists():
            st.divider()
            with st.expander(t("recent_alerts_log_expander", lang)):
                lines = ALERTS_LOG.read_text().strip().splitlines()[-20:]
                for line in reversed(lines):
                    st.caption(line)


# ══════════════════════════════════════════════
#  PÁGINA: DIAGNÓSTICO VIDEO
# ══════════════════════════════════════════════
elif page == t("nav_video", lang):
    st.title(t("video_title", lang))

    with st.expander(t("options_expander", lang)):
        test_host  = st.selectbox(t("test_server_select", lang),
            ["8.8.8.8 (Google DNS)", "1.1.1.1 (Cloudflare)", "208.67.222.222 (OpenDNS)"])
        ping_count = st.slider(t("ping_count_slider", lang), 5, 20, 10)

    host_ip = test_host.split()[0]

    if st.button(t("diagnose_now_btn", lang), type="primary"):
        with st.spinner(t("measuring_towards", lang, host=host_ip)):
            lat_data = measure_latency(host_ip, count=ping_count)

        diag = diagnose_streaming(lat_data)
        color_map = {"ok": "success", "warn": "warning", "bad": "error"}
        getattr(st, color_map[diag["color"]])(diag["verdict"])

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(t("diagnosis_subheader", lang))
            for issue in diag["issues"]:
                st.write(issue)
            if lat_data.get("avg_ms"):
                st.divider()
                m1, m2, m3, m4 = st.columns(4)
                m1.metric(t("metric_average", lang),  f"{lat_data['avg_ms']:.1f} ms")
                m2.metric(t("metric_minimum", lang),    f"{lat_data['min_ms']:.1f} ms")
                m3.metric(t("metric_jitter", lang),    f"{lat_data['jitter_ms']:.1f} ms")
                m4.metric(t("metric_loss", lang),   f"{lat_data['packet_loss']}%")

        with col2:
            st.subheader(t("recommendations_subheader", lang))
            for rec in diag["recommendations"]:
                st.info(rec)

        st.divider()
        st.subheader(t("streaming_reference_subheader", lang))
        ref = {
            t("ref_metric_col", lang): [t("ref_latency_row", lang), t("ref_jitter_row", lang), t("ref_loss_row", lang)],
            t("ref_excellent_col", lang):    ["< 20 ms",  "< 5 ms",  "0%"],
            t("ref_acceptable_col", lang):    ["20–80 ms", "5–20 ms", "< 1%"],
            t("ref_problematic_col", lang): ["> 150 ms", "> 30 ms", "> 2%"],
        }
        st.table(pd.DataFrame(ref))

        with st.expander(t("video_other_checks_expander", lang)):
            st.markdown(t("video_other_checks_body", lang))


# ══════════════════════════════════════════════
#  PÁGINA: TEST DE VELOCIDAD
# ══════════════════════════════════════════════
elif page == t("nav_speed", lang):
    st.title(t("speed_title", lang))
    st.markdown(t("speed_intro", lang))

    st.warning(t("speed_warning", lang))

    if "speedtest_history" not in st.session_state:
        st.session_state.speedtest_history = []

    if st.button(t("start_speedtest_btn", lang), type="primary"):
        progress = st.progress(0, text=t("starting_speedtest", lang))
        for i in range(1, 4):
            time.sleep(0.3)
            progress.progress(i * 10, text=t("connecting_server", lang))

        with st.spinner(t("measuring_up_down", lang)):
            result = run_speedtest()
        progress.progress(100, text=t("ready", lang))

        if result.get("success"):
            st.session_state.speedtest_history.append(result)

            dl = result["download_mbps"]
            ul = result["upload_mbps"]
            pi = result["ping_ms"]

            # Clasificación de velocidad
            def speed_label(mbps):
                if mbps >= 100: return t("speed_excellent", lang)
                if mbps >= 25:  return t("speed_good", lang)
                if mbps >= 10:  return t("speed_acceptable", lang)
                return t("speed_slow", lang)

            c1, c2, c3 = st.columns(3)
            c1.metric(t("metric_download", lang), f"{dl:.1f} Mbps", speed_label(dl))
            c2.metric(t("metric_upload", lang),   f"{ul:.1f} Mbps", speed_label(ul))
            c3.metric(t("metric_ping", lang),     f"{pi:.0f} ms")

            # Referencia por uso
            st.divider()
            st.subheader(t("speed_use_case_subheader", lang))
            usos = [
                (t("use_email_browsing", lang), 1,   dl >= 1),
                (t("use_hd_video", lang),           8,   dl >= 8),
                (t("use_gaming", lang),              15,  dl >= 15),
                (t("use_4k_streaming", lang),               25,  dl >= 25),
                (t("use_4k_multi", lang),     50,  dl >= 50),
                (t("use_4k_video_calls", lang),          25,  dl >= 25),
            ]
            for label, req, ok in usos:
                icon = "✅" if ok else "❌"
                st.write(f"{icon} {label} ({t('requires_mbps', lang, n=req)})")

        else:
            st.error(t("speedtest_error", lang, error=result.get('error', t('unknown', lang))))
            st.info(t("speedtest_install_hint", lang))

    # Historial de tests en sesión
    if st.session_state.speedtest_history:
        st.divider()
        st.subheader(t("speedtest_history_subheader", lang))
        hist_df = pd.DataFrame(st.session_state.speedtest_history)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=hist_df["timestamp"], y=hist_df["download_mbps"],
                             name=t("metric_download", lang), marker_color="#3b82f6"))
        fig.add_trace(go.Bar(x=hist_df["timestamp"], y=hist_df["upload_mbps"],
                             name=t("metric_upload", lang), marker_color="#10b981"))
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
elif page == t("nav_history", lang):
    st.title(t("history_title", lang))

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
    c1.metric(t("metric_total_received", lang), bytes_to_human(stats.get("bytes_recv", 0)))
    c2.metric(t("metric_total_sent", lang),  bytes_to_human(stats.get("bytes_sent", 0)))
    c3.metric(t("metric_errors", lang),         stats.get("errin", 0))
    c4.metric(t("metric_dropped_packets", lang), stats.get("dropin", 0))

    st.divider()

    # Gráfica en tiempo real (sesión)
    if st.session_state.traffic_history:
        df_rt = pd.DataFrame(st.session_state.traffic_history)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_rt["time"], y=df_rt["download_kb"],
                                 name=t("download_kbs", lang), fill="tozeroy",
                                 line=dict(color="#3b82f6", width=2)))
        fig.add_trace(go.Scatter(x=df_rt["time"], y=df_rt["upload_kb"],
                                 name=t("upload_kbs", lang), fill="tozeroy",
                                 line=dict(color="#10b981", width=2)))
        fig.update_layout(
            title=t("realtime_traffic_title", lang),
            xaxis_title=t("time_axis", lang), yaxis_title="KB/s",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.8)",
            font={"color": "white"}, height=300,
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=50, b=30, l=50, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Gráfica histórica CSV (7 días)
    df_hist = load_traffic_history()
    if not df_hist.empty and len(df_hist) > 1:
        st.subheader(t("last_7_days_subheader", lang))

        # Filtro de rango
        days = st.slider(t("show_last_n_days_slider", lang), 1, 7, 7)
        cutoff = datetime.now() - timedelta(days=days)
        df_f = df_hist[df_hist["timestamp"] >= cutoff].copy()

        if not df_f.empty:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df_f["timestamp"], y=df_f["download_kb_s"],
                                      name=t("download_kbs_short", lang), fill="tozeroy",
                                      line=dict(color="#3b82f6")))
            fig2.add_trace(go.Scatter(x=df_f["timestamp"], y=df_f["upload_kb_s"],
                                      name=t("upload_kbs_short", lang), fill="tozeroy",
                                      line=dict(color="#10b981")))

            # Señal
            df_sig = df_f.dropna(subset=["signal_dbm"])
            if not df_sig.empty:
                fig2.add_trace(go.Scatter(
                    x=df_sig["timestamp"], y=df_sig["signal_dbm"],
                    name=t("signal_dbm_trace", lang), yaxis="y2",
                    line=dict(color="#f59e0b", dash="dot")
                ))

            fig2.update_layout(
                xaxis_title=t("datetime_axis", lang), yaxis_title="KB/s",
                yaxis2=dict(title="dBm", overlaying="y", side="right",
                            range=[-100, -20]),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.8)",
                font={"color": "white"}, height=380,
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=30, b=30, l=60, r=60),
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Tabla resumen
            st.subheader(t("stats_summary_subheader", lang))
            summary = df_f[["download_kb_s", "upload_kb_s", "signal_dbm"]].describe().round(2)
            st.dataframe(summary, use_container_width=True)

            # Descargar CSV
            st.download_button(
                t("download_history_csv_btn", lang),
                data=df_f.to_csv(index=False),
                file_name=f"wifi_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info(t("history_autobuild_note", lang, path=TRAFFIC_CSV))

    if st.button(t("refresh_btn", lang)):
        st.rerun()


# ══════════════════════════════════════════════
#  PÁGINA: ALERTAS
# ══════════════════════════════════════════════
elif page == t("nav_alerts", lang):
    st.title(t("alerts_title", lang))
    st.markdown(t("alerts_intro", lang))

    cfg = load_alert_config()

    with st.form("alert_form"):
        st.subheader(t("thresholds_subheader", lang))
        enabled = st.toggle(t("alerts_enabled_toggle", lang), value=cfg.get("enabled", True))

        c1, c2, c3 = st.columns(3)
        sig_thr  = c1.slider(t("min_signal_slider", lang),   -90, -50, cfg["signal_threshold"])
        lat_thr  = c2.slider(t("max_latency_slider", lang),  50, 500, cfg["latency_threshold"])
        loss_thr = c3.slider(t("max_loss_slider", lang),         1,  50, cfg["loss_threshold"])

        submitted = st.form_submit_button(t("save_config_btn", lang), type="primary")
        if submitted:
            new_cfg = {
                "enabled": enabled,
                "signal_threshold": sig_thr,
                "latency_threshold": lat_thr,
                "loss_threshold": loss_thr,
            }
            save_alert_config(new_cfg)
            st.success(t("config_saved", lang))

    st.divider()

    # Test manual de alertas
    st.subheader(t("test_alerts_subheader", lang))
    if st.button(t("send_test_notification_btn", lang)):
        send_desktop_notification(
            t("test_notification_title", lang),
            t("test_notification_body", lang)
        )
        st.success(t("notification_sent", lang))

    st.divider()

    # Log de alertas
    st.subheader(t("alerts_log_subheader", lang))
    if ALERTS_LOG.exists():
        lines = ALERTS_LOG.read_text().strip().splitlines()
        if lines:
            df_log = pd.DataFrame(
                [l.split(" | ", 1) for l in lines if " | " in l],
                columns=[t("col_datetime", lang), t("col_message", lang)]
            )
            st.dataframe(df_log.iloc[::-1], use_container_width=True, hide_index=True)
            if st.button(t("clear_log_btn", lang)):
                ALERTS_LOG.write_text("")
                st.rerun()
        else:
            st.info(t("no_alerts_logged", lang))
    else:
        st.info(t("no_alerts_logged", lang))

    st.divider()
    st.subheader(t("how_notifications_work_subheader", lang))
    st.markdown(t("notifications_explanation", lang))
