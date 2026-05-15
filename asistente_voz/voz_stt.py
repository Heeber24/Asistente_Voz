"""Micrófono + Google Speech-to-Text."""

from __future__ import annotations

# Reconocimiento: calibración de ruido, listen() y recognize_google con LANGUAGE_STT.
# Parámetros finos (timeouts, umbral de energía, índice de mic) vienen de config.py o variables ASISTENTE_*.
# ASISTENTE_LISTAR_MICS=1 al arrancar imprime todos los índices de entrada (útil para elegir MIC_DEVICE_INDEX_OVERRIDE).

import time

import speech_recognition as sr

from asistente_voz.config import (
    AMBIENT_NOISE_DURATION_S,
    AMBIENT_RECALIBRATE_EVERY,
    LANGUAGE_STT,
    LISTEN_TIMEOUT_S,
    MIC_DEVICE_INDEX,
    PHRASE_TIME_LIMIT_S,
    PRE_LISTEN_SILENCE_S,
    STT_DEBUG,
    STT_DYNAMIC_ENERGY,
    STT_ENERGY_THRESHOLD_MAX,
    STT_ENERGY_THRESHOLD_MIN,
    STT_ENERGY_THRESHOLD_MULT,
    env_si,
)


def _indice_entrada_por_defecto() -> int | None:
    try:
        pa = sr.Microphone.get_pyaudio().PyAudio()
        try:
            return int(pa.get_default_input_device_info()["index"])
        finally:
            pa.terminate()
    except OSError:
        return None


def _texto_mic_activo() -> str:
    nombres = sr.Microphone.list_microphone_names()
    if MIC_DEVICE_INDEX is not None:
        if 0 <= MIC_DEVICE_INDEX < len(nombres):
            return f"índice {MIC_DEVICE_INDEX} → {nombres[MIC_DEVICE_INDEX]}"
        return f"índice {MIC_DEVICE_INDEX} (inválido; hay {len(nombres)} dispositivos)"
    idx = _indice_entrada_por_defecto()
    if idx is None:
        return "entrada por defecto del sistema"
    nm = nombres[idx] if 0 <= idx < len(nombres) else "?"
    return f"por defecto Windows, índice {idx} → {nm}"


class ReconocimientoVoz:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = STT_DYNAMIC_ENERGY
        self.recognizer.pause_threshold = 0.55
        self._mic_index = MIC_DEVICE_INDEX
        self._calibrado = False
        self._n_escucha = 0

        print(f"Micrófono: {_texto_mic_activo()}")
        if MIC_DEVICE_INDEX is None:
            print(
                "(Sin índice fijo: Windows usa el micrófono por defecto. "
                "Puedes fijar ASISTENTE_MIC_INDEX o MIC_DEVICE_INDEX_OVERRIDE en config.)\n"
            )

        if env_si("ASISTENTE_LISTAR_MICS"):
            activo = MIC_DEVICE_INDEX if MIC_DEVICE_INDEX is not None else _indice_entrada_por_defecto()
            print("Dispositivos de entrada:")
            for i, nombre in enumerate(sr.Microphone.list_microphone_names()):
                extra = "  <-- este" if activo is not None and i == activo else ""
                print(f"  {i}: {nombre}{extra}")

    def _recalibrar(self) -> bool:
        n = AMBIENT_RECALIBRATE_EVERY
        if not self._calibrado:
            return True
        if n <= 0:
            return False
        if n == 1:
            return True
        return ((self._n_escucha - 1) % n) == 0

    def _ajustar_umbral_opcional(self) -> None:
        if abs(STT_ENERGY_THRESHOLD_MULT - 1.0) < 1e-9:
            if STT_DEBUG:
                print(f"[STT] umbral energía: {self.recognizer.energy_threshold:.0f}")
            return
        base = float(self.recognizer.energy_threshold)
        val = int(base * STT_ENERGY_THRESHOLD_MULT)
        val = max(STT_ENERGY_THRESHOLD_MIN, min(STT_ENERGY_THRESHOLD_MAX, val))
        self.recognizer.energy_threshold = val
        if STT_DEBUG:
            print(f"[STT] umbral {base:.0f} → {val}")

    def escuchar_audio(self) -> str:
        self._n_escucha += 1
        if PRE_LISTEN_SILENCE_S > 0:
            time.sleep(PRE_LISTEN_SILENCE_S)
        try:
            kwargs: dict = {}
            if self._mic_index is not None:
                kwargs["device_index"] = self._mic_index
            with sr.Microphone(**kwargs) as source:
                if self._recalibrar():
                    print("Calibrando ruido de fondo…")
                    self.recognizer.adjust_for_ambient_noise(
                        source, duration=AMBIENT_NOISE_DURATION_S
                    )
                    self._ajustar_umbral_opcional()
                    self._calibrado = True
                elif STT_DEBUG:
                    print("[STT] sin recalibrar")

                lim = f", máx. {PHRASE_TIME_LIMIT_S:.0f}s" if PHRASE_TIME_LIMIT_S > 0 else ""
                print(f"Escuchando (espera hasta {LISTEN_TIMEOUT_S}s para hablar{lim})…")

                kw: dict = {"timeout": LISTEN_TIMEOUT_S}
                if PHRASE_TIME_LIMIT_S > 0:
                    kw["phrase_time_limit"] = PHRASE_TIME_LIMIT_S
                audio = self.recognizer.listen(source, **kw)
                if STT_DEBUG:
                    print(f"[STT] bytes audio: {len(audio.frame_data)}")
                print("Enviando a Google…")
                text = self.recognizer.recognize_google(audio, language=LANGUAGE_STT)
                print(f"Texto: {text}")
                return text.lower()
        except sr.WaitTimeoutError:
            print("Se acabó el tiempo sin detectar voz.")
        except sr.UnknownValueError:
            print("Google no entendió el audio.")
        except sr.RequestError as e:
            print(f"Fallo de red o del servicio: {e}")
        except OSError as e:
            print(f"Micrófono: {e}")
        return ""
