# Punto de entrada del proyecto.
# Desde la carpeta raiz corres: python Asistente_Voz_IA.py
# Este archivo solo prepara el path y manda a llamar al agente.

from __future__ import annotations

import sys
from pathlib import Path

# Metemos la raiz del repo en sys.path para poder importar los modulos del proyecto
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agente import main

# Si lo ejecutas directo (no como import), arranca el bucle del asistente
if __name__ == "__main__":
    main()
