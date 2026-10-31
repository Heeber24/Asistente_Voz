# Archivo de configuracion.
# Aqui concentramos lo que normalmente se anda cambiando:
# idioma, microfono, wake words, verbos, apps y rutas de Windows.
# Si mueves wake words / verbos / apps, la gramatica se arma sola con esto
# (mira gramatica.py -> construir_gramatica_texto).

from __future__ import annotations

import os
from pathlib import Path


def env_si(nombre: str) -> bool:
    # Lee variables de entorno tipo "bandera".
    # Ejemplo: ASISTENTE_TEXTO=1  -> True
    return os.environ.get(nombre, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "si",
        "sí",
    }


# ----- reconocimiento de voz (STT) -----

# Idioma que le mandamos a Google Speech. Se puede sobreescribir con ASISTENTE_LANG_STT
LANGUAGE_STT = os.environ.get("ASISTENTE_LANG_STT", "es-MX").strip() or "es-MX"

# Segundos que espera a que empieces a hablar
LISTEN_TIMEOUT_S = 5

# Tope de duracion de la frase capturada (evita que se quede grabando por siempre)
PHRASE_TIME_LIMIT_S = 7.0

# Indice del microfono. None = el que traiga el sistema por defecto.
# Para ver la lista de micros:
#   python -c "import speech_recognition as sr; [print(i, n) for i, n in enumerate(sr.Microphone.list_microphone_names())]"
MIC_DEVICE_INDEX = None
_mic = os.environ.get("ASISTENTE_MIC_INDEX", "").strip()
if _mic.isdigit():
    MIC_DEVICE_INDEX = int(_mic)


# ----- voz de salida (TTS) -----

TTS_RATE = 120      # que tan rapido habla
TTS_VOLUME = 1.0    # volumen de 0.0 a 1.0


# ----- cosas utiles en clase / demo -----

# Si estan en True, en consola ves el arbol CFG y los hechos/regla que disparo
MOSTRAR_ARBOL = True
MOSTRAR_HECHOS = True
LISTAR_REGLAS = True


# ----- lexico del asistente (esto alimenta la CFG) -----

# Palabras de activacion: la frase debe empezar con una de estas
WAKE_WORDS = frozenset({"alexa", "siri", "google", "cortana"})

# Verbos que el sistema reconoce
VERBOS = frozenset(
    {"reproduce", "reproducir", "busca", "buscar", "abre", "abrir", "inicia"}
)

# Con estos verbos NO listamos todas las canciones/busquedas en la gramatica.
# Lo que venga despues se trata como objeto libre (__objeto__).
VERBOS_OBJETO_ABIERTO = frozenset({"reproduce", "reproducir", "busca", "buscar"})

# Apps permitidas para "abre ..." (aqui si es lexico cerrado)
APPS_LEXICO = frozenset({"notepad", "word", "edge", "documento"})

# Articulos que pueden ir antes del nombre de la app: "abre el notepad"
DETERMINANTES = frozenset({"el", "la", "los", "las", "al"})

# Nombre bonito para que el TTS no diga "notepad" crudo
ALIAS_ETIQUETA = {
    "notepad": "Bloc de notas",
    "word": "Word",
    "documento": "Word",
    "edge": "Microsoft Edge",
}


def resolver_ruta_aplicacion(alias: str) -> Path | None:
    # Devuelve la ruta del .exe si existe en el equipo.
    # Si en tu PC Word/Edge estan en otra carpeta, agrega esa ruta a la lista.
    alias = alias.lower()
    root = Path(os.environ.get("SystemRoot", r"C:\Windows"))

    # Bloc de notas siempre viene con Windows
    if alias == "notepad":
        p = root / "System32" / "notepad.exe"
        return p if p.is_file() else None

    # Word: probamos un par de rutas tipicas de Office
    if alias in ("word", "documento"):
        candidatos = [
            Path(r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"),
            Path(r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE"),
        ]
        for p in candidatos:
            if p.is_file():
                return p
        return None

    # Edge: igual, un par de instalaciones comunes
    if alias == "edge":
        candidatos = [
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        ]
        for p in candidatos:
            if p.is_file():
                return p
        return None

    # Alias desconocido
    return None
