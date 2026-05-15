"""Bucle del asistente: escucha o lee texto, pasa la gramática y ejecuta acciones."""

from __future__ import annotations

# Ciclo percibir → interpretar → actuar.
# Si quieres un comando nuevo: (1) amplía la CFG en gramatica.py y VERBOS/WAKE en config.py alineados;
# (2) pon la lógica en acciones.py si conviene reutilizar; (3) aquí en procesar_comando agrega un elif
# con el verbo y llama a tu función (igual que reproduce / busca / abre).

import time

from asistente_voz.acciones import (
    detectar_alias_app_en_tokens,
    ejecutar_abrir_aplicacion,
    ejecutar_busqueda_google,
    ejecutar_reproducir_youtube,
)
from asistente_voz.config import POST_WELCOME_SILENCE_S, VERBOS, WAKE_WORDS, env_si
from asistente_voz.gramatica import comando_valido_según_gramatica
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


def _verbo_y_resto(tokens: list[str]) -> tuple[str | None, list[str]]:
    # Tras la wake word, el verbo es la primera palabra que coincida con VERBOS (config.py).
    if len(tokens) < 2:
        return None, []
    for i, tok in enumerate(tokens[1:], start=1):
        if tok in VERBOS:
            return tok, tokens[i + 1 :]
    return None, []


def procesar_comando(comando_normalizado: str, generador_voz: GeneradorVoz) -> None:
    tokens = poner_wake_word_primera(
        tokenizar(comando_normalizado), WAKE_WORDS, verbos=VERBOS
    )
    if not tokens:
        return

    if tokens[0] not in WAKE_WORDS:
        muestra = " ".join(tokens[:12]) + ("…" if len(tokens) > 12 else "")
        print(f"(Falta Alexa/Siri/Google/Cortana al inicio. Transcripción: {muestra})")
        generador_voz.generar_voz(
            "Inicia el comando con Alexa, Siri, Google o Cortana."
        )
        return

    if not comando_valido_según_gramatica(tokens):
        print("Esa frase no cuadra con la gramática.")
        generador_voz.generar_voz(
            "Esa frase no coincide con la gramática que programamos."
        )
        return

    verbo, cola = _verbo_y_resto(tokens)
    if verbo is None:
        generador_voz.generar_voz("No encontré un verbo de acción en tu comando.")
        return

    def hablar(msg: str) -> None:
        generador_voz.generar_voz(msg)

    if verbo in ("reproduce", "reproducir"):
        ejecutar_reproducir_youtube(" ".join(cola), hablar)
    elif verbo in ("busca", "buscar"):
        ejecutar_busqueda_google(" ".join(cola), hablar)
    elif verbo in ("abre", "abrir", "inicia"):
        alias = detectar_alias_app_en_tokens(cola)
        if alias is None:
            print("Di: notepad, word, edge o documento.")
            hablar("Di qué aplicación abrir: bloc de notas, Word o Edge.")
        else:
            ejecutar_abrir_aplicacion(alias, hablar)
    else:
        hablar("No tengo una acción definida para ese verbo todavía.")


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

    generador.generar_voz("Asistente listo. Di un comando.")
    if not modo_texto and POST_WELCOME_SILENCE_S > 0:
        time.sleep(POST_WELCOME_SILENCE_S)
    print("Ctrl+C para salir.")
    if modo_texto:
        print("(Modo texto: ASISTENTE_TEXTO=1)")

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
