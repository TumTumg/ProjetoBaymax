import pyttsx3

def Falar(texto):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.say(texto)
    engine.runAndWait()
