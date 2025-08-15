AI Video Generator Project 🎬🤖

An end-to-end AI-powered video generator that converts AI-generated narrations into fully edited videos. This project uses a GPT 120B model from OpenRouter for narration, Pexels API for video clips, and Lovable.ai for the frontend UI, integrated with a FastAPI backend.

Features

Generate natural language narrations using GPT 120B.

Download relevant video clips using Pexels API.

Automatically generate audio narration from text.

Edit videos: cut clips appropriately, merge them with audio.

Interactive and modern UI using Lovable.ai.

Fully functional backend with FastAPI.

Preview generated videos directly in the UI.

Tech Stack

AI Model: GPT 120B via OpenRouter API

Video Source: Pexels API

Frontend: Lovable.ai

Backend: FastAPI (main.py)

Video Processing: FFmpeg or Python video libraries

Audio Generation: Text-to-Speech (TTS) from narration

Architecture / Workflow

Text Generation:

User inputs a topic or narration request in the UI.

GPT 120B generates detailed narration text via OpenRouter API using your API key.

Video Retrieval:

Extract keywords from narration.

Fetch relevant videos from Pexels API.

Audio Generation:

Convert narration text into audio using a TTS engine.

Video Editing:

Automatically cut video clips according to narration timestamps.

Merge clips with generated audio.

Rendering & Preview:

Render final video.

Show output directly in the UI.

Demo

Sample Video Link

Setup & Installation

Clone the repository

git clone https://github.com/yourusername/ai-video-generator.git
cd ai-video-generator


Create virtual environment

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


Install dependencies

pip install -r requirements.txt


Setup API keys

Create a .env file and add:

OPENROUTER_API_KEY=your_openrouter_api_key
PEXELS_API_KEY=your_pexels_api_key


Run FastAPI backend

uvicorn main:app --reload


Open Frontend UI

Access your Lovable.ai UI and connect it to the backend endpoints.

Usage

Enter a topic or narration prompt in the UI.

Click Generate Video.

The system will:

Generate narration with GPT 120B

Download relevant videos from Pexels

Generate audio narration

Cut and merge video clips

Preview or download the final video.

Folder Structure
ai-video-generator/
│
├─ main.py                 # FastAPI backend
├─ frontend/               # Lovable.ai frontend files
├─ videos/                 # Downloaded and edited videos
├─ audio/                  # Generated audio files
├─ requirements.txt
├─ README.md
└─ .env

APIs Used

OpenRouter GPT 120B: AI text generation
https://openrouter.ai/

Pexels API: Video downloading
https://www.pexels.com/api/

Future Improvements

Add custom voice options for TTS.

Support multiple languages.

Add advanced video effects or transitions.

Implement user authentication and saved projects.

License

MIT License © 2025 Your Name

If you want, I can also create a short, visually rich GitHub README with badges, API links, and a cleaner workflow diagram that would look amazing on your repo’s front page. It could include an embedded GIF/video preview and a workflow diagram showing narration → video → merge.

Do you want me to do that next?
