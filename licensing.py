"""
WiFi Monitor — modo gratuito, licencia y solicitud de reseña
============================================================

Este módulo NO muestra interfaz: solo decide cosas. Así se puede probar en
Linux/macOS sin abrir Streamlit.

Reglas de diseño (importantes):

1. **El modo gratuito es el default.** Si no se puede verificar una compra,
   la app funciona en gratuito. Nunca se bloquea a nadie por un error de red
   o porque la API de la Store falló.

2. **Fuentes de "premium", en este orden:**
     a. variable de entorno  WIFIMONITOR_PREMIUM=1   (pruebas locales)
     b. archivo local  ~/.wifi_monitor/license.json  {"premium": true}
        (sirve también para códigos promocionales: entregas ese archivo)
     c. licencia de la Microsoft Store (solo Windows + paquete MSIX)

3. **La consulta a la Store se cachea** (TTL 300 s). Streamlit reejecuta el
   script completo en cada interacción; sin caché esto golpearía la API de la
   Store decenas de veces por minuto.

4. **Modo gratuito = 4 páginas gratis, 3 de pago.** El corte:
     GRATIS   Resumen · Dispositivos · Diagnóstico de video · Velocidad
     PREMIUM  Intrusos (lista blanca + alertas) · Historial 7 días · Alertas
   Es el modelo que funcionó mejor en el análisis de la Store: lo gratis
   consigue instalaciones y reseñas; lo de pago es lo que duele perder.

5. **Reparto de responsabilidades con Microsoft (importante):**
     · Microsoft emite la licencia, cobra y **hace cumplir** la prueba: si la
       prueba de una app de pago vence antes de abrirla, la app no arranca
       (Microsoft Learn, "Implement a trial version of your app").
     · Tu código NO decide quién paga: solo decide **qué páginas se abren**
       según la licencia que Microsoft ya emitió. Eso es lo que hace este
       módulo y es lo único que hay que programar.
   Por eso el modelo recomendado es **app gratis + add-on de desbloqueo**:
   así la app siempre abre (aunque no hayan pagado) y el modo gratuito sirve
   de algo. Con "app de pago + prueba", en el día 8 no hay app que abrir.

Uso desde la app:

    from licensing import is_premium, paywall_text, mark_value_event

    if page in PREMIUM_PAGES and not is_premium():
        ...render del paywall y st.stop()

    mark_value_event("scan")   # dentro de scan_network()
    mark_value_event("alert")  # cuando salta una alerta real

Autor: añadido para la versión de Microsoft Store.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
# RUTAS (misma convención que wifi_monitor.py)
# ─────────────────────────────────────────────
DATA_DIR          = Path.home() / ".wifi_monitor"
LICENSE_FILE      = DATA_DIR / "license.json"
REVIEW_STATE_FILE = DATA_DIR / "review_state.json"

# ID de producto en la Microsoft Store (el de "Wifi_Monitor")
STORE_PRODUCT_ID  = "9P51J5MN0DGM"

# Claves de navegación (las mismas de i18n.py) que quedan tras el pago
PREMIUM_NAV_KEYS  = ("nav_intruders", "nav_history", "nav_alerts")
FREE_NAV_KEYS     = ("nav_summary", "nav_devices", "nav_video", "nav_speed")

_CACHE_TTL        = 300      # segundos
_cache            = {"state": None, "at": 0.0}
_lock             = threading.Lock()

# Cuándo pedir la reseña: hace falta al menos un evento de valor real
_REVIEW_MIN_SCANS = 3        # escaneos completados
_REVIEW_MIN_DAYS  = 2        # días desde la primera ejecución


# ─────────────────────────────────────────────
# UTILIDADES DE ARCHIVO
# ─────────────────────────────────────────────

def _read_json(path: Path, default: dict) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return dict(default)


def _write_json(path: Path, data: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


# Testigo en disco: si en algún momento se confirmó una compra, se recuerda.
# Sirve para no degradar a un cliente que YA pagó cuando la consulta a la Store
# falla (sin red, error transitorio, API caída). Sin este testigo, un fallo de
# consulta lo dejaría viendo el paywall teniendo licencia.
_PREMIUM_MARKER = DATA_DIR / "premium_confirmed"


def _remember_premium() -> None:
    try:
        _PREMIUM_MARKER.parent.mkdir(parents=True, exist_ok=True)
        _PREMIUM_MARKER.write_text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), encoding="utf-8")
    except Exception:
        pass


def _was_premium() -> bool:
    return _PREMIUM_MARKER.exists()


# ─────────────────────────────────────────────
# FUENTES DE LICENCIA
# ─────────────────────────────────────────────

def _local_license() -> dict | None:
    """Archivo local (pruebas y códigos promocionales)."""
    if os.environ.get("WIFIMONITOR_PREMIUM") == "1":
        return {"premium": True, "source": "env", "is_trial": False}
    data = _read_json(LICENSE_FILE, {})
    if data.get("premium") is True:
        return {"premium": True, "source": "license_file", "is_trial": False}
    return None


def _store_license() -> dict | None:
    """
    Licencia de la Microsoft Store (Windows + paquete MSIX).

    Devuelve None si no se puede consultar (otra plataforma, no empaquetado,
    sin el paquete winrt instalado, o error). Nunca lanza.

    Requiere:  pip install winrt-Windows.Services.Store winrt-Windows.Foundation
    Qué significa cada campo:
      is_active  → el usuario tiene derecho a usar la app (compra o prueba)
      is_trial   → ese derecho es de prueba, no una compra
    """
    if platform.system() != "Windows":
        return None
    try:
        import asyncio
        from winrt.windows.services.store import StoreContext
    except Exception:
        return None

    async def _query():
        ctx = StoreContext.get_default()
        lic = await ctx.get_app_license_async()

        # Add-on de desbloqueo (modelo "app gratis + versión completa de pago").
        # Si el add-on existe y está activo, el usuario pagó.
        addon_active = False
        addons = getattr(lic, "add_on_licenses", None) or {}
        for sku_id, a in addons.items():
            if bool(getattr(a, "is_active", False)):
                addon_active = True
                break

        return {
            "is_active":    bool(lic.is_active),
            "is_trial":     bool(lic.is_trial),
            "addon_active": addon_active,
            "sku":          getattr(lic, "sku_store_id", "") or "",
        }

    try:
        res = asyncio.run(asyncio.wait_for(_query(), timeout=8))
    except Exception:
        return None

    if not res.get("is_active"):
        # Derecho inactivo: la prueba terminó y no hay compra → gratuito
        return {"premium": False, "source": "store", "is_trial": False,
                "detail": "licencia inactiva"}
    # Dos modelos posibles, según cómo esté configurada la app en Partner Center:
    #   1. App gratis + add-on de desbloqueo  → premium si el add-on está activo
    #   2. App de pago con prueba             → premium si la licencia es de compra
    #      (si es de prueba, todas las páginas están abiertas: es la prueba)
    if res["addon_active"]:
        return {"premium": True, "source": "store_addon", "is_trial": False}
    return {
        "premium":  not res["is_trial"],
        "source":   "store",
        "is_trial": res["is_trial"],
    }


# ─────────────────────────────────────────────
# API PÚBLICA
# ─────────────────────────────────────────────

def license_state(force: bool = False) -> dict:
    """Estado actual de licencia, cacheado. Nunca lanza."""
    now = time.time()
    with _lock:
        if not force and _cache["state"] and (now - _cache["at"]) < _CACHE_TTL:
            return dict(_cache["state"])

    state = {"premium": False, "source": "free", "is_trial": False, "detail": ""}
    store_unavailable = False
    for probe in (_local_license, _store_license):
        try:
            got = probe()
        except Exception as exc:                      # nunca romper la app
            got = None
            state["detail"] = f"{probe.__name__}: {exc}"
        if got is None and probe is _store_license:
            store_unavailable = True
        if got:
            state = got
            break

    # Si no se pudo consultar la Store y este equipo ya había confirmado una
    # compra, se mantiene premium: un fallo de red nunca debe cobrar dos veces
    # en forma de paywall.
    if not state.get("premium") and store_unavailable and _was_premium():
        state = {"premium": True, "source": "cached_license", "is_trial": False,
                 "detail": "Store no respondió; se usa la compra ya confirmada"}

    if state.get("premium"):
        _remember_premium()

    with _lock:
        _cache["state"] = dict(state)
        _cache["at"] = now
    return state


def is_premium() -> bool:
    """True si el usuario pagó. Ante cualquier duda, False (modo gratuito)."""
    return bool(license_state().get("premium"))


def clear_cache() -> None:
    """Para llamar tras una compra sin reiniciar la app."""
    with _lock:
        _cache["state"] = None
        _cache["at"] = 0.0


def is_premium_page(nav_label: str, translate) -> bool:
    """
    Comodidad para la app: nav_label es el texto ya traducido del radio, así
    que hay que comparar contra las traducciones de las claves premium.
    translate es la función t(clave, idioma) de i18n.
    """
    return any(nav_label == translate(k, None) for k in PREMIUM_NAV_KEYS)


# ─────────────────────────────────────────────
# TEXTO DEL PAYWALL (6 idiomas)
# ─────────────────────────────────────────────

_PAYWALL = {
    "es": {
        "title": "🔒 Esta función es de la versión completa",
        "lead": "El modo gratuito te deja ver tu red entera. Lo que queda del otro lado es lo que te avisa cuando algo cambia:",
        "bullets": [
            "**Intrusos** — marcas tus aparatos una vez y te avisa si aparece uno que no es tuyo",
            "**Historial de 7 días** — quién consume y a qué hora, para saber si el problema es tu casa o el operador",
            "**Alertas** — avisos de escritorio cuando la señal cae, sube la latencia o hay pérdida de paquetes",
        ],
        "cta": "Abrir en Microsoft Store",
        "note": "Gratis 7 días con todo activo · Después, USD 2,99. El modo gratuito sigue funcionando siempre.",
    },
    "en": {
        "title": "🔒 This feature is part of the full version",
        "lead": "Free mode lets you see your whole network. What's behind the paywall is what tells you when something changes:",
        "bullets": [
            "**Intruders** — mark your devices once and get told when one that isn't yours shows up",
            "**7-day history** — who uses what, and when, to tell whether the problem is your house or your ISP",
            "**Alerts** — desktop notifications when signal drops, latency spikes or packets are lost",
        ],
        "cta": "Open in Microsoft Store",
        "note": "7 days free with everything enabled · Then USD 2.99. Free mode always keeps working.",
    },
    "pt": {
        "title": "🔒 Este recurso é da versão completa",
        "lead": "O modo gratuito mostra toda a sua rede. O que fica do outro lado é o que avisa quando algo muda:",
        "bullets": [
            "**Intrusos** — marque seus aparelhos uma vez e receba aviso quando aparecer um que não é seu",
            "**Histórico de 7 dias** — quem consome e a que hora, para saber se o problema é a sua casa ou a operadora",
            "**Alertas** — notificações na área de trabalho quando o sinal cai, a latência sobe ou há perda de pacotes",
        ],
        "cta": "Abrir na Microsoft Store",
        "note": "7 dias grátis com tudo ativo · Depois, USD 2,99. O modo gratuito continua funcionando.",
    },
    "fr": {
        "title": "🔒 Cette fonction fait partie de la version complète",
        "lead": "Le mode gratuit vous laisse voir tout votre réseau. Ce qui est derrière, c'est ce qui vous prévient quand quelque chose change :",
        "bullets": [
            "**Intrus** — marquez vos appareils une fois et soyez averti si un autre se connecte",
            "**Historique 7 jours** — qui consomme et à quelle heure, pour savoir si le problème vient de chez vous ou de l'opérateur",
            "**Alertes** — notifications de bureau quand le signal baisse, la latence grimpe ou des paquets se perdent",
        ],
        "cta": "Ouvrir dans le Microsoft Store",
        "note": "7 jours gratuits, tout activé · Ensuite, 2,99 USD. Le mode gratuit reste disponible.",
    },
    "de": {
        "title": "🔒 Diese Funktion gehört zur Vollversion",
        "lead": "Im Gratis-Modus siehst du dein ganzes Netzwerk. Was dahinter liegt, meldet sich, wenn sich etwas ändert:",
        "bullets": [
            "**Eindringlinge** — Geräte einmal markieren und erfahren, wenn ein fremdes dazukommt",
            "**7-Tage-Verlauf** — wer wann wie viel verbraucht, um Haus oder Anbieter als Ursache zu erkennen",
            "**Warnungen** — Desktop-Hinweise bei Signalabfall, hoher Latenz oder Paketverlust",
        ],
        "cta": "Im Microsoft Store öffnen",
        "note": "7 Tage gratis mit allen Funktionen · Danach 2,99 USD. Der Gratis-Modus bleibt erhalten.",
    },
    "it": {
        "title": "🔒 Questa funzione fa parte della versione completa",
        "lead": "La modalità gratuita ti mostra tutta la rete. Quello che sta oltre avvisa quando qualcosa cambia:",
        "bullets": [
            "**Intrusi** — segna i tuoi dispositivi una volta e ricevi un avviso se ne compare uno non tuo",
            "**Cronologia 7 giorni** — chi consuma e quando, per capire se il problema è casa tua o l'operatore",
            "**Avvisi** — notifiche desktop quando il segnale cala, la latenza sale o ci sono pacchetti persi",
        ],
        "cta": "Apri in Microsoft Store",
        "note": "7 giorni gratis con tutto attivo · Poi 2,99 USD. La modalità gratuita resta sempre disponibile.",
    },
}


def paywall_text(lang: str = "es") -> dict:
    """Textos del paywall en el idioma pedido (cae en español)."""
    return _PAYWALL.get((lang or "es").lower(), _PAYWALL["es"])


_REVIEW = {
    "es": {"title": "¿Te sirvió la app?",
           "body": "Si te ayudó a ver qué pasaba en tu red, una valoración en la Store ayuda a que la encuentre más gente. Toma 10 segundos.",
           "y": "Dejar una valoración", "n": "Ahora no"},
    "en": {"title": "Did the app help?",
           "body": "If it helped you see what was happening on your network, a Store rating helps more people find it. It takes 10 seconds.",
           "y": "Rate it", "n": "Not now"},
    "pt": {"title": "O app ajudou?",
           "body": "Se ajudou você a ver o que acontecia na sua rede, uma avaliação na Store ajuda mais gente a encontrá-lo. Leva 10 segundos.",
           "y": "Avaliar", "n": "Agora não"},
    "fr": {"title": "L'application vous a aidé ?",
           "body": "Si elle vous a aidé à voir ce qui se passait sur votre réseau, une note sur le Store aide d'autres personnes à la trouver. Ça prend 10 secondes.",
           "y": "Noter", "n": "Plus tard"},
    "de": {"title": "Hat die App geholfen?",
           "body": "Wenn sie dir gezeigt hat, was in deinem Netzwerk passiert, hilft eine Bewertung im Store anderen, sie zu finden. Dauert 10 Sekunden.",
           "y": "Bewerten", "n": "Später"},
    "it": {"title": "L'app è stata utile?",
           "body": "Se ti ha aiutato a capire cosa succedeva sulla tua rete, una valutazione sullo Store aiuta altri a trovarla. Ci vogliono 10 secondi.",
           "y": "Valuta", "n": "Non ora"},
}


def review_text(lang: str = "es") -> dict:
    return _REVIEW.get((lang or "es").lower(), _REVIEW["es"])


# ─────────────────────────────────────────────
# EVENTOS DE VALOR Y SOLICITUD DE RESEÑA
# ─────────────────────────────────────────────

def mark_value_event(name: str) -> None:
    """
    Registra que la app hizo algo útil de verdad. Se llama desde:
      · scan_network()            → "scan"
      · check_and_fire_alerts()   → "alert"
      · detección de intrusos     → "intruder"
    """
    st = _read_json(REVIEW_STATE_FILE, {})
    st.setdefault("first_run", datetime.now().strftime("%Y-%m-%d"))
    counts = st.setdefault("events", {})
    counts[name] = int(counts.get(name, 0)) + 1
    _write_json(REVIEW_STATE_FILE, st)


def review_prompt_due() -> bool:
    """
    Cuándo pedir la reseña (regla de oro: después de un momento útil, nunca
    al arrancar, y solo una vez).
    """
    if platform.system() != "Windows":
        return False
    st = _read_json(REVIEW_STATE_FILE, {})
    if st.get("review_shown"):
        return False
    counts = st.get("events", {})
    if not (counts.get("intruder") or counts.get("alert") or
            int(counts.get("scan", 0)) >= _REVIEW_MIN_SCANS):
        return False
    first = st.get("first_run")
    if first:
        try:
            days = (datetime.now() - datetime.strptime(first, "%Y-%m-%d")).days
            if days < _REVIEW_MIN_DAYS:
                return False
        except Exception:
            pass
    return True


def mark_review_prompt_shown(accepted: bool = False) -> None:
    st = _read_json(REVIEW_STATE_FILE, {})
    st["review_shown"] = True
    st["review_accepted"] = bool(accepted)
    st["review_shown_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _write_json(REVIEW_STATE_FILE, st)


# ─────────────────────────────────────────────
# ABRIR LA STORE
# ─────────────────────────────────────────────

def open_store_page(which: str = "review") -> bool:
    """
    which = "review"  → abre la página de valoración de la app
    which = "product" → abre la ficha para comprarla

    Usa el esquema ms-windows-store: documentado por Microsoft. En Windows
    empaquetado (MSIX) basta con os.startfile; si falla, se intenta la URI
    por línea de comandos.
    """
    uri = (f"ms-windows-store://review/?ProductId={STORE_PRODUCT_ID}"
           if which == "review"
           else f"ms-windows-store://pdp/?ProductId={STORE_PRODUCT_ID}")

    if platform.system() != "Windows":
        return False
    try:
        os.startfile(uri)                       # noqa: S606  (Windows)
        return True
    except Exception:
        pass
    try:
        subprocess.Popen(["cmd", "/c", "start", "", uri],
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return True
    except Exception:
        return False
