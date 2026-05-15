"""Arranque del asistente. Desde la carpeta del proyecto: python Asistente_Voz_IA.py"""

# Punto de entrada: mete la raíz del repo en sys.path y delega en asistente_voz.agente.main().
# Equivale a scripts/ejecutar_asistente.py pero asumiendo que corres este archivo desde la raíz (donde está el .py).

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from asistente_voz.agente import main

if __name__ == "__main__":
    main()
