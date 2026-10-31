# Cerebro / orquestador del asistente.
# Aqui se conecta todo el pipeline:
#
#   escuchar o leer
#        |
#        v
#   normalizar + tokenizar
#        |
#        v
#   gramatica CFG  ----si falla----> mensaje de error por voz
#        |
#        v
#   base de hechos
#        |
#        v
#   motor de inferencia (reglas)
#        |
#        v
#   accion (YouTube / Google / abrir app) + TTS

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
    # Una peticion completa: del texto ya normalizado hasta la accion

    # 1) tokens + acomodar wake word si Google la puso al reves
    tokens = poner_wake_word_primera(tokenizar(comando), WAKE_WORDS, verbos=VERBOS)
    if not tokens:
        return

    # 2) analisis sintactico (CFG)
    analisis = analizar_comando(tokens)

    # 3) pasamos el analisis a hechos
    hechos = hechos_desde_analisis(analisis)

    # 4) el motor elige que regla aplica
    resultado = inferir(hechos)

    # 5) ejecutamos la accion (o el error sintactico)
    ejecutar_resultado(resultado, voz.generar_voz)


def main() -> None:
    # Arranque del bucle infinito del asistente

    # Si ASISTENTE_TEXTO=1, no usamos micro: escribes el comando a mano
    modo_texto = env_si("ASISTENTE_TEXTO")
    voz = GeneradorVoz()
    mic = None if modo_texto else ReconocimientoVoz()

    # Al inicio mostramos las reglas cargadas (util en clase)
    if LISTAR_REGLAS:
        listar_reglas()

    voz.generar_voz("Asistente listo. Di un comando.")
    print("Ctrl+C para salir.")
    if modo_texto:
        print("(Modo texto activo)")

    try:
        while True:
            if modo_texto:
                # Entrada por teclado
                raw = input("Comando > ").strip()
                if not raw:
                    continue
                comando = normalize(raw)
            else:
                # Entrada por microfono
                raw = mic.escuchar_audio() if mic else ""
                if raw:
                    print(f"\n  [Google] {raw}")
                comando = normalize(raw)
                if not comando:
                    print("(Sin texto: silencio, red o microfono.)\n")
                    continue

            procesar_comando(comando, voz)

    except (KeyboardInterrupt, EOFError):
        # Ctrl+C o fin de entrada
        print("\nSaliendo.")
        voz.generar_voz("Hasta luego.")


if __name__ == "__main__":
    main()
