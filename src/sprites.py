"""
NyangBuddy Modern Pixel-Art Sprite Engine — 4-Frame Fluid Edition
High-framerate 32x32 kawaii chubby pixel cat with 4-frame walk cycles,
breathing idles, dynamic 8-direction eye follow, keyboard kneading,
overheat steam mode, paper unroll scroll reaction, petting/purr reactions,
and custom accessories (Boss Oyen shades & chain).
"""

from PIL import Image, ImageDraw
import os
from typing import Dict, Tuple, List, Optional

# ─── COLOR PALETTES ─────────────────────────────────────────────────────────
PALETTES: Dict[str, Dict[str, Tuple[int, int, int, int]]] = {
    "boss_oyen": {
        "name": "Boss Oyen (Kacamata Hitam 🕶️)",
        "fur_main": (238, 122, 34, 255),    # Vibrant warm orange
        "fur_shade": (188, 78, 14, 255),    # Dark tiger stripe
        "fur_belly": (255, 250, 242, 255),  # Creamy white muzzle/belly
        "inner_ear": (255, 175, 185, 255),  # Pink ear
        "outline": (26, 18, 12, 255),       # Deep dark outline
        "eye_iris": (26, 18, 12, 255),      # Hidden by shades
        "collar": (255, 195, 15, 255),      # Solid gold chain
        "accent": (255, 235, 90, 255),      # Gold shine
        "has_shades": True,
        "has_chain": True,
    },
    "oyen": {
        "name": "Si Oyen (Orange Tabby 🐱)",
        "fur_main": (238, 122, 34, 255),
        "fur_shade": (188, 78, 14, 255),
        "fur_belly": (255, 250, 242, 255),
        "inner_ear": (255, 175, 185, 255),
        "outline": (26, 18, 12, 255),
        "eye_iris": (46, 185, 95, 255),     # Emerald green
        "collar": (235, 55, 75, 255),      # Red collar
        "accent": (255, 215, 35, 255),     # Gold bell
        "has_shades": False,
        "has_chain": False,
    },
    "mochi": {
        "name": "Si Kalung Biru (Mochi 🐾)",
        "fur_main": (168, 178, 192, 255),  # Soft slate grey
        "fur_shade": (118, 128, 142, 255), # Dark grey stripe
        "fur_belly": (250, 252, 255, 255), # Snow white
        "inner_ear": (255, 170, 188, 255),
        "outline": (30, 34, 42, 255),
        "eye_iris": (45, 145, 235, 255),    # Sky blue
        "collar": (25, 185, 215, 255),     # Turquoise cyan
        "accent": (255, 215, 35, 255),     # Gold bell
        "has_shades": False,
        "has_chain": True,
    },
    "shiro": {
        "name": "Si Putih (Snow White ❄️)",
        "fur_main": (250, 252, 255, 255),  # Pure white
        "fur_shade": (218, 226, 238, 255), # Soft blue shadow
        "fur_belly": (255, 255, 255, 255),
        "inner_ear": (255, 180, 200, 255),
        "outline": (45, 52, 64, 255),
        "eye_iris": (52, 148, 235, 255),    # Sapphire
        "collar": (245, 95, 145, 255),     # Pink
        "accent": (255, 225, 50, 255),
        "has_shades": False,
        "has_chain": False,
    },
    "tuxedo": {
        "name": "Si Tuxedo (Black & White 🎩)",
        "fur_main": (38, 42, 52, 255),     # Midnight black
        "fur_shade": (22, 24, 30, 255),
        "fur_belly": (252, 254, 255, 255), # White chest & socks
        "inner_ear": (255, 165, 185, 255),
        "outline": (14, 16, 22, 255),
        "eye_iris": (245, 195, 25, 255),    # Amber gold
        "collar": (225, 45, 55, 255),      # Red bow
        "accent": (255, 225, 50, 255),
        "has_shades": False,
        "has_chain": False,
    },
    "calico": {
        "name": "Belang Tiga (Calico 🎨)",
        "fur_main": (250, 252, 255, 255),  # White
        "fur_shade": (230, 115, 25, 255),  # Ginger patch
        "fur_belly": (255, 255, 255, 255),
        "inner_ear": (255, 172, 190, 255),
        "outline": (32, 36, 44, 255),
        "eye_iris": (46, 185, 95, 255),
        "collar": (180, 75, 230, 255),     # Purple
        "accent": (255, 215, 35, 255),
        "has_shades": False,
        "has_chain": False,
    },
    "grey": {
        "name": "Abu-Abu (Grey Tabby 🩶)",
        "fur_main": (160, 170, 182, 255),
        "fur_shade": (105, 115, 128, 255),
        "fur_belly": (238, 242, 248, 255),
        "inner_ear": (255, 168, 188, 255),
        "outline": (36, 42, 52, 255),
        "eye_iris": (52, 148, 235, 255),
        "collar": (255, 185, 20, 255),
        "accent": (255, 230, 80, 255),
        "has_shades": False,
        "has_chain": False,
    },
}

_CACHE: Dict[Tuple[str, str, int, int, int], Image.Image] = {}


# ─── 1. FRONT-FACING IDLE (BREATHING + EYE FOLLOW) ──────────────────────────
def _draw_idle_front(p: dict, frame_idx: int, look_dx: int = 0, look_dy: int = 0) -> Image.Image:
    """
    Chubby front-facing cat with subtle breathing expansion, tail wagging,
    and pupil offset tracking the mouse cursor vector (look_dx, look_dy).
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    K = p["outline"]
    E = p["inner_ear"]

    # Breathing height offset
    breath_y = -1 if frame_idx == 1 else 0

    # Tail sway
    tail_dir = 1 if frame_idx in (1, 2) else 0
    if tail_dir == 1:
        d.line([(24, 25 + breath_y), (27, 22 + breath_y), (27, 17 + breath_y), (25, 15 + breath_y)], fill=O, width=2)
        d.line([(25, 26 + breath_y), (28, 22 + breath_y), (28, 17 + breath_y), (25, 14 + breath_y)], fill=K)
    else:
        d.line([(24, 25 + breath_y), (28, 24 + breath_y), (29, 21 + breath_y), (28, 19 + breath_y)], fill=O, width=2)
        d.line([(24, 26 + breath_y), (29, 25 + breath_y), (30, 21 + breath_y), (29, 18 + breath_y)], fill=K)

    # Cat Body
    body_top = 17 + breath_y
    d.ellipse([7, body_top, 24, 28 + breath_y], fill=O, outline=K)
    d.ellipse([11, body_top + 1, 20, 27 + breath_y], fill=W)
    d.line([(7, body_top + 4), (10, body_top + 4)], fill=S)
    d.line([(21, body_top + 4), (24, body_top + 4)], fill=S)

    # Paws
    paw_y = 27 + breath_y
    d.rectangle([8, paw_y, 11, 29 + breath_y], fill=W, outline=K)
    d.rectangle([12, paw_y, 14, 29 + breath_y], fill=W, outline=K)
    d.rectangle([17, paw_y, 19, 29 + breath_y], fill=W, outline=K)
    d.rectangle([20, paw_y, 23, 29 + breath_y], fill=W, outline=K)

    # Head
    head_y = 6 + breath_y
    d.polygon([(7, head_y + 3), (7, head_y - 3), (12, head_y + 3)], fill=O, outline=K)
    d.polygon([(19, head_y + 3), (24, head_y - 3), (24, head_y + 3)], fill=O, outline=K)
    d.polygon([(8, head_y + 2), (8, head_y - 1), (11, head_y + 2)], fill=E)
    d.polygon([(20, head_y + 2), (23, head_y - 1), (23, head_y + 2)], fill=E)

    d.ellipse([6, head_y, 25, head_y + 12], fill=O, outline=K)
    d.line([(15, head_y + 1), (15, head_y + 3)], fill=S)
    d.line([(13, head_y + 2), (13, head_y + 4)], fill=S)
    d.line([(18, head_y + 2), (18, head_y + 4)], fill=S)

    # Muzzle
    d.ellipse([10, head_y + 6, 15, head_y + 10], fill=W)
    d.ellipse([16, head_y + 6, 21, head_y + 10], fill=W)
    img.putpixel((15, head_y + 6), (225, 75, 55, 255))
    img.putpixel((16, head_y + 6), (225, 75, 55, 255))
    d.line([(14, head_y + 8), (15, head_y + 7)], fill=K)
    d.line([(16, head_y + 7), (17, head_y + 8)], fill=K)

    # Eyes / Sunglasses
    if p.get("has_shades", False):
        d.rectangle([8, head_y + 3, 23, head_y + 6], fill=(18, 18, 22, 255), outline=K)
        img.putpixel((10, head_y + 4), (255, 255, 255, 255))
        img.putpixel((18, head_y + 4), (255, 255, 255, 255))
    else:
        px = max(-1, min(1, look_dx))
        py = max(-1, min(1, look_dy))

        if frame_idx == 3:
            d.line([(9, head_y + 5), (13, head_y + 5)], fill=K, width=2)
            d.line([(18, head_y + 5), (22, head_y + 5)], fill=K, width=2)
        else:
            d.ellipse([9, head_y + 3, 13, head_y + 7], fill=(255, 255, 255, 255), outline=K)
            d.ellipse([18, head_y + 3, 22, head_y + 7], fill=(255, 255, 255, 255), outline=K)
            iris = p.get("eye_iris", (46, 185, 95, 255))
            d.rectangle([10 + px, head_y + 4 + py, 12 + px, head_y + 6 + py], fill=iris)
            d.rectangle([19 + px, head_y + 4 + py, 21 + px, head_y + 6 + py], fill=iris)
            img.putpixel((11 + px, head_y + 5 + py), (20, 20, 20, 255))
            img.putpixel((20 + px, head_y + 5 + py), (20, 20, 20, 255))
            img.putpixel((10, head_y + 4), (255, 255, 255, 255))
            img.putpixel((19, head_y + 4), (255, 255, 255, 255))

    # Collar / Gold Chain
    if p.get("has_chain", False):
        chain_y = head_y + 11
        for cx in range(10, 22):
            cy = chain_y + (1 if cx in (14, 15, 16, 17) else 0)
            img.putpixel((cx, cy), p["collar"])
        img.putpixel((15, chain_y + 2), p["accent"])
        img.putpixel((16, chain_y + 2), p["accent"])
    elif p.get("collar"):
        chain_y = head_y + 11
        d.line([(10, chain_y), (21, chain_y)], fill=p["collar"], width=1)
        if p.get("accent"):
            img.putpixel((15, chain_y + 1), p["accent"])
            img.putpixel((16, chain_y + 1), p["accent"])

    return img


# ─── 2. FLUID 4-FRAME WALK CYCLE (SIDE PROFILE) ────────────────────────────
def _draw_walk_side(p: dict, frame_idx: int, flip_left: bool = False) -> Image.Image:
    """4-Frame walk gait with alternating 4 legs, body bobbing, and curved tail."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    K = p["outline"]
    E = p["inner_ear"]

    bob_y = 0 if frame_idx in (0, 2) else (-1 if frame_idx == 3 else 1)

    # Tail animation
    tail_sway = 1 if frame_idx in (1, 2) else 0
    d.line([(5, 18 + bob_y), (3, 14 + bob_y), (4, 9 + bob_y + tail_sway), (7, 7 + bob_y + tail_sway)], fill=O, width=2)
    d.line([(5, 19 + bob_y), (2, 14 + bob_y), (3, 8 + bob_y + tail_sway), (7, 6 + bob_y + tail_sway)], fill=K)

    # Legs (4 distinct gait phases)
    leg_y = 25 + bob_y
    if frame_idx == 0:
        d.rectangle([21, leg_y, 24, 29], fill=W, outline=K)
        d.rectangle([17, leg_y, 20, 28], fill=W, outline=K)
        d.rectangle([9, leg_y, 12, 29], fill=W, outline=K)
        d.rectangle([6, leg_y, 9, 28], fill=W, outline=K)
    elif frame_idx == 1:
        d.rectangle([22, leg_y, 25, 29], fill=W, outline=K)
        d.rectangle([16, leg_y - 1, 19, 27], fill=W, outline=K)
        d.rectangle([10, leg_y, 13, 29], fill=W, outline=K)
        d.rectangle([5, leg_y - 1, 8, 27], fill=W, outline=K)
    elif frame_idx == 2:
        d.rectangle([18, leg_y, 21, 29], fill=W, outline=K)
        d.rectangle([22, leg_y, 25, 28], fill=W, outline=K)
        d.rectangle([7, leg_y, 10, 29], fill=W, outline=K)
        d.rectangle([10, leg_y, 13, 28], fill=W, outline=K)
    else:
        d.rectangle([19, leg_y - 1, 22, 27], fill=W, outline=K)
        d.rectangle([23, leg_y, 26, 29], fill=W, outline=K)
        d.rectangle([8, leg_y - 1, 11, 27], fill=W, outline=K)
        d.rectangle([11, leg_y, 14, 29], fill=W, outline=K)

    # Torso
    d.ellipse([5, 14 + bob_y, 24, 26 + bob_y], fill=O, outline=K)
    d.line([(10, 15 + bob_y), (10, 20 + bob_y)], fill=S)
    d.line([(14, 15 + bob_y), (14, 20 + bob_y)], fill=S)
    d.line([(18, 15 + bob_y), (18, 20 + bob_y)], fill=S)
    d.ellipse([11, 21 + bob_y, 20, 26 + bob_y], fill=W)

    # Head
    head_y = 8 + bob_y
    d.polygon([(18, head_y), (21, head_y - 5), (24, head_y)], fill=O, outline=K)
    d.polygon([(24, head_y), (27, head_y - 5), (29, head_y)], fill=O, outline=K)
    img.putpixel((21, head_y - 2), E)
    img.putpixel((27, head_y - 2), E)

    d.ellipse([16, head_y, 30, head_y + 12], fill=O, outline=K)
    d.ellipse([24, head_y + 5, 30, head_y + 10], fill=W)
    img.putpixel((29, head_y + 5), (225, 75, 55, 255))

    if p.get("has_shades", False):
        d.rectangle([20, head_y + 3, 28, head_y + 6], fill=(18, 18, 22, 255), outline=K)
        img.putpixel((22, head_y + 4), (255, 255, 255, 255))
    else:
        d.ellipse([21, head_y + 3, 25, head_y + 7], fill=(255, 255, 255, 255), outline=K)
        d.rectangle([23, head_y + 4, 25, head_y + 6], fill=p.get("eye_iris", (46, 185, 95, 255)))
        img.putpixel((24, head_y + 5), (20, 20, 20, 255))
        img.putpixel((22, head_y + 4), (255, 255, 255, 255))

    if p.get("has_chain", False):
        d.line([(18, head_y + 11), (25, head_y + 11)], fill=p["collar"], width=1)
        img.putpixel((22, head_y + 12), p["accent"])
    elif p.get("collar"):
        d.line([(18, head_y + 11), (25, head_y + 11)], fill=p["collar"], width=1)

    if flip_left:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    return img


# ─── 3. KEYBOARD KNEADING (4-FRAME LAPTOP TYPING) ──────────────────────────
def _draw_knead_work(p: dict, frame_idx: int) -> Image.Image:
    """Cute 4-frame keyboard kneading on mini laptop with screen glow and paw tapping."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    K = p["outline"]
    E = p["inner_ear"]

    # Head
    d.ellipse([7, 6, 24, 17], fill=O, outline=K)
    d.polygon([(7, 6), (7, 1), (12, 6)], fill=O, outline=K)
    d.polygon([(19, 6), (24, 1), (24, 6)], fill=O, outline=K)
    img.putpixel((8, 4), E)
    img.putpixel((23, 4), E)

    if p.get("has_shades", False):
        d.rectangle([9, 8, 22, 11], fill=(18, 18, 22, 255), outline=K)
        glint_col = (72, 215, 120, 255) if frame_idx % 2 == 0 else (255, 255, 255, 255)
        img.putpixel((11, 9), glint_col)
        img.putpixel((18, 9), glint_col)
    else:
        d.line([(10, 10), (12, 8), (14, 10)], fill=K)
        d.line([(17, 10), (19, 8), (21, 10)], fill=K)

    d.ellipse([11, 11, 15, 15], fill=W)
    d.ellipse([16, 11, 20, 15], fill=W)
    img.putpixel((15, 11), (225, 75, 55, 255))

    d.ellipse([7, 16, 24, 27], fill=O, outline=K)
    d.ellipse([11, 17, 20, 25], fill=W)

    # Mini Laptop
    d.rectangle([5, 23, 26, 26], fill=(55, 60, 72, 255), outline=K)
    d.rectangle([8, 19, 23, 23], fill=(35, 38, 46, 255), outline=K)
    screen_cols = [(72, 215, 120, 255), (90, 235, 150, 255), (50, 180, 95, 255)]
    sc = screen_cols[frame_idx % len(screen_cols)]
    d.line([(9, 20), (15, 20)], fill=sc)
    d.line([(9, 21), (21, 21)], fill=sc)
    d.line([(9, 22), (18, 22)], fill=sc)

    # 4-Phase Paw Kneading
    if frame_idx == 0:
        d.rectangle([7, 23, 11, 25], fill=W, outline=K)
        d.rectangle([20, 21, 24, 23], fill=W, outline=K)
    elif frame_idx == 1:
        d.rectangle([8, 22, 12, 24], fill=W, outline=K)
        d.rectangle([19, 22, 23, 24], fill=W, outline=K)
    elif frame_idx == 2:
        d.rectangle([7, 21, 11, 23], fill=W, outline=K)
        d.rectangle([20, 23, 24, 25], fill=W, outline=K)
    else:
        d.rectangle([8, 22, 12, 24], fill=W, outline=K)
        d.rectangle([19, 22, 23, 24], fill=W, outline=K)

    return img


# ─── 4. OVERHEAT MODE (STEAM PUFFS + FLUSHED FACE + FRANTIC TYPING) ─────────
def _draw_overheat(p: dict, frame_idx: int) -> Image.Image:
    """
    Overheat mode triggered by typing super fast (>75 WPM):
    Flushed red face, frantic typing, glowing fiery laptop, and animated rising steam puffs!
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Flushed Red Warm Tone
    O_hot = (255, 95, 75, 255)
    W = p["fur_belly"]
    K = p["outline"]

    # ── Rising Steam Clouds (Puffing upward across frames) ──
    steam_col = (235, 240, 255, 220)
    steam_shade = (195, 210, 235, 180)

    # Animated steam puffs on top of head
    sy = -1 * (frame_idx % 4)
    # Left puff
    d.ellipse([7, 2 + sy, 12, 6 + sy], fill=steam_col)
    d.ellipse([8, 1 + sy, 11, 4 + sy], fill=steam_shade)
    # Right puff
    d.ellipse([19, 1 + sy, 24, 5 + sy], fill=steam_col)
    d.ellipse([20, 0 + sy, 23, 3 + sy], fill=steam_shade)

    # Sweat Droplet on Cheek (animating down)
    sweat_col = (110, 200, 255, 255)
    sw_y = 10 + (frame_idx % 3)
    img.putpixel((25, sw_y), sweat_col)
    img.putpixel((25, sw_y + 1), sweat_col)

    # Cat Head (Red Flushed)
    d.ellipse([7, 6, 24, 17], fill=O_hot, outline=K)
    d.polygon([(7, 6), (7, 1), (12, 6)], fill=O_hot, outline=K)
    d.polygon([(19, 6), (24, 1), (24, 6)], fill=O_hot, outline=K)

    # Frantic Face: (> <) or Red Fiery Sunglasses
    if p.get("has_shades", False):
        d.rectangle([9, 8, 22, 11], fill=(25, 15, 20, 255), outline=K)
        # Red hot laser reflection
        fire_col = (255, 60, 40, 255) if frame_idx % 2 == 0 else (255, 200, 50, 255)
        img.putpixel((11, 9), fire_col)
        img.putpixel((18, 9), fire_col)
    else:
        # Panicked closed eyes (> <)
        d.line([(10, 8), (13, 10), (10, 12)], fill=K)
        d.line([(21, 8), (18, 10), (21, 12)], fill=K)

    # Hot red blushing cheeks
    d.rectangle([8, 13, 11, 14], fill=(255, 45, 65, 240))
    d.rectangle([20, 13, 23, 14], fill=(255, 45, 65, 240))

    # Muzzle
    d.ellipse([11, 11, 15, 15], fill=W)
    d.ellipse([16, 11, 20, 15], fill=W)
    img.putpixel((15, 11), (230, 50, 60, 255))

    # Body
    d.ellipse([7, 16, 24, 27], fill=O_hot, outline=K)
    d.ellipse([11, 17, 20, 25], fill=W)

    # Steaming Red Hot Laptop
    d.rectangle([5, 23, 26, 26], fill=(80, 45, 45, 255), outline=K)
    d.rectangle([8, 19, 23, 23], fill=(50, 25, 25, 255), outline=K)
    # Fire red glowing screen
    d.line([(9, 20), (21, 20)], fill=(255, 80, 50, 255))
    d.line([(9, 21), (18, 21)], fill=(255, 210, 60, 255))
    d.line([(9, 22), (21, 22)], fill=(255, 60, 40, 255))

    # Frantic Blazing Paws
    if frame_idx % 2 == 0:
        d.rectangle([6, 23, 11, 25], fill=W, outline=K)
        d.rectangle([20, 20, 25, 23], fill=W, outline=K)
    else:
        d.rectangle([6, 20, 11, 23], fill=W, outline=K)
        d.rectangle([20, 23, 25, 25], fill=W, outline=K)

    return img


# ─── 5. PAPER UNROLL (SCROLL REACTION — TOILET PAPER ROLL FRENZY) ───────────
def _draw_paper_unroll(p: dict, frame_idx: int) -> Image.Image:
    """
    Comnyang Feature #10: Toilet Paper Frenzy!
    When user scrolls pages, cat vigorously claws and unrolls a 3D toilet paper roll,
    unspooling a trailing perforated paper sheet across the floor with flying paper bits!
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    W = p["fur_belly"]
    K = p["outline"]
    E = p["inner_ear"]

    T_white = (252, 254, 255, 255)
    T_shade = (210, 218, 230, 255)
    T_line = (185, 195, 210, 255)
    Core_brown = (145, 115, 90, 255)

    # 1. Cat Body sitting behind
    d.ellipse([10, 12, 27, 27], fill=O, outline=K)
    d.ellipse([14, 14, 22, 25], fill=W)

    # 2. Cat Head (Playful focused look tilted forward)
    head_y = 5
    d.polygon([(11, head_y + 3), (10, head_y - 2), (15, head_y + 3)], fill=O, outline=K)
    d.polygon([(21, head_y + 3), (25, head_y - 2), (25, head_y + 3)], fill=O, outline=K)
    img.putpixel((11, head_y + 1), E)
    img.putpixel((24, head_y + 1), E)

    d.ellipse([9, head_y, 27, head_y + 12], fill=O, outline=K)
    d.ellipse([13, head_y + 6, 18, head_y + 10], fill=W)
    d.ellipse([18, head_y + 6, 23, head_y + 10], fill=W)
    img.putpixel((18, head_y + 6), (225, 75, 55, 255))

    # Eyes or Sunglasses
    if p.get("has_shades", False):
        d.rectangle([11, head_y + 3, 25, head_y + 7], fill=(18, 18, 22, 255), outline=K)
        img.putpixel((13, head_y + 4), (255, 255, 255, 255))
        img.putpixel((21, head_y + 4), (255, 255, 255, 255))
    else:
        # Excited wide eyes looking down at toilet paper roll (* w *)
        d.ellipse([12, head_y + 3, 16, head_y + 7], fill=(255, 255, 255, 255), outline=K)
        d.ellipse([20, head_y + 3, 24, head_y + 7], fill=(255, 255, 255, 255), outline=K)
        img.putpixel((13, head_y + 5), (20, 20, 20, 255))
        img.putpixel((21, head_y + 5), (20, 20, 20, 255))

    # 3. Big Iconic Toilet Paper Roll (Placed Higher Up next to head/chest at y = 9)
    roll_x, roll_y = 3, 9
    # Cylinder side body
    d.rectangle([roll_x + 2, roll_y + 2, roll_x + 11, roll_y + 15], fill=T_white, outline=K)
    # Bottom round edge
    d.ellipse([roll_x + 2, roll_y + 11, roll_x + 11, roll_y + 16], fill=T_shade, outline=K)
    # Top round cap
    d.ellipse([roll_x + 2, roll_y - 1, roll_x + 11, roll_y + 5], fill=T_white, outline=K)
    # Brown cardboard core hole
    d.ellipse([roll_x + 5, roll_y + 1, roll_x + 9, roll_y + 4], fill=Core_brown, outline=K)

    # 4. Trailing Unspooling Toilet Paper Sheet (Cascades down from roll to floor)
    wave = (frame_idx % 4)
    sheet_pts = [
        (roll_x + 10, roll_y + 3),
        (roll_x + 16, roll_y + 9 + (1 if wave in (1, 2) else 0)),
        (roll_x + 23, roll_y + 15 - (1 if wave in (2, 3) else 0)),
        (roll_x + 28, roll_y + 19),
        (roll_x + 27, roll_y + 22),
        (roll_x + 20, roll_y + 19),
        (roll_x + 14, roll_y + 13),
        (roll_x + 10, roll_y + 7)
    ]
    d.polygon(sheet_pts, fill=T_white, outline=K)

    # Perforation lines on paper sheets
    if wave % 2 == 0:
        d.line([(roll_x + 16, roll_y + 10), (roll_x + 15, roll_y + 14)], fill=T_line)
        d.line([(roll_x + 23, roll_y + 16), (roll_x + 22, roll_y + 20)], fill=T_line)

    # Flying paper shreds
    if frame_idx in (1, 2):
        img.putpixel((roll_x + 13, roll_y - 1), T_white)
        img.putpixel((roll_x + 19, roll_y + 4), T_white)
    elif frame_idx == 3:
        img.putpixel((roll_x + 16, roll_y), T_white)
        img.putpixel((roll_x + 24, roll_y + 12), T_white)

    # 5. Paw Clawing Animations (Reaching up and clawing down)
    if frame_idx == 0:
        d.rectangle([roll_x + 5, roll_y + 4, roll_x + 9, roll_y + 7], fill=W, outline=K)
        d.line([(roll_x + 6, roll_y + 7), (roll_x + 8, roll_y + 7)], fill=K)
        d.rectangle([roll_x + 11, roll_y, roll_x + 15, roll_y + 3], fill=W, outline=K)
    elif frame_idx == 1:
        d.rectangle([roll_x + 6, roll_y + 6, roll_x + 10, roll_y + 9], fill=W, outline=K)
        d.rectangle([roll_x + 10, roll_y + 3, roll_x + 14, roll_y + 6], fill=W, outline=K)
    elif frame_idx == 2:
        d.rectangle([roll_x + 6, roll_y, roll_x + 10, roll_y + 3], fill=W, outline=K)
        d.rectangle([roll_x + 10, roll_y + 4, roll_x + 14, roll_y + 7], fill=W, outline=K)
        d.line([(roll_x + 11, roll_y + 7), (roll_x + 13, roll_y + 7)], fill=K)
    else:
        d.rectangle([roll_x + 7, roll_y + 3, roll_x + 11, roll_y + 6], fill=W, outline=K)
        d.rectangle([roll_x + 9, roll_y + 6, roll_x + 13, roll_y + 9], fill=W, outline=K)

    return img


# ─── 6. PURRING & PETTING ──────────────────────────────────────────────────
def _draw_pet_purr(p: dict, frame_idx: int) -> Image.Image:
    """Cute purring reaction with blushing cheeks, smiling eyes, and rising hearts."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    W = p["fur_belly"]
    K = p["outline"]

    d.ellipse([6, 17, 25, 28], fill=O, outline=K)
    d.ellipse([11, 18, 20, 26], fill=W)
    d.rectangle([8, 27, 12, 29], fill=W, outline=K)
    d.rectangle([19, 27, 23, 29], fill=W, outline=K)

    d.ellipse([5, 8, 26, 18], fill=O, outline=K)
    d.polygon([(6, 9), (4, 6), (10, 9)], fill=O, outline=K)
    d.polygon([(21, 9), (27, 6), (25, 9)], fill=O, outline=K)

    d.line([(9, 12), (11, 10), (13, 12)], fill=K, width=2)
    d.line([(18, 12), (20, 10), (22, 12)], fill=K, width=2)

    d.rectangle([8, 14, 11, 15], fill=(255, 130, 160, 240))
    d.rectangle([20, 14, 23, 15], fill=(255, 130, 160, 240))

    d.ellipse([11, 12, 15, 16], fill=W)
    d.ellipse([16, 12, 20, 16], fill=W)
    img.putpixel((15, 12), (225, 75, 55, 255))

    heart_y = max(1, 7 - frame_idx * 2)
    heart_x = 22 + (frame_idx % 2)
    heart_col = (255, 60, 110, 255)
    d.rectangle([heart_x, heart_y + 1, heart_x + 3, heart_y + 2], fill=heart_col)
    img.putpixel((heart_x, heart_y), heart_col)
    img.putpixel((heart_x + 2, heart_y), heart_col)
    img.putpixel((heart_x + 1, heart_y + 3), heart_col)

    return img


# ─── 7. SLEEPING LOAF ──────────────────────────────────────────────────────
def _draw_sleep_loaf(p: dict, frame_idx: int) -> Image.Image:
    """Cozy curled loaf sleeping pose with animated floating Zzz."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    K = p["outline"]

    by = -1 if frame_idx in (1, 2) else 0

    d.ellipse([4, 16 + by, 27, 28 + by], fill=O, outline=K)
    d.line([(10, 17 + by), (10, 23 + by)], fill=S)
    d.line([(15, 17 + by), (15, 23 + by)], fill=S)
    d.line([(20, 17 + by), (20, 23 + by)], fill=S)
    d.arc([20, 18 + by, 29, 26 + by], 270, 90, fill=O, width=2)

    d.ellipse([4, 14 + by, 17, 25 + by], fill=O, outline=K)
    d.polygon([(5, 14 + by), (5, 10 + by), (9, 14 + by)], fill=O, outline=K)
    d.polygon([(12, 14 + by), (16, 10 + by), (16, 14 + by)], fill=O, outline=K)

    d.line([(7, 19 + by), (10, 19 + by)], fill=K)
    d.line([(12, 19 + by), (15, 19 + by)], fill=K)

    z_col = (130, 180, 255, 240)
    z_offset = (frame_idx % 4)
    d.text((18 + z_offset, 10 - z_offset), "z", fill=z_col)
    if frame_idx >= 2:
        d.text((23 + z_offset, 5 - z_offset), "Z", fill=z_col)

    return img


# ─── 8. MOCHI DRAG & DANGLING ──────────────────────────────────────────────
def _draw_mochi_drag(p: dict, frame_idx: int) -> Image.Image:
    """Elongated dangling cat with swinging paws when dragged."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    W = p["fur_belly"]
    K = p["outline"]

    d.polygon([(14, 2), (16, 0), (18, 2)], fill=K)
    d.ellipse([9, 2, 22, 13], fill=O, outline=K)
    d.polygon([(9, 3), (9, 0), (12, 3)], fill=O, outline=K)
    d.polygon([(19, 3), (22, 0), (22, 3)], fill=O, outline=K)

    if p.get("has_shades", False):
        d.rectangle([10, 5, 21, 8], fill=(18, 18, 22, 255), outline=K)
        img.putpixel((12, 6), (255, 255, 255, 255))
    else:
        d.ellipse([11, 5, 14, 8], fill=(255, 255, 255, 255), outline=K)
        d.ellipse([17, 5, 20, 8], fill=(255, 255, 255, 255), outline=K)
        img.putpixel((12, 6), (20, 20, 20, 255))
        img.putpixel((18, 6), (20, 20, 20, 255))

    d.ellipse([10, 12, 21, 26], fill=O, outline=K)
    d.ellipse([12, 13, 19, 24], fill=W)

    paw_swing = -1 if frame_idx in (0, 1) else 1
    d.rectangle([8 + paw_swing, 26, 12 + paw_swing, 30], fill=W, outline=K)
    d.rectangle([19 - paw_swing, 26, 23 - paw_swing, 30], fill=W, outline=K)

    return img


# ─── 9. CELEBRATE / JUMP ───────────────────────────────────────────────────
def _draw_celebrate_jump(p: dict, frame_idx: int) -> Image.Image:
    """Jumping high in the air with open paws and star sparkles."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    W = p["fur_belly"]
    K = p["outline"]

    d.ellipse([8, 5, 23, 18], fill=O, outline=K)
    d.polygon([(8, 5), (8, 1), (12, 5)], fill=O, outline=K)
    d.polygon([(19, 5), (23, 1), (23, 5)], fill=O, outline=K)

    d.line([(10, 9), (12, 11), (14, 9)], fill=K, width=2)
    d.line([(17, 9), (19, 11), (21, 9)], fill=K, width=2)

    d.ellipse([12, 12, 19, 16], fill=W)
    img.putpixel((15, 14), (240, 70, 90, 255))

    d.ellipse([9, 16, 22, 24], fill=O, outline=K)
    d.rectangle([4, 11, 8, 15], fill=W, outline=K)
    d.rectangle([23, 11, 27, 15], fill=W, outline=K)
    d.rectangle([8, 24, 12, 27], fill=W, outline=K)
    d.rectangle([19, 24, 23, 27], fill=W, outline=K)

    star_col = (255, 225, 50, 255)
    d.line([(3, 4), (5, 4)], fill=star_col)
    d.line([(4, 3), (4, 5)], fill=star_col)
    d.line([(26, 5), (28, 5)], fill=star_col)
    d.line([(27, 4), (27, 6)], fill=star_col)

    return img


# ─── 10. THINKING ──────────────────────────────────────────────────────────
def _draw_thinking(p: dict, frame_idx: int) -> Image.Image:
    """Curious tilted head with 3 animated floating dots."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    W = p["fur_belly"]
    K = p["outline"]

    d.ellipse([7, 17, 24, 28], fill=O, outline=K)
    d.ellipse([11, 18, 20, 26], fill=W)
    d.rectangle([9, 27, 13, 29], fill=W, outline=K)
    d.rectangle([18, 27, 22, 29], fill=W, outline=K)

    d.ellipse([8, 7, 25, 18], fill=O, outline=K)
    d.polygon([(8, 7), (8, 2), (13, 7)], fill=O, outline=K)
    d.polygon([(19, 8), (24, 4), (25, 9)], fill=O, outline=K)

    d.ellipse([11, 10, 14, 13], fill=(255, 255, 255, 255), outline=K)
    d.ellipse([18, 10, 21, 13], fill=(255, 255, 255, 255), outline=K)
    img.putpixel((12, 10), (20, 20, 20, 255))
    img.putpixel((19, 10), (20, 20, 20, 255))

    d.ellipse([12, 13, 16, 16], fill=W)
    d.ellipse([16, 13, 20, 16], fill=W)
    img.putpixel((16, 13), (225, 75, 55, 255))

    dot_count = (frame_idx % 3) + 1
    dot_col = (90, 160, 255, 255)
    for i in range(dot_count):
        d.rectangle([21 + i * 3, 2, 22 + i * 3, 3], fill=dot_col)

    return img


# ─── MAIN FRAME DISPATCHER (PUBLIC API) ────────────────────────────────────
def render_cat_frame(skin_key: str = "boss_oyen",
                     state: str = "idle",
                     frame_idx: int = 0,
                     look_dx: int = 0,
                     look_dy: int = 0) -> Image.Image:
    """
    Return a 128x128 RGBA PIL Image for the given skin / state / frame.
    Supports nearest-neighbor 4x scaling (32x32 -> 128x128) with dynamic eye follow.
    """
    global _CACHE
    cache_key = (skin_key, state, frame_idx % 4, look_dx, look_dy)
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    p = PALETTES.get(skin_key, PALETTES["boss_oyen"])
    fi = frame_idx % 4

    # Generate native 32x32 frame based on state
    if state in ("walk_left", "run_W"):
        native = _draw_walk_side(p, fi, flip_left=True)
    elif state in ("walk_right", "run_E", "walk"):
        native = _draw_walk_side(p, fi, flip_left=False)
    elif state in ("work", "knead", "typing"):
        native = _draw_knead_work(p, fi)
    elif state in ("overheat", "heat", "hot"):
        native = _draw_overheat(p, fi)
    elif state in ("paper_unroll", "scroll", "paper"):
        native = _draw_paper_unroll(p, fi)
    elif state in ("pet", "purr", "happy"):
        native = _draw_pet_purr(p, fi)
    elif state == "sleep":
        native = _draw_sleep_loaf(p, fi)
    elif state in ("drag", "dangle", "mochi"):
        native = _draw_mochi_drag(p, fi)
    elif state in ("celebrate", "jump", "done"):
        native = _draw_celebrate_jump(p, fi)
    elif state in ("thinking", "alert"):
        native = _draw_thinking(p, fi)
    else:
        native = _draw_idle_front(p, fi, look_dx=look_dx, look_dy=look_dy)

    # Scale 4x nearest-neighbor to crisp 128x128
    scaled = native.resize((128, 128), Image.Resampling.NEAREST)
    _CACHE[cache_key] = scaled
    return scaled


def pregenerate_all_sprites(output_dir: str = "assets/sprites") -> None:
    """Pre-generate all sprite frames to disk."""
    os.makedirs(output_dir, exist_ok=True)
    states = [
        "idle", "walk_left", "walk_right", "work", "overheat",
        "paper_unroll", "pet", "sleep", "drag", "celebrate", "thinking"
    ]
    for skin in PALETTES:
        skin_dir = os.path.join(output_dir, skin)
        os.makedirs(skin_dir, exist_ok=True)
        for state in states:
            for fi in range(4):
                img = render_cat_frame(skin, state, fi)
                img.save(os.path.join(skin_dir, f"{state}_{fi}.png"))
    print(f"[SpriteEngine] Pregenerated modern 4-frame sprites (Phase 2 included) for {len(PALETTES)} skins.")


if __name__ == "__main__":
    pregenerate_all_sprites()
