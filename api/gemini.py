import google.generativeai as genai
import os, time

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
# Adding 'models/' helps the API find the correct path
model = genai.GenerativeModel("models/gemini-1.5-flash")


def transcribe_assamese(video_path):
    print(f"Uploading: {video_path}")
    video_file = genai.upload_file(path=video_path)

    while video_file.state.name == "PROCESSING":
        time.sleep(2)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise Exception("Gemini could not process the file")

    print("Transcribing...")
    response = model.generate_content([
        video_file,
        """You are an Assamese language transcription assistant.
Transcribe all speech in this video in Assamese (অসমীয়া) script.
Return ONLY segments in this exact format, one per line:
START_SECONDS | END_SECONDS | ASSAMESE_TEXT

Rules:
- Timestamps in seconds e.g. 0.0, 3.5, 12.0
- Each segment 3 to 7 seconds long
- Proper Assamese Unicode script only
- No explanations, no headers, nothing extra
- If no speech: 0.0 | 3.0 | (কোনো কথা নাই)

Example:
0.0 | 3.5 | নমস্কাৰ বন্ধুসকল
3.5 | 7.2 | আজি আমি এটা বিষয়ত কথা পাতিম
7.2 | 11.0 | এই বিষয়টো বহুত গুৰুত্বপূৰ্ণ"""
    ])

    try:
        genai.delete_file(video_file.name)
    except:
        pass

    return parse_segments(response.text)

def parse_segments(raw_text):
    segments = []
    for i, line in enumerate(raw_text.strip().split("\n")):
        line = line.strip()
        if not line or "|" not in line:
            continue
        parts = line.split("|")
        if len(parts) != 3:
            continue
        try:
            segments.append({
                "id": i + 1,
                "start": float(parts[0].strip()),
                "end": float(parts[1].strip()),
                "text": parts[2].strip()
            })
        except ValueError:
            continue
    return segments
