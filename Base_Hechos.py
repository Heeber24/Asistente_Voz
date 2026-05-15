# =================================================================
# Sistema experto simple: identificar un animal a partir de rasgos.
#
# Flujo: el usuario introduce características; el programa las compara
# contra BASE_DE_CONOCIMIENTOS y ordena los animales por qué tan bien encajan.
#
# La puntuación usa F1 entre lo que dijiste y los rasgos de cada animal:
# equilibra "cuánto acertaste de tu lista" y "cuánto cubriste del animal".
# Los textos se comparan sin mayúsculas ni acentos para que coincida mejor con lo que escribe la persona.
# =================================================================

from __future__ import annotations

# -----------------------------------------------------------------------------
# Base de conocimiento: cada animal y lista de rasgos (una palabra o frase corta por rasgo).
# Todo debe estar en minúsculas o texto comparable tras normalizar (sin acentos).
# Si amplías animales, añade rasgos discriminativos (pocos pero útiles).
# -----------------------------------------------------------------------------
BASE_DE_CONOCIMIENTOS = {
    "Perro": ["ladra", "juega", "pelaje", "domesticado", "obedece"],
    "Gato": ["rasca", "juega", "maulla", "independiente", "pelaje"],
    "Pájaro": ["plumas", "pico", "vuela", "canta", "domesticado"],
    "Pez": ["branquias", "escamas", "nada", "aletas"],
    "Serpiente": ["reptil", "escamas", "se arrastra", "no tiene patas"],
    "Tigre": ["garras", "pelaje", "caza", "salvaje"],
}


def _normalizar(texto: str) -> str:
    """Minúsculas y sin acentos para comparar entrada humana con la base."""
    s = texto.strip().lower()
    for a, b in (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("ü", "u"),
        ("ñ", "n"),
    ):
        s = s.replace(a, b)
    return s


def obtener_caracteristicas() -> list[str]:
    """
    Pide entre 1 y 4 características. Escribe 'fin' para terminar antes del máximo.
    Devuelve lista normalizada (sin acentos, minúsculas).
    """
    caracteristicas: list[str] = []
    print("Ingrese entre 1 y 4 características (escriba 'fin' para terminar):")

    while len(caracteristicas) < 4:
        entrada = input(f"Característica #{len(caracteristicas) + 1}: ").strip()
        if _normalizar(entrada) == "fin":
            break
        norm = _normalizar(entrada)
        if norm and norm not in caracteristicas:
            caracteristicas.append(norm)
        else:
            print("Por favor, ingrese una característica válida y única.")

    if not caracteristicas:
        print("Debe ingresar al menos una característica. Inténtelo de nuevo.")
        return obtener_caracteristicas()

    return caracteristicas


def _f1_coincidencia(usuario: set[str], animal: set[str]) -> tuple[float, int]:
    """
    F1 entre conjuntos de rasgos: combina precisión y recall.
    Devuelve (puntuación 0–100, número de rasgos que coinciden exactamente).
    """
    if not usuario or not animal:
        return 0.0, 0
    inter = usuario & animal
    coincidencias = len(inter)
    if coincidencias == 0:
        return 0.0, 0
    precision = coincidencias / len(usuario)
    recall = coincidencias / len(animal)
    denominador = precision + recall
    if denominador <= 0:
        return 0.0, coincidencias
    f1 = 2 * precision * recall / denominador
    return f1 * 100.0, coincidencias


def inferir_animal(
    caracteristicas_ingresadas: list[str],
    base_de_conocimientos: dict[str, list[str]],
) -> list[tuple[str, float, int]]:
    """
    Ordena los animales por F1 de coincidencia de rasgos (mayor primero).
    Cada tupla es (nombre_animal, puntuación %, número de rasgos coincidentes).
    """
    usuario = {_normalizar(c) for c in caracteristicas_ingresadas}

    resultados: list[tuple[str, float, int]] = []
    for nombre, rasgos in base_de_conocimientos.items():
        conjunto_animal = {_normalizar(r) for r in rasgos}
        score, matches = _f1_coincidencia(usuario, conjunto_animal)
        resultados.append((nombre, score, matches))

    resultados.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return resultados


def main() -> None:
    print("--- Sistema de identificación de animales ---")

    caracteristicas = obtener_caracteristicas()
    print(f"\nCaracterísticas usadas: {', '.join(caracteristicas)}")

    resultados = inferir_animal(caracteristicas, BASE_DE_CONOCIMIENTOS)

    print("\nAnimales ordenados por encaje (F1 sobre tus rasgos vs los del animal):")
    hay_alguno = False
    for animal, puntaje, coinc in resultados:
        if puntaje <= 0:
            continue
        hay_alguno = True
        print(f"- {animal}: {puntaje:.0f}% ({coinc} rasgo(s) coincidente(s))")

    if not hay_alguno:
        print("\nNo hubo coincidencias con la base. Prueba sinónimos o rasgos de la lista del animal.")


if __name__ == "__main__":
    main()
