# Asistente de voz por comandos

Asistente sencillo en Python: escucha (o lees el comando), valida la frase con una **gramática libre de contexto**, aplica **reglas de un sistema experto** y responde con voz.

No usa LLM. Si la frase no parsea, no inventa respuesta.

## Flujo

1. Escuchar / leer texto  
2. Normalizar y tokenizar  
3. Analizar con la CFG (NLTK) → árbol sintáctico  
4. Armar hechos y disparar una regla SI … ENTONCES …  
5. Ejecutar acción (YouTube, Google, abrir app) y hablar  

## Cómo correrlo

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python Asistente_Voz_IA.py
```

Sin micrófono (solo teclado):

```powershell
$env:ASISTENTE_TEXTO = "1"
python Asistente_Voz_IA.py
```

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
