# Gramatica libre de contexto (CFG) con NLTK.
# La idea: si la frase no encaja en estas reglas, el asistente NO inventa nada.
# Solo responde cuando el parseo sale bien.

from __future__ import annotations

from dataclasses import dataclass, field

import nltk
from nltk.tree import Tree

from asistente_voz.config import (
    APPS_LEXICO,
    DETERMINANTES,
    MOSTRAR_ARBOL,
    VERBOS,
    VERBOS_OBJETO_ABIERTO,
    WAKE_WORDS,
)


@dataclass
class AnalisisSintactico:
    # Lo que le pasamos despues a la base de hechos
    valido: bool
    tokens: list[str] = field(default_factory=list)
    plantilla: list[str] = field(default_factory=list)
    wake: str | None = None
    verbo: str | None = None
    objeto_tokens: list[str] = field(default_factory=list)
    arbol: Tree | None = None
    arbol_texto: str = ""
    codigo_error: str | None = None
    mensaje_error: str | None = None


def _alts(palabras) -> str:
    # Arma 'alexa' | 'siri' | ... para pegarlo en el string de la CFG
    return " | ".join(f"'{p}'" for p in sorted(palabras))


def construir_gramatica_texto() -> str:
    # La CFG se arma desde config para no desalinear vocabulario a mano.
    # OBJ (__objeto__) es el comodin para "reproduce X" / "busca Y".
    return f"""
S -> AV VP
AV -> {_alts(WAKE_WORDS)}
VP -> V | V OBJ | V DET N | V N
DET -> {_alts(DETERMINANTES)}
N -> {_alts(APPS_LEXICO)}
V -> {_alts(VERBOS)}
OBJ -> '__objeto__'
""".strip()


_parser = nltk.ChartParser(nltk.CFG.fromstring(construir_gramatica_texto()))


def gramatica_actual() -> str:
    return construir_gramatica_texto()


def _indice_verbo(tokens: list[str]) -> int | None:
    for i, tok in enumerate(tokens[1:], start=1):
        if tok in VERBOS:
            return i
    return None


def _error_previo(tokens: list[str]) -> AnalisisSintactico | None:
    # Revisamos lo obvio antes de llamar al parser (mensajes mas claros)
    if not tokens:
        return AnalisisSintactico(
            valido=False,
            codigo_error="SIN_TOKENS",
            mensaje_error="No recibí ninguna palabra para analizar.",
        )

    if tokens[0] not in WAKE_WORDS:
        wakes = ", ".join(sorted(WAKE_WORDS))
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            codigo_error="FALTA_WAKE",
            mensaje_error=f"Empieza con una palabra de activacion ({wakes}).",
        )

    vi = _indice_verbo(tokens)
    if vi is None:
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            wake=tokens[0],
            codigo_error="SIN_VERBO",
            mensaje_error=f"No encontre un verbo conocido. Usa: {', '.join(sorted(VERBOS))}.",
        )

    verbo = tokens[vi]
    cola = tokens[vi + 1 :]
    if verbo in VERBOS_OBJETO_ABIERTO and not cola:
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            wake=tokens[0],
            verbo=verbo,
            codigo_error="OBJETO_VACIO",
            mensaje_error=f"Despues de «{verbo}» tienes que decir que reproducir o buscar.",
        )

    return None


def _plantilla(tokens: list[str]) -> tuple[list[str], str, list[str]]:
    # Para reproduce/busca no listamos cada cancion en la CFG:
    # cambiamos la cola por __objeto__ y el parser solo checa la estructura.
    vi = _indice_verbo(tokens)
    assert vi is not None
    verbo = tokens[vi]
    cola = tokens[vi + 1 :]
    if verbo in VERBOS_OBJETO_ABIERTO:
        return [tokens[0], verbo, "__objeto__"], verbo, cola
    return tokens, verbo, cola


def analizar_comando(tokens: list[str], *, mostrar_arbol: bool | None = None) -> AnalisisSintactico:
    # 1) errores faciles  2) armar plantilla  3) parsear  4) mostrar arbol
    previo = _error_previo(tokens)
    if previo is not None:
        return previo

    plantilla, verbo, cola = _plantilla(tokens)
    wake = tokens[0]

    try:
        arboles = list(_parser.parse(plantilla))
    except (ValueError, RuntimeError) as e:
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            plantilla=plantilla,
            wake=wake,
            verbo=verbo,
            objeto_tokens=cola,
            codigo_error="ERROR_PARSER",
            mensaje_error=f"El parser fallo: {e}",
        )

    if not arboles:
        apps = ", ".join(sorted(APPS_LEXICO))
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            plantilla=plantilla,
            wake=wake,
            verbo=verbo,
            objeto_tokens=cola,
            codigo_error="FUERA_DE_GRAMATICA",
            mensaje_error=(
                f"La frase no cuadra con la gramatica. "
                f"Si usas «abre», prueba: {apps}."
            ),
        )

    arbol = arboles[0]
    arbol_texto = arbol.pformat(margin=70)
    if mostrar_arbol if mostrar_arbol is not None else MOSTRAR_ARBOL:
        print("\n--- Arbol sintactico ---")
        print(f"Original : {' '.join(tokens)}")
        print(f"Plantilla: {' '.join(plantilla)}")
        print(arbol_texto)
        print("--- fin arbol ---\n")

    return AnalisisSintactico(
        valido=True,
        tokens=tokens,
        plantilla=plantilla,
        wake=wake,
        verbo=verbo,
        objeto_tokens=cola,
        arbol=arbol,
        arbol_texto=arbol_texto,
    )
