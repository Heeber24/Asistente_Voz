"""Gramática NLTK de comandos y comprobación de que la frase encaje."""

from __future__ import annotations

# GRAMATICA_TEXTO: CFG en formato string de NLTK. AV = wake, V = verbo, N = sustantivos concretos para "abre".
# Para reproduce/busca no hace falta listar cada canción o búsqueda: la cola se reemplaza por el token ficticio __objeto__
# y el parser solo comprueba estructura (S -> AV V OBJ). Si agregas un verbo nuevo, añádelo en V y en VERBOS en config.py.

import nltk

from asistente_voz.config import VERBOS, WAKE_WORDS

GRAMATICA_TEXTO = r"""
S -> AV VP
AV -> 'alexa' | 'siri' | 'google' | 'cortana'
VP -> V | V OBJ | V DET N | V N
DET -> 'el' | 'la' | 'los' | 'las' | 'al'
N -> 'perro' | 'gato' | 'luis' | 'miguel' | 'mana' | 'moderato' | 'jose'
N -> 'notepad' | 'word' | 'edge' | 'documento'
V -> 'canta' | 'escribe' | 'reproduce' | 'reproducir' | 'busca' | 'buscar' | 'abre' | 'abrir' | 'inicia'
OBJ -> '__objeto__'
"""

_gramatica = nltk.CFG.fromstring(GRAMATICA_TEXTO)
_parser = nltk.ChartParser(_gramatica)
# Verbos cuya cola libre se comprueba como un solo objeto (plantilla con __objeto__).
VERBOS_CON_OBJETO_ABIERTO = frozenset({"reproduce", "reproducir", "busca", "buscar"})


def _indice_primer_verbo(tokens: list[str]) -> int | None:
    for i, tok in enumerate(tokens[1:], start=1):
        if tok in VERBOS:
            return i
    return None


def _tokens_para_parser(tokens: list[str]) -> list[str] | None:
    if not tokens or tokens[0] not in WAKE_WORDS:
        return None
    vi = _indice_primer_verbo(tokens)
    if vi is None:
        return None
    verbo = tokens[vi]
    cola = tokens[vi + 1 :]
    if verbo in VERBOS_CON_OBJETO_ABIERTO:
        if not cola:
            return None
        return [tokens[0], verbo, "__objeto__"]
    return tokens


def comando_valido_según_gramatica(tokens: list[str]) -> bool:
    plantilla = _tokens_para_parser(tokens)
    if plantilla is None:
        return False
    try:
        return any(_parser.parse(plantilla))
    except (ValueError, RuntimeError):
        return False
