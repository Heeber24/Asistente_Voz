# Efectos reales del asistente: YouTube, Google y abrir programas.
# El motor de inferencia llama a estas funciones cuando una regla dispara.

from __future__ import annotations

import subprocess
import threading
import time
import webbrowser
from urllib.parse import quote_plus

from asistente_voz.config import ALIAS_ETIQUETA, resolver_ruta_aplicacion


def _url_youtube(q: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(q)}"


def _url_google(q: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(q)}"


def ejecutar_reproducir_youtube(consulta: str, hablar) -> None:
    q = consulta.strip()
    if not q:
        hablar("Di que quieres reproducir en YouTube.")
        return

    msg = f"Reproduciendo {q} en YouTube."
    print(msg)
    hablar(msg)
    time.sleep(0.5)

    def _hilo() -> None:
        try:
            import pywhatkit

            pywhatkit.playonyt(q)
        except Exception as e:
            print(f"[YouTube] {e} — abro busqueda en el navegador.")
            webbrowser.open(_url_youtube(q))

    threading.Thread(target=_hilo, daemon=True).start()


def ejecutar_busqueda_google(consulta: str, hablar) -> None:
    q = consulta.strip()
    if not q:
        hablar("Di que quieres buscar en Google.")
        return

    msg = f"Buscando {q} en Google."
    print(msg)
    hablar(msg)
    time.sleep(0.5)

    def _hilo() -> None:
        try:
            import pywhatkit

            pywhatkit.search(q)
        except Exception as e:
            print(f"[Google] {e}")
            webbrowser.open(_url_google(q))

    threading.Thread(target=_hilo, daemon=True).start()


def ejecutar_abrir_aplicacion(alias: str, hablar) -> None:
    alias = alias.lower()
    ruta = resolver_ruta_aplicacion(alias)
    nombre = ALIAS_ETIQUETA.get(alias, alias)

    if ruta is None:
        hablar(f"No encontre {nombre}. Revisa las rutas en config.py.")
        return

    msg = f"Abriendo {nombre}."
    print(msg)
    hablar(msg)
    time.sleep(0.4)
    try:
        subprocess.Popen([str(ruta)])
    except OSError as e:
        hablar("No pude lanzar la aplicacion.")
        print(e)
