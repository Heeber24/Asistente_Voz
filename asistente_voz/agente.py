"""Bucle del asistente: percibir → analizar (CFG) → inferir (experto) → actuar.

Ya no despacha con if/elif por verbo: tras un parse válido, la *base de hechos*
y el *motor de inferencia* eligen la regla SI … ENTONCES …
(ver ``asistente_voz/experto/``).
"""

from __future__ import annotations

import time

from asistente_voz.config import (
    LISTAR_REGLAS_AL_INICIO,
    POST_WELCOME_SILENCE_S,
    VERBOS,
    WAKE_WORDS,
    env_si,
)
from asistente_voz.experto.hechos import hechos_desde_analisis
from asistente_voz.experto.motor import ejecutar_resultado, inferir
from asistente_voz.experto.reglas import listar_reglas
from asistente_voz.gramatica import analizar_comando
from asistente_voz.texto import normalize, poner_wake_word_primera, tokenizar
from asistente_voz.voz_stt import ReconocimientoVoz
from asistente_voz.voz_tts import GeneradorVoz


def _mostrar_transcripcion(raw: str, voz: GeneradorVoz | None) -> None:
    # Eco en consola; ASISTENTE_REPETIR_STT_VOZ=1 hace que el TTS repita lo escuchado (útil para depurar STT).
    raw = raw.strip()
    if not raw:
        return
    print(f"\n  [Google] {raw}")
    if voz is not None and env_si("ASISTENTE_REPETIR_STT_VOZ"):
        eco = raw if len(raw) <= 160 else raw[:157] + "..."
        voz.generar_voz(f"He escuchado: {eco}")


def procesar_comando(comando_normalizado: str, generador_voz: GeneradorVoz) -> None:
    tokens = poner_wake_word_primera(
        tokenizar(comando_normalizado), WAKE_WORDS, verbos=VERBOS
    )
    if not tokens:
        return

    # 1) Analizador sintáctico (CFG)
    analisis = analizar_comando(tokens)
    # 2) Base de hechos a partir del árbol / diagnóstico
    hechos = hechos_desde_analisis(analisis)
    # 3) Motor de inferencia (reglas de producción)
    resultado = inferir(hechos)

    def hablar(msg: str) -> None:
        generador_voz.generar_voz(msg)

    # 4) Ejecutar la acción inferida (o el mensaje de error sintáctico)
    ejecutar_resultado(resultado, hablar)


def _entrada_texto() -> str:
    try:
        return input("Comando > ").strip()
    except EOFError:
        return ""


def main() -> None:
    # ASISTENTE_TEXTO=1: sin micrófono, escribes el comando en consola (útil en aula o depuración).
    modo_texto = env_si("ASISTENTE_TEXTO")
    generador = GeneradorVoz()
    escucha = None if modo_texto else ReconocimientoVoz()

    if LISTAR_REGLAS_AL_INICIO:
        listar_reglas()

    generador.generar_voz("Asistente listo. Di un comando.")
    if not modo_texto and POST_WELCOME_SILENCE_S > 0:
        time.sleep(POST_WELCOME_SILENCE_S)
    print("Ctrl+C para salir.")
    if modo_texto:
        print("(Modo texto: ASISTENTE_TEXTO=1)")
    print(
        "Pipeline: STT/texto → CFG (árbol) → hechos → reglas → acción → TTS. "
        "Oculta árbol/hechos con ASISTENTE_OCULTAR_ARBOL=1 o ASISTENTE_OCULTAR_HECHOS=1."
    )

    try:
        while True:
            if modo_texto:
                raw = _entrada_texto()
                if not raw:
                    continue
                comando = normalize(raw)
            else:
                raw = escucha.escuchar_audio() if escucha else ""
                _mostrar_transcripcion(raw, generador)
                comando = normalize(raw)
                if not comando:
                    print("(Sin texto: silencio, red o micrófono.)\n")

            procesar_comando(comando, generador)
    except KeyboardInterrupt:
        print("\nSaliendo.")
        generador.generar_voz("Hasta luego.")


if __name__ == "__main__":
    main()
