# Bucle principal del asistente.
# Flujo: escuchar/leer -> normalizar -> CFG -> hechos -> reglas -> actuar -> hablar

from __future__ import annotations

from asistente_voz.config import LISTAR_REGLAS, VERBOS, WAKE_WORDS, env_si
from asistente_voz.experto.hechos import hechos_desde_analisis
from asistente_voz.experto.motor import ejecutar_resultado, inferir
from asistente_voz.experto.reglas import listar_reglas
from asistente_voz.gramatica import analizar_comando
from asistente_voz.texto import normalize, poner_wake_word_primera, tokenizar
from asistente_voz.voz_stt import ReconocimientoVoz
from asistente_voz.voz_tts import GeneradorVoz


def procesar_comando(comando: str, voz: GeneradorVoz) -> None:
    tokens = poner_wake_word_primera(tokenizar(comando), WAKE_WORDS, verbos=VERBOS)
    if not tokens:
        return

    analisis = analizar_comando(tokens)
    hechos = hechos_desde_analisis(analisis)
    resultado = inferir(hechos)
    ejecutar_resultado(resultado, voz.generar_voz)


def main() -> None:
    # ASISTENTE_TEXTO=1 = escribes el comando en consola (util en clase)
    modo_texto = env_si("ASISTENTE_TEXTO")
    voz = GeneradorVoz()
    mic = None if modo_texto else ReconocimientoVoz()

    if LISTAR_REGLAS:
        listar_reglas()

    voz.generar_voz("Asistente listo. Di un comando.")
    print("Ctrl+C para salir.")
    if modo_texto:
        print("(Modo texto activo)")

    try:
        while True:
            if modo_texto:
                raw = input("Comando > ").strip()
                if not raw:
                    continue
                comando = normalize(raw)
            else:
                raw = mic.escuchar_audio() if mic else ""
                if raw:
                    print(f"\n  [Google] {raw}")
                comando = normalize(raw)
                if not comando:
                    print("(Sin texto: silencio, red o microfono.)\n")
                    continue

            procesar_comando(comando, voz)
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo.")
        voz.generar_voz("Hasta luego.")


if __name__ == "__main__":
    main()
