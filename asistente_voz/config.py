"""
Ajustes del asistente: idioma, micrófono, STT, TTS, rutas de programas en Windows.

Si cambias la gramática (gramatica.py), mantén alineados WAKE_WORDS y VERBOS con las reglas V y AV.
"""

from __future__ import annotations

import os
from pathlib import Path

_ENV_SI = frozenset({"1", "true", "yes", "si", "sí"})


def env_si(nombre: str) -> bool:
    """True si la variable de entorno está en 1 / true / yes / si / sí (mayúsculas da igual)."""
    return os.environ.get(nombre, "").strip().lower() in _ENV_SI


def _env_int(nombre: str, default: int) -> int:
    try:
        return int(os.environ.get(nombre, str(default)).strip())
    except ValueError:
        return default


def _env_float(nombre: str, default: float) -> float:
    try:
        return float(os.environ.get(nombre, str(default)).strip())
    except ValueError:
        return default


# Idioma que se manda a Google Speech (es-MX, es-ES, etc.). Se puede sobreescribir con ASISTENTE_LANG_STT.
LANGUAGE_STT: str = os.environ.get("ASISTENTE_LANG_STT", "es-MX").strip() or "es-MX"

# Velocidad y volumen del habla (TTS). ASISTENTE_TTS_RATE y ASISTENTE_TTS_VOLUME si quieres probar sin tocar código.
TTS_RATE: int = _env_int("ASISTENTE_TTS_RATE", 120)
TTS_VOLUME: float = max(0.0, min(1.0, _env_float("ASISTENTE_TTS_VOLUME", 1.0)))

# Cuánto espera el micrófono a que empieces a hablar (timeout). ASISTENTE_ESCUCHA_TIMEOUT en segundos.
LISTEN_TIMEOUT_S: int = _env_int("ASISTENTE_ESCUCHA_TIMEOUT", 5)
# Segundos de audio que usa adjust_for_ambient_noise al calibrar ruido de fondo.
AMBIENT_NOISE_DURATION_S: float = _env_float("ASISTENTE_RUIDO_CALIBRACION_S", 0.10)
# 0 = calibrar ruido solo la primera escucha; 1 = cada vez; N>=2 = cada N escuchas (ASISTENTE_RECALIBRAR_RUIDO_CADA).
AMBIENT_RECALIBRATE_EVERY: int = _env_int("ASISTENTE_RECALIBRAR_RUIDO_CADA", 0)
# Tope de duración de la frase capturada; 0 = sin tope (cuidado con TV de fondo). ASISTENTE_FRASE_MAX_S.
PHRASE_TIME_LIMIT_S: float = _env_float("ASISTENTE_FRASE_MAX_S", 7.0)

# Afinado del umbral de energía del reconocedor (sensibilidad al habla). Mult, min y max; ASISTENTE_DYNAMIC_ENERGY=1 activa umbral dinámico.
STT_ENERGY_THRESHOLD_MULT: float = _env_float("ASISTENTE_ENERGY_MULT", 1.0)
STT_ENERGY_THRESHOLD_MIN: int = _env_int("ASISTENTE_ENERGY_MIN", 80)
STT_ENERGY_THRESHOLD_MAX: int = _env_int("ASISTENTE_ENERGY_MAX", 4000)
STT_DYNAMIC_ENERGY: bool = env_si("ASISTENTE_DYNAMIC_ENERGY")
STT_DEBUG: bool = env_si("ASISTENTE_DEBUG_STT")

# Silencios opcionales tras el mensaje de bienvenida y justo antes de escuchar (evita cortar la primera sílaba).
POST_WELCOME_SILENCE_S: float = _env_float("ASISTENTE_SILENCIO_TRAS_BIENVENIDA_S", 0.0)
PRE_LISTEN_SILENCE_S: float = _env_float("ASISTENTE_SILENCIO_ANTES_ESCUCHAR_S", 0.0)

# En esta parte se debe poner el índice del micrófono que se va a usar. En este caso se usa el micrófono Brio por motivos de calidad de audio.
# Desde la raíz del proyecto (con el venv ya creado):
#   .venv\Scripts\python.exe -c "import speech_recognition as sr; [print(i, '-', n) for i, n in enumerate(sr.Microphone.list_microphone_names())]"
# 0 - Microphone (Realtek High Definition Audio)
# 1 - Microphone (Realtek High Definition Audio)
# 2 - Microphone (Realtek High Definition Audio)
# 3 - Microphone (Brio)
MIC_DEVICE_INDEX_OVERRIDE: int | None = 3

_mic_raw = os.environ.get("ASISTENTE_MIC_INDEX", "").strip()
if _mic_raw:
    try:
        MIC_DEVICE_INDEX: int | None = int(_mic_raw)
    except ValueError:
        print("ASISTENTE_MIC_INDEX debe ser un número; se ignora.")
        MIC_DEVICE_INDEX = MIC_DEVICE_INDEX_OVERRIDE
else:
    MIC_DEVICE_INDEX = MIC_DEVICE_INDEX_OVERRIDE

# Palabras de activación y verbos permitidos: deben coincidir con la gramática en gramatica.py (AV y V).
WAKE_WORDS: frozenset[str] = frozenset({"alexa", "siri", "google", "cortana"})
VERBOS: frozenset[str] = frozenset(
    {
        "canta",
        "escribe",
        "reproduce",
        "reproducir",
        "busca",
        "buscar",
        "abre",
        "abrir",
        "inicia",
    }
)


def _windows_root() -> Path:
    return Path(os.environ.get("SystemRoot", r"C:\Windows"))


def _candidates_edge() -> list[Path]:
    return [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]


def _candidates_word() -> list[Path]:
    return [
        Path(r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"),
        Path(r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE"),
        Path(r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE"),
    ]


def _first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.is_file():
            return p
    return None


def resolver_ruta_aplicacion(alias: str) -> Path | None:
    """Devuelve la ruta al .exe si existe (notepad, word, documento, edge). Si Edge/Word están en otra carpeta, agrega rutas en _candidates_*."""
    alias = alias.lower()
    if alias == "notepad":
        p = _windows_root() / "System32" / "notepad.exe"
        return p if p.is_file() else None
    if alias in ("word", "documento"):
        return _first_existing(_candidates_word())
    if alias == "edge":
        return _first_existing(_candidates_edge())
    return None


# Nombres amigables para que el TTS diga "abriendo Word" en lugar del alias crudo.
ALIAS_ETIQUETA: dict[str, str] = {
    "notepad": "Bloc de notas",
    "word": "Word",
    "documento": "Word",
    "edge": "Microsoft Edge",
}
