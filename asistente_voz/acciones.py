"""YouTube, Google y programas (lo que hace el agente en el equipo)."""

from __future__ import annotations

# Cada función recibe la cola del comando (texto tras el verbo) y un callback hablar(msg) que usa el TTS.
# pywhatkit intenta abrir el navegador; si falla, se usa webbrowser como respaldo.
# Para nuevas apps en "abre", amplía resolver_ruta_aplicacion y ALIAS_ETIQUETA en config.py, y detectar_alias_app_en_tokens aquí.

import subprocess
import threading
import time
import webbrowser
from urllib.parse import quote_plus

import pywhatkit

from asistente_voz.config import ALIAS_ETIQUETA, resolver_ruta_aplicacion


def _youtube_url(q: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(q)}"


def _google_url(q: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(q)}"


def _play_youtube_hilo(q: str) -> None:
    try:
        pywhatkit.playonyt(q)
    except Exception as e:
        print(f"[YouTube] {e} — abriendo búsqueda en el navegador.")
        webbrowser.open(_youtube_url(q))


def _buscar_google_hilo(q: str) -> None:
    try:
        pywhatkit.search(q)
    except Exception as e:
        print(f"[Google] pywhatkit: {e}")
        webbrowser.open(_google_url(q))


def ejecutar_reproducir_youtube(consulta: str, hablar) -> None:
    q = consulta.strip()
    if not q:
        hablar("Di qué quieres reproducir en YouTube.")
        return
    msg = f"Reproduciendo {q} en YouTube."
    print(msg)
    hablar(msg)
    time.sleep(0.7)
    threading.Thread(target=_play_youtube_hilo, args=(q,), daemon=True, name="yt").start()


def ejecutar_busqueda_google(consulta: str, hablar) -> None:
    q = consulta.strip()
    if not q:
        hablar("Di qué quieres buscar en Google.")
        return
    msg = f"Buscando {q} en Google."
    print(msg)
    hablar(msg)
    time.sleep(0.5)
    threading.Thread(target=_buscar_google_hilo, args=(q,), daemon=True, name="gg").start()


def ejecutar_abrir_aplicacion(alias: str, hablar) -> None:
    alias = alias.lower()
    ruta = resolver_ruta_aplicacion(alias)
    etiqueta = ALIAS_ETIQUETA.get(alias, alias)
    if ruta is None:
        hablar(f"No encontré instalada la aplicación {etiqueta}. Revisa config.py.")
        print(f"No hay ruta para: {alias}")
        return
    msg = f"Abriendo {etiqueta}."
    print(msg)
    hablar(msg)
    time.sleep(0.5)
    try:
        subprocess.Popen([str(ruta)], shell=False)
    except OSError as e:
        hablar("No pude lanzar la aplicación.")
        print(e)


def detectar_alias_app_en_tokens(tokens: list[str]) -> str | None:
    # Primera coincidencia con la lista; debe alinearse con lo que entiende resolver_ruta_aplicacion.
    apps = ("notepad", "word", "edge", "documento")
    found: str | None = None
    for t in tokens:
        if t in apps:
            found = t
    return found
