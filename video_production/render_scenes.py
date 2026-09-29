import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = "/Users/aspa/Desktop/abhishek/IP_Sakti"
PROD_DIR = os.path.join(BASE_DIR, "video_production")
SHOTS_DIR = os.path.join(PROD_DIR, "shots")
AUDIO_DIR = os.path.join(PROD_DIR, "audio")
CLIPS_DIR = os.path.join(PROD_DIR, "clips")
FINAL_MP4 = os.path.join(BASE_DIR, "ayurx_sih2026_demo.mp4")

FFMPEG = os.path.join(BASE_DIR, "venv/lib/python3.14/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1")

os.makedirs(CLIPS_DIR, exist_ok=True)

WIDTH, HEIGHT = 1920, 1080
FPS = 30

FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

def get_font(size, bold=False):
    path = FONT_BOLD_PATH if bold else FONT_REG_PATH
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

FONT_TITLE = get_font(52, bold=True)
FONT_SUBTITLE = get_font(28, bold=False)
FONT_BADGE = get_font(22, bold=True)
FONT_CAPTIONS = get_font(30, bold=True)

def get_audio_duration(wav_path):
    cmd = [FFMPEG, "-i", wav_path]
    proc = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    for line in proc.stderr.split("\n"):
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, sec = parts.split(":")
            return float(h) * 3600 + float(m) * 60 + float(sec)
    return 10.0

def make_title_card(title, subtitle, tag, sub_text, progress_ratio=0.0):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (11, 15, 25, 255))
    draw = ImageDraw.Draw(img)
    
    # Gradient background
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(10 * (1 - ratio) + 15 * ratio)
        g = int(22 * (1 - ratio) + 35 * ratio)
        b = int(35 * (1 - ratio) + 45 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
        
    # Glowing concentric rings
    for rad in range(380, 50, -10):
        alpha = int(28 * (1 - rad / 380))
        draw.ellipse([WIDTH//2 - rad, HEIGHT//2 - rad - 40, WIDTH//2 + rad, HEIGHT//2 + rad - 40], outline=(16, 185, 129, alpha), width=3)

    # Top Tag
    badge_text = tag.upper()
    badge_w = len(badge_text) * 14 + 50
    badge_x = (WIDTH - badge_w) // 2
    draw.rounded_rectangle([badge_x, 240, badge_x + badge_w, 296], radius=28, fill=(16, 185, 129, 45), outline=(16, 185, 129, 220), width=2)
    draw.text((WIDTH//2, 268), badge_text, font=FONT_BADGE, fill=(52, 211, 153, 255), anchor="mm")

    # Main Title
    draw.text((WIDTH//2, 400), title, font=FONT_TITLE, fill=(255, 255, 255, 255), anchor="mm")
    
    # Subtitle
    draw.text((WIDTH//2, 490), subtitle, font=FONT_SUBTITLE, fill=(203, 213, 225, 255), anchor="mm")

    # Subtitle caption at bottom
    if sub_text:
        cap_h = 75
        cap_y = HEIGHT - 130
        cap_w = min(1760, max(850, len(sub_text) * 16 + 60))
        cap_x = (WIDTH - cap_w) // 2
        draw.rounded_rectangle([cap_x, cap_y, cap_x + cap_w, cap_y + cap_h], radius=20, fill=(15, 23, 42, 235), outline=(148, 163, 184, 150), width=2)
        draw.text((WIDTH // 2, cap_y + cap_h // 2), sub_text, font=FONT_CAPTIONS, fill=(254, 240, 138, 255), anchor="mm")

    # Footer
    draw.text((WIDTH//2, 980), "SMART INDIA HACKATHON 2026 • MINISTRY OF AYUSH • IP-SAKTI SAHAYAK", font=FONT_BADGE, fill=(148, 163, 184, 255), anchor="mm")

    # Progress bar at bottom
    draw.rectangle([0, HEIGHT - 8, int(WIDTH * progress_ratio), HEIGHT], fill=(16, 185, 129, 255))
    return img.convert("RGB")

def render_ui_scene(shot1_path, shot2_path, tag, sub_text, duration, wav_path, out_clip_path, scene_idx, total_scenes):
    total_frames = int(duration * FPS)
    
    # Load screenshots
    img1 = Image.open(shot1_path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    img2 = Image.open(shot2_path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS) if shot2_path else img1
    
    pipe = subprocess.Popen([
        FFMPEG, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", wav_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_clip_path
    ], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    half_frames = total_frames // 2

    for f in range(total_frames):
        # Determine image blend / switch
        if f < half_frames:
            # First half: show img1 with subtle slow zoom (1.00 to 1.03)
            scale = 1.0 + 0.03 * (f / half_frames)
            w_scaled, h_scaled = int(WIDTH * scale), int(HEIGHT * scale)
            res = img1.resize((w_scaled, h_scaled), Image.Resampling.BILINEAR)
            left = (w_scaled - WIDTH) // 2
            top = (h_scaled - HEIGHT) // 2
            base = res.crop((left, top, left + WIDTH, top + HEIGHT))
        else:
            # Second half: show img2 with subtle zoom (1.00 to 1.03)
            progress2 = (f - half_frames) / max(1, half_frames)
            scale = 1.0 + 0.03 * progress2
            w_scaled, h_scaled = int(WIDTH * scale), int(HEIGHT * scale)
            res = img2.resize((w_scaled, h_scaled), Image.Resampling.BILINEAR)
            left = (w_scaled - WIDTH) // 2
            top = (h_scaled - HEIGHT) // 2
            base = res.crop((left, top, left + WIDTH, top + HEIGHT))

        # Add UI Overlays
        draw = ImageDraw.Draw(base)

        # Top Glassmorphic Navigation Banner
        draw.rectangle([0, 0, WIDTH, 70], fill=(15, 23, 42, 230))
        draw.line([(0, 70), (WIDTH, 70)], fill=(51, 65, 85, 255), width=2)

        # Logo & Badge
        draw.text((40, 35), "AYURX", font=FONT_TITLE, fill=(52, 211, 153, 255), anchor="lm")
        draw.text((220, 35), "•  IP-SAKTI SAHAYAK (SIH 2026)", font=FONT_SUBTITLE, fill=(241, 245, 249, 255), anchor="lm")

        # Current Module Tag
        draw.rounded_rectangle([WIDTH - 480, 15, WIDTH - 40, 55], radius=20, fill=(30, 41, 59, 240), outline=(16, 185, 129, 200), width=2)
        draw.text((WIDTH - 260, 35), tag.upper(), font=FONT_BADGE, fill=(52, 211, 153, 255), anchor="mm")

        # Bottom Caption Container
        if sub_text:
            cap_h = 75
            cap_y = HEIGHT - 120
            cap_w = min(1760, max(850, len(sub_text) * 16 + 60))
            cap_x = (WIDTH - cap_w) // 2
            draw.rounded_rectangle([cap_x, cap_y, cap_x + cap_w, cap_y + cap_h], radius=20, fill=(15, 23, 42, 240), outline=(148, 163, 184, 160), width=2)
            draw.text((WIDTH // 2, cap_y + cap_h // 2), sub_text, font=FONT_CAPTIONS, fill=(254, 240, 138, 255), anchor="mm")

        # Global timeline progress
        overall_progress = (scene_idx + f / total_frames) / total_scenes
        draw.rectangle([0, HEIGHT - 8, WIDTH, HEIGHT], fill=(30, 41, 59, 255))
        draw.rectangle([0, HEIGHT - 8, int(WIDTH * overall_progress), HEIGHT], fill=(16, 185, 129, 255))

        pipe.stdin.write(base.convert("RGB").tobytes())

    pipe.stdin.close()
    pipe.wait()
    print(f"Scene {scene_idx} rendered: {out_clip_path}")

def render_title_scene(title, subtitle, tag, sub_text, duration, wav_path, out_clip_path, scene_idx, total_scenes):
    total_frames = int(duration * FPS)
    pipe = subprocess.Popen([
        FFMPEG, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", wav_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_clip_path
    ], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    for f in range(total_frames):
        overall_progress = (scene_idx + f / total_frames) / total_scenes
        frame = make_title_card(title, subtitle, tag, sub_text, overall_progress)
        pipe.stdin.write(frame.tobytes())

    pipe.stdin.close()
    pipe.wait()
    print(f"Title scene {scene_idx} rendered: {out_clip_path}")

scenes_config = [
    {
        "id": "scene_01",
        "type": "title",
        "title": "AYURX — IP-SAKTI SAHAYAK",
        "subtitle": "Multilingual AI Engine for Ayurveda IP & Regulatory Guidance",
        "tag": "SMART INDIA HACKATHON 2026",
        "sub": "Ayurveda innovation is booming. But bridging classical formulations with modern laws is a bottleneck.",
        "wav": os.path.join(AUDIO_DIR, "scene_01.wav")
    },
    {
        "id": "scene_02",
        "type": "ui",
        "shot1": os.path.join(SHOTS_DIR, "01_landing_hero.png"),
        "shot2": os.path.join(SHOTS_DIR, "02_landing_features.png"),
        "tag": "INTELLIGENCE ENGINE OVERVIEW",
        "sub": "Meet AyurX: A source-grounded AI engine decoding formulations into actionable IP & regulatory guidance.",
        "wav": os.path.join(AUDIO_DIR, "scene_02.wav")
    },
    {
        "id": "scene_03",
        "type": "ui",
        "shot1": os.path.join(SHOTS_DIR, "04_app_step1_jurisdiction.png"),
        "shot2": os.path.join(SHOTS_DIR, "05_app_step2_formulation.png"),
        "tag": "6-STEP GUIDED WIZARD",
        "sub": "Instead of generic chat, we use a structured wizard with target jurisdiction and formulation details.",
        "wav": os.path.join(AUDIO_DIR, "scene_03.wav")
    },
    {
        "id": "scene_04",
        "type": "ui",
        "shot1": os.path.join(SHOTS_DIR, "06_app_step3_issues.png"),
        "shot2": os.path.join(SHOTS_DIR, "07_app_step4_analysis.png"),
        "tag": "IP & ABS MULTI-DOMAIN RISK",
        "sub": "AyurX flags Section 3(p) traditional knowledge hurdles, Section 3(e) criteria, and NBA Form I ABS rules.",
        "wav": os.path.join(AUDIO_DIR, "scene_04.wav")
    },
    {
        "id": "scene_05",
        "type": "ui",
        "shot1": os.path.join(SHOTS_DIR, "08_app_step5_sources.png"),
        "shot2": os.path.join(SHOTS_DIR, "09_app_step6_action_plan.png"),
        "tag": "ZERO-HALLUCINATION GROUNDING",
        "sub": "Every claim is anchored to official statutory sources, with verifiable citations and reciprocal rank fusion.",
        "wav": os.path.join(AUDIO_DIR, "scene_05.wav")
    },
    {
        "id": "scene_06",
        "type": "ui",
        "shot1": os.path.join(SHOTS_DIR, "10_app_export_markets.png"),
        "shot2": os.path.join(SHOTS_DIR, "11_app_law_timeline.png"),
        "tag": "GLOBAL EXPORT & LAW TIMELINE",
        "sub": "Evaluates export pathways across US FDA and EMA while tracking statutory amendment timelines.",
        "wav": os.path.join(AUDIO_DIR, "scene_06.wav")
    },
    {
        "id": "scene_07",
        "type": "ui",
        "shot1": os.path.join(SHOTS_DIR, "13_app_chat_query.png"),
        "shot2": os.path.join(SHOTS_DIR, "12_app_eval_dashboard.png"),
        "tag": "MULTILINGUAL REGULATORY CHAT",
        "sub": "Researchers and patent attorneys query the engine in natural or regional languages with live citations.",
        "wav": os.path.join(AUDIO_DIR, "scene_07.wav")
    },
    {
        "id": "scene_08",
        "type": "title",
        "title": "AYURX: ANCIENT WISDOM. SMARTER ANSWERS.",
        "subtitle": "From Formulation to Evidence to Actionable Guidance",
        "tag": "SIH 2026 WINNING SOLUTION",
        "sub": "Protecting Indian traditional knowledge while accelerating commercial innovation.",
        "wav": os.path.join(AUDIO_DIR, "scene_08.wav")
    }
]

total_scenes = len(scenes_config)

clip_files = []
for idx, sc in enumerate(scenes_config):
    dur = get_audio_duration(sc["wav"])
    out_clip = os.path.join(CLIPS_DIR, f"{sc['id']}.mp4")
    clip_files.append(out_clip)
    
    if sc["type"] == "title":
        render_title_scene(sc["title"], sc["subtitle"], sc["tag"], sc["sub"], dur, sc["wav"], out_clip, idx, total_scenes)
    else:
        render_ui_scene(sc["shot1"], sc["shot2"], sc["tag"], sc["sub"], dur, sc["wav"], out_clip, idx, total_scenes)

# Concatenate all clips into final video
concat_txt = os.path.join(CLIPS_DIR, "concat_list.txt")
with open(concat_txt, "w") as f:
    for clip in clip_files:
        f.write(f"file '{clip}'\n")

print("Concatenating all clips into final video...")
cmd_concat = [
    FFMPEG, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", concat_txt,
    "-c", "copy",
    FINAL_MP4
]
subprocess.run(cmd_concat, check=True)
print(f"Final MP4 Video created successfully: {FINAL_MP4}")
