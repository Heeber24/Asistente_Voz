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

El flujo sigue el esquema clásico **percibir → interpretar → actuar**:

1. **Percibir**: se captura audio del micrófono (o se escribe un comando en consola) y se obtiene texto mediante reconocimiento automático del habla.
2. **Interpretar**: el texto se normaliza (minúsculas, sin acentos), se divide en palabras (*tokens*) y se comprueba si la secuencia encaja en una **gramática** definida en el código. Así se evita ejecutar frases mal formadas.
3. **Actuar**: si la frase es válida, según el verbo se llama a funciones que abren el navegador, lanzan un `.exe` o generan mensajes de voz.

La voz de respuesta confirma lo que va a hacer el sistema y guía al usuario si falta información (por ejemplo, no se dijo qué buscar).

---

## Tecnologías y piezas del proyecto

### Reconocimiento de voz (entrada de audio)

- **Librerías**: [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) captura audio con **PyAudio** y, en esta configuración, envía el audio al **reconocimiento en la nube de Google** (`recognize_google`), que devuelve texto. Requiere **conexión a Internet**.
- **Idioma**: por defecto `es-MX`; se puede cambiar con variable de entorno o en `asistente_voz/config.py` (`LANGUAGE_STT`). Códigos típicos: `es-ES`, `es-MX`, `en-US`, etc. (los que soporte el proveedor).
- **Micrófono**: el índice del dispositivo se configura en `config.py` (comentarios en ese archivo explican cómo listar micrófonos con un comando de Python). También puedes fijar `ASISTENTE_MIC_INDEX` sin tocar el código.

### Gramática (validación de la frase)

- **Librería**: [NLTK](https://www.nltk.org/) con una **gramática libre de contexto (CFG)** escrita como texto en `asistente_voz/gramatica.py`.
- **Idea**: las órdenes válidas tienen una estructura fija, por ejemplo *palabra de activación* + *verbo* + *complemento*. La CFG describe patrones como “Alexa reproduce …” o “Google abre el notepad”.
- **Consultas abiertas** (canción, término de búsqueda): no se listan todas las frases posibles en la gramática; para verbos como `reproduce` o `busca`, la cola de palabras se sustituye internamente por un comodín (`__objeto__`) y el analizador solo comprueba que haya “algo” después del verbo. Para `abre`, los nombres de aplicación sí van como reglas concretas en la gramática (alineadas con `acciones.py` y `config.py`).

### Síntesis de voz (respuesta hablada)

- **En Windows**: por defecto se intenta usar **SAPI** a través de `win32com` (habitualmente instalado con el paquete **pywin32**). Si no está disponible, se usa **pyttsx3** con el motor `sapi5`.
- **En otros sistemas**: pyttsx3 con el motor que tenga disponible el SO.
- **Parámetros**: velocidad y volumen se ajustan en `config.py` o con variables de entorno (`ASISTENTE_TTS_RATE`, `ASISTENTE_TTS_VOLUME`). Ver comentarios en `asistente_voz/voz_tts.py` para forzar solo pyttsx3 o preferir voz en español.

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

### Arranque alternativo (desde la misma raíz)

```powershell
python scripts/ejecutar_asistente.py
```

Ese script añade la raíz al `PYTHONPATH` y llama al mismo punto de entrada; es útil si prefieres tener el comando bajo `scripts/`.

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

La lista completa de ajustes finos está documentada con comentarios en `config.py`, `voz_stt.py` y `voz_tts.py`.

---

## Estructura del repositorio

```
Asistente_Voz/
├── asistente_voz/           # Código del asistente (paquete Python)
│   ├── agente.py            # Bucle principal: escucha/lee, valida, despacha acciones
│   ├── config.py            # Parámetros y rutas (mic, STT, TTS, verbos, aplicaciones)
│   ├── gramatica.py         # CFG NLTK y comprobación de validez de la frase
│   ├── texto.py             # Normalización de texto y orden de tokens
│   ├── voz_stt.py           # Micrófono + reconocimiento (SpeechRecognition / Google)
│   ├── voz_tts.py           # Síntesis de voz (SAPI / pyttsx3)
│   └── acciones.py          # YouTube, Google, apertura de programas
├── requirements.txt
├── README.md
├── Asistente_Voz_IA.py      # Punto de entrada recomendado
└── Base de hechos (animales).py   # Otro script del repositorio (independiente del asistente)
```

Para **ampliar** el asistente suele bastar con:

1. Añadir reglas y vocabulario en `gramatica.py` y los mismos tokens en `VERBOS` / `WAKE_WORDS` en `config.py`.
2. Implementar la lógica nueva en `acciones.py` (o en otro módulo tuyo) y enlazar el verbo en `agente.py` dentro de `procesar_comando`.

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
| Gramática rechaza la frase | Orden de palabras, palabra de activación al inicio (tras normalización), verbo en `VERBOS` y reglas en `gramatica.py`. |
