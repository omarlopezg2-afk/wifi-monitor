# -*- coding: utf-8 -*-
"""
i18n.py — Sistema de internacionalización para WiFi Monitor
Idiomas soportados: Español, Inglés, Portugués, Francés, Alemán, Italiano
"""

LANGUAGES = {
    "es": "🇪🇸 Español",
    "en": "🇬🇧 English",
    "pt": "🇵🇹 Português",
    "fr": "🇫🇷 Français",
    "de": "🇩🇪 Deutsch",
    "it": "🇮🇹 Italiano",
}

DEFAULT_LANG = "es"

TRANSLATIONS = {

    # ───────────────────────────── SIDEBAR ─────────────────────────────
    "app_title": {
        "es": "📡 WiFi Monitor v2", "en": "📡 WiFi Monitor v2", "pt": "📡 WiFi Monitor v2",
        "fr": "📡 WiFi Monitor v2", "de": "📡 WiFi Monitor v2", "it": "📡 WiFi Monitor v2",
    },
    "host_caption": {
        "es": "Host: **{host}** | {system} {release}",
        "en": "Host: **{host}** | {system} {release}",
        "pt": "Host: **{host}** | {system} {release}",
        "fr": "Hôte : **{host}** | {system} {release}",
        "de": "Host: **{host}** | {system} {release}",
        "it": "Host: **{host}** | {system} {release}",
    },
    "language_label": {
        "es": "🌐 Idioma", "en": "🌐 Language", "pt": "🌐 Idioma",
        "fr": "🌐 Langue", "de": "🌐 Sprache", "it": "🌐 Lingua",
    },
    "section_label": {
        "es": "Sección", "en": "Section", "pt": "Seção",
        "fr": "Section", "de": "Bereich", "it": "Sezione",
    },
    "nav_summary": {
        "es": "🏠 Resumen", "en": "🏠 Summary", "pt": "🏠 Resumo",
        "fr": "🏠 Résumé", "de": "🏠 Übersicht", "it": "🏠 Riepilogo",
    },
    "nav_devices": {
        "es": "📱 Dispositivos", "en": "📱 Devices", "pt": "📱 Dispositivos",
        "fr": "📱 Appareils", "de": "📱 Geräte", "it": "📱 Dispositivi",
    },
    "nav_intruders": {
        "es": "🔐 Intrusos", "en": "🔐 Intruders", "pt": "🔐 Intrusos",
        "fr": "🔐 Intrus", "de": "🔐 Eindringlinge", "it": "🔐 Intrusi",
    },
    "nav_video": {
        "es": "🎬 Diagnóstico Video", "en": "🎬 Video Diagnosis", "pt": "🎬 Diagnóstico de Vídeo",
        "fr": "🎬 Diagnostic Vidéo", "de": "🎬 Video-Diagnose", "it": "🎬 Diagnosi Video",
    },
    "nav_speed": {
        "es": "⚡ Velocidad", "en": "⚡ Speed", "pt": "⚡ Velocidade",
        "fr": "⚡ Vitesse", "de": "⚡ Geschwindigkeit", "it": "⚡ Velocità",
    },
    "nav_history": {
        "es": "📊 Historial", "en": "📊 History", "pt": "📊 Histórico",
        "fr": "📊 Historique", "de": "📊 Verlauf", "it": "📊 Cronologia",
    },
    "nav_alerts": {
        "es": "🔔 Alertas", "en": "🔔 Alerts", "pt": "🔔 Alertas",
        "fr": "🔔 Alertes", "de": "🔔 Benachrichtigungen", "it": "🔔 Avvisi",
    },
    "sudo_password_expander": {
        "es": "🔑 Contraseña sudo", "en": "🔑 Sudo password", "pt": "🔑 Senha sudo",
        "fr": "🔑 Mot de passe sudo", "de": "🔑 Sudo-Passwort", "it": "🔑 Password sudo",
    },
    "sudo_password_help": {
        "es": "Necesaria para escanear dispositivos con **arp-scan**. No se almacena en disco.",
        "en": "Needed to scan devices with **arp-scan**. It is not stored on disk.",
        "pt": "Necessária para escanear dispositivos com **arp-scan**. Não é armazenada em disco.",
        "fr": "Nécessaire pour scanner les appareils avec **arp-scan**. N'est pas stocké sur le disque.",
        "de": "Wird benötigt, um Geräte mit **arp-scan** zu scannen. Wird nicht auf der Festplatte gespeichert.",
        "it": "Necessaria per scansionare i dispositivi con **arp-scan**. Non viene salvata su disco.",
    },
    "sudo_password_input": {
        "es": "Contraseña del sistema", "en": "System password", "pt": "Senha do sistema",
        "fr": "Mot de passe système", "de": "Systempasswort", "it": "Password di sistema",
    },
    "sudo_password_placeholder": {
        "es": "Tu contraseña de Ubuntu", "en": "Your Ubuntu password", "pt": "Sua senha do Ubuntu",
        "fr": "Votre mot de passe Ubuntu", "de": "Dein Ubuntu-Passwort", "it": "La tua password Ubuntu",
    },
    "sudo_password_ready": {
        "es": "✅ Contraseña lista", "en": "✅ Password ready", "pt": "✅ Senha pronta",
        "fr": "✅ Mot de passe prêt", "de": "✅ Passwort bereit", "it": "✅ Password pronta",
    },
    "sudo_password_missing": {
        "es": "Sin contraseña — se usará fallback (ping sweep)",
        "en": "No password — fallback will be used (ping sweep)",
        "pt": "Sem senha — será usado o método alternativo (ping sweep)",
        "fr": "Pas de mot de passe — solution de repli utilisée (balayage ping)",
        "de": "Kein Passwort — Fallback wird verwendet (Ping-Sweep)",
        "it": "Nessuna password — verrà usato il metodo alternativo (ping sweep)",
    },
    "auto_refresh": {
        "es": "Auto-refresh (15s)", "en": "Auto-refresh (15s)", "pt": "Auto-atualização (15s)",
        "fr": "Actualisation auto (15s)", "de": "Auto-Aktualisierung (15s)", "it": "Aggiornamento automatico (15s)",
    },

    # ───────────────────────────── RESUMEN ─────────────────────────────
    "summary_title": {
        "es": "🏠 Resumen de Red", "en": "🏠 Network Summary", "pt": "🏠 Resumo da Rede",
        "fr": "🏠 Résumé du Réseau", "de": "🏠 Netzwerkübersicht", "it": "🏠 Riepilogo Rete",
    },
    "metric_ssid": {
        "es": "📶 Red (SSID)", "en": "📶 Network (SSID)", "pt": "📶 Rede (SSID)",
        "fr": "📶 Réseau (SSID)", "de": "📶 Netzwerk (SSID)", "it": "📶 Rete (SSID)",
    },
    "metric_signal": {
        "es": "Señal", "en": "Signal", "pt": "Sinal",
        "fr": "Signal", "de": "Signal", "it": "Segnale",
    },
    "metric_your_ip": {
        "es": "📍 Tu IP", "en": "📍 Your IP", "pt": "📍 Seu IP",
        "fr": "📍 Votre IP", "de": "📍 Deine IP", "it": "📍 Il tuo IP",
    },
    "metric_interface": {
        "es": "🔌 Interfaz", "en": "🔌 Interface", "pt": "🔌 Interface",
        "fr": "🔌 Interface", "de": "🔌 Schnittstelle", "it": "🔌 Interfaccia",
    },
    "metric_frequency": {
        "es": "📺 Frecuencia", "en": "📺 Frequency", "pt": "📺 Frequência",
        "fr": "📺 Fréquence", "de": "📺 Frequenz", "it": "📺 Frequenza",
    },
    "metric_channel": {
        "es": "📡 Canal", "en": "📡 Channel", "pt": "📡 Canal",
        "fr": "📡 Canal", "de": "📡 Kanal", "it": "📡 Canale",
    },
    "metric_sent": {
        "es": "⬆️ Enviado", "en": "⬆️ Sent", "pt": "⬆️ Enviado",
        "fr": "⬆️ Envoyé", "de": "⬆️ Gesendet", "it": "⬆️ Inviato",
    },
    "metric_received": {
        "es": "⬇️ Recibido", "en": "⬇️ Received", "pt": "⬇️ Recebido",
        "fr": "⬇️ Reçu", "de": "⬇️ Empfangen", "it": "⬇️ Ricevuto",
    },
    "latency_test_subheader": {
        "es": "⚡ Test de Latencia Rápido", "en": "⚡ Quick Latency Test", "pt": "⚡ Teste de Latência Rápido",
        "fr": "⚡ Test de Latence Rapide", "de": "⚡ Schneller Latenztest", "it": "⚡ Test di Latenza Rapido",
    },
    "measure_latency_btn": {
        "es": "Medir latencia (8.8.8.8)", "en": "Measure latency (8.8.8.8)", "pt": "Medir latência (8.8.8.8)",
        "fr": "Mesurer la latence (8.8.8.8)", "de": "Latenz messen (8.8.8.8)", "it": "Misura latenza (8.8.8.8)",
    },
    "measuring": {
        "es": "Midiendo…", "en": "Measuring…", "pt": "Medindo…",
        "fr": "Mesure en cours…", "de": "Wird gemessen…", "it": "Misurazione…",
    },
    "metric_average": {
        "es": "Promedio", "en": "Average", "pt": "Média",
        "fr": "Moyenne", "de": "Durchschnitt", "it": "Media",
    },
    "metric_minimum": {
        "es": "Mínimo", "en": "Minimum", "pt": "Mínimo",
        "fr": "Minimum", "de": "Minimum", "it": "Minimo",
    },
    "metric_maximum": {
        "es": "Máximo", "en": "Maximum", "pt": "Máximo",
        "fr": "Maximum", "de": "Maximum", "it": "Massimo",
    },
    "metric_loss": {
        "es": "Pérdida", "en": "Loss", "pt": "Perda",
        "fr": "Perte", "de": "Verlust", "it": "Perdita",
    },
    "error_word": {
        "es": "Error", "en": "Error", "pt": "Erro",
        "fr": "Erreur", "de": "Fehler", "it": "Errore",
    },
    "signal_gauge_title": {
        "es": "Calidad de señal WiFi", "en": "WiFi Signal Quality", "pt": "Qualidade do Sinal WiFi",
        "fr": "Qualité du Signal WiFi", "de": "WLAN-Signalqualität", "it": "Qualità Segnale WiFi",
    },

    # ───────────────────────────── DISPOSITIVOS ─────────────────────────────
    "devices_title": {
        "es": "📱 Dispositivos Conectados", "en": "📱 Connected Devices", "pt": "📱 Dispositivos Conectados",
        "fr": "📱 Appareils Connectés", "de": "📱 Verbundene Geräte", "it": "📱 Dispositivi Connessi",
    },
    "scan_now_btn": {
        "es": "🔍 Escanear red ahora", "en": "🔍 Scan network now", "pt": "🔍 Escanear rede agora",
        "fr": "🔍 Scanner le réseau maintenant", "de": "🔍 Netzwerk jetzt scannen", "it": "🔍 Scansiona rete ora",
    },
    "scan_first_time_note": {
        "es": "El primer escaneo puede tardar ~15–30 s.",
        "en": "The first scan may take ~15–30 s.",
        "pt": "A primeira varredura pode levar ~15–30 s.",
        "fr": "Le premier scan peut prendre ~15–30 s.",
        "de": "Der erste Scan kann ~15–30 Sek. dauern.",
        "it": "La prima scansione può richiedere ~15–30 s.",
    },
    "scanning_network": {
        "es": "Escaneando red…", "en": "Scanning network…", "pt": "Escaneando rede…",
        "fr": "Analyse du réseau…", "de": "Netzwerk wird gescannt…", "it": "Scansione rete…",
    },
    "devices_found": {
        "es": "✅ {count} dispositivo(s) encontrado(s)",
        "en": "✅ {count} device(s) found",
        "pt": "✅ {count} dispositivo(s) encontrado(s)",
        "fr": "✅ {count} appareil(s) trouvé(s)",
        "de": "✅ {count} Gerät(e) gefunden",
        "it": "✅ {count} dispositivo/i trovato/i",
    },
    "col_ip": {
        "es": "IP", "en": "IP", "pt": "IP", "fr": "IP", "de": "IP", "it": "IP",
    },
    "col_mac": {
        "es": "MAC", "en": "MAC", "pt": "MAC", "fr": "MAC", "de": "MAC", "it": "MAC",
    },
    "col_vendor": {
        "es": "Fabricante", "en": "Vendor", "pt": "Fabricante",
        "fr": "Fabricant", "de": "Hersteller", "it": "Produttore",
    },
    "col_hostname": {
        "es": "Hostname", "en": "Hostname", "pt": "Hostname",
        "fr": "Nom d'hôte", "de": "Hostname", "it": "Hostname",
    },
    "col_latency": {
        "es": "Latencia", "en": "Latency", "pt": "Latência",
        "fr": "Latence", "de": "Latenz", "it": "Latenza",
    },
    "col_this_pc": {
        "es": "Este PC", "en": "This PC", "pt": "Este PC",
        "fr": "Ce PC", "de": "Dieser PC", "it": "Questo PC",
    },
    "col_count": {
        "es": "Cantidad", "en": "Count", "pt": "Quantidade",
        "fr": "Nombre", "de": "Anzahl", "it": "Conteggio",
    },
    "devices_by_vendor_chart": {
        "es": "Dispositivos por fabricante", "en": "Devices by vendor", "pt": "Dispositivos por fabricante",
        "fr": "Appareils par fabricant", "de": "Geräte nach Hersteller", "it": "Dispositivi per produttore",
    },
    "press_scan_hint": {
        "es": "Presiona **Escanear red ahora** para ver los dispositivos.",
        "en": "Press **Scan network now** to see the devices.",
        "pt": "Pressione **Escanear rede agora** para ver os dispositivos.",
        "fr": "Appuyez sur **Scanner le réseau maintenant** pour voir les appareils.",
        "de": "Drücke **Netzwerk jetzt scannen**, um die Geräte zu sehen.",
        "it": "Premi **Scansiona rete ora** per vedere i dispositivi.",
    },

    # ───────────────────────────── INTRUSOS ─────────────────────────────
    "intruders_title": {
        "es": "🔐 Detector de Intrusos", "en": "🔐 Intruder Detector", "pt": "🔐 Detector de Intrusos",
        "fr": "🔐 Détecteur d'Intrus", "de": "🔐 Eindringlings-Detektor", "it": "🔐 Rilevatore Intrusi",
    },
    "intruders_intro": {
        "es": "La app **aprende** cuáles son tus dispositivos. Los que no estén aprobados aparecen como **intrusos**.",
        "en": "The app **learns** which devices are yours. Unapproved ones appear as **intruders**.",
        "pt": "O app **aprende** quais são seus dispositivos. Os não aprovados aparecem como **intrusos**.",
        "fr": "L'application **apprend** quels sont vos appareils. Ceux non approuvés apparaissent comme **intrus**.",
        "de": "Die App **lernt**, welche Geräte dir gehören. Nicht genehmigte erscheinen als **Eindringlinge**.",
        "it": "L'app **apprende** quali sono i tuoi dispositivi. Quelli non approvati appaiono come **intrusi**.",
    },
    "scan_now_short_btn": {
        "es": "🔍 Escanear ahora", "en": "🔍 Scan now", "pt": "🔍 Escanear agora",
        "fr": "🔍 Scanner maintenant", "de": "🔍 Jetzt scannen", "it": "🔍 Scansiona ora",
    },
    "intruders_first_scan_note": {
        "es": "La primera vez todos aparecerán como desconocidos. Apruébalos con un nombre y la próxima vez serán reconocidos.",
        "en": "The first time, all will appear as unknown. Approve them with a name and they'll be recognized next time.",
        "pt": "Na primeira vez todos aparecerão como desconhecidos. Aprove-os com um nome e na próxima vez serão reconhecidos.",
        "fr": "La première fois, tous apparaîtront comme inconnus. Approuvez-les avec un nom et ils seront reconnus la prochaine fois.",
        "de": "Beim ersten Mal erscheinen alle als unbekannt. Genehmige sie mit einem Namen, dann werden sie nächstes Mal erkannt.",
        "it": "La prima volta tutti appariranno come sconosciuti. Approvali con un nome e la prossima volta saranno riconosciuti.",
    },
    "scanning": {
        "es": "Escaneando…", "en": "Scanning…", "pt": "Escaneando…",
        "fr": "Analyse en cours…", "de": "Wird gescannt…", "it": "Scansione in corso…",
    },
    "unknown_devices_subheader": {
        "es": "🚨 Dispositivos desconocidos ({count})",
        "en": "🚨 Unknown devices ({count})",
        "pt": "🚨 Dispositivos desconhecidos ({count})",
        "fr": "🚨 Appareils inconnus ({count})",
        "de": "🚨 Unbekannte Geräte ({count})",
        "it": "🚨 Dispositivi sconosciuti ({count})",
    },
    "no_unknown_devices": {
        "es": "✅ No hay dispositivos desconocidos en tu red.",
        "en": "✅ There are no unknown devices on your network.",
        "pt": "✅ Não há dispositivos desconhecidos na sua rede.",
        "fr": "✅ Aucun appareil inconnu sur votre réseau.",
        "de": "✅ Es gibt keine unbekannten Geräte in deinem Netzwerk.",
        "it": "✅ Non ci sono dispositivi sconosciuti nella tua rete.",
    },
    "unknown_devices_found": {
        "es": "Se encontraron **{count}** dispositivo(s) no reconocidos.",
        "en": "**{count}** unrecognized device(s) found.",
        "pt": "Foram encontrados **{count}** dispositivo(s) não reconhecidos.",
        "fr": "**{count}** appareil(s) non reconnu(s) trouvé(s).",
        "de": "**{count}** nicht erkannte Gerät(e) gefunden.",
        "it": "Trovati **{count}** dispositivo/i non riconosciuto/i.",
    },
    "hostname_label": {
        "es": "**Hostname:**", "en": "**Hostname:**", "pt": "**Hostname:**",
        "fr": "**Nom d'hôte :**", "de": "**Hostname:**", "it": "**Hostname:**",
    },
    "latency_label": {
        "es": "**Latencia:**", "en": "**Latency:**", "pt": "**Latência:**",
        "fr": "**Latence :**", "de": "**Latenz:**", "it": "**Latenza:**",
    },
    "device_name_input": {
        "es": "Nombre para este dispositivo", "en": "Name for this device", "pt": "Nome para este dispositivo",
        "fr": "Nom pour cet appareil", "de": "Name für dieses Gerät", "it": "Nome per questo dispositivo",
    },
    "device_name_placeholder": {
        "es": "ej: Celular Omar, Smart TV, Laptop Invitado",
        "en": "e.g.: Omar's Phone, Smart TV, Guest Laptop",
        "pt": "ex: Celular Omar, Smart TV, Notebook Visitante",
        "fr": "ex : Téléphone Omar, Smart TV, Ordinateur Invité",
        "de": "z. B.: Handy Omar, Smart-TV, Gast-Laptop",
        "it": "es: Cellulare Omar, Smart TV, Laptop Ospite",
    },
    "approve_save_btn": {
        "es": "✅ Aprobar y guardar", "en": "✅ Approve and save", "pt": "✅ Aprovar e salvar",
        "fr": "✅ Approuver et enregistrer", "de": "✅ Genehmigen und speichern", "it": "✅ Approva e salva",
    },
    "ignore_for_now_btn": {
        "es": "🚫 Ignorar por ahora", "en": "🚫 Ignore for now", "pt": "🚫 Ignorar por agora",
        "fr": "🚫 Ignorer pour le moment", "de": "🚫 Vorerst ignorieren", "it": "🚫 Ignora per ora",
    },
    "ignored_will_reappear": {
        "es": "Ignorado. Aparecerá de nuevo en el próximo escaneo.",
        "en": "Ignored. It will appear again on the next scan.",
        "pt": "Ignorado. Aparecerá novamente na próxima varredura.",
        "fr": "Ignoré. Il réapparaîtra au prochain scan.",
        "de": "Ignoriert. Erscheint beim nächsten Scan erneut.",
        "it": "Ignorato. Riapparirà alla prossima scansione.",
    },
    "known_devices_subheader": {
        "es": "✅ Dispositivos conocidos ({count})",
        "en": "✅ Known devices ({count})",
        "pt": "✅ Dispositivos conhecidos ({count})",
        "fr": "✅ Appareils connus ({count})",
        "de": "✅ Bekannte Geräte ({count})",
        "it": "✅ Dispositivi conosciuti ({count})",
    },
    "vendor_label": {
        "es": "**Fabricante:**", "en": "**Vendor:**", "pt": "**Fabricante:**",
        "fr": "**Fabricant :**", "de": "**Hersteller:**", "it": "**Produttore:**",
    },
    "approved_at_label": {
        "es": "**Aprobado:**", "en": "**Approved:**", "pt": "**Aprovado:**",
        "fr": "**Approuvé :**", "de": "**Genehmigt:**", "it": "**Approvato:**",
    },
    "rename_input": {
        "es": "Renombrar", "en": "Rename", "pt": "Renomear",
        "fr": "Renommer", "de": "Umbenennen", "it": "Rinomina",
    },
    "save_name_btn": {
        "es": "💾 Guardar nombre", "en": "💾 Save name", "pt": "💾 Salvar nome",
        "fr": "💾 Enregistrer le nom", "de": "💾 Namen speichern", "it": "💾 Salva nome",
    },
    "remove_from_list_btn": {
        "es": "🗑️ Eliminar de lista blanca", "en": "🗑️ Remove from whitelist", "pt": "🗑️ Remover da lista branca",
        "fr": "🗑️ Retirer de la liste blanche", "de": "🗑️ Aus Whitelist entfernen", "it": "🗑️ Rimuovi dalla whitelist",
    },
    "recent_alerts_log_expander": {
        "es": "📋 Log de alertas recientes", "en": "📋 Recent alerts log", "pt": "📋 Log de alertas recentes",
        "fr": "📋 Journal des alertes récentes", "de": "📋 Protokoll aktueller Benachrichtigungen", "it": "📋 Registro avvisi recenti",
    },

    # ───────────────────────────── DIAGNÓSTICO VIDEO ─────────────────────────────
    "video_title": {
        "es": "🎬 ¿Por qué va lento mi video?", "en": "🎬 Why is my video slow?", "pt": "🎬 Por que meu vídeo está lento?",
        "fr": "🎬 Pourquoi ma vidéo est-elle lente ?", "de": "🎬 Warum ist mein Video langsam?", "it": "🎬 Perché il mio video è lento?",
    },
    "options_expander": {
        "es": "⚙️ Opciones", "en": "⚙️ Options", "pt": "⚙️ Opções",
        "fr": "⚙️ Options", "de": "⚙️ Optionen", "it": "⚙️ Opzioni",
    },
    "test_server_select": {
        "es": "Servidor de prueba", "en": "Test server", "pt": "Servidor de teste",
        "fr": "Serveur de test", "de": "Testserver", "it": "Server di test",
    },
    "ping_count_slider": {
        "es": "Número de pings", "en": "Number of pings", "pt": "Número de pings",
        "fr": "Nombre de pings", "de": "Anzahl der Pings", "it": "Numero di ping",
    },
    "diagnose_now_btn": {
        "es": "🔬 Diagnosticar ahora", "en": "🔬 Diagnose now", "pt": "🔬 Diagnosticar agora",
        "fr": "🔬 Diagnostiquer maintenant", "de": "🔬 Jetzt diagnostizieren", "it": "🔬 Diagnostica ora",
    },
    "measuring_towards": {
        "es": "Midiendo hacia {host}…", "en": "Measuring towards {host}…", "pt": "Medindo em direção a {host}…",
        "fr": "Mesure vers {host}…", "de": "Messung Richtung {host}…", "it": "Misurazione verso {host}…",
    },
    "diagnosis_subheader": {
        "es": "📋 Diagnóstico", "en": "📋 Diagnosis", "pt": "📋 Diagnóstico",
        "fr": "📋 Diagnostic", "de": "📋 Diagnose", "it": "📋 Diagnosi",
    },
    "metric_jitter": {
        "es": "Jitter", "en": "Jitter", "pt": "Jitter", "fr": "Jitter", "de": "Jitter", "it": "Jitter",
    },
    "recommendations_subheader": {
        "es": "💡 Recomendaciones", "en": "💡 Recommendations", "pt": "💡 Recomendações",
        "fr": "💡 Recommandations", "de": "💡 Empfehlungen", "it": "💡 Raccomandazioni",
    },
    "streaming_reference_subheader": {
        "es": "📖 Referencia para streaming", "en": "📖 Streaming reference", "pt": "📖 Referência para streaming",
        "fr": "📖 Référence pour le streaming", "de": "📖 Referenz für Streaming", "it": "📖 Riferimento per lo streaming",
    },
    "ref_metric_col": {
        "es": "Métrica", "en": "Metric", "pt": "Métrica",
        "fr": "Métrique", "de": "Kennzahl", "it": "Metrica",
    },
    "ref_excellent_col": {
        "es": "✅ Excelente", "en": "✅ Excellent", "pt": "✅ Excelente",
        "fr": "✅ Excellent", "de": "✅ Ausgezeichnet", "it": "✅ Eccellente",
    },
    "ref_acceptable_col": {
        "es": "🟡 Aceptable", "en": "🟡 Acceptable", "pt": "🟡 Aceitável",
        "fr": "🟡 Acceptable", "de": "🟡 Akzeptabel", "it": "🟡 Accettabile",
    },
    "ref_problematic_col": {
        "es": "🔴 Problemático", "en": "🔴 Problematic", "pt": "🔴 Problemático",
        "fr": "🔴 Problématique", "de": "🔴 Problematisch", "it": "🔴 Problematico",
    },
    "ref_latency_row": {
        "es": "Latencia", "en": "Latency", "pt": "Latência",
        "fr": "Latence", "de": "Latenz", "it": "Latenza",
    },
    "ref_jitter_row": {
        "es": "Jitter", "en": "Jitter", "pt": "Jitter", "fr": "Jitter", "de": "Jitter", "it": "Jitter",
    },
    "ref_loss_row": {
        "es": "Pérdida", "en": "Loss", "pt": "Perda",
        "fr": "Perte", "de": "Verlust", "it": "Perdita",
    },
    "video_other_checks_expander": {
        "es": "📚 Si la red está bien, revisa también", "en": "📚 If the network is fine, also check", "pt": "📚 Se a rede estiver bem, verifique também",
        "fr": "📚 Si le réseau va bien, vérifiez aussi", "de": "📚 Wenn das Netzwerk in Ordnung ist, prüfe auch", "it": "📚 Se la rete va bene, controlla anche",
    },
    "video_other_checks_body": {
        "es": "- 🌐 **Servidor saturado** — intenta en horario no pico\n- 📊 **Plan de internet**: HD requiere ~8 Mbps, 4K ~25 Mbps\n- 💻 **CPU/RAM** ocupado — cierra otras apps\n- 🔄 **Actualizaciones en segundo plano**\n- 🔒 **VPN activa** que añade latencia",
        "en": "- 🌐 **Overloaded server** — try off-peak hours\n- 📊 **Internet plan**: HD needs ~8 Mbps, 4K ~25 Mbps\n- 💻 **Busy CPU/RAM** — close other apps\n- 🔄 **Background updates**\n- 🔒 **Active VPN** adding latency",
        "pt": "- 🌐 **Servidor sobrecarregado** — tente em horário fora de pico\n- 📊 **Plano de internet**: HD precisa de ~8 Mbps, 4K ~25 Mbps\n- 💻 **CPU/RAM** ocupada — fecher outros apps\n- 🔄 **Atualizações em segundo plano**\n- 🔒 **VPN ativa** que adiciona latência",
        "fr": "- 🌐 **Serveur saturé** — essayez en heures creuses\n- 📊 **Forfait internet** : la HD nécessite ~8 Mbps, le 4K ~25 Mbps\n- 💻 **CPU/RAM** occupé — fermez d'autres applications\n- 🔄 **Mises à jour en arrière-plan**\n- 🔒 **VPN actif** ajoutant de la latence",
        "de": "- 🌐 **Überlasteter Server** — versuche es außerhalb der Stoßzeiten\n- 📊 **Internettarif**: HD benötigt ~8 Mbit/s, 4K ~25 Mbit/s\n- 💻 **CPU/RAM ausgelastet** — schließe andere Apps\n- 🔄 **Hintergrundaktualisierungen**\n- 🔒 **Aktives VPN**, das Latenz hinzufügt",
        "it": "- 🌐 **Server sovraccarico** — prova in orari non di punta\n- 📊 **Piano internet**: l'HD richiede ~8 Mbps, il 4K ~25 Mbps\n- 💻 **CPU/RAM occupata** — chiudi altre app\n- 🔄 **Aggiornamenti in background**\n- 🔒 **VPN attiva** che aggiunge latenza",
    },

    # ───────────────────────────── VELOCIDAD ─────────────────────────────
    "speed_title": {
        "es": "⚡ Test de Velocidad Real", "en": "⚡ Real Speed Test", "pt": "⚡ Teste de Velocidade Real",
        "fr": "⚡ Test de Vitesse Réel", "de": "⚡ Echter Geschwindigkeitstest", "it": "⚡ Test di Velocità Reale",
    },
    "speed_intro": {
        "es": "Mide el ancho de banda real de tu conexión a internet usando servidores de **Speedtest.net**.",
        "en": "Measures your real internet connection bandwidth using **Speedtest.net** servers.",
        "pt": "Mede a largura de banda real da sua conexão à internet usando servidores do **Speedtest.net**.",
        "fr": "Mesure la bande passante réelle de votre connexion internet via les serveurs **Speedtest.net**.",
        "de": "Misst die tatsächliche Bandbreite deiner Internetverbindung über **Speedtest.net**-Server.",
        "it": "Misura la larghezza di banda reale della tua connessione internet usando i server di **Speedtest.net**.",
    },
    "speed_warning": {
        "es": "⏱️ El test tarda entre **30 y 60 segundos**. No cierres la página mientras corre.",
        "en": "⏱️ The test takes between **30 and 60 seconds**. Don't close the page while it runs.",
        "pt": "⏱️ O teste leva entre **30 e 60 segundos**. Não feche a página enquanto ele roda.",
        "fr": "⏱️ Le test dure entre **30 et 60 secondes**. Ne fermez pas la page pendant son exécution.",
        "de": "⏱️ Der Test dauert zwischen **30 und 60 Sekunden**. Schließe die Seite während der Ausführung nicht.",
        "it": "⏱️ Il test dura tra **30 e 60 secondi**. Non chiudere la pagina durante l'esecuzione.",
    },
    "start_speedtest_btn": {
        "es": "🚀 Iniciar test de velocidad", "en": "🚀 Start speed test", "pt": "🚀 Iniciar teste de velocidade",
        "fr": "🚀 Démarrer le test de vitesse", "de": "🚀 Geschwindigkeitstest starten", "it": "🚀 Avvia test di velocità",
    },
    "starting_speedtest": {
        "es": "Iniciando speedtest…", "en": "Starting speed test…", "pt": "Iniciando teste de velocidade…",
        "fr": "Démarrage du test de vitesse…", "de": "Geschwindigkeitstest wird gestartet…", "it": "Avvio test di velocità…",
    },
    "connecting_server": {
        "es": "Conectando al servidor más cercano…", "en": "Connecting to nearest server…", "pt": "Conectando ao servidor mais próximo…",
        "fr": "Connexion au serveur le plus proche…", "de": "Verbindung zum nächstgelegenen Server wird hergestellt…", "it": "Connessione al server più vicino…",
    },
    "measuring_up_down": {
        "es": "Midiendo descarga y subida…", "en": "Measuring download and upload…", "pt": "Medindo download e upload…",
        "fr": "Mesure du téléchargement et de l'envoi…", "de": "Download und Upload werden gemessen…", "it": "Misurazione download e upload…",
    },
    "ready": {
        "es": "¡Listo!", "en": "Done!", "pt": "Pronto!",
        "fr": "Terminé !", "de": "Fertig!", "it": "Pronto!",
    },
    "metric_download": {
        "es": "⬇️ Descarga", "en": "⬇️ Download", "pt": "⬇️ Download",
        "fr": "⬇️ Téléchargement", "de": "⬇️ Download", "it": "⬇️ Download",
    },
    "metric_upload": {
        "es": "⬆️ Subida", "en": "⬆️ Upload", "pt": "⬆️ Upload",
        "fr": "⬆️ Envoi", "de": "⬆️ Upload", "it": "⬆️ Upload",
    },
    "metric_ping": {
        "es": "🏓 Ping", "en": "🏓 Ping", "pt": "🏓 Ping",
        "fr": "🏓 Ping", "de": "🏓 Ping", "it": "🏓 Ping",
    },
    "speed_excellent": {
        "es": "🟢 Excelente", "en": "🟢 Excellent", "pt": "🟢 Excelente",
        "fr": "🟢 Excellent", "de": "🟢 Ausgezeichnet", "it": "🟢 Eccellente",
    },
    "speed_good": {
        "es": "🟡 Buena", "en": "🟡 Good", "pt": "🟡 Boa",
        "fr": "🟡 Bonne", "de": "🟡 Gut", "it": "🟡 Buona",
    },
    "speed_acceptable": {
        "es": "🟠 Aceptable", "en": "🟠 Acceptable", "pt": "🟠 Aceitável",
        "fr": "🟠 Acceptable", "de": "🟠 Akzeptabel", "it": "🟠 Accettabile",
    },
    "speed_slow": {
        "es": "🔴 Lenta", "en": "🔴 Slow", "pt": "🔴 Lenta",
        "fr": "🔴 Lente", "de": "🔴 Langsam", "it": "🔴 Lenta",
    },
    "speed_use_case_subheader": {
        "es": "¿Para qué alcanza tu velocidad?", "en": "What is your speed good for?", "pt": "Para que sua velocidade é boa?",
        "fr": "À quoi suffit votre vitesse ?", "de": "Wofür reicht deine Geschwindigkeit?", "it": "Per cosa basta la tua velocità?",
    },
    "use_email_browsing": {
        "es": "📧 Email / Navegación básica", "en": "📧 Email / Basic browsing", "pt": "📧 Email / Navegação básica",
        "fr": "📧 Email / Navigation de base", "de": "📧 E-Mail / Grundlegendes Surfen", "it": "📧 Email / Navigazione di base",
    },
    "use_hd_video": {
        "es": "📺 Video HD (1080p)", "en": "📺 HD Video (1080p)", "pt": "📺 Vídeo HD (1080p)",
        "fr": "📺 Vidéo HD (1080p)", "de": "📺 HD-Video (1080p)", "it": "📺 Video HD (1080p)",
    },
    "use_gaming": {
        "es": "🎮 Gaming online", "en": "🎮 Online gaming", "pt": "🎮 Jogos online",
        "fr": "🎮 Jeu en ligne", "de": "🎮 Online-Gaming", "it": "🎮 Gaming online",
    },
    "use_4k_streaming": {
        "es": "🎬 4K Streaming", "en": "🎬 4K Streaming", "pt": "🎬 Streaming 4K",
        "fr": "🎬 Streaming 4K", "de": "🎬 4K-Streaming", "it": "🎬 Streaming 4K",
    },
    "use_4k_multi": {
        "es": "👨‍👩‍👧 4K + varios usuarios", "en": "👨‍👩‍👧 4K + multiple users", "pt": "👨‍👩‍👧 4K + vários usuários",
        "fr": "👨‍👩‍👧 4K + plusieurs utilisateurs", "de": "👨‍👩‍👧 4K + mehrere Nutzer", "it": "👨‍👩‍👧 4K + più utenti",
    },
    "use_4k_video_calls": {
        "es": "☁️  Videollamadas 4K", "en": "☁️  4K Video calls", "pt": "☁️  Videochamadas 4K",
        "fr": "☁️  Appels vidéo 4K", "de": "☁️  4K-Videoanrufe", "it": "☁️  Videochiamate 4K",
    },
    "requires_mbps": {
        "es": "requiere {n} Mbps", "en": "requires {n} Mbps", "pt": "requer {n} Mbps",
        "fr": "nécessite {n} Mbps", "de": "benötigt {n} Mbit/s", "it": "richiede {n} Mbps",
    },
    "speedtest_error": {
        "es": "Error al correr el test: {error}", "en": "Error running the test: {error}", "pt": "Erro ao executar o teste: {error}",
        "fr": "Erreur lors de l'exécution du test : {error}", "de": "Fehler beim Ausführen des Tests: {error}", "it": "Errore durante l'esecuzione del test: {error}",
    },
    "speedtest_install_hint": {
        "es": "Verifica que `speedtest-cli` esté instalado: `pip install speedtest-cli`",
        "en": "Check that `speedtest-cli` is installed: `pip install speedtest-cli`",
        "pt": "Verifique se o `speedtest-cli` está instalado: `pip install speedtest-cli`",
        "fr": "Vérifiez que `speedtest-cli` est installé : `pip install speedtest-cli`",
        "de": "Prüfe, ob `speedtest-cli` installiert ist: `pip install speedtest-cli`",
        "it": "Verifica che `speedtest-cli` sia installato: `pip install speedtest-cli`",
    },
    "speedtest_history_subheader": {
        "es": "📈 Historial de tests (esta sesión)", "en": "📈 Test history (this session)", "pt": "📈 Histórico de testes (esta sessão)",
        "fr": "📈 Historique des tests (cette session)", "de": "📈 Testverlauf (diese Sitzung)", "it": "📈 Cronologia test (questa sessione)",
    },

    # ───────────────────────────── HISTORIAL ─────────────────────────────
    "history_title": {
        "es": "📊 Historial de Red (7 días)", "en": "📊 Network History (7 days)", "pt": "📊 Histórico de Rede (7 dias)",
        "fr": "📊 Historique Réseau (7 jours)", "de": "📊 Netzwerkverlauf (7 Tage)", "it": "📊 Cronologia Rete (7 giorni)",
    },
    "metric_total_received": {
        "es": "⬇️ Total recibido", "en": "⬇️ Total received", "pt": "⬇️ Total recebido",
        "fr": "⬇️ Total reçu", "de": "⬇️ Insgesamt empfangen", "it": "⬇️ Totale ricevuto",
    },
    "metric_total_sent": {
        "es": "⬆️ Total enviado", "en": "⬆️ Total sent", "pt": "⬆️ Total enviado",
        "fr": "⬆️ Total envoyé", "de": "⬆️ Insgesamt gesendet", "it": "⬆️ Totale inviato",
    },
    "metric_errors": {
        "es": "❌ Errores", "en": "❌ Errors", "pt": "❌ Erros",
        "fr": "❌ Erreurs", "de": "❌ Fehler", "it": "❌ Errori",
    },
    "metric_dropped_packets": {
        "es": "📦 Paquetes perdidos", "en": "📦 Dropped packets", "pt": "📦 Pacotes perdidos",
        "fr": "📦 Paquets perdus", "de": "📦 Verlorene Pakete", "it": "📦 Pacchetti persi",
    },
    "realtime_traffic_title": {
        "es": "Tráfico en tiempo real (sesión actual)", "en": "Real-time traffic (current session)", "pt": "Tráfego em tempo real (sessão atual)",
        "fr": "Trafic en temps réel (session actuelle)", "de": "Echtzeit-Datenverkehr (aktuelle Sitzung)", "it": "Traffico in tempo reale (sessione attuale)",
    },
    "download_kbs": {
        "es": "⬇️ Descarga (KB/s)", "en": "⬇️ Download (KB/s)", "pt": "⬇️ Download (KB/s)",
        "fr": "⬇️ Téléchargement (KB/s)", "de": "⬇️ Download (KB/s)", "it": "⬇️ Download (KB/s)",
    },
    "upload_kbs": {
        "es": "⬆️ Subida (KB/s)", "en": "⬆️ Upload (KB/s)", "pt": "⬆️ Upload (KB/s)",
        "fr": "⬆️ Envoi (KB/s)", "de": "⬆️ Upload (KB/s)", "it": "⬆️ Upload (KB/s)",
    },
    "time_axis": {
        "es": "Hora", "en": "Time", "pt": "Hora",
        "fr": "Heure", "de": "Zeit", "it": "Ora",
    },
    "last_7_days_subheader": {
        "es": "📅 Últimos 7 días — tráfico acumulado", "en": "📅 Last 7 days — accumulated traffic", "pt": "📅 Últimos 7 dias — tráfego acumulado",
        "fr": "📅 7 derniers jours — trafic cumulé", "de": "📅 Letzte 7 Tage — kumulierter Datenverkehr", "it": "📅 Ultimi 7 giorni — traffico accumulato",
    },
    "show_last_n_days_slider": {
        "es": "Mostrar últimos N días", "en": "Show last N days", "pt": "Mostrar últimos N dias",
        "fr": "Afficher les N derniers jours", "de": "Letzte N Tage anzeigen", "it": "Mostra ultimi N giorni",
    },
    "download_kbs_short": {
        "es": "⬇️ Descarga KB/s", "en": "⬇️ Download KB/s", "pt": "⬇️ Download KB/s",
        "fr": "⬇️ Téléchargement KB/s", "de": "⬇️ Download KB/s", "it": "⬇️ Download KB/s",
    },
    "upload_kbs_short": {
        "es": "⬆️ Subida KB/s", "en": "⬆️ Upload KB/s", "pt": "⬆️ Upload KB/s",
        "fr": "⬆️ Envoi KB/s", "de": "⬆️ Upload KB/s", "it": "⬆️ Upload KB/s",
    },
    "signal_dbm_trace": {
        "es": "📶 Señal dBm", "en": "📶 Signal dBm", "pt": "📶 Sinal dBm",
        "fr": "📶 Signal dBm", "de": "📶 Signal dBm", "it": "📶 Segnale dBm",
    },
    "datetime_axis": {
        "es": "Fecha/Hora", "en": "Date/Time", "pt": "Data/Hora",
        "fr": "Date/Heure", "de": "Datum/Zeit", "it": "Data/Ora",
    },
    "stats_summary_subheader": {
        "es": "📋 Resumen estadístico", "en": "📋 Statistical summary", "pt": "📋 Resumo estatístico",
        "fr": "📋 Résumé statistique", "de": "📋 Statistische Zusammenfassung", "it": "📋 Riepilogo statistico",
    },
    "download_history_csv_btn": {
        "es": "⬇️ Descargar historial CSV", "en": "⬇️ Download CSV history", "pt": "⬇️ Baixar histórico CSV",
        "fr": "⬇️ Télécharger l'historique CSV", "de": "⬇️ CSV-Verlauf herunterladen", "it": "⬇️ Scarica cronologia CSV",
    },
    "history_autobuild_note": {
        "es": "El historial se construye automáticamente mientras la app está abierta. Los datos se guardan en `{path}`",
        "en": "The history builds automatically while the app is open. Data is saved at `{path}`",
        "pt": "O histórico é construído automaticamente enquanto o app está aberto. Os dados são salvos em `{path}`",
        "fr": "L'historique se construit automatiquement pendant que l'application est ouverte. Les données sont enregistrées dans `{path}`",
        "de": "Der Verlauf wird automatisch erstellt, während die App geöffnet ist. Die Daten werden unter `{path}` gespeichert",
        "it": "La cronologia si costruisce automaticamente mentre l'app è aperta. I dati vengono salvati in `{path}`",
    },
    "refresh_btn": {
        "es": "🔄 Actualizar", "en": "🔄 Refresh", "pt": "🔄 Atualizar",
        "fr": "🔄 Actualiser", "de": "🔄 Aktualisieren", "it": "🔄 Aggiorna",
    },

    # ───────────────────────────── ALERTAS ─────────────────────────────
    "alerts_title": {
        "es": "🔔 Configuración de Alertas", "en": "🔔 Alert Settings", "pt": "🔔 Configuração de Alertas",
        "fr": "🔔 Configuration des Alertes", "de": "🔔 Benachrichtigungseinstellungen", "it": "🔔 Configurazione Avvisi",
    },
    "alerts_intro": {
        "es": "Las alertas se envían como **notificación de escritorio Ubuntu** y como **banner rojo en la app**. También quedan registradas en el log.",
        "en": "Alerts are sent as **Ubuntu desktop notifications** and as a **red banner in the app**. They are also logged.",
        "pt": "Os alertas são enviados como **notificação de área de trabalho do Ubuntu** e como **banner vermelho no app**. Também ficam registrados no log.",
        "fr": "Les alertes sont envoyées sous forme de **notification bureau Ubuntu** et de **bannière rouge dans l'application**. Elles sont également enregistrées dans le journal.",
        "de": "Benachrichtigungen werden als **Ubuntu-Desktop-Benachrichtigung** und als **rotes Banner in der App** gesendet. Sie werden außerdem protokolliert.",
        "it": "Gli avvisi vengono inviati come **notifica desktop Ubuntu** e come **banner rosso nell'app**. Vengono anche registrati nel log.",
    },
    "thresholds_subheader": {
        "es": "⚙️ Umbrales", "en": "⚙️ Thresholds", "pt": "⚙️ Limites",
        "fr": "⚙️ Seuils", "de": "⚙️ Schwellenwerte", "it": "⚙️ Soglie",
    },
    "alerts_enabled_toggle": {
        "es": "Alertas activadas", "en": "Alerts enabled", "pt": "Alertas ativados",
        "fr": "Alertes activées", "de": "Benachrichtigungen aktiviert", "it": "Avvisi attivati",
    },
    "min_signal_slider": {
        "es": "Señal mínima (dBm)", "en": "Minimum signal (dBm)", "pt": "Sinal mínimo (dBm)",
        "fr": "Signal minimum (dBm)", "de": "Mindestsignal (dBm)", "it": "Segnale minimo (dBm)",
    },
    "max_latency_slider": {
        "es": "Latencia máxima (ms)", "en": "Maximum latency (ms)", "pt": "Latência máxima (ms)",
        "fr": "Latence maximale (ms)", "de": "Maximale Latenz (ms)", "it": "Latenza massima (ms)",
    },
    "max_loss_slider": {
        "es": "Pérdida máx (%)", "en": "Max loss (%)", "pt": "Perda máx (%)",
        "fr": "Perte max (%)", "de": "Max. Verlust (%)", "it": "Perdita max (%)",
    },
    "save_config_btn": {
        "es": "💾 Guardar configuración", "en": "💾 Save settings", "pt": "💾 Salvar configuração",
        "fr": "💾 Enregistrer la configuration", "de": "💾 Konfiguration speichern", "it": "💾 Salva configurazione",
    },
    "config_saved": {
        "es": "✅ Configuración guardada.", "en": "✅ Settings saved.", "pt": "✅ Configuração salva.",
        "fr": "✅ Configuration enregistrée.", "de": "✅ Konfiguration gespeichert.", "it": "✅ Configurazione salvata.",
    },
    "test_alerts_subheader": {
        "es": "🧪 Probar alertas", "en": "🧪 Test alerts", "pt": "🧪 Testar alertas",
        "fr": "🧪 Tester les alertes", "de": "🧪 Benachrichtigungen testen", "it": "🧪 Test avvisi",
    },
    "send_test_notification_btn": {
        "es": "Enviar notificación de prueba al escritorio", "en": "Send test notification to desktop", "pt": "Enviar notificação de teste para a área de trabalho",
        "fr": "Envoyer une notification de test sur le bureau", "de": "Test-Benachrichtigung an den Desktop senden", "it": "Invia notifica di test al desktop",
    },
    "test_notification_title": {
        "es": "📡 WiFi Monitor — Prueba", "en": "📡 WiFi Monitor — Test", "pt": "📡 WiFi Monitor — Teste",
        "fr": "📡 WiFi Monitor — Test", "de": "📡 WiFi Monitor — Test", "it": "📡 WiFi Monitor — Test",
    },
    "test_notification_body": {
        "es": "Las notificaciones de escritorio funcionan correctamente ✅", "en": "Desktop notifications are working correctly ✅", "pt": "As notificações de área de trabalho funcionam corretamente ✅",
        "fr": "Les notifications de bureau fonctionnent correctement ✅", "de": "Desktop-Benachrichtigungen funktionieren korrekt ✅", "it": "Le notifiche desktop funzionano correttamente ✅",
    },
    "notification_sent": {
        "es": "Notificación enviada. Revisa el área de notificaciones de Ubuntu.",
        "en": "Notification sent. Check Ubuntu's notification area.",
        "pt": "Notificação enviada. Verifique a área de notificações do Ubuntu.",
        "fr": "Notification envoyée. Vérifiez la zone de notification d'Ubuntu.",
        "de": "Benachrichtigung gesendet. Überprüfe den Ubuntu-Benachrichtigungsbereich.",
        "it": "Notifica inviata. Controlla l'area di notifica di Ubuntu.",
    },
    "alerts_log_subheader": {
        "es": "📋 Log de alertas", "en": "📋 Alerts log", "pt": "📋 Log de alertas",
        "fr": "📋 Journal des alertes", "de": "📋 Benachrichtigungsprotokoll", "it": "📋 Registro avvisi",
    },
    "col_datetime": {
        "es": "Fecha/Hora", "en": "Date/Time", "pt": "Data/Hora",
        "fr": "Date/Heure", "de": "Datum/Zeit", "it": "Data/Ora",
    },
    "col_message": {
        "es": "Mensaje", "en": "Message", "pt": "Mensagem",
        "fr": "Message", "de": "Nachricht", "it": "Messaggio",
    },
    "clear_log_btn": {
        "es": "🗑️ Limpiar log", "en": "🗑️ Clear log", "pt": "🗑️ Limpar log",
        "fr": "🗑️ Effacer le journal", "de": "🗑️ Protokoll löschen", "it": "🗑️ Pulisci registro",
    },
    "no_alerts_logged": {
        "es": "Sin alertas registradas aún.", "en": "No alerts logged yet.", "pt": "Nenhum alerta registrado ainda.",
        "fr": "Aucune alerte enregistrée pour l'instant.", "de": "Noch keine Benachrichtigungen protokolliert.", "it": "Nessun avviso registrato ancora.",
    },
    "how_notifications_work_subheader": {
        "es": "ℹ️ ¿Cómo funcionan las notificaciones de escritorio?", "en": "ℹ️ How do desktop notifications work?", "pt": "ℹ️ Como funcionam as notificações de área de trabalho?",
        "fr": "ℹ️ Comment fonctionnent les notifications de bureau ?", "de": "ℹ️ Wie funktionieren Desktop-Benachrichtigungen?", "it": "ℹ️ Come funzionano le notifiche desktop?",
    },
    "notifications_explanation": {
        "es": "La app usa `notify-send` (incluido en Ubuntu por defecto).\n\nSi no ves las notificaciones, ejecuta en terminal:\n```bash\nsudo apt install libnotify-bin\n```\nY asegúrate de que la app corra en la **misma sesión gráfica** (no por SSH sin `-X`).",
        "en": "The app uses `notify-send` (included in Ubuntu by default).\n\nIf you don't see notifications, run in terminal:\n```bash\nsudo apt install libnotify-bin\n```\nAnd make sure the app runs in the **same graphical session** (not via SSH without `-X`).",
        "pt": "O app usa `notify-send` (incluído no Ubuntu por padrão).\n\nSe você não vê as notificações, execute no terminal:\n```bash\nsudo apt install libnotify-bin\n```\nE certifique-se de que o app rode na **mesma sessão gráfica** (não via SSH sem `-X`).",
        "fr": "L'application utilise `notify-send` (inclus dans Ubuntu par défaut).\n\nSi vous ne voyez pas les notifications, exécutez dans un terminal :\n```bash\nsudo apt install libnotify-bin\n```\nEt assurez-vous que l'application s'exécute dans la **même session graphique** (pas via SSH sans `-X`).",
        "de": "Die App verwendet `notify-send` (standardmäßig in Ubuntu enthalten).\n\nWenn du keine Benachrichtigungen siehst, führe im Terminal aus:\n```bash\nsudo apt install libnotify-bin\n```\nUnd stelle sicher, dass die App in der **gleichen grafischen Sitzung** läuft (nicht über SSH ohne `-X`).",
        "it": "L'app usa `notify-send` (incluso in Ubuntu per impostazione predefinita).\n\nSe non vedi le notifiche, esegui nel terminale:\n```bash\nsudo apt install libnotify-bin\n```\nE assicurati che l'app sia in esecuzione nella **stessa sessione grafica** (non via SSH senza `-X`).",
    },

    # ───────────────────────────── VALORES COMPARTIDOS / DATOS ─────────────────────────────
    "na": {
        "es": "N/D", "en": "N/A", "pt": "N/D",
        "fr": "N/D", "de": "N/V", "it": "N/D",
    },
    "unknown": {
        "es": "Desconocido", "en": "Unknown", "pt": "Desconhecido",
        "fr": "Inconnu", "de": "Unbekannt", "it": "Sconosciuto",
    },
    "this_pc": {
        "es": "Este PC", "en": "This PC", "pt": "Este PC",
        "fr": "Ce PC", "de": "Dieser PC", "it": "Questo PC",
    },

    # ───────────────────────────── MENSAJES DE LÓGICA (diagnose_streaming) ─────────────────────────────
    "diag_no_data_verdict": {
        "es": "Sin datos", "en": "No data", "pt": "Sem dados",
        "fr": "Aucune donnée", "de": "Keine Daten", "it": "Nessun dato",
    },
    "diag_no_connection_issue": {
        "es": "No se pudo alcanzar el servidor", "en": "Could not reach the server", "pt": "Não foi possível alcançar o servidor",
        "fr": "Impossible d'atteindre le serveur", "de": "Server konnte nicht erreicht werden", "it": "Impossibile raggiungere il server",
    },
    "diag_check_wifi_rec": {
        "es": "Verifica tu conexión WiFi", "en": "Check your WiFi connection", "pt": "Verifique sua conexão WiFi",
        "fr": "Vérifiez votre connexion WiFi", "de": "Überprüfe deine WLAN-Verbindung", "it": "Controlla la tua connessione WiFi",
    },
    "diag_high_loss_issue": {
        "es": "⚠️ Pérdida de paquetes alta: {loss}%", "en": "⚠️ High packet loss: {loss}%", "pt": "⚠️ Perda de pacotes alta: {loss}%",
        "fr": "⚠️ Perte de paquets élevée : {loss}%", "de": "⚠️ Hoher Paketverlust: {loss}%", "it": "⚠️ Perdita di pacchetti elevata: {loss}%",
    },
    "diag_high_latency_issue": {
        "es": "⚠️ Latencia alta: {avg:.1f} ms", "en": "⚠️ High latency: {avg:.1f} ms", "pt": "⚠️ Latência alta: {avg:.1f} ms",
        "fr": "⚠️ Latence élevée : {avg:.1f} ms", "de": "⚠️ Hohe Latenz: {avg:.1f} ms", "it": "⚠️ Latenza elevata: {avg:.1f} ms",
    },
    "diag_high_jitter_issue": {
        "es": "⚠️ Jitter elevado: {jitter:.1f} ms", "en": "⚠️ High jitter: {jitter:.1f} ms", "pt": "⚠️ Jitter elevado: {jitter:.1f} ms",
        "fr": "⚠️ Jitter élevé : {jitter:.1f} ms", "de": "⚠️ Hoher Jitter: {jitter:.1f} ms", "it": "⚠️ Jitter elevato: {jitter:.1f} ms",
    },
    "diag_no_issues_label": {
        "es": "Sin problemas detectados", "en": "No issues detected", "pt": "Nenhum problema detectado",
        "fr": "Aucun problème détecté", "de": "Keine Probleme festgestellt", "it": "Nessun problema rilevato",
    },
    "diag_ok_verdict": {
        "es": "🟢 La red está bien — el problema es externo", "en": "🟢 The network is fine — the problem is external", "pt": "🟢 A rede está bem — o problema é externo",
        "fr": "🟢 Le réseau va bien — le problème est externe", "de": "🟢 Das Netzwerk ist in Ordnung — das Problem liegt extern", "it": "🟢 La rete va bene — il problema è esterno",
    },
    "diag_ok_rec_1": {
        "es": "Tu conexión tiene buena latencia y sin pérdidas.", "en": "Your connection has good latency and no losses.", "pt": "Sua conexão tem boa latência e sem perdas.",
        "fr": "Votre connexion a une bonne latence et aucune perte.", "de": "Deine Verbindung hat eine gute Latenz und keine Verluste.", "it": "La tua connessione ha una buona latenza e nessuna perdita.",
    },
    "diag_ok_rec_2": {
        "es": "Revisa: servidor saturado, plan de internet, CPU/RAM del dispositivo, VPN activa.", "en": "Check: overloaded server, internet plan, device CPU/RAM, active VPN.", "pt": "Verifique: servidor sobrecarregado, plano de internet, CPU/RAM do dispositivo, VPN ativa.",
        "fr": "Vérifiez : serveur saturé, forfait internet, CPU/RAM de l'appareil, VPN actif.", "de": "Prüfe: überlasteter Server, Internettarif, Geräte-CPU/RAM, aktives VPN.", "it": "Controlla: server sovraccarico, piano internet, CPU/RAM del dispositivo, VPN attiva.",
    },
    "diag_bad_verdict": {
        "es": "🔴 Problema de RED confirmado", "en": "🔴 Confirmed NETWORK problem", "pt": "🔴 Problema de REDE confirmado",
        "fr": "🔴 Problème RÉSEAU confirmé", "de": "🔴 Bestätigtes NETZWERK-Problem", "it": "🔴 Problema di RETE confermato",
    },
    "diag_bad_rec_1": {
        "es": "Reinicia el router (desenchufa 30 seg).", "en": "Restart the router (unplug for 30 sec).", "pt": "Reinicie o roteador (desligue por 30 seg).",
        "fr": "Redémarrez le routeur (débranchez 30 sec).", "de": "Starte den Router neu (30 Sek. trennen).", "it": "Riavvia il router (scollega per 30 sec).",
    },
    "diag_bad_rec_2": {
        "es": "Acércate al router o usa cable Ethernet.", "en": "Get closer to the router or use an Ethernet cable.", "pt": "Aproxime-se do roteador ou use cabo Ethernet.",
        "fr": "Rapprochez-vous du routeur ou utilisez un câble Ethernet.", "de": "Geh näher an den Router oder verwende ein Ethernet-Kabel.", "it": "Avvicinati al router o usa un cavo Ethernet.",
    },
    "diag_bad_rec_3": {
        "es": "Verifica si muchos dispositivos consumen ancho de banda.", "en": "Check if many devices are consuming bandwidth.", "pt": "Verifique se muitos dispositivos estão consumindo largura de banda.",
        "fr": "Vérifiez si de nombreux appareils consomment de la bande passante.", "de": "Prüfe, ob viele Geräte Bandbreite verbrauchen.", "it": "Controlla se molti dispositivi consumano larghezza di banda.",
    },
    "diag_bad_rec_4": {
        "es": "Contacta a tu ISP si persiste.", "en": "Contact your ISP if it persists.", "pt": "Contate seu provedor se persistir.",
        "fr": "Contactez votre FAI si le problème persiste.", "de": "Kontaktiere deinen ISP, wenn es weiterhin auftritt.", "it": "Contatta il tuo ISP se persiste.",
    },
    "diag_warn_verdict": {
        "es": "🟡 Red con leve degradación", "en": "🟡 Network with slight degradation", "pt": "🟡 Rede com leve degradação",
        "fr": "🟡 Réseau avec légère dégradation", "de": "🟡 Netzwerk mit leichter Verschlechterung", "it": "🟡 Rete con leggero degrado",
    },
    "diag_warn_rec_1": {
        "es": "Prueba cambiar al canal 5 GHz si tu router lo soporta.", "en": "Try switching to the 5 GHz channel if your router supports it.", "pt": "Tente mudar para o canal de 5 GHz se seu roteador suportar.",
        "fr": "Essayez de passer au canal 5 GHz si votre routeur le prend en charge.", "de": "Versuche, auf den 5-GHz-Kanal zu wechseln, falls dein Router das unterstützt.", "it": "Prova a passare al canale 5 GHz se il tuo router lo supporta.",
    },
    "diag_warn_rec_2": {
        "es": "Cierra aplicaciones que usen internet en segundo plano.", "en": "Close apps using internet in the background.", "pt": "Fecher aplicativos que usam internet em segundo plano.",
        "fr": "Fermez les applications utilisant internet en arrière-plan.", "de": "Schließe Apps, die im Hintergrund Internet nutzen.", "it": "Chiudi le app che usano internet in background.",
    },

    # ───────────────────────────── MENSAJES DE ALERTAS (check_and_fire_alerts) ─────────────────────────────
    "alert_low_signal_title": {
        "es": "🔴 Señal baja", "en": "🔴 Low signal", "pt": "🔴 Sinal baixo",
        "fr": "🔴 Signal faible", "de": "🔴 Schwaches Signal", "it": "🔴 Segnale debole",
    },
    "alert_low_signal_msg": {
        "es": "Señal WiFi baja: {sig} dBm (umbral {threshold} dBm)", "en": "Low WiFi signal: {sig} dBm (threshold {threshold} dBm)", "pt": "Sinal WiFi baixo: {sig} dBm (limite {threshold} dBm)",
        "fr": "Signal WiFi faible : {sig} dBm (seuil {threshold} dBm)", "de": "Schwaches WLAN-Signal: {sig} dBm (Schwellenwert {threshold} dBm)", "it": "Segnale WiFi debole: {sig} dBm (soglia {threshold} dBm)",
    },
    "alert_desktop_low_signal_title": {
        "es": "📡 WiFi Monitor — Señal Baja", "en": "📡 WiFi Monitor — Low Signal", "pt": "📡 WiFi Monitor — Sinal Baixo",
        "fr": "📡 WiFi Monitor — Signal Faible", "de": "📡 WiFi Monitor — Schwaches Signal", "it": "📡 WiFi Monitor — Segnale Debole",
    },
    "alert_high_latency_title": {
        "es": "🟡 Latencia alta", "en": "🟡 High latency", "pt": "🟡 Latência alta",
        "fr": "🟡 Latence élevée", "de": "🟡 Hohe Latenz", "it": "🟡 Latenza elevata",
    },
    "alert_high_latency_msg": {
        "es": "Latencia alta: {lat:.0f} ms (umbral {threshold} ms)", "en": "High latency: {lat:.0f} ms (threshold {threshold} ms)", "pt": "Latência alta: {lat:.0f} ms (limite {threshold} ms)",
        "fr": "Latence élevée : {lat:.0f} ms (seuil {threshold} ms)", "de": "Hohe Latenz: {lat:.0f} ms (Schwellenwert {threshold} ms)", "it": "Latenza elevata: {lat:.0f} ms (soglia {threshold} ms)",
    },
    "alert_desktop_high_latency_title": {
        "es": "📡 WiFi Monitor — Latencia Alta", "en": "📡 WiFi Monitor — High Latency", "pt": "📡 WiFi Monitor — Latência Alta",
        "fr": "📡 WiFi Monitor — Latence Élevée", "de": "📡 WiFi Monitor — Hohe Latenz", "it": "📡 WiFi Monitor — Latenza Elevata",
    },
    "alert_packet_loss_title": {
        "es": "🔴 Pérdida paquetes", "en": "🔴 Packet loss", "pt": "🔴 Perda de pacotes",
        "fr": "🔴 Perte de paquets", "de": "🔴 Paketverlust", "it": "🔴 Perdita di pacchetti",
    },
    "alert_packet_loss_msg": {
        "es": "Pérdida de paquetes: {loss}% (umbral {threshold}%)", "en": "Packet loss: {loss}% (threshold {threshold}%)", "pt": "Perda de pacotes: {loss}% (limite {threshold}%)",
        "fr": "Perte de paquets : {loss}% (seuil {threshold}%)", "de": "Paketverlust: {loss}% (Schwellenwert {threshold}%)", "it": "Perdita di pacchetti: {loss}% (soglia {threshold}%)",
    },
    "alert_desktop_packet_loss_title": {
        "es": "📡 WiFi Monitor — Paquetes Perdidos", "en": "📡 WiFi Monitor — Dropped Packets", "pt": "📡 WiFi Monitor — Pacotes Perdidos",
        "fr": "📡 WiFi Monitor — Paquets Perdus", "de": "📡 WiFi Monitor — Verlorene Pakete", "it": "📡 WiFi Monitor — Pacchetti Persi",
    },
    "alert_device_approved_title": {
        "es": "📡 WiFi Monitor — Dispositivo Aprobado", "en": "📡 WiFi Monitor — Device Approved", "pt": "📡 WiFi Monitor — Dispositivo Aprovado",
        "fr": "📡 WiFi Monitor — Appareil Approuvé", "de": "📡 WiFi Monitor — Gerät Genehmigt", "it": "📡 WiFi Monitor — Dispositivo Approvato",
    },
    "alert_device_approved_msg": {
        "es": "{label} agregado a la lista blanca", "en": "{label} added to the whitelist", "pt": "{label} adicionado à lista branca",
        "fr": "{label} ajouté à la liste blanche", "de": "{label} zur Whitelist hinzugefügt", "it": "{label} aggiunto alla whitelist",
    },
}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """
    Devuelve la traducción de `key` en el idioma `lang`.
    Acepta kwargs para interpolar valores dinámicos, ej: t("devices_found", lang, count=5)
    Si la clave o el idioma no existen, hace fallback a español y luego a la clave misma.
    """
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
