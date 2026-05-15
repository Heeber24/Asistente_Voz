import subprocess # Módulo para ejecutar comandos del sistema
import nltk  # bibliotecas para el Procesamiento del Lenguaje Natural (PLN) (gramática y parser)
import pywhatkit  # Permite interactuar con YouTube y Google
import speech_recognition as sr  # Reconocimiento de voz
import pyttsx3  # Síntesis de voz para generar respuestas de audio

# pip install nltk pyttsx3 pywhatkit SpeechRecognition pyaudio
# pip pywhatkit 
# pip SpeechRecognition 
# pip pyttsx3 pyaudio   
# pip pyaudio 
# es necesario para el micrófono

# Clase para la síntesis de voz
class GeneradorVoz:
    def __init__(self):
        """Inicializa el motor de voz."""
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 120)  # Configura la velocidad de la voz

    def generar_voz(self, textoAudio):
        """Genera audio a partir de texto."""
        self.engine.say(textoAudio)
        self.engine.runAndWait()

# Definición de la gramática que vamos a usar para reconocer comandos
gramatica = nltk.grammar.FeatureGrammar.fromstring("""
        S -> AV NP VP 
        AV -> 'alexa' | 'siri' | 'google' | 'cortana'
        NP -> DET N | IND N | CONJ N | N
        VP -> V NP | V
        DET -> 'el' | 'la' | 'los' | 'las' | 'al'
        IND -> 'un' | 'una' | 'uno' | 'unos' | 'unas'
        CONJ -> 'y' | 'o' | 'u' | 'a' | 'e' | 'que' | 'como' | 'cuando' | 'donde'
        N -> 'perro' | 'gato' | 'luis' | 'miguel' | 'mana' | 'moderato' | 'jose' | 'notepad' | 'word' | 'edge' | 'documento'
        V -> 'canta' | 'escribe' | 'reproduce' | 'reproducir' | 'busca' | 'buscar' | 'abre' | 'abrir' | 'inicia'
    """)

# alexa repruduce a luis miguel

parser = nltk.FeatureEarleyChartParser(gramatica)  # Parser que usaremos para la gramática

# Instancia para la síntesis de voz
generador_voz = GeneradorVoz()

# Clase para el reconocimiento de voz
class ReconocimientoVoz:
    def __init__(self):
        """Inicializa el reconocimiento de voz."""
        self.recognizer = sr.Recognizer()

    def escuchar_audio(self):
        """Captura y procesa el audio del micrófono."""
        with sr.Microphone() as source:
            print("Ajustando el ruido ambiente...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.10)
            print("Escuchando...")
            try:
                # Captura el audio
                audio = self.recognizer.listen(source, timeout=6)
                # Usa Google para reconocer el audio
                text = self.recognizer.recognize_google(audio, language="es-MX")
                print("Texto reconocido: {}".format(text))
                return text.lower()  # Convierte el texto a minúsculas
            except sr.WaitTimeoutError:
                print("No se detectó ningún audio.")
                return ""
            except sr.UnknownValueError:
                print("No se pudo reconocer el audio.")
                return ""

# Función para normalizar texto (quita acentos)
def normalize(s):
    """Normaliza caracteres acentuados en el texto."""
    replacements = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"))
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s

# Función para procesar el comando de voz reconocido
def procesar_comando(comando):
    """Procesa el comando de voz y ejecuta la acción adecuada."""
    text2 = comando.split()  # Divide el texto en palabras
    try:
        parser.parse(text2)  # Verifica si el comando cumple la gramática
        if len(text2) < 2:
            return  # Si no hay suficientes palabras, no se procesa

        # Extrae la acción principal (verbo) del comando
        accion = text2[1]

        # Si la acción es reproducir, busca en YouTube
        if accion in ['reproduce', 'reproducir']:
            busqueda = ' '.join(text2[2:])  # Extrae lo que se quiere reproducir
            textoAudio = f"Reproduciendo {busqueda} en YouTube"
            generador_voz.generar_voz(textoAudio)
            pywhatkit.playonyt(busqueda)

        # Si la acción es buscar, hace una búsqueda en Google
        elif accion in ['buscar', 'busca']:
            busqueda = ' '.join(text2[2:])  # Extrae lo que se quiere buscar
            textoAudio = f"Buscando {busqueda} en Google"
            generador_voz.generar_voz(textoAudio)
            pywhatkit.search(busqueda)

        # Si la acción es abrir una aplicación, lanza el programa especificado
        elif accion in ['abre', 'abrir', 'inicia']:
            if len(text2) < 3:
                print("Especifica qué aplicación abrir.")
                return

            app = text2[2]  # Extrae la aplicación a abrir
            apps = {
                'notepad': 'C:/Windows/System32/notepad.exe',
                'word': 'C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE',
                'edge': 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
            }

            if app in apps:
                textoAudio = f"Abriendo {app}"
                generador_voz.generar_voz(textoAudio)
                subprocess.run(apps[app])
            else:
                textoAudio = "No reconozco la aplicación que quieres abrir"
                generador_voz.generar_voz(textoAudio)
        else:
            generador_voz.generar_voz("No entendí el comando que quieres ejecutar.")

    except ValueError:
        print("El comando no está en la gramática. Inténtalo de nuevo.")

# Función principal del programa
def main():
    reconocimiento = ReconocimientoVoz()
    while True:
        comando = reconocimiento.escuchar_audio()  # Escucha el audio
        comando = normalize(comando)  # Normaliza el texto
        procesar_comando(comando)  # Procesa el comando

if __name__ == "__main__":
    main()  # Ejecuta el programa
