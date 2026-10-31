# Text-To-Speech (TTS): texto -> voz.
# En Windows intentamos SAPI (la voz del sistema).
# Si no esta pywin32 o falla, caemos a pyttsx3.
# Con uno de los dos alcanza para la demo.

from __future__ import annotations

import sys

import pyttsx3

from asistente_voz.config import TTS_RATE, TTS_VOLUME, env_si


def _hablar_con_sapi(texto: str) -> bool:
    # SAPI viene con Windows. Necesitas el paquete pywin32 instalado.
    try:
        import win32com.client  # type: ignore

        voz = win32com.client.Dispatch("SAPI.SpVoice")
        voz.Volume = int(TTS_VOLUME * 100)
        voz.Speak(texto, 0)  # 0 = habla y espera a terminar
        return True
    except Exception:
        # Si truena, el caller usa el plan B
        return False


def _crear_pyttsx3() -> pyttsx3.Engine:
    # Motor multiplataforma. En Windows tambien puede usar voces SAPI por debajo.
    motor = pyttsx3.init()
    motor.setProperty("rate", TTS_RATE)
    motor.setProperty("volume", TTS_VOLUME)
    return motor


class GeneradorVoz:
    def __init__(self) -> None:
        # Por defecto en Windows preferimos SAPI.
        # Si pones ASISTENTE_TTS_PYTTSX3=1, forzamos pyttsx3 desde el inicio.
        self._usar_sapi = sys.platform == "win32" and not env_si("ASISTENTE_TTS_PYTTSX3")
        self._motor = None if self._usar_sapi else _crear_pyttsx3()

    def generar_voz(self, texto: str) -> None:
        # Habla el texto. Si esta vacio, no hacemos nada.
        if not texto:
            return

        # Tambien lo imprimimos para verlo en consola
        print(f"[TTS] {texto}")

        # Intento 1: SAPI
        if self._usar_sapi and _hablar_con_sapi(texto):
            return

        # Intento 2: pyttsx3
        if self._motor is None:
            self._motor = _crear_pyttsx3()
        try:
            self._motor.say(texto)
            self._motor.runAndWait()
        except Exception as e:
            print(f"No pude hablar con pyttsx3: {e}")
