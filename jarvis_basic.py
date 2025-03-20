import speech_recognition as sr
import pyttsx3
from pydub import AudioSegment
from gtts import gTTS
import playsound
import os
import webbrowser
import datetime
import requests
import json

# Initialize recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()


def ask_gpt_brain(prompt):
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'mistral', 'prompt': prompt},
            stream=True  
        )
        
        reply = ""

        # Stream line by line
        for line in response.iter_lines(decode_unicode=True):
            if line:
                json_data = json.loads(line)
                # Each streamed JSON has a "response" field
                chunk = json_data.get('response', '')
                reply += chunk
                print(chunk, end='', flush=True)  # Show streaming chunks live
        
        print()  # newline after stream ends
        return reply

    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't connect to my brain."

def change_speed(sound):
    # Manually adjust speed (without changing pitch)
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
         "frame_rate": int(sound.frame_rate * 1.2)
      })
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

def speak(text):
    print(f"Jarvis says: {text}")
    
    tts = gTTS(text=text, lang='en', tld='co.in')
    tts.save("voice.mp3")
    
    # Load with pydub
    sound = AudioSegment.from_file("voice.mp3")
    
    modified_sound = change_speed(sound)
    
    # Export modified file
    modified_sound.export("modified_voice.mp3", format="mp3")
    
    # Play the modified voice
    playsound.playsound("modified_voice.mp3")
    
    # Clean up
    os.remove("voice.mp3")
    os.remove("modified_voice.mp3")

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio)
        print(f"You said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return ""

def main():
    speak("Hello, I am your assistant. How can I help you?")
    while True:
        command = listen()
        
        if "hello" in command:
            speak("Hello Abhishek! How are you?")
        
        elif 'open youtube' in command:
            webbrowser.open("https://www.youtube.com")
            continue
        
        elif 'open google' in command:
            webbrowser.open("https://www.google.com")
            continue
        
        elif 'time' in command:
            time = datetime.datetime.now().strftime("%H:%M:%S")
            speak(time)
            continue

        elif "exit" in command or "stop" in command or "bye" in command:
            speak("Goodbye!")
            break
        
        else:
            reply = ask_gpt_brain(command)
            speak(reply)

if __name__ == "__main__":
    main()
