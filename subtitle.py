def format_time_srt(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def format_time_vtt(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"

def to_srt(segments):
    lines = []
    for i, seg in enumerate(segments, 1):
        start = format_time_srt(seg["start"])
        end = format_time_srt(seg["end"])
        lines.append(f"{i}\n{start} --> {end}\n{seg['text']}\n")
    return "\n".join(lines)

def to_vtt(segments):
    lines = ["WEBVTT\n"]
    for i, seg in enumerate(segments, 1):
        start = format_time_vtt(seg["start"])
        end = format_time_vtt(seg["end"])
        lines.append(f"{i}\n{start} --> {end}\n{seg['text']}\n")
    return "\n".join(lines)
