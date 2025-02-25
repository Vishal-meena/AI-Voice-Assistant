import gradio as gr
from gtts import gTTS
import speech_recognition as sr
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline
import requests
import re
import os
import tempfile
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# Initialize LLM pipeline
try:
    llm_pipeline = pipeline(
        "text-generation",
        model="distilgpt2",
        max_new_tokens=100,
        temperature=0.7,
        truncation=True,
        pad_token_id=50256
    )
    llm = HuggingFacePipeline(pipeline=llm_pipeline)
except Exception as e:
    print(f"Error initializing LLM: {e}")
    exit()

# Weather API Configuration
if "YOUR_OPENWEATHER" in API_KEY or not API_KEY:
    raise ValueError("Missing OpenWeatherMap API key. Get one from https://openweathermap.org/api")

# Speech-to-Text Function
def capture_voice(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language="en-US")
    except sr.UnknownValueError:
        return "Sorry, I didn’t understand that. Please try again."
    except sr.RequestError as e:
        return f"Speech service error: {e}"

# Query Processing Function
def process_query(query):
    if any(word in query.lower() for word in ["sorry", "error", "didn't understand", "no speech"]):
        return "Please try speaking again clearly."
    
    if "exit" in query.lower():
        return "Goodbye!"
    
    if "weather" in query.lower():
        match = re.search(r"weather in (.+?)(?: please|\.|\?|$)", query, re.IGNORECASE)
        if not match:
            return "Please specify a city after 'weather in' (e.g., 'weather in London')."
        
        city = match.group(1).strip().title()
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
            weather_data = response.json()
            
            if weather_data.get("cod") == 200:
                temp = weather_data['main']['temp']
                desc = weather_data['weather'][0]['description']
                return f"The weather in {city} is {temp}°C with {desc}."
            return f"Error: {weather_data.get('message', 'Unknown error')}"
        except requests.exceptions.RequestException as e:
            return f"Couldn't connect to the weather service: {e}"
    
    try:
        prompt = f"Give a concise and helpful answer to: {query}"
        response = llm.invoke(prompt).strip()
        return response.split(".")[0] + "."
    except Exception as e:
        return f"Error processing your query: {e}"

# Text-to-Speech Function
def speak_response(response):
    tts = gTTS(response, lang='en')
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        tts.write_to_fp(temp_file)
        return temp_file.name

# Main function for Gradio
def process_audio(audio_path):
    if audio_path is None:
        return speak_response("No audio recorded. Please try again.")
    text = capture_voice(audio_path)
    response_text = process_query(text)
    response_audio_path = speak_response(response_text)
    return response_audio_path

# Gradio Interface
demo = gr.Interface(
    fn=process_audio,
    inputs=gr.Audio(type="filepath", label="Record your query here"),  # Updated for recording
    outputs=gr.Audio(type="filepath", label="Listen to the response"),  # Updated for playback
    title="Voice Assistant",
    description="Record your query (e.g., 'weather in London' or 'What’s the time?'). Say 'exit' to hear 'Goodbye!'"
)
if __name__ == "__main__":
    demo.launch(share = True)