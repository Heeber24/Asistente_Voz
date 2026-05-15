"""Limpieza del texto que viene del reconocedor (minúsculas, sin acentos, tokens)."""

from __future__ import annotations

# Google devuelve texto con mayúsculas y a veces acentos; normalize() lo deja estable para comparar con WAKE_WORDS y VERBOS.
# tokenizar quita puntuación típica; poner_wake_word_primera corrige cuando el STT pone primero el verbo y luego la wake word.

import string


def normalize(texto: str) -> str:
    if not texto:
        return ""
    s = texto.strip().lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        s = s.replace(a, b)
    return s


def tokenizar(comando_normalizado: str) -> list[str]:
    borde = string.punctuation + "¿¡«»"
    return [t for t in (w.strip(borde) for w in comando_normalizado.split()) if t]


def poner_wake_word_primera(
    tokens: list[str],
    wake_words: frozenset[str],
    *,
    verbos: frozenset[str],
) -> list[str]:
    """Si Google dice primero el verbo y luego Alexa/Siri/…, reordena para que el wake vaya primero."""
    if not tokens or tokens[0] in wake_words:
        return tokens
    if tokens[0] not in verbos:
        return tokens
    if len(tokens) >= 3 and tokens[1] == "google" and tokens[2] in ("busca", "buscar"):
        return tokens
    for i, t in enumerate(tokens):
        if t in wake_words:
            v0 = tokens[0]
            return [tokens[i]] + [v0] + tokens[1:i] + tokens[i + 1 :]
    return tokens
