# Speech-To-Text (STT): microfono -> texto.
# Usamos SpeechRecognition + el servicio de Google (necesita internet).
# Si no quieres pelearte con el micro, en el agente pon ASISTENTE_TEXTO=1.

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
        # El Recognizer es el que calibra ruido, escucha y manda a Google
        self.recognizer = sr.Recognizer()
        # Un poquito de pausa para no cortar la frase a la mitad
        self.recognizer.pause_threshold = 0.55
        self._ya_calibre = False

        # Aviso en consola de que micro vamos a usar
        nombres = sr.Microphone.list_microphone_names()
        if MIC_DEVICE_INDEX is not None and 0 <= MIC_DEVICE_INDEX < len(nombres):
            print(f"Microfono: {MIC_DEVICE_INDEX} -> {nombres[MIC_DEVICE_INDEX]}")
        else:
            print("Microfono: el de por defecto del sistema")

    def escuchar_audio(self) -> str:
        # Devuelve el texto reconocido o "" si hubo silencio / error
        try:
            # Si fijamos un indice de micro en config, se lo pasamos aqui
            kwargs = {}
            if MIC_DEVICE_INDEX is not None:
                kwargs["device_index"] = MIC_DEVICE_INDEX

            with sr.Microphone(**kwargs) as source:
                # Solo la primera vez medimos el ruido de fondo
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

                # Aqui sale a internet: Google nos regresa el texto
                print("Enviando a Google...")
                texto = self.recognizer.recognize_google(audio, language=LANGUAGE_STT)
                print(f"Texto: {texto}")
                return texto.lower()

        except sr.WaitTimeoutError:
            # Nadie hablo a tiempo
            print("Se acabo el tiempo y no detecte voz.")
        except sr.UnknownValueError:
            # Hubo audio pero Google no saco texto claro
            print("Google no entendio el audio.")
        except sr.RequestError as e:
            # Sin red o el servicio fallo
            print(f"Fallo de red o del servicio: {e}")
        except OSError as e:
            # El micro no abrio (permisos, dispositivo, etc.)
            print(f"Problema con el microfono: {e}")

        return ""
