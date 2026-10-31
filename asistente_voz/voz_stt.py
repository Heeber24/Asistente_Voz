# Aqui se escucha el microfono y se manda el audio a Google para sacar texto.
# Si quieres probar sin micro, usa ASISTENTE_TEXTO=1 en el agente.

from __future__ import annotations

import speech_recognition as sr

from asistente_voz.config import (
    LANGUAGE_STT,
    LISTEN_TIMEOUT_S,
    MIC_DEVICE_INDEX,
    PHRASE_TIME_LIMIT_S,
)


class ReconocimientoVoz:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.55
        self._ya_calibre = False

        # Solo para saber que micro estamos usando
        nombres = sr.Microphone.list_microphone_names()
        if MIC_DEVICE_INDEX is not None and 0 <= MIC_DEVICE_INDEX < len(nombres):
            print(f"Microfono: {MIC_DEVICE_INDEX} -> {nombres[MIC_DEVICE_INDEX]}")
        else:
            print("Microfono: el de por defecto del sistema")

    def escuchar_audio(self) -> str:
        try:
            kwargs = {}
            if MIC_DEVICE_INDEX is not None:
                kwargs["device_index"] = MIC_DEVICE_INDEX

            with sr.Microphone(**kwargs) as source:
                # La primera vez ajustamos un poco el ruido de fondo
                if not self._ya_calibre:
                    print("Calibrando ruido de fondo...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    self._ya_calibre = True

                print(f"Escuchando (espera hasta {LISTEN_TIMEOUT_S}s)...")
                audio = self.recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT_S,
                    phrase_time_limit=PHRASE_TIME_LIMIT_S,
                )

                print("Enviando a Google...")
                texto = self.recognizer.recognize_google(audio, language=LANGUAGE_STT)
                print(f"Texto: {texto}")
                return texto.lower()

        except sr.WaitTimeoutError:
            print("Se acabo el tiempo y no detecte voz.")
        except sr.UnknownValueError:
            print("Google no entendio el audio.")
        except sr.RequestError as e:
            print(f"Fallo de red o del servicio: {e}")
        except OSError as e:
            print(f"Problema con el microfono: {e}")

        return ""
