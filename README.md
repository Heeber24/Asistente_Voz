# Asistente de voz por comandos

Asistente sencillo en Python: escucha (o lees el comando), valida la frase con una **gramática libre de contexto**, aplica **reglas de un sistema experto** y responde con voz.

No usa LLM. Si la frase no parsea, no inventa respuesta.

## Flujo

1. Escuchar / leer texto  
2. Normalizar y tokenizar  
3. Analizar con la CFG (NLTK) → árbol sintáctico  
4. Armar hechos y disparar una regla SI … ENTONCES …  
5. Ejecutar acción (YouTube, Google, abrir app) y hablar  

## Requisitos

- Windows (recomendado para la demo: rutas de apps y TTS).  
- **Python 3.12** de preferencia.  
  En 3.13/3.14 `PyAudio` suele fallar al instalarse. Con 3.12 casi siempre entra bien.  
- Internet (el reconocimiento de voz usa Google).  
- Opcional: [uv](https://github.com/astral-sh/uv) para crear el entorno fácil.

## Cómo armar el entorno (VS Code / PowerShell)

Abre la carpeta del repo en Visual Studio Code y usa la terminal integrada.

### 1) Crear el entorno con Python 3.12

Con `uv` (recomendado; no te cambia el Python global, solo el `.venv` del proyecto):

```powershell
uv venv --python 3.12 .venv
.\.venv\Scripts\activate
python --version
```

Debe salir algo como `Python 3.12.x`.

Si `uv` no está, puedes usar el launcher de Windows (con 3.12 ya instalado en la PC):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

### 2) Asegurar pip e instalar dependencias

En algunos venvs creados con `uv`, pip no viene activo. Si hace falta:

```powershell
python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si `PyAudio` falla, revisa que el `python --version` del venv sea 3.12 (no 3.14).

### 3) Correr el asistente

**Modo texto** (sin micrófono; útil para probar gramática y reglas):

```powershell
$env:ASISTENTE_TEXTO = "1"
python Asistente_Voz_IA.py
```

Cuando aparezca `Comando >`, escribe por ejemplo:

```text
alexa reproduce luis miguel
```

**Modo voz** (necesita micrófono + PyAudio + internet):

```powershell
python Asistente_Voz_IA.py
```

Para salir: `Ctrl+C`.

### Si el micrófono no es el correcto

```powershell
python -c "import speech_recognition as sr; [print(i, n) for i, n in enumerate(sr.Microphone.list_microphone_names())]"
$env:ASISTENTE_MIC_INDEX = "3"
python Asistente_Voz_IA.py
```

(cambia `3` por el índice de tu mic)

## Ejemplos

- `alexa reproduce luis miguel`
- `siri busca tutorial python`
- `google abre el notepad`
- `cortana abre edge`

## Estructura

```
Asistente_Voz_IA.py      # entrada
asistente_voz/
  agente.py              # bucle principal
  config.py              # wake words, verbos, apps, mic, etc.
  gramatica.py           # CFG + árbol
  texto.py               # normalizar / tokenizar
  voz_stt.py             # microfono -> texto
  voz_tts.py             # texto -> voz
  acciones.py            # YouTube / Google / apps
  experto/
    hechos.py            # base de hechos
    reglas.py            # reglas SI...ENTONCES (ampliar aqui)
    motor.py             # elige y ejecuta la regla
requirements.txt
README.md
```

## Ampliar en clase

1. Léxico: `asistente_voz/config.py` (`WAKE_WORDS`, `VERBOS`, `APPS_LEXICO`)  
2. Regla nueva: `asistente_voz/experto/reglas.py`  
3. Acción nueva: `acciones.py` + registrarla en `experto/motor.py`  

## Notas rápidas

- El reconocimiento usa Google (`recognize_google`), necesita internet.  
- En Windows el TTS intenta SAPI; si falla, usa pyttsx3.  
- `reproduce` / `busca` aceptan cualquier texto después del verbo (objeto abierto).  
- `abre` solo acepta apps del léxico cerrado.  
- Tu Python global (por ejemplo 3.14) no se toca: el proyecto vive en `.venv` con 3.12.  
