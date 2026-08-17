# Modules :- 

import pyttsx3
import speech_recognition as sr 
import webbrowser
import datetime
import pyjokes

import time
import os 

def sptext():
    recognizer=sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening..")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)  
        try:
            print("recoginzing..")
            data = recognizer.recognize_google(audio)
            
            print(data)
            return data
        except sr.UnknownValueError:
            print("Not understanfing....")
def textsp(x):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice',voices[1].id)
    speed = engine.getProperty('rate')
    engine.setProperty('rate',150)
    engine.say(x)
    engine.runAndWait()
print("Hello")


if __name__ == "__main__":
    # if sptext().lower() == "hello dora":    
        # print("test")
 while(1):    
    data1 = sptext().lower()
    if "your name" in data1:
        name = "my name is dora"
        textsp(name)
        
    elif "how old are you" in data1:
        age = "i'm 2 years old"   
        textsp(age)
    elif 'time' in data1:
        time = datetime.datetime.now().strftime("%I%M%p")  
        textsp(time)
    elif 'youtube' in data1:
        textsp("Wait few seconds i will open youtube")
        webbrowser.open("https://www.youtube.com/")
    elif 'vgi' in data1:
        textsp("Wait")
        webbrowser.open("https://vgiagencies.vercel.app/")
    elif 'joke' in data1:
        joke_1=pyjokes.get_joke(language='en',category="politics")
        textsp(joke_1) 
        print(joke_1)  
    elif 'exit' in data1:
        textsp("Bye Bye")
        exit()
            
    time.sleep(5)
        # print("Thanks..")
        




