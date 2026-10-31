"""YouTube, Google y programas (efectos secundarios tras la inferencia)."""

from __future__ import annotations

# Cada función recibe la cola del comando (texto tras el verbo) y un callback hablar(msg) que usa el TTS.
# pywhatkit se importa solo al ejecutar (así gramática/experto se prueban sin esa dependencia).
# Para nuevas apps en "abre", amplía resolver_ruta_aplicacion y ALIAS_ETIQUETA en config.py.

import subprocess
import threading
import time
import webbrowser
from urllib.parse import quote_plus

from asistente_voz.config import ALIAS_ETIQUETA, APPS_LEXICO, resolver_ruta_aplicacion


def _youtube_url(q: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(q)}"


def _google_url(q: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(q)}"


def _play_youtube_hilo(q: str) -> None:
    try:
        import pywhatkit

        pywhatkit.playonyt(q)
    except Exception as e:
        print(f"[YouTube] {e} — abriendo búsqueda en el navegador.")
        webbrowser.open(_youtube_url(q))


def _buscar_google_hilo(q: str) -> None:
    try:
        import pywhatkit

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
    """Última coincidencia con APPS_LEXICO; alineado con resolver_ruta_aplicacion."""
    found: str | None = None
    for t in tokens:
        if t in APPS_LEXICO:
            found = t
    return found
