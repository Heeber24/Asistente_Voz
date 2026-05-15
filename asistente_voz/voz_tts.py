"""Voz de salida: en Windows usa SAPI por COM; si no, pyttsx3."""

from __future__ import annotations

# En Windows por defecto se usa SAPI (win32com) para evitar bloqueos de pyttsx3.
# ASISTENTE_TTS_PYTTSX3=1 fuerza motor pyttsx3. ASISTENTE_TTS_VOZ_ES=1 intenta elegir voz en español si el sistema la tiene.
# ASISTENTE_SAPI_RATE: -10 a 10 (ritmo SAPI); el volumen sigue TTS_VOLUME de config.

import os
import sys
import traceback

import pyttsx3

from asistente_voz.config import TTS_RATE, TTS_VOLUME, env_si


def _sapi_rate() -> int:
    raw = os.environ.get("ASISTENTE_SAPI_RATE", "").strip()
    if raw:
        try:
            return max(-10, min(10, int(raw)))
        except ValueError:
            pass
    return 0


def _hablar_sapi_com(texto: str) -> bool:
    try:
        import win32com.client  # type: ignore[import-untyped]

        sp = win32com.client.Dispatch("SAPI.SpVoice")
        sp.Volume = int(max(0, min(100, round(TTS_VOLUME * 100))))
        sp.Rate = _sapi_rate()
        sp.Speak(texto, 0)
        return True
    except Exception as e:
        print(f"[TTS] SAPI: {e}")
        return False


def _motor_pyttsx3() -> pyttsx3.Engine:
    if sys.platform == "win32":
        try:
            eng = pyttsx3.init("sapi5")
        except Exception:
            eng = pyttsx3.init()
    else:
        eng = pyttsx3.init()
    eng.setProperty("rate", TTS_RATE)
    try:
        eng.setProperty("volume", max(0.0, min(1.0, TTS_VOLUME)))
    except Exception:
        pass
    if env_si("ASISTENTE_TTS_VOZ_ES"):
        try:
            for v in eng.getProperty("voices") or []:
                n = (getattr(v, "name", "") or "").lower()
                vid = (getattr(v, "id", "") or "").lower()
                if any(
                    x in n or x in vid
                    for x in ("español", "spanish", "es-mx", "es_es", "helena", "sabina", "pablo")
                ):
                    eng.setProperty("voice", v.id)
                    break
        except Exception:
            pass
    return eng


class GeneradorVoz:
    def __init__(self) -> None:
        self._pyttsx3: pyttsx3.Engine | None = None
        self._preferir_com = sys.platform == "win32" and not env_si("ASISTENTE_TTS_PYTTSX3")
        if not self._preferir_com:
            self._pyttsx3 = _motor_pyttsx3()

    def generar_voz(self, texto: str) -> None:
        if not texto:
            return
        print(f"[TTS] {texto[:100]}{'…' if len(texto) > 100 else ''}", flush=True)
        if self._preferir_com and _hablar_sapi_com(texto):
            return
        if self._pyttsx3 is None:
            self._pyttsx3 = _motor_pyttsx3()
        try:
            self._pyttsx3.say(texto)
            self._pyttsx3.runAndWait()
        except Exception as e:
            print(f"[TTS] pyttsx3: {e}")
            traceback.print_exc()
            try:
                self._pyttsx3.stop()
            except Exception:
                pass
            self._pyttsx3 = _motor_pyttsx3()
            try:
                self._pyttsx3.say(texto)
                self._pyttsx3.runAndWait()
            except Exception as e2:
                print(f"[TTS] reintento: {e2}")
