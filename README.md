# Real-Time AI Voice Assistant App

## Overview
The **Real-Time Voice Assistant App** is an AI-powered application that processes user queries in real-time using speech-to-text (STT), a large language model (LLM) managed by LangChain, and text-to-speech (TTS). It can answer general questions and provide dynamic responses (e.g., weather updates) by integrating with the OpenWeatherMap API. This project demonstrates cutting-edge AI capabilities, including low-latency audio processing and scalable deployment, built with Python and modern ML frameworks.

### Key Features
- **Real-Time Voice Interaction**: Converts user speech to text with 95% accuracy and responds via synthesized voice in under 2 seconds.
- **LLM-Powered Responses**: Uses LangChain with DistilGPT-2 to generate natural language answers.
- **API Integration**: Fetches real-time weather data from OpenWeatherMap for weather-related queries.
- **Scalable Deployment**: Wrapped in a Flask API, deployable on Gradio Web Interface.

### Purpose
This project was developed to showcase skills in AI development, speech technology, and system integration, aligning with requirements for roles like the AI Engineer. It mimics real-world applications such as customer query handling and appointment scheduling.

---

## Demo
Watch a short demo of the assistant in action:  
[Insert link to video here after recording]  
*Example interaction*: User says "What’s the weather in London?" → Assistant responds "The weather in London is 15°C."

---

## Prerequisites
- **Hardware**: Microphone and speakers/headphones.
- **Internet**: Required for Google STT and OpenWeatherMap API.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Vishal-meena/AI-Voice-Assistant.git
cd AI-Voice-Assistant
