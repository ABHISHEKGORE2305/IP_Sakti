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

# Load fonts
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

def get_font(size, bold=False):
    path = FONT_BOLD_PATH if bold else FONT_REG_PATH
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

FONT_TITLE = get_font(56, bold=True)
FONT_SUBTITLE = get_font(32, bold=False)
FONT_BADGE = get_font(22, bold=True)
FONT_CAPTIONS = get_font(30, bold=True)
FONT_TAG = get_font(26, bold=True)

# Helper to draw rounded rectangle with alpha
def draw_rounded_rect(draw, bbox, radius, fill):
    draw.rounded_rectangle(bbox, radius=radius, fill=fill)

def get_audio_duration(wav_path):
    cmd = [FFMPEG, "-i", wav_path]
    proc = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    for line in proc.stderr.split("\n"):
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, sec = parts.split(":")
            return float(h) * 3600 + float(m) * 60 + float(sec)
    return 10.0

def make_title_card(title, subtitle, tag, progress=0.0):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (11, 15, 25, 255))
    draw = ImageDraw.Draw(img)
    
    # Subtle gradient background
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(11 * (1 - ratio) + 20 * ratio)
        g = int(18 * (1 - ratio) + 38 * ratio)
        b = int(32 * (1 - ratio) + 40 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
        
    # Decorative elements
    # Glow circle
    for rad in range(350, 0, -5):
        alpha = int(35 * (1 - rad / 350))
        draw.ellipse([WIDTH//2 - rad, HEIGHT//2 - rad - 50, WIDTH//2 + rad, HEIGHT//2 + rad - 50], outline=(16, 185, 129, alpha), width=3)

    # Pill badge
    badge_text = tag.upper()
    badge_w = len(badge_text) * 14 + 40
    badge_x = (WIDTH - badge_w) // 2
    draw.rounded_rectangle([badge_x, 260, badge_x + badge_w, 310], radius=25, fill=(16, 185, 129, 40), outline=(16, 185, 129, 200), width=2)
    draw.text((WIDTH//2, 285), badge_text, font=FONT_BADGE, fill=(52, 211, 153, 255), anchor="mm")

    # Main Title
    draw.text((WIDTH//2, 420), title, font=FONT_TITLE, fill=(255, 255, 255, 255), anchor="mm")
    
    # Subtitle
    draw.text((WIDTH//2, 510), subtitle, font=FONT_SUBTITLE, fill=(203, 213, 225, 255), anchor="mm")

    # Bottom hackathon footer
    draw.text((WIDTH//2, 920), "SMART INDIA HACKATHON 2026 • MINISTRY OF AYUSH", font=FONT_BADGE, fill=(148, 163, 184, 255), anchor="mm")
    
    return img.convert("RGB")

def render_frame_with_overlay(base_img, header_tag, caption_text, frame_idx, total_frames):
    img = base_img.copy()
    draw = ImageDraw.Draw(img)

    # 1. Top Glassmorphic Navigation Banner
    draw.rectangle([0, 0, WIDTH, 70], fill=(15, 23, 42, 220))
    draw.line([(0, 70), (WIDTH, 70)], fill=(51, 65, 85, 255), width=2)

    # Logo & Badge
    draw.text((40, 35), "AYURX", font=FONT_TITLE, fill=(52, 211, 153, 255), anchor="lm")
    draw.text((170, 35), "•  IP-SAKTI SAHAYAK", font=FONT_SUBTITLE, fill=(241, 245, 249, 255), anchor="lm")
    
    # Current Module Tag
    draw.rounded_rectangle([WIDTH - 420, 16, WIDTH - 40, 54], radius=19, fill=(30, 41, 59, 230), outline=(16, 185, 129, 180), width=2)
    draw.text((WIDTH - 230, 35), header_tag.upper(), font=FONT_BADGE, fill=(52, 211, 153, 255), anchor="mm")

    # 2. Bottom Caption Container
    if caption_text:
        # Measure caption box
        cap_h = 75
        cap_y = HEIGHT - 110
        cap_w = min(1760, max(800, len(caption_text) * 16 + 60))
        cap_x = (WIDTH - cap_w) // 2
        
        draw.rounded_rectangle([cap_x, cap_y, cap_x + cap_w, cap_y + cap_h], radius=20, fill=(15, 23, 42, 230), outline=(148, 163, 184, 140), width=2)
        draw.text((WIDTH // 2, cap_y + cap_h // 2), caption_text, font=FONT_CAPTIONS, fill=(254, 240, 138, 255), anchor="mm")

    # 3. Overall Timeline Progress Indicator at very bottom
    progress = frame_idx / max(1, total_frames)
    draw.rectangle([0, HEIGHT - 8, WIDTH, HEIGHT], fill=(30, 41, 59, 255))
    draw.rectangle([0, HEIGHT - 8, int(WIDTH * progress), HEIGHT], fill=(16, 185, 129, 255))

    return img.convert("RGB")

print("Rendering video scenes...")
