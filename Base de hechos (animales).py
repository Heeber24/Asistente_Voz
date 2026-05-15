# =================================================================
# COMPONENTE 1: BASE DE CONOCIMIENTOS (Hechos y Reglas)
#
# Esta sección contiene el conocimiento estático del sistema.
# Es un diccionario que asocia cada animal con una lista de características.
# Puedes agregar más animales y sus características aquí.
# =================================================================
BASE_DE_CONOCIMIENTOS = {
    "Perro": ["ladra", "juega", "pelaje", "domesticado", "obedece"],
    "Gato": ["araña", "juega", "maulla", "independiente", "pelaje"],
    "Pájaro": ["plumas", "pico", "vuela", "canta", "domesticado"],
    "Pez": ["branquias", "escamas", "nada", "aletas"],
    "Serpiente": ["reptil", "escamas", "se arrastra", "no tiene patas"],
    "Tigre": ["garras", "pelaje", "caza", "salvaje"],
}

# =================================================================
# COMPONENTE 2: OBTENCIÓN DE HECHOS (Interacción con el usuario)
#
# Esta función se encarga de recolectar los "hechos" o
# datos que el usuario proporciona al sistema.
# =================================================================
def obtener_caracteristicas():
    """
    Solicita al usuario que ingrese características para identificar un animal.
    Retorna una lista de las características ingresadas.
    """
    caracteristicas = []
    print("Ingrese entre 1 y 4 características (escriba 'fin' para terminar):")
    
    while len(caracteristicas) < 4:
        caracteristica = input(f"Característica #{len(caracteristicas) + 1}: ").strip().lower()
        if caracteristica == 'fin':
            break
        if caracteristica and caracteristica not in caracteristicas:
            caracteristicas.append(caracteristica)
        else:
            print("Por favor, ingrese una característica válida y única.")
    
    if len(caracteristicas) == 0:
        print("Debe ingresar al menos una característica. Inténtelo de nuevo.")
        return obtener_caracteristicas()
    
    return caracteristicas

# =================================================================
# COMPONENTE 3: MECANISMO DE INFERENCIA
#
# Esta función es el "cerebro" del sistema. Utiliza los hechos
# y la base de conocimientos para inferir la respuesta.
# =================================================================
def inferir_animal(caracteristicas_ingresadas, base_de_conocimientos):
    """
    Compara las características ingresadas con la base de conocimientos.
    Calcula un puntaje de coincidencia para cada animal.
    Retorna una lista de tuplas (animal, puntaje) ordenadas.
    """
    puntajes = {}
    
    for animal, caracteristicas_animal in base_de_conocimientos.items():
        # Contamos cuántas características ingresadas coinciden con el animal
        coincidencias = sum(1 for c in caracteristicas_ingresadas if c in caracteristicas_animal)
        
        # Calculamos el puntaje como la proporción de coincidencias
        # con respecto a las características que el animal tiene en la base de datos.
        puntaje = (coincidencias / len(caracteristicas_animal)) * 100 if caracteristicas_animal else 0
        puntajes[animal] = puntaje

    # Ordenamos los resultados del más probable al menos probable
    animales_ordenados = sorted(puntajes.items(), key=lambda x: x[1], reverse=True)
    
    return animales_ordenados

# =================================================================
# COMPONENTE 4: MECANISMO DE CONTROL (Orquestación del sistema)
#
# Esta es la función principal que coordina el flujo del programa.
# =================================================================
def main():
    """
    Función principal para ejecutar el sistema experto de identificación.
    """
    print("--- Sistema de Identificación de Animales ---")
    
    # 1. Obtención de hechos
    caracteristicas = obtener_caracteristicas()
    print(f"\nCaracterísticas ingresadas: {', '.join(caracteristicas)}")
    
    # 2. Inferencia y obtención de resultados
    resultados = inferir_animal(caracteristicas, BASE_DE_CONOCIMIENTOS)
    
    # 3. Presentación de la respuesta
    print("\nPosibles animales basados en las características ingresadas:")
    for animal, puntaje in resultados:
        # Solo mostramos los resultados que tengan al menos 1 coincidencia
        if puntaje > 0:
            print(f"- {animal} (Probabilidad: {puntaje:.0f}%)")
    
    # Si no hubo ninguna coincidencia
    if not any(puntaje > 0 for _, puntaje in resultados):
        print("\nNo se encontraron coincidencias para las características ingresadas.")

# Ejecución del sistema
if __name__ == "__main__":
    main()
