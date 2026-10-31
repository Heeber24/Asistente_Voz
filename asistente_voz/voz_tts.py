# Aqui el asistente habla. En Windows intento SAPI; si no jala, uso pyttsx3.
# No hay que complicarlo: con uno de los dos basta para la demo.

from __future__ import annotations

import sys

import pyttsx3

from asistente_voz.config import TTS_RATE, TTS_VOLUME, env_si


def _hablar_con_sapi(texto: str) -> bool:
    # Esto solo existe en Windows si tienes pywin32
    try:
        import win32com.client  # type: ignore

        voz = win32com.client.Dispatch("SAPI.SpVoice")
        voz.Volume = int(TTS_VOLUME * 100)
        voz.Speak(texto, 0)
        return True
    except Exception:
        return False


def _crear_pyttsx3() -> pyttsx3.Engine:
    motor = pyttsx3.init()
    motor.setProperty("rate", TTS_RATE)
    motor.setProperty("volume", TTS_VOLUME)
    return motor


class GeneradorVoz:
    def __init__(self) -> None:
        # En Windows preferimos SAPI; si pones ASISTENTE_TTS_PYTTSX3=1 forzamos pyttsx3
        self._usar_sapi = sys.platform == "win32" and not env_si("ASISTENTE_TTS_PYTTSX3")
        self._motor = None if self._usar_sapi else _crear_pyttsx3()

    def generar_voz(self, texto: str) -> None:
        if not texto:
            return

        print(f"[TTS] {texto}")

        if self._usar_sapi and _hablar_con_sapi(texto):
            return

        # Plan B: pyttsx3
        if self._motor is None:
            self._motor = _crear_pyttsx3()
        try:
            self._motor.say(texto)
            self._motor.runAndWait()
        except Exception as e:
            print(f"No pude hablar con pyttsx3: {e}")
