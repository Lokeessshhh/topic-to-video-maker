import os
import time
import json
import textwrap
import requests
from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
)
from gtts import gTTS
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

# ----------------------------
# 0. API Keys (PUT YOUR KEYS HERE)
# ----------------------------
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# ----------------------------
# 1. NVIDIA / OpenAI API Setup
# ----------------------------
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

# ----------------------------
# 2. Narration generation
# ----------------------------
# ----------------------------
# 2. Generate single narration line
# ----------------------------
def generate_narrations(prompt, num_lines=4, words_per_line=(5, 6)):
    """
    Generates `num_lines` narration lines, each with word count between words_per_line[0] and words_per_line[1].
    """
    try:
        instruction = (
            f"Create {num_lines} short information lines about '{prompt}'. "
            f"Each line should be between {words_per_line[0]} and {words_per_line[1]} words. "
            "Make them engaging and descriptive, like lines for a short cinematic video. "
            "Output them as a numbered list without extra explanation."
        )

        response = client.chat.completions.create(
            model="meta/llama3-8b-instruct",  # change to your desired NVIDIA model
            messages=[
                {"role": "system", "content": "You are a creative video narration writer."},
                {"role": "user", "content": instruction}
            ],
            temperature=0.8,
            max_tokens=150
        )

        raw_text = response.choices[0].message.content
        narrations = [
            line.strip("0123456789. ").strip()
            for line in raw_text.split("\n") if line.strip()
        ]
        return narrations[:num_lines]

    except Exception as e:
        print(f"Error generating narrations: {e}")
        return [f"{prompt} scene {i+1}" for i in range(num_lines)]

# ----------------------------
# 3. TTS generation (gTTS)
# ----------------------------
def generate_tts_audio(text, filename):
    """Saves TTS to filename and returns an AudioFileClip."""
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(filename)
    audio = AudioFileClip(filename)
    return audio

# ----------------------------
# 4. Pexels clip fetch (streamed)
# ----------------------------
def fetch_clip_from_pexels(query, index, orientation="portrait"):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 1, "orientation": orientation}

    try:
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params=params,
            timeout=15
        )
        if response.status_code != 200:
            print(f"Pexels search failed ({response.status_code}) for query: {query}")
            return None

        data = response.json()
        videos = data.get("videos") or []
        if not videos:
            print(f"No videos returned for: {query}")
            return None

        video_files = videos[0].get("video_files", [])
        if not video_files:
            print(f"No video_files for: {query}")
            return None

        # Pick highest width video
        video_files_sorted = sorted(video_files, key=lambda v: v.get("width", 0), reverse=True)
        video_url = video_files_sorted[0].get("link")
        if not video_url:
            print(f"No link found in video_files for: {query}")
            return None

        local_filename = f"pexels_scene_{index+1}.mp4"
        with requests.get(video_url, stream=True, timeout=60) as r:
            if r.status_code != 200:
                print(f"Failed to download video file ({r.status_code}) for: {query}")
                return None
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        clip = VideoFileClip(local_filename)
        return clip

    except Exception as e:
        print(f"Error fetching Pexels clip for '{query}': {e}")
        return None

# ----------------------------
# 5. Fallback image clip (PIL -> ImageClip)
# ----------------------------
def create_fallback_image_clip(text, duration, index, size=(1080, 1920), bgcolor=(0, 0, 0), textcolor=(255, 255, 255)):
    w, h = size
    img = Image.new("RGB", size, bgcolor)
    draw = ImageDraw.Draw(img)

    font_size = 72
    truetype_available = True
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except Exception:
        truetype_available = False
        font = ImageFont.load_default()

    wrapped = textwrap.fill(text, 18)
    lines = wrapped.splitlines()

    def text_size(fnt, line):
        bbox = fnt.getbbox(line)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    if truetype_available:
        while True:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
            line_heights = [text_size(font, line)[1] for line in lines]
            total_h = sum(line_heights) + (len(lines) - 1) * 10
            if total_h <= h * 0.55 or font_size <= 28:
                break
            font_size -= 4

    y = (h - sum([text_size(font, line)[1] for line in lines])) // 2
    for line in lines:
        line_w, line_h = text_size(font, line)
        x = (w - line_w) // 2
        draw.text((x, y), line, fill=textcolor, font=font)
        y += line_h + 10

    img_path = f"fallback_{index+1}.png"
    img.save(img_path)
    img_clip = ImageClip(img_path).set_duration(duration)
    return img_clip

# ----------------------------
# 6. Convert clip to vertical 1080x1920
# ----------------------------
def make_clip_vertical(clip, target_size=(1080, 1920)):
    target_w, target_h = target_size
    clip = clip.resize(height=target_h)

    if clip.w > target_w:
        clip = clip.crop(width=target_w, height=target_h, x_center=clip.w / 2, y_center=clip.h / 2)
    elif clip.w < target_w:
        clip = clip.resize(width=target_w)
        if clip.h > target_h:
            clip = clip.crop(width=target_w, height=target_h, x_center=clip.w / 2, y_center=clip.h / 2)
        elif clip.h < target_h:
            clip = clip.on_color(size=(target_w, target_h), color=(0, 0, 0), pos=('center', 'center'))
    return clip

# ----------------------------
# 7. Main build pipeline
# ----------------------------
def build_video(topic, output_filename="final_video.mp4", cleanup_temp=True):
    narration_lines = generate_narrations(topic, num_lines=4, words_per_line=(5, 6))
    print("Narration Lines:", narration_lines)

    processed_clips = []
    temp_audio_files, temp_video_files, temp_image_files = [], [], []

    # Create matching search queries (can modify to be different)
    search_variations = [
        topic,
        topic + " outdoors",
        topic + " close-up",
        topic + " cinematic"
    ]

    for i, (query, narration) in enumerate(zip(search_variations, narration_lines)):
        print(f"Fetching clip {i+1}/4 for query: '{query}'")
        clip = fetch_clip_from_pexels(query, i)

        # Generate TTS for this line
        audio_filename = f"audio_{i+1}.mp3"
        try:
            audio = generate_tts_audio(narration, audio_filename)
            temp_audio_files.append(audio_filename)
        except Exception as e:
            print(f"Failed to create TTS: {e}")
            audio = None

        if clip:
            try:
                clip = make_clip_vertical(clip, target_size=(1080, 1920))
                if audio:
                    clip = clip.set_audio(audio)
                    clip = clip.set_duration(audio.duration)
                else:
                    clip = clip.set_duration(3)
                processed_clips.append(clip)
                temp_video_files.append(f"pexels_scene_{i+1}.mp4")
            except Exception as e:
                print(f"Error preparing Pexels clip: {e}")
                img_clip = create_fallback_image_clip(narration, 3, i)
                if audio:
                    img_clip = img_clip.set_audio(audio)
                processed_clips.append(img_clip)
                temp_image_files.append(f"fallback_{i+1}.png")
        else:
            img_clip = create_fallback_image_clip(narration, 3, i)
            if audio:
                img_clip = img_clip.set_audio(audio)
            processed_clips.append(img_clip)
            temp_image_files.append(f"fallback_{i+1}.png")

    # Concatenate + export
    if processed_clips:
        try:
            final_clip = concatenate_videoclips(processed_clips, method="compose")
            final_clip.write_videofile(
                output_filename,
                codec="libx264",
                audio_codec="aac",
                fps=30,
                threads=4,
                preset="ultrafast"
            )
            print("Final video saved as", output_filename)
        finally:
            for c in processed_clips:
                try:
                    c.close()
                except:
                    pass
            try:
                final_clip.close()
            except:
                pass
    else:
        print("No clips produced.")

    if cleanup_temp:
        for f in temp_audio_files + temp_video_files + temp_image_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass


# ----------------------------
# FastAPI Setup
# ----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class VideoRequest(BaseModel):
    topic: str

def run_video_generation(topic: str):
    output_file = os.path.join("static", "final_video.mp4")
    build_video(topic, output_filename=output_file, cleanup_temp=True)

@app.post("/generate_video")
async def generate_video(request: VideoRequest):
    output_file = os.path.join("static", "final_video.mp4")
    build_video(request.topic, output_filename=output_file, cleanup_temp=True)
    video_url = "http://localhost:8000/static/final_video.mp4"
    return {"status": "done", "video_url": video_url}

