"""Prueba rápida del pipeline CFG → hechos → inferencia (sin micrófono ni TTS).

Desde la raíz del repo:
    python scripts/probar_experto.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Silenciar ruido didáctico en la prueba automatizada
import os

os.environ.setdefault("ASISTENTE_MOSTRAR_ARBOL", "0")
os.environ.setdefault("ASISTENTE_MOSTRAR_HECHOS", "0")
os.environ.setdefault("ASISTENTE_LISTAR_REGLAS", "0")

from config import VERBOS, WAKE_WORDS
from experto.hechos import hechos_desde_analisis
from experto.motor import inferir
from gramatica import analizar_comando, gramatica_actual
from texto import normalize, poner_wake_word_primera, tokenizar


def _pipeline(frase: str) -> str:
    tokens = poner_wake_word_primera(
        tokenizar(normalize(frase)), WAKE_WORDS, verbos=VERBOS
    )
    analisis = analizar_comando(tokens, mostrar_arbol=False)
    hechos = hechos_desde_analisis(analisis)
    return inferir(hechos).accion


CASOS = [
    ("alexa reproduce luis miguel", "reproducir_youtube"),
    ("siri busca tutorial python", "buscar_google"),
    ("google abre el notepad", "abrir_aplicacion"),
    ("cortana abre edge", "abrir_aplicacion"),
    ("alexa abre", "pedir_aplicacion"),
    ("reproduce algo", "error_sintactico"),  # falta wake
    ("alexa reproduce", "error_sintactico"),  # objeto vacío
    ("alexa vuela a casa", "error_sintactico"),  # verbo desconocido
]


def main() -> int:
    print("CFG vigente:\n")
    print(gramatica_actual())
    print()
    fallos = 0
    for frase, esperada in CASOS:
        obtenida = _pipeline(frase)
        ok = obtenida == esperada
        marca = "OK" if ok else "FAIL"
        if not ok:
            fallos += 1
        print(f"[{marca}] {frase!r} → {obtenida} (esperada {esperada})")
    print(f"\n{len(CASOS) - fallos}/{len(CASOS)} casos correctos.")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
