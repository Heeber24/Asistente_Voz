# Asistente de voz por comandos

Aplicación en Python que escucha instrucciones en lenguaje natural (o las lee por teclado), las valida con una gramática formal y ejecuta acciones concretas: buscar o reproducir contenido en la web, abrir programas en Windows y responder por voz sintética.

Está pensada como **base modular**: puedes ampliar verbos, reglas gramaticales y acciones editando unos pocos archivos, sin reescribir todo el flujo.

---

## ¿Qué es y para qué sirve?

Es un **asistente por comandos** con palabra de activación (por ejemplo “Alexa …”, “Google …”). Tras la activación, reconoce un **verbo** (`reproduce`, `busca`, `abre`, etc.) y el **resto de la frase** se usa como argumento (búsqueda en YouTube/Google o nombre de aplicación).

Sirve para:

- Automatizar tareas habituales con la voz (o con texto en modo depuración).
- Experimentar con **reconocimiento de voz**, **síntesis de voz** y **procesamiento del lenguaje natural ligero** (gramática) en un solo proyecto pequeño.
- Partir de un código ordenado si quieres integrar más servicios o reglas propias.

---

## Cómo funciona (visión general)

El flujo sigue el esquema de un **asistente clásico / sistema experto** (sin LLM):

1. **Percibir**: audio del micrófono (o texto en consola) → reconocimiento del habla → texto.
2. **Analizar (CFG)**: se normaliza, se tokeniza y un **analizador sintáctico** (gramática libre de contexto con NLTK `ChartParser`) acepta o rechaza la frase. Si es válida, se imprime el **árbol sintáctico** para ver cómo el parser estructura la orden.
3. **Inferir (experto)**: el resultado del parseo se convierte en **hechos** (`asistente_voz/experto/hechos.py`). Un **motor de inferencia** evalúa **reglas de producción** del tipo *SI parse válido Y verbo = X Y objeto cumple Y ENTONCES acción Z* (`asistente_voz/experto/reglas.py` + `asistente_voz/experto/motor.py`).
4. **Actuar**: solo entonces se ejecutan efectos (YouTube, Google, abrir apps) y se responde por **voz sintética**.

Si el parse falla, **no** se inventa una respuesta: se explica el error (falta wake word, verbo desconocido, fuera de gramática, etc.). Eso es deliberado: modela un sistema con reglas rígidas, frente a un asistente basado en LLM.

---

## Tecnologías y piezas del proyecto

### Reconocimiento de voz (entrada de audio)

- **Librerías**: [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) captura audio con **PyAudio** y, en esta configuración, envía el audio al **reconocimiento en la nube de Google** (`recognize_google`), que devuelve texto. Requiere **conexión a Internet**.
- **Idioma**: por defecto `es-MX`; se puede cambiar con variable de entorno o en `asistente_voz/config.py` (`LANGUAGE_STT`). Códigos típicos: `es-ES`, `es-MX`, `en-US`, etc. (los que soporte el proveedor).
- **Micrófono**: el índice del dispositivo se configura en `asistente_voz/config.py` (comentarios en ese archivo explican cómo listar micrófonos con un comando de Python). También puedes fijar `ASISTENTE_MIC_INDEX` sin tocar el código.

### Gramática (análisis sintáctico)

- **Librería**: [NLTK](https://www.nltk.org/) con una **CFG** armada desde `asistente_voz/config.py` (wake words, verbos, apps, determinantes) en `asistente_voz/gramatica.py`.
- **Idea**: *palabra de activación* + *verbo* + *complemento*. Tras un parse correcto verás en consola el **árbol sintáctico**.
- **Consultas abiertas** (`reproduce` / `busca`): la cola se resume en el comodín `__objeto__` (no se enumera cada canción en la CFG).
- **Léxico cerrado** (`abre`): apps en `APPS_LEXICO` (`notepad`, `word`, `edge`, `documento`).
- En clase: ampliar terminales en `config.py` o producciones en `_producciones_extra()` dentro de `gramatica.py`.

### Sistema experto (hechos + reglas + motor)

- `asistente_voz/experto/hechos.py` — hechos de la petición actual (wake, verbo, objeto, alias de app, …).
- `asistente_voz/experto/reglas.py` — reglas SI … ENTONCES … (aquí añaden más los estudiantes).
- `asistente_voz/experto/motor.py` — elige la regla de mayor prioridad y ejecuta la acción registrada.

### Síntesis de voz (respuesta hablada)

- **En Windows**: por defecto se intenta usar **SAPI** a través de `win32com` (habitualmente instalado con el paquete **pywin32**). Si no está disponible, se usa **pyttsx3** con el motor `sapi5`.
- **En otros sistemas**: pyttsx3 con el motor que tenga disponible el SO.
- **Parámetros**: velocidad y volumen se ajustan en `asistente_voz/config.py` o con variables de entorno (`ASISTENTE_TTS_RATE`, `ASISTENTE_TTS_VOLUME`). Ver comentarios en `asistente_voz/voz_tts.py` para forzar solo pyttsx3 o preferir voz en español.

### Acciones (efectos en el equipo y la web)

- **Librerías**: [pywhatkit](https://pypi.org/project/pywhatkit/) para abrir búsquedas o reproducción en el navegador; **webbrowser** y **subprocess** como respaldo o para lanzar ejecutables (Bloc de notas, Word, Edge, etc.).
- Las rutas de aplicaciones en Windows están centralizadas en `config.py` para que puedas adaptarlas a tu instalación.

### Normalización de texto

- En `asistente_voz/texto.py` se unifica el formato del texto reconocido para que coincida con las palabras de la gramática y se corrige el orden si el motor de reconocimiento devuelve primero el verbo y después la palabra de activación.

---

## Requisitos

- **Sistema operativo**: probado y orientado a **Windows** (rutas de Edge/Office y TTS por SAPI). Con cambios menores en rutas y dependencias puede adaptarse a Linux o macOS.
- **Python**: 3.10 o superior recomendado.
- **Hardware**: micrófono si usas modo voz.
- **Red**: obligatoria para el reconocimiento con Google en la configuración actual.

---

## Entorno virtual (recomendado)

Aislar las dependencias en un entorno virtual (`.venv`) evita conflictos con otros proyectos y deja claro qué paquetes usa este código.

### Crear el entorno (Windows, PowerShell)

Desde la carpeta raíz del repositorio (donde está `requirements.txt`):

```powershell
python -m venv .venv
```

### Activar el entorno

**PowerShell** (si aparece error de política de ejecución, puede hacer falta `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` una vez):

```powershell
.\.venv\Scripts\Activate.ps1
```

**Símbolo del sistema (cmd)**:

```bat
.\.venv\Scripts\activate.bat
```

Tras activar, el prompt suele mostrar `(.venv)` al inicio.

### Instalar dependencias dentro del entorno

Con el entorno **activado**:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Eso instala lo declarado en `requirements.txt` (entre otros: `nltk`, `SpeechRecognition`, `pyaudio`, `pyttsx3`, `pywhatkit`).

**Si falla la instalación de PyAudio en Windows**, es un caso frecuente; suele resolverse con ruedas precompiladas o herramientas como `pipwin` (indicaciones en comentarios al inicio de `requirements.txt`).

### Opcional: voz SAPI con `win32com` en Windows

Para que el programa use primero **SAPI por COM** (comportamiento por defecto en Windows en `voz_tts.py`), instala también:

```powershell
pip install pywin32
```

Si no está instalado, el código sigue funcionando usando **pyttsx3**.

---

## Cómo ejecutar el proyecto

La carpeta raíz debe ser la del repositorio (donde está `Asistente_Voz_IA.py`), con el entorno virtual activado y dependencias instaladas.

### Arranque principal

```powershell
python Asistente_Voz_IA.py
```

### Probar gramática y reglas (sin micrófono ni TTS)

```powershell
python scripts/probar_experto.py
```

### Modo solo texto (sin micrófono)

Útil en entornos ruidosos, sin permisos de micrófono o para depurar la gramática y las acciones:

**PowerShell**

```powershell
$env:ASISTENTE_TEXTO = "1"
python Asistente_Voz_IA.py
```

**cmd**

```bat
set ASISTENTE_TEXTO=1
python Asistente_Voz_IA.py
```

En modo texto escribes el comando cuando aparezca `Comando >`. La misma gramática y las mismas acciones se aplican que en modo voz.

---

## Ejemplos de comandos

La frase debe incluir una **palabra de activación** al inicio (tras la normalización): `alexa`, `siri`, `google` o `cortana`. Luego un **verbo** reconocido y el resto según la acción.

- `alexa reproduce luis miguel`
- `siri busca tutorial python`
- `google abre el notepad`
- `cortana abre edge`

Los verbos y las palabras de activación deben estar alineados entre `asistente_voz/gramatica.py` y `asistente_voz/config.py`.

---

## Configuración

### Archivo `asistente_voz/config.py`

Ahí se concentran:

- **Lista de palabras de activación y verbos** (`WAKE_WORDS`, `VERBOS`): deben coincidir con la CFG en `gramatica.py`.
- **Idioma del reconocimiento**, tiempos de escucha, calibración de ruido, límites de duración de frase.
- **Volumen y velocidad del TTS**.
- **Índice del micrófono** y comentarios con el comando para listar dispositivos.
- **Rutas** a ejecutables (Edge, Word, Bloc de notas) y etiquetas amigables para la voz.

En el propio archivo hay comentarios en español que explican bloque por bloque qué tocar y para qué sirve cada valor.

### Variables de entorno (opcional)

Muchas claves tienen un valor por defecto en código; las variables permiten probar sin editar archivos. Algunas de las más útiles:

| Variable | Efecto |
|----------|--------|
| `ASISTENTE_TEXTO` | `1` activa modo consola en lugar del micrófono. |
| `ASISTENTE_MIC_INDEX` | Número de dispositivo de entrada; anula el índice por defecto de `config.py`. |
| `ASISTENTE_LISTAR_MICS` | `1` lista todos los micrófonos al iniciar (para elegir índice). |
| `ASISTENTE_LANG_STT` | Idioma del reconocimiento (p. ej. `es-MX`, `es-ES`). |
| `ASISTENTE_ESCUCHA_TIMEOUT` | Segundos de espera a que empieces a hablar. |
| `ASISTENTE_FRASE_MAX_S` | Duración máxima capturada por comando (0 = sin tope). |
| `ASISTENTE_TTS_RATE` / `ASISTENTE_TTS_VOLUME` | Ritmo y volumen del habla. |
| `ASISTENTE_TTS_PYTTSX3` | `1` fuerza motor pyttsx3 en Windows en lugar de SAPI/COM. |
| `ASISTENTE_TTS_VOZ_ES` | `1` intenta seleccionar una voz en español si existe. |
| `ASISTENTE_DEBUG_STT` | `1` imprime información extra del reconocimiento. |
| `ASISTENTE_REPETIR_STT_VOZ` | `1` hace que el asistente repita por voz lo que entendió (útil para depurar). |
| `ASISTENTE_MOSTRAR_ARBOL` | `0` oculta el árbol sintáctico en consola (por defecto se muestra). |
| `ASISTENTE_MOSTRAR_HECHOS` | `0` oculta hechos + regla disparada (por defecto se muestran). |
| `ASISTENTE_LISTAR_REGLAS` | `0` no lista las reglas al arrancar (por defecto sí). |

La lista completa de ajustes finos está documentada con comentarios en `asistente_voz/config.py`, `voz_stt.py` y `voz_tts.py`.

---

## Estructura del repositorio

```
Asistente_Voz/
├── asistente_voz/              # Código del asistente
│   ├── agente.py               # Percibir → CFG → experto → actuar
│   ├── config.py               # Léxico CFG, mic, STT, TTS, rutas de apps
│   ├── gramatica.py            # CFG NLTK, árbol sintáctico, errores de parseo
│   ├── texto.py                # Normalización y tokens
│   ├── voz_stt.py / voz_tts.py # Entrada / salida de voz
│   ├── acciones.py             # Efectos: YouTube, Google, programas
│   └── experto/                # Sistema experto de peticiones
│       ├── hechos.py           # Base de hechos (memoria de trabajo)
│       ├── reglas.py           # Reglas de producción (ampliar aquí)
│       └── motor.py            # Motor de inferencia + tabla de acciones
├── scripts/
│   └── probar_experto.py       # Casos de prueba CFG → inferencia
├── Asistente_Voz_IA.py         # Punto de entrada
├── requirements.txt
└── README.md
```

Para **ampliar** el asistente en clase:

1. **Léxico / CFG**: `WAKE_WORDS`, `VERBOS`, `APPS_LEXICO` en `asistente_voz/config.py` (la gramática se regenera sola).
2. **Regla nueva**: añade un `Regla(...)` en `asistente_voz/experto/reglas.py`.
3. **Acción nueva**: impleméntala en `asistente_voz/acciones.py` (si aplica) y regístrala en `asistente_voz/experto/motor.py` → `ACCIONES`.
4. No hace falta tocar `if/elif` en `agente.py`: el motor elige la regla.

---

## Privacidad y uso del micrófono

El audio del micrófono se envía al proveedor de reconocimiento configurado (Google en el código actual) para obtener texto. No sustituye leer la documentación oficial de ese servicio sobre retención y términos de uso. En modo `ASISTENTE_TEXTO=1` no se usa el micrófono para los comandos.

---

## Resolución rápida de problemas

| Síntoma | Qué revisar |
|---------|-------------|
| No instala PyAudio | Ruedas para tu versión de Python/Windows o `pipwin` (ver `requirements.txt`). |
| No escucha o escucha el mic equivocado | `ASISTENTE_LISTAR_MICS=1` y ajusta índice en `config.py` o `ASISTENTE_MIC_INDEX`. |
| Sin respuesta de voz en Windows | Instala `pywin32` o fuerza `ASISTENTE_TTS_PYTTSX3=1`. |
| “No entendió” o timeout | Ruido de fondo, `ASISTENTE_ESCUCHA_TIMEOUT`, `ASISTENTE_FRASE_MAX_S` o umbral de energía en `config.py`. |
| Gramática rechaza la frase | Lee el mensaje de error en consola/voz (`FALTA_WAKE`, `SIN_VERBO`, `OBJETO_VACIO`, `FUERA_DE_GRAMATICA`). Revisa `VERBOS` / `APPS_LEXICO` en `config.py`. |
| Parse OK pero “no hay regla” | Añade o ajusta una `Regla` en `experto/reglas.py` y registra la acción en `experto/motor.py`. |
