import speech_recognition as sr
import webbrowser
from gtts import gTTS
import pygame
import os
import requests
from openai import OpenAI
import musiclibrary

# Initialize OpenAI client
client = OpenAI(api_key="<Your Key Here>")

# News API key
newsapi = "<Your Key Here>"

# This function converts text to speech and plays it
def speak(text):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save('temp.mp3')
    
    # Adjust pitch and speed using pydub
    from pydub import AudioSegment
    sound = AudioSegment.from_mp3("temp.mp3")
    # Lower pitch by 2 semitones and increase speed by 10%
    adjusted_sound = sound.speedup(playback_speed=1.1)
    # Remove or comment out the following line:
    # adjusted_sound = adjusted_sound.pitch_shift(-2)
    adjusted_sound.export("temp.mp3", format="mp3")

    # Initialize Pygame mixer
    pygame.mixer.init()

    # Load and play the MP3 file
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()

    # Wait for the audio to finish
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    os.remove("temp.mp3")

def aiProcess(command):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a virtual assistant named Jarvis skilled in general tasks like Alexa and Google Cloud. Give short responses please"},
            {"role": "user", "content": command}
        ]
    )
    return completion.choices[0].message.content

def processCommand(command):
    command = command.lower()
    if "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://google.com")
    elif "open facebook" in command:
        speak("Opening Facebook")
        webbrowser.open("https://facebook.com")
    elif "open youtube" in command:
        speak("Opening Youtube")
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in command:
        speak("Opening Linkedin")
        webbrowser.open("https://linkedin.com")
    elif command.startswith("play"):
        speak(f"Playing the song {command.lower().split(" ")[1]}")
        song = command.lower().split(" ")[1]
        link = musiclibrary.music.get(song)
        if link:
            webbrowser.open(link)
        else:
            speak("Sorry, I couldn't find that song in the music library.")
    elif "news" in command:
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}")
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            for article in articles[:3]:  # Limit to first 3 articles
                speak(article['title'])
        else:
            speak("Sorry, I couldn't fetch the news at the moment.")
    else:
        # Let OpenAI handle the request
        output = aiProcess(command)
        speak(output)

if __name__ == "__main__":
    speak("Initializing Jarvis...")

while True:
    # Listen for the wake word "Jarvis"
    r = sr.Recognizer()
    
    print("Listening for wake word...")
    try:
        with sr.Microphone() as source:
            audio = r.listen(source, timeout=2, phrase_time_limit=1)
        
        word = r.recognize_google(audio).lower()
        if "jarvis" in word:
            speak("Hello Boss welcome back. How can I help you?")
            
            # Listen for command
            print("Jarvis is active. Listening for command...")
            with sr.Microphone() as source:
                command_audio = r.listen(source)
            command = r.recognize_google(command_audio)
            
            # Process the command
            processCommand(command)
    
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        print(f"Error: {e}")

