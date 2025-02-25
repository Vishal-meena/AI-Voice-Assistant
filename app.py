import speech_recognition as sr
import pyttsx3
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline
import requests
import re
import os

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")


# Initialize TTS engine once (global to avoid reinitialization errors)
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Speech rate
engine.setProperty("volume", 0.9)  # Volume level



try:
    llm_pipeline = pipeline(
        "text-generation",
        model="distilgpt2",  # Use GPT-2 for better responses
        max_new_tokens=100,  # Limit response length
        temperature=0.7,  # Control randomness
        truncation=True,  # Explicitly enable truncation
        pad_token_id=50256  # Set pad token ID
    )
    llm = HuggingFacePipeline(pipeline=llm_pipeline)
except Exception as e:
    print(f"Error initializing LLM: {e}")
    exit()



# Weather API Configuration

if "YOUR_OPENWEATHER" in API_KEY:
    raise ValueError("Missing OpenWeatherMap API key. Get one from https://openweathermap.org/api")

# Speech-to-Text Function
def capture_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise
            audio = recognizer.listen(source, timeout=5)  # Listen for 5 seconds
        except sr.WaitTimeoutError:
            return "No speech detected. Please try again."
        
    try:
        return recognizer.recognize_google(audio, language="en-US")  # Recognize speech
    except sr.UnknownValueError:
        return "Sorry, I didn’t understand that. Please try again."
    except sr.RequestError as e:
        return f"Speech service error: {e}"

# Query Processing Function
def process_query(query):
    # Handle speech recognition errors
    if any(word in query.lower() for word in ["sorry", "error", "didn't understand", "no speech"]):
        return "Please try speaking again clearly."
    
    # Handle weather queries
    if "weather" in query.lower():
        # Extract city name using regex
        match = re.search(r"weather in (.+?)(?: please|\.|\?|$)", query, re.IGNORECASE)
        if not match:
            return "Please specify a city after 'weather in' (e.g., 'weather in London')."
        
        city = match.group(1).strip().title()  # Format city name
        try:
            # Make API request
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTP errors
            weather_data = response.json()
            
            # Parse response
            if weather_data.get("cod") == 200:
                temp = weather_data['main']['temp']
                desc = weather_data['weather'][0]['description']
                return f"The weather in {city} is {temp}°C with {desc}."
            return f"Error: {weather_data.get('message', 'Unknown error')}"
            
        except requests.exceptions.RequestException as e:
            return f"Couldn't connect to the weather service: {e}"
    
    # Handle other queries using LLM
    try:
        prompt = f"Give a concise and helpful answer to: {query}"
        response = llm.invoke(prompt).strip()  # Use invoke() instead of __call__
        return response.split(".")[0] + "."  # Return only the first complete sentence
    except Exception as e:
        return f"Error processing your query: {e}"

# Text-to-Speech Function
def speak_response(response):
    try:
        engine.say(response)
        engine.runAndWait()
        engine.stop()  # Clear any pending commands
    except Exception as e:
        print(f"TTS Error: {e}")

# Main Loop
if __name__ == "__main__":
    print("Voice Assistant Started. Say 'exit' to stop.")
    while True:
        try:
            # Capture user input
            query = capture_voice()
            print(f"User said: {query}")
            
            # Exit condition
            if "exit" in query.lower():
                speak_response("Goodbye!")
                break
            
            # Process query and respond
            response = process_query(query)
            print(f"Response: {response}")
            speak_response(response)
            
        except KeyboardInterrupt:
            speak_response("Goodbye!")
            break
        except Exception as e:
            print(f"Critical error: {e}")
            speak_response("Sorry, I encountered a critical error. Please restart the program.")