"""Arranque del asistente. Desde la raíz del repo: python Asistente_Voz_IA.py"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agente import main

if __name__ == "__main__":
    main()
