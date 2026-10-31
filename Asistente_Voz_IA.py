# Arranque: python Asistente_Voz_IA.py
# (desde la carpeta raiz del repo)

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from asistente_voz.agente import main

if __name__ == "__main__":
    main()
