"""
Automated Daily Bass Music Video Pipeline
- Fetches HD Car footage (via Pexels API or curated car reels)
- Fetches Bass Music track (royalty-free bass boosted beats)
- Montages video + audio using FFmpeg with cinematic grading
- Generates YouTube Title, Description & Tags using Gemini API
- Uploads video directly to YouTube via YouTube Data API v3
"""

import os
import sys
import json
import random
import subprocess
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Environment configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
YOUTUBE_CLIENT_SECRET_JSON = os.getenv("YOUTUBE_CLIENT_SECRET_JSON")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")
YOUTUBE_PRIVACY = os.getenv("YOUTUBE_PRIVACY", "public")

OUTPUT_DIR = "build_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CAR_SEARCH_QUERIES = [
    "supercars night drive",
    "bmw night drift",
    "sports car aesthetic night city",
    "jdm drift cars",
    "luxury car driving rain",
    "hypercar cinematic 4k"
]

FALLBACK_MUSIC_URLS = [
    # Curated copyright-free high-bass / phonk / trap beats
    "https://cdn.pixabay.com/download/audio/2022/10/14/audio_9939f77610.mp3",
    "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
    "https://cdn.pixabay.com/download/audio/2023/04/17/audio_3321589ca3.mp3"
]

def fetch_bass_audio(output_file):
    """Downloads or prepares a royalty-free bass music track."""
    print("[1/5] Fetching bass music track...")
    audio_url = random.choice(FALLBACK_MUSIC_URLS)
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(audio_url, headers=headers, stream=True, timeout=60)
    r.raise_for_status()
    with open(output_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Music downloaded successfully: {output_file}")
    return output_file

def fetch_car_videos(api_key, output_dir, count=3):
    """Fetches high quality car footage from Pexels API."""
    print("[2/5] Fetching car videos...")
    video_files = []
    
    if api_key:
        query = random.choice(CAR_SEARCH_QUERIES)
        url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&per_page=15&orientation=landscape"
        headers = {"Authorization": api_key}
        res = requests.get(url, headers=headers, timeout=30)
        if res.status_code == 200:
            data = res.json()
            videos = data.get("videos", [])
            random.shuffle(videos)
            downloaded = 0
            for vid in videos:
                if downloaded >= count:
                    break
                # Find best resolution (1080p or highest available)
                files = vid.get("video_files", [])
                files.sort(key=lambda x: (x.get("width") or 0) * (x.get("height") or 0), reverse=True)
                for vf in files:
                    link = vf.get("link")
                    if link:
                        filepath = os.path.join(output_dir, f"car_clip_{downloaded}.mp4")
                        print(f"Downloading clip {downloaded+1}: {link[:60]}...")
                        vr = requests.get(link, stream=True, timeout=60)
                        if vr.status_code == 200:
                            with open(filepath, "wb") as f:
                                for chunk in vr.iter_content(chunk_size=16384):
                                    f.write(chunk)
                            video_files.append(filepath)
                            downloaded += 1
                            break

    # If no API key or failed to download, create a synthetic cinematic background
    if not video_files:
        print("Using fallback cinematic video generator with FFmpeg...")
        fallback_path = os.path.join(output_dir, "fallback_clip.mp4")
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "mptestsrc=rate=30:duration=30:size=1920x1080",
            "-vf", "hue=s=0.2,eq=contrast=1.3:brightness=-0.1",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", fallback_path
        ]
        subprocess.run(cmd, check=True)
        video_files.append(fallback_path)

    print(f"Total video clips ready: {len(video_files)}")
    return video_files

def get_audio_duration(audio_file):
    """Gets audio duration in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(result.stdout.strip())

def montage_video(audio_file, video_files, output_mp4):
    """Combines car video clips with bass music into a polished 1080p MP4."""
    print("[3/5] Montaging video with FFmpeg...")
    duration = get_audio_duration(audio_file)
    print(f"Target duration: {duration:.2f} seconds")

    # Create FFmpeg concat list
    concat_list_file = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        # Loop clips enough to cover the duration
        for _ in range(max(1, int(duration // 15) + 2)):
            for vf in video_files:
                abs_path = os.path.abspath(vf).replace("\\", "/")
                f.write(f"file '{abs_path}'\n")

    # Render final video
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list_file,
        "-i", audio_file,
        "-t", str(duration),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,eq=contrast=1.15:saturation=1.2",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "320k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f"Render complete: {output_mp4}")
    return output_mp4

def generate_metadata(gemini_api_key):
    """Uses Gemini API to generate catchy title, description, and tags."""
    print("[4/5] Generating SEO metadata with Gemini...")
    prompt = """
    Generate YouTube metadata for a high-energy bass boosted car music / night drive video.
    Return ONLY a JSON object with this exact structure:
    {
      "title": "catchy high-CTR title with emojis, under 70 chars (e.g. BASS BOOSTED 2026 🔥 | Night Drive & Drift)",
      "description": "engaging YouTube description with track vibes, car aesthetic, hashtags, and call to action",
      "tags": ["bass boosted", "car music", "night drive", "drift", "trap bass", "phonk", "subwoofer test"]
    }
    """
    
    if gemini_api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                raw_json = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(raw_json)
        except Exception as e:
            print(f"Gemini generation error: {e}")

    # Fallback metadata
    year = 2026
    return {
        "title": f"DEEP BASS BOOSTED CAR MUSIC {year} 🚗💨 | Night Drive & Drift Vibes",
        "description": f"Best high-energy deep bass music for car audio systems and night driving.\n\n🔥 Turn up the volume & feel the sub bass!\n🔔 Subscribe for daily bass tracks!\n\n#bassboosted #carmusic #nightdrive #drift #deepbass #{year}",
        "tags": ["bass boosted", "car music", "night drive", "drift bass", "subwoofer bass", "extreme bass", "phonk", "edm"]
    }

def upload_to_youtube(video_path, metadata):
    """Uploads final video to YouTube Channel via OAuth refresh token."""
    print("[5/5] Uploading video to YouTube...")
    if not YOUTUBE_CLIENT_SECRET_JSON or not YOUTUBE_REFRESH_TOKEN:
        print("YouTube credentials missing in environment variables. Skipping upload.")
        print(f"Video file saved locally at: {video_path}")
        return None

    client_info = json.loads(YOUTUBE_CLIENT_SECRET_JSON)
    # Support both 'installed' and 'web' client secret formats
    app_info = client_info.get("installed") or client_info.get("web") or client_info
    
    creds = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=app_info.get("client_id"),
        client_secret=app_info.get("client_secret")
    )

    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": metadata.get("title")[:100],
            "description": metadata.get("description")[:5000],
            "tags": metadata.get("tags")[:30],
            "categoryId": "10"  # Music category
        },
        "status": {
            "privacyStatus": YOUTUBE_PRIVACY,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, mimetype="video/mp4", chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    print(f"Uploaded successfully! Video URL: https://youtu.be/{video_id}")
    return video_id

def main():
    audio_file = os.path.join(OUTPUT_DIR, "bass_track.mp3")
    final_video = os.path.join(OUTPUT_DIR, "final_bass_car_video.mp4")

    fetch_bass_audio(audio_file)
    video_files = fetch_car_videos(PEXELS_API_KEY, OUTPUT_DIR)
    montage_video(audio_file, video_files, final_video)
    metadata = generate_metadata(GEMINI_API_KEY)
    print("Metadata generated:")
    print(f"Title: {metadata['title']}")
    
    upload_to_youtube(final_video, metadata)
    print("All pipeline steps completed successfully!")

if __name__ == "__main__":
    main()
