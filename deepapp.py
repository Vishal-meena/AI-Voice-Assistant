import speech_recognition as sr
import pyttsx3
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline
import requests
import re
import os
import gradio as gr
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 0.9)

# Initialize LLM
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

def process_query(query):
    # Handle speech recognition errors
    if any(word in query.lower() for word in ["sorry", "error", "didn't understand", "no speech"]):
        return "Please try speaking again clearly."
    
    # Handle weather queries
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
    
    # Handle other queries
    try:
        prompt = f"Give a concise and helpful answer to: {query}"
        response = llm.invoke(prompt).strip()
        return response.split(".")[0] + "."
    except Exception as e:
        return f"Error processing your query: {e}"

def gradio_interface(audio):
    # Convert audio file to text
    r = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data)
        except:
            text = "Sorry, I didn't understand that."
    
    # Process query
    response = process_query(text)
    
    # Convert response to speech
    engine.save_to_file(response, "response.wav")
    engine.runAndWait()
    
    return text, response, "response.wav"

# Create Gradio interface
demo = gr.Interface(
    fn=gradio_interface,
    inputs=gr.Audio(sources="microphone", type="filepath"),
    outputs=[
        gr.Textbox(label="Transcribed Text"),
        gr.Textbox(label="Assistant Response"), 
        gr.Audio(label="Voice Response", autoplay=True)
    ],
    title="AI Voice Assistant",
    description="Speak to the assistant and get both text and voice responses!"
)

if __name__ == "__main__":
    demo.launch(share = True)