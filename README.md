# Asistente de voz por comandos

Aplicación en Python que funciona como un **asistente virtual sencillo**: escucha instrucciones (o las lees por teclado), valida que la frase tenga una estructura correcta con una **gramática libre de contexto (CFG)**, aplica **reglas de un sistema experto** y ejecuta acciones concretas (YouTube, Google, abrir programas), respondiendo con **voz sintética**.

La idea didáctica es mostrar cómo se arma un asistente “de la vieja escuela”:

- **No usa un LLM** para inventar respuestas.
- Solo actúa si el **analizador sintáctico** acepta la frase según nuestras reglas.
- Después del parseo, un **motor de inferencia** decide qué hacer con reglas del tipo  
  *SI el parse es válido Y el verbo es X Y el objeto cumple Y → ENTONCES ejecuta Z*.

Así se entiende la diferencia entre un asistente actual apoyado en modelos grandes y un sistema con reglas rígidas (como un sistema experto clásico).

---

## ¿Para qué sirve?

- Automatizar comandos de voz/texto: reproducir, buscar, abrir apps.
- Practicar en un solo proyecto el reconocimiento de voz, síntesis de voz, CFG y reglas.
- Servir de base para crear más verbos, más apps y más reglas.

---

## Cómo funciona (pipeline)

1. **Percibir** — micrófono → texto (Google STT) **o** texto escrito en consola.  
2. **Normalizar** — minúsculas, sin acentos, tokens.  
3. **Analizar (CFG)** — NLTK `ChartParser`. Si no hay árbol válido → error, no inventa.  
4. **Inferir (experto)** — se arman *hechos* y se evalúan *reglas SI…ENTONCES…*.  
5. **Actuar** — YouTube / Google / abrir app + respuesta por TTS.

```text
voz o teclado
    → STT / texto
    → normalize + tokens
    → gramática CFG (árbol)
    → hechos
    → reglas / motor
    → acción + voz
```

---

## Librerías y para qué se usan

| Librería | Para qué |
|----------|----------|
| **SpeechRecognition** | Captura audio y lo manda a reconocimiento (aquí: Google). |
| **PyAudio** | Permite usar el **micrófono** desde Python. Sin esto no hay modo voz. |
| **NLTK** | Define y parsea la **gramática libre de contexto (CFG)**. |
| **pyttsx3** | **Síntesis de voz** (texto → habla). En Windows puede apoyarse en SAPI. |
| **pywin32** (opcional) | Acceso a **SAPI** por COM en Windows (voz del sistema). |
| **pywhatkit** | Abre reproducción/búsqueda en **YouTube** y **Google**. |
| **webbrowser** / **subprocess** | Respaldo del navegador y para lanzar `.exe` (Notepad, Word, Edge). |

Declaradas en `requirements.txt`.

---

## Estructura del repositorio

Todo el código del asistente vive en la **raíz** (sin carpeta intermedia duplicada):

```text
Asistente_Voz/
├── Asistente_Voz_IA.py   # Arranque: python Asistente_Voz_IA.py
├── agente.py             # Bucle principal (orquesta todo el pipeline)
├── config.py             # Ajustes: idioma, mic, wake words, verbos, apps, rutas
├── texto.py              # Normalizar, tokenizar, acomodar wake word
├── gramatica.py          # CFG NLTK, árbol sintáctico, errores de parseo
├── voz_stt.py            # Micrófono → texto (Speech-To-Text)
├── voz_tts.py            # Texto → voz (Text-To-Speech)
├── acciones.py           # Efectos: YouTube, Google, abrir programas
├── experto/              # Sistema experto de la petición
│   ├── hechos.py         # Base de hechos (qué sabemos de la frase)
│   ├── reglas.py         # Reglas SI…ENTONCES… (aquí amplían los alumnos)
│   └── motor.py          # Elige la regla y ejecuta la acción
├── requirements.txt      # Dependencias
├── README.md             # Este documento
└── .gitignore
```

### Para qué sirve cada archivo

| Archivo | Rol |
|---------|-----|
| `Asistente_Voz_IA.py` | Punto de entrada. Prepara el path y llama a `agente.main()`. |
| `agente.py` | Une STT/texto → gramática → hechos → reglas → acción → TTS. |
| `config.py` | Configuración central: `WAKE_WORDS`, `VERBOS`, apps, mic, TTS, rutas de Windows. |
| `texto.py` | Limpia el texto del reconocedor o del teclado. |
| `gramatica.py` | Arma la CFG, parsea, muestra el árbol o un mensaje de error claro. |
| `voz_stt.py` | Escucha el micrófono y obtiene texto con Google. |
| `voz_tts.py` | Habla la respuesta (SAPI en Windows o pyttsx3). |
| `acciones.py` | Lo que “hace” el asistente en el sistema/navegador. |
| `experto/hechos.py` | Traduce el parseo a hechos (`verbo`, `objeto`, `alias_app`, …). |
| `experto/reglas.py` | Lista de reglas de producción. |
| `experto/motor.py` | Evalúa reglas por prioridad y dispara la acción. |

---

## Por qué crear un entorno virtual (`.venv`)

Un **entorno virtual** aísla las librerías de **este** proyecto para no mezclarlas con el Python global de tu PC ni con otros trabajos.

| Si creas el `.venv` | Si no lo creas |
|---------------------|----------------|
| Las dependencias quedan solo en la carpeta del proyecto | `pip install` puede romper o mezclar versiones de otros proyectos |
| Todos usan las mismas libs del `requirements.txt` | En otra máquina “a mí me jala” y a ti no |
| Puedes usar **Python 3.12 solo para este asistente** | Chocas con tu Python global (por ejemplo 3.14) |

**Importante:** el `.venv` **no reemplaza** tu Python global. Tu 3.14 (u otra versión) sigue igual; este proyecto trabaja dentro de su propio entorno.

### Preferir Python 3.12

Para que **PyAudio** (micrófono) se instale bien en Windows, usa **Python 3.12** en el venv. En 3.13/3.14 suele fallar al compilar.

---

## Cómo armar el entorno (VS Code / PowerShell)

Abre la carpeta del repo en Visual Studio Code → terminal integrada.

### 1) Crear el entorno con Python 3.12

Con [uv](https://github.com/astral-sh/uv) (recomendado):

```powershell
uv venv --python 3.12 .venv
.\.venv\Scripts\activate
python --version
```

Debe decir `Python 3.12.x`.

Sin `uv` (si ya tienes 3.12 instalado en la PC):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

### 2) Pip e instalación de librerías

A veces el venv de `uv` no trae pip listo. Si hace falta:

```powershell
python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si `PyAudio` falla, confirma que `python --version` dentro del venv sea **3.12**, no 3.14.

Opcional en Windows (voz SAPI):

```powershell
python -m pip install pywin32
```

---

## Cómo correr el asistente

Con el `(.venv)` activado:

### Modo solo texto (sin micrófono)

Ideal para clase, depurar la gramática o si PyAudio no instaló:

```powershell
$env:ASISTENTE_TEXTO = "1"
python Asistente_Voz_IA.py
```

Cuando aparezca `Comando >`, escribes la frase y Enter.

### Modo voz (micrófono)

Necesitas PyAudio, micrófono e internet:

```powershell
python Asistente_Voz_IA.py
```

Para salir: `Ctrl+C`.

### Elegir micrófono

```powershell
python -c "import speech_recognition as sr; [print(i, n) for i, n in enumerate(sr.Microphone.list_microphone_names())]"
$env:ASISTENTE_MIC_INDEX = "3"
python Asistente_Voz_IA.py
```

(cambia `3` por el índice de tu mic)

---

## Palabras y ejemplos que entiende

La frase, después de normalizar, debe ir así:

**palabra de activación + verbo + complemento**

| Pieza | Valores |
|-------|---------|
| Activación | `alexa`, `siri`, `google`, `cortana` |
| Verbos abiertos | `reproduce` / `reproducir`, `busca` / `buscar` (después puede ir cualquier texto) |
| Verbos de app | `abre` / `abrir` / `inicia` |
| Apps | `notepad`, `word`, `edge`, `documento` (opcional: `el`, `la`, …) |

Ejemplos válidos:

- `alexa reproduce luis miguel`
- `siri busca tutorial python`
- `google abre el notepad`
- `cortana abre edge`

Si no cuadra con la gramática, el asistente **no inventa**: avisa y pide intentar otra petición.

---

## Ampliar en clase

1. **Léxico / CFG:** `WAKE_WORDS`, `VERBOS`, `APPS_LEXICO` en `config.py` (la gramática se regenera sola).  
2. **Regla nueva:** agrega un `Regla(...)` en `experto/reglas.py`.  
3. **Acción nueva:** impleméntala en `acciones.py` y regístrala en `experto/motor.py` → `ACCIONES`.  

---

## Privacidad

En modo voz, el audio se envía a Google para obtener el texto. En modo `ASISTENTE_TEXTO=1` no se usa el micrófono.

---

## Problemas frecuentes

| Síntoma | Qué hacer |
|---------|-----------|
| `python` no se reconoce | Usa `py` o el Python del `.venv` activado. |
| PyAudio no instala | Usa **Python 3.12** en el venv; o trabaja en modo texto. |
| No escucha | Lista micros y fija `ASISTENTE_MIC_INDEX`. |
| Sin voz de salida | Instala `pywin32` o deja que use pyttsx3. |
| “No entendí / gramática” | Revisa wake word al inicio, verbo permitido y, si es `abre`, una app del léxico. |
