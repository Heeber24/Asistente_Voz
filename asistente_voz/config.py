# Aqui van los ajustes basicos del asistente.
# Si cambias wake words, verbos o apps, la gramatica se arma sola con esto.

from __future__ import annotations

import os
from pathlib import Path


def env_si(nombre: str) -> bool:
    # Sirve para leer banderas tipo ASISTENTE_TEXTO=1
    return os.environ.get(nombre, "").strip().lower() in {"1", "true", "yes", "si", "sí"}


# Idioma que le mandamos a Google al reconocer voz
LANGUAGE_STT = os.environ.get("ASISTENTE_LANG_STT", "es-MX").strip() or "es-MX"

# Voz de salida (velocidad / volumen)
TTS_RATE = 120
TTS_VOLUME = 1.0

# Cuanto esperamos a que empieces a hablar y cuanto dura max la frase
LISTEN_TIMEOUT_S = 5
PHRASE_TIME_LIMIT_S = 7.0

# En clase conviene ver el arbol y los hechos; pon ASISTENTE_TEXTO=1 para probar sin mic
MOSTRAR_ARBOL = True
MOSTRAR_HECHOS = True
LISTAR_REGLAS = True

# Indice del micro. None = el que traiga Windows por defecto.
# Para listarlos:
#   python -c "import speech_recognition as sr; [print(i, n) for i, n in enumerate(sr.Microphone.list_microphone_names())]"
MIC_DEVICE_INDEX = None
_mic = os.environ.get("ASISTENTE_MIC_INDEX", "").strip()
if _mic.isdigit():
    MIC_DEVICE_INDEX = int(_mic)

# Palabras que activan al asistente (tienen que coincidir con la CFG)
WAKE_WORDS = frozenset({"alexa", "siri", "google", "cortana"})

# Verbos que entiende el sistema
VERBOS = frozenset(
    {"reproduce", "reproducir", "busca", "buscar", "abre", "abrir", "inicia"}
)

# Estos verbos aceptan cualquier texto despues (no lo listamos en la gramatica)
VERBOS_OBJETO_ABIERTO = frozenset({"reproduce", "reproducir", "busca", "buscar"})

# Apps permitidas para "abre ..." (lexico cerrado)
APPS_LEXICO = frozenset({"notepad", "word", "edge", "documento"})

# Articulos que pueden ir antes de la app
DETERMINANTES = frozenset({"el", "la", "los", "las", "al"})

# Como se escuchan las apps cuando el TTS habla
ALIAS_ETIQUETA = {
    "notepad": "Bloc de notas",
    "word": "Word",
    "documento": "Word",
    "edge": "Microsoft Edge",
}


def resolver_ruta_aplicacion(alias: str) -> Path | None:
    # Busca el .exe en rutas tipicas de Windows. Si tu Word/Edge esta en otra
    # carpeta, agrega la ruta aqui.
    alias = alias.lower()
    root = Path(os.environ.get("SystemRoot", r"C:\Windows"))

    if alias == "notepad":
        p = root / "System32" / "notepad.exe"
        return p if p.is_file() else None

    if alias in ("word", "documento"):
        candidatos = [
            Path(r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"),
            Path(r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE"),
        ]
        for p in candidatos:
            if p.is_file():
                return p
        return None

    if alias == "edge":
        candidatos = [
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        ]
        for p in candidatos:
            if p.is_file():
                return p
        return None

    return None
