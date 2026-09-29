import os
import subprocess

AUDIO_DIR = "/Users/aspa/Desktop/abhishek/IP_Sakti/video_production/audio"
FFMPEG = "/Users/aspa/Desktop/abhishek/IP_Sakti/venv/lib/python3.14/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1"

scenes = [
    {
        "id": "scene_01",
        "text": "Ayurveda innovation is booming. But bridging classical formulations with modern patent laws, traditional knowledge clearance, and National Biodiversity rules is a massive legal bottleneck."
    },
    {
        "id": "scene_02",
        "text": "Meet AyurX — IP-SAKTI Sahayak. A source-grounded AI intelligence engine designed specifically to decode Ayurveda formulations and convert them into actionable IP, ABS, and regulatory guidance."
    },
    {
        "id": "scene_03",
        "text": "Instead of unstructured chatbot prompts, AyurX uses a structured six-step guided wizard. We select our target jurisdiction and enter a modern nano-emulsion formulation of Ashwagandha and Haridra."
    },
    {
        "id": "scene_04",
        "text": "Within seconds, AyurX breaks down the complete legal posture. It highlights Section 3(p) traditional knowledge hurdles under the Indian Patents Act, identifies Section 3(e) synergistic efficacy criteria, and flags mandatory Access and Benefit Sharing compliance under the National Biodiversity Authority."
    },
    {
        "id": "scene_05",
        "text": "Crucially, unlike generic AI models that hallucinate legal advice, every insight is anchored directly to official statutory sources, with verifiable citations and reciprocal rank fusion across thousands of legal chunks."
    },
    {
        "id": "scene_06",
        "text": "AyurX also evaluates international export pathways across the US FDA and European Medicines Agency, while tracking historical amendments to statutory rules to ensure compliance over time."
    },
    {
        "id": "scene_07",
        "text": "Researchers and patent attorneys can also query the engine in natural language or regional Indian languages, receiving instant, source-backed answers for complex regulatory queries."
    },
    {
        "id": "scene_08",
        "text": "From ancient formulation to evidence-backed commercialization — AyurX protects Indian traditional knowledge while accelerating global innovation. AyurX: Ancient Wisdom, Smarter Answers."
    }
]

durations = {}

for s in scenes:
    aiff_path = os.path.join(AUDIO_DIR, f"{s['id']}.aiff")
    wav_path = os.path.join(AUDIO_DIR, f"{s['id']}.wav")
    
    # 1. Run say with Rishi voice (natural rate ~165 wpm)
    cmd = ["say", "-v", "Rishi", "-r", "165", "-o", aiff_path, s["text"]]
    subprocess.run(cmd, check=True)
    
    # 2. Convert to 44.1kHz stereo WAV using ffmpeg
    cmd_ffmpeg = [FFMPEG, "-y", "-i", aiff_path, "-ar", "44100", "-ac", "2", wav_path]
    subprocess.run(cmd_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # 3. Get duration
    cmd_probe = [
        FFMPEG, "-i", wav_path
    ]
    proc = subprocess.run(cmd_probe, stderr=subprocess.PIPE, text=True)
    for line in proc.stderr.split("\n"):
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            # HH:MM:SS.ms
            h, m, sec = parts.split(":")
            total_sec = float(h) * 3600 + float(m) * 60 + float(sec)
            durations[s["id"]] = round(total_sec, 2)
            print(f"{s['id']}: {durations[s['id']]} seconds")
            break

print("All audio files generated successfully!")
print("Durations summary:", durations)
