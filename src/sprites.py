"""
NyangBuddy Modern Pixel-Art Sprite Engine — 4-Frame Fluid Edition
High-framerate 32x32 kawaii chubby pixel cat with 4-frame walk cycles,
breathing idles, dynamic 8-direction eye follow, keyboard kneading on 3D mechanical keycaps,
overheat steam mode, official Comnyang paper unroll scroll reaction, petting/purr reactions,
and mochi drag with sleek lower flank animated tail.
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


# ─── 3. KEYBOARD KNEADING (3D MECHANICAL KEYCAPS STEPPING) ─────────────────
def _draw_knead_work(p: dict, frame_idx: int) -> Image.Image:
    """
    Comnyang Official Typing Animation:
    Cat stepping and kneading on 2 giant 3D mechanical keyboard keycaps,
    with alternating left/right keypress bevel depths, white ring eyes, whiskers, and curled tail!
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    K = (18, 18, 22, 255)
    E = p["inner_ear"]

    # Keycap Palette
    K_TOP = (185, 188, 198, 255)       # Top face light grey
    K_LIGHT = (235, 238, 248, 255)     # Highlight rim
    K_SIDE = (118, 122, 134, 255)      # Bevel shadow
    K_DARK = (78, 82, 94, 255)         # Deep shadow

    # Keycap stepping offsets (2 pixels dip on press)
    if frame_idx == 0:
        l_y, r_y = 21, 17
    elif frame_idx == 1:
        l_y, r_y = 19, 19
    elif frame_idx == 2:
        l_y, r_y = 17, 21
    else:
        l_y, r_y = 19, 19

    body_bob = -1 if frame_idx in (0, 2) else 0

    # ── 1. Tail (Pointed up on the right side) ──
    t_bob = 1 if frame_idx in (1, 2) else 0
    d.polygon([(23, 16), (26, 14 - t_bob), (27, 10 - t_bob), (25, 9 - t_bob), (24, 13), (22, 16)], fill=O, outline=K)
    d.line([(25, 12 - t_bob), (27, 12 - t_bob)], fill=S)

    # ── 2. Back Body & Hind Feet ──
    d.ellipse([9, 9 + body_bob, 25, 21 + body_bob], fill=O, outline=K)
    d.rectangle([21, 18 + body_bob, 24, 22 + body_bob], fill=O, outline=K)
    d.rectangle([21, 21 + body_bob, 24, 23 + body_bob], fill=W, outline=K)

    # ── 3. Giant 3D Mechanical Keycaps ──
    # Left Keycap
    d.polygon([(4, l_y), (13, l_y), (11, l_y + 5), (2, l_y + 5)], fill=K_TOP, outline=K)
    d.line([(4, l_y), (13, l_y)], fill=K_LIGHT)
    d.polygon([(2, l_y + 5), (2, l_y + 8), (11, l_y + 8), (11, l_y + 5)], fill=K_SIDE, outline=K)
    d.polygon([(11, l_y + 5), (11, l_y + 8), (13, l_y + 7), (13, l_y)], fill=K_DARK, outline=K)

    # Right Keycap
    d.polygon([(16, r_y), (25, r_y), (23, r_y + 5), (14, r_y + 5)], fill=K_TOP, outline=K)
    d.line([(16, r_y), (25, r_y)], fill=K_LIGHT)
    d.polygon([(14, r_y + 5), (14, r_y + 8), (23, r_y + 8), (23, r_y + 5)], fill=K_SIDE, outline=K)
    d.polygon([(23, r_y + 5), (23, r_y + 8), (25, r_y + 7), (25, r_y)], fill=K_DARK, outline=K)

    # ── 4. Front Stepping Legs & Paws ──
    d.polygon([(7, 12 + body_bob), (6, l_y), (10, l_y), (11, 12 + body_bob)], fill=O, outline=K)
    d.rectangle([6, l_y, 10, l_y + 2], fill=W, outline=K)

    d.polygon([(15, 12 + body_bob), (15, r_y), (19, r_y), (19, 12 + body_bob)], fill=O, outline=K)
    d.rectangle([15, r_y, 19, r_y + 2], fill=W, outline=K)

    # ── 5. Cat Head & Ears ──
    head_y = 3 + body_bob
    d.polygon([(8, head_y + 4), (8, head_y - 2), (13, head_y + 4)], fill=O, outline=K)
    d.polygon([(9, head_y + 3), (9, head_y), (12, head_y + 3)], fill=E)
    d.polygon([(16, head_y + 4), (20, head_y - 2), (21, head_y + 4)], fill=O, outline=K)
    d.polygon([(17, head_y + 3), (20, head_y), (20, head_y + 3)], fill=E)

    d.ellipse([7, head_y + 1, 23, head_y + 12], fill=O, outline=K)
    d.line([(15, head_y + 2), (15, head_y + 4)], fill=S)
    d.line([(12, head_y + 3), (13, head_y + 5)], fill=S)
    d.line([(18, head_y + 3), (17, head_y + 5)], fill=S)

    # Whiskers on left cheek
    d.line([(6, head_y + 7), (2, head_y + 7)], fill=K)
    d.line([(6, head_y + 9), (2, head_y + 9)], fill=K)

    # Eyes: Exact Comnyang White Square Rings 'O O'
    if p.get("has_shades", False):
        d.rectangle([9, head_y + 4, 21, head_y + 7], fill=(18, 18, 22, 255), outline=K)
        img.putpixel((11, head_y + 5), (255, 255, 255, 255))
        img.putpixel((18, head_y + 5), (255, 255, 255, 255))
    else:
        d.rectangle([9, head_y + 4, 12, head_y + 7], outline=(255, 255, 255, 255), fill=None)
        d.rectangle([15, head_y + 4, 18, head_y + 7], outline=(255, 255, 255, 255), fill=None)

    return img


# ─── 4. OVERHEAT MODE (STEAM PUFFS + STEAMING KEYCAPS) ──────────────────────
def _draw_overheat(p: dict, frame_idx: int) -> Image.Image:
    """
    Overheat mode:
    Cat frantically stepping on blazing hot red keycaps with rising steam clouds & sweat!
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O_hot = (255, 95, 75, 255)
    W = p["fur_belly"]
    K = (18, 18, 22, 255)

    # Blazing Keycap Colors
    K_TOP = (255, 130, 110, 255)
    K_LIGHT = (255, 220, 200, 255)
    K_SIDE = (180, 60, 50, 255)
    K_DARK = (120, 30, 25, 255)

    # Rapid keycap dip
    if frame_idx % 2 == 0:
        l_y, r_y = 21, 17
    else:
        l_y, r_y = 17, 21

    body_bob = -1 if frame_idx in (0, 2) else 0

    # ── Rising Steam Clouds (Puffing upward) ──
    steam_col = (235, 240, 255, 220)
    steam_shade = (195, 210, 235, 180)
    sy = -1 * (frame_idx % 4)
    d.ellipse([7, 1 + sy, 12, 5 + sy], fill=steam_col)
    d.ellipse([18, 0 + sy, 23, 4 + sy], fill=steam_col)

    # Sweat Droplet
    sweat_col = (110, 200, 255, 255)
    d.line([(24, 7 + (frame_idx % 3)), (24, 9 + (frame_idx % 3))], fill=sweat_col)

    # Tail
    d.polygon([(23, 16), (26, 14), (27, 10), (25, 9), (24, 13), (22, 16)], fill=O_hot, outline=K)

    # Body
    d.ellipse([9, 9 + body_bob, 25, 21 + body_bob], fill=O_hot, outline=K)
    d.rectangle([21, 18 + body_bob, 24, 22 + body_bob], fill=O_hot, outline=K)

    # Blazing Red Keycaps
    d.polygon([(4, l_y), (13, l_y), (11, l_y + 5), (2, l_y + 5)], fill=K_TOP, outline=K)
    d.line([(4, l_y), (13, l_y)], fill=K_LIGHT)
    d.polygon([(2, l_y + 5), (2, l_y + 8), (11, l_y + 8), (11, l_y + 5)], fill=K_SIDE, outline=K)
    d.polygon([(11, l_y + 5), (11, l_y + 8), (13, l_y + 7), (13, l_y)], fill=K_DARK, outline=K)

    d.polygon([(16, r_y), (25, r_y), (23, r_y + 5), (14, r_y + 5)], fill=K_TOP, outline=K)
    d.line([(16, r_y), (25, r_y)], fill=K_LIGHT)
    d.polygon([(14, r_y + 5), (14, r_y + 8), (23, r_y + 8), (23, r_y + 5)], fill=K_SIDE, outline=K)
    d.polygon([(23, r_y + 5), (23, r_y + 8), (25, r_y + 7), (25, r_y)], fill=K_DARK, outline=K)

    # Legs & Paws
    d.polygon([(7, 12 + body_bob), (6, l_y), (10, l_y), (11, 12 + body_bob)], fill=O_hot, outline=K)
    d.rectangle([6, l_y, 10, l_y + 2], fill=W, outline=K)

    d.polygon([(15, 12 + body_bob), (15, r_y), (19, r_y), (19, 12 + body_bob)], fill=O_hot, outline=K)
    d.rectangle([15, r_y, 19, r_y + 2], fill=W, outline=K)

    # Head
    head_y = 3 + body_bob
    d.polygon([(8, head_y + 4), (8, head_y - 2), (13, head_y + 4)], fill=O_hot, outline=K)
    d.polygon([(16, head_y + 4), (20, head_y - 2), (21, head_y + 4)], fill=O_hot, outline=K)

    d.ellipse([7, head_y + 1, 23, head_y + 12], fill=O_hot, outline=K)

    # Panicked Face
    if p.get("has_shades", False):
        d.rectangle([9, head_y + 4, 21, head_y + 7], fill=(25, 15, 20, 255), outline=K)
        fire_col = (255, 60, 40, 255) if frame_idx % 2 == 0 else (255, 200, 50, 255)
        img.putpixel((11, head_y + 5), fire_col)
        img.putpixel((18, head_y + 5), fire_col)
    else:
        d.line([(9, head_y + 4), (12, head_y + 6), (9, head_y + 8)], fill=K)
        d.line([(18, head_y + 4), (15, head_y + 6), (18, head_y + 8)], fill=K)

    return img


# ─── 5. PAPER UNROLL (SCROLL REACTION — OFFICIAL COMNYANG STANCE) ──────────
def _draw_paper_unroll(p: dict, frame_idx: int) -> Image.Image:
    """
    Comnyang Official Stance Feature #10:
    Standing upright cat with striped tail, wide whisker cheeks,
    spinning a 3D toilet paper roll mounted at shoulder level on the far left,
    with a straight vertical sheet unspooling downwards and rapid batting paws!
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    K = (18, 18, 22, 255)
    E = p["inner_ear"]
    P_WHITE = (228, 230, 236, 255)
    P_SHADE = (190, 195, 205, 255)
    P_CORE = (20, 20, 24, 255)

    # ── 1. Tail (Striped curled tail on right side) ──
    t_y = 1 if frame_idx in (1, 2) else 0
    d.polygon([(24, 24), (28, 22 - t_y), (28, 17 - t_y), (26, 16 - t_y), (25, 20), (23, 24)], fill=O, outline=K)
    d.line([(26, 19 - t_y), (28, 19 - t_y)], fill=S)
    d.line([(25, 22 - t_y), (27, 22 - t_y)], fill=S)

    # ── 2. Hind Feet & Body ──
    d.rectangle([13, 27, 18, 29], fill=W, outline=K)
    d.rectangle([20, 27, 25, 29], fill=W, outline=K)

    d.ellipse([11, 14, 26, 27], fill=O, outline=K)
    d.line([(12, 18), (14, 19)], fill=S)
    d.line([(12, 22), (14, 23)], fill=S)
    d.line([(25, 18), (23, 19)], fill=S)
    d.line([(25, 22), (23, 23)], fill=S)

    # White chest patch (Large V-shape)
    d.polygon([(18, 14), (13, 16), (15, 24), (22, 24), (24, 16)], fill=W)

    # ── 3. Head (Chibi with horizontal whisker cheeks) ──
    head_y = 3
    # Ears
    d.polygon([(12, head_y + 4), (12, head_y - 2), (17, head_y + 4)], fill=O, outline=K)
    d.polygon([(13, head_y + 3), (13, head_y), (16, head_y + 3)], fill=E)
    d.line([(13, head_y + 3), (15, head_y + 3)], fill=W)

    d.polygon([(21, head_y + 4), (26, head_y - 2), (26, head_y + 4)], fill=O, outline=K)
    d.polygon([(22, head_y + 3), (25, head_y), (25, head_y + 3)], fill=E)
    d.line([(23, head_y + 3), (25, head_y + 3)], fill=W)

    d.ellipse([10, head_y + 1, 27, head_y + 13], fill=O, outline=K)
    # Forehead Stripes
    d.line([(18, head_y + 2), (18, head_y + 5)], fill=S)
    d.line([(15, head_y + 3), (16, head_y + 5)], fill=S)
    d.line([(22, head_y + 3), (21, head_y + 5)], fill=S)

    # White Whisker Cheeks & Muzzle
    d.ellipse([13, head_y + 7, 24, head_y + 12], fill=W)
    d.polygon([(10, head_y + 7), (7, head_y + 8), (10, head_y + 9)], fill=W, outline=K)
    d.polygon([(27, head_y + 7), (30, head_y + 8), (27, head_y + 9)], fill=W, outline=K)

    img.putpixel((18, head_y + 7), (20, 20, 24, 255))
    d.line([(17, head_y + 9), (18, head_y + 8), (19, head_y + 9)], fill=K)

    # Eyes / Sunglasses
    if p.get("has_shades", False):
        d.rectangle([12, head_y + 4, 25, head_y + 7], fill=(18, 18, 22, 255), outline=K)
        img.putpixel((14, head_y + 5), (255, 255, 255, 255))
        img.putpixel((22, head_y + 5), (255, 255, 255, 255))
    else:
        d.rectangle([13, head_y + 4, 17, head_y + 7], fill=K)
        d.rectangle([20, head_y + 4, 24, head_y + 7], fill=K)
        img.putpixel((14, head_y + 5), (255, 255, 255, 255))
        img.putpixel((15, head_y + 5), (255, 255, 255, 255))
        img.putpixel((21, head_y + 5), (255, 255, 255, 255))
        img.putpixel((22, head_y + 5), (255, 255, 255, 255))
        iris = p.get("eye_iris", (45, 145, 235, 255))
        img.putpixel((15, head_y + 6), iris)
        img.putpixel((22, head_y + 6), iris)

    # ── 4. Iconic Toilet Paper Roll on Far Left (x: 1..9, y: 7..28) ──
    d.polygon([(1, 9), (3, 7), (6, 7), (7, 9), (7, 12), (5, 14), (2, 14), (1, 12)], fill=P_WHITE, outline=K)
    d.rectangle([3, 9, 4, 12], fill=P_CORE)

    d.polygon([(5, 7), (9, 7), (9, 11), (5, 11)], fill=P_WHITE)
    d.line([(5, 7), (9, 7)], fill=K)
    d.line([(5, 14), (6, 14)], fill=K)

    sheet_bottom = 28
    d.rectangle([4, 8, 9, sheet_bottom], fill=P_WHITE)
    d.line([(9, 7), (9, sheet_bottom)], fill=K)
    d.line([(4, 14), (4, sheet_bottom)], fill=K)
    d.line([(4, sheet_bottom), (9, sheet_bottom)], fill=K)

    if frame_idx % 2 == 0:
        d.line([(2, 17), (2, 21)], fill=K)
        d.line([(7, 13), (7, 17)], fill=P_SHADE)
    else:
        d.line([(2, 19), (2, 23)], fill=K)
        d.line([(10, 18), (10, 22)], fill=K)
        d.line([(7, 18), (7, 22)], fill=P_SHADE)

    # ── 5. Cat Paws (Clawing & Batting the Roll) ──
    if frame_idx == 0:
        d.rectangle([6, 11, 12, 15], fill=O, outline=K)
        d.rectangle([6, 13, 10, 16], fill=W, outline=K)
        d.rectangle([14, 14, 18, 17], fill=W, outline=K)
    elif frame_idx == 1:
        d.rectangle([7, 14, 12, 18], fill=O, outline=K)
        d.rectangle([6, 16, 10, 19], fill=W, outline=K)
        d.rectangle([12, 13, 16, 16], fill=W, outline=K)
    elif frame_idx == 2:
        d.rectangle([7, 10, 13, 14], fill=O, outline=K)
        d.rectangle([6, 12, 10, 15], fill=W, outline=K)
        d.rectangle([11, 16, 15, 19], fill=W, outline=K)
    else:
        d.rectangle([6, 12, 11, 15], fill=W, outline=K)
        d.rectangle([10, 14, 15, 17], fill=W, outline=K)

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


# ─── 8. MOCHI DRAG & DANGLING (SLEEK LOWER FLANK TAIL) ─────────────────────
def _draw_mochi_drag(p: dict, frame_idx: int) -> Image.Image:
    """Elongated dangling cat with swinging paws and sleek animated tail at lower flank."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    K = (18, 18, 22, 255)
    E = p["inner_ear"]

    # ── 1. Sleek Low Side-Curled Tail (Lower flank x: 19..27, y: 17..24) ──
    flick_y = [-1, 0, 1, 0][frame_idx % 4]
    tail_pts_outer = [
        (19, 23), (22, 24), (25, 24 + flick_y), (27, 22 + flick_y),
        (27, 18 + flick_y), (25, 17 + flick_y), (24, 18 + flick_y),
        (25, 20 + flick_y), (23, 22 + flick_y), (19, 21)
    ]
    d.polygon(tail_pts_outer, fill=O, outline=K)
    d.line([(22, 23), (24, 23 + flick_y)], fill=S)
    d.line([(25, 21 + flick_y), (26, 20 + flick_y)], fill=S)

    # ── 2. Dangling Head & Body ──
    d.polygon([(14, 2), (16, 0), (18, 2)], fill=K)
    d.ellipse([9, 2, 22, 13], fill=O, outline=K)
    d.polygon([(9, 3), (9, 0), (12, 3)], fill=O, outline=K)
    d.polygon([(19, 3), (22, 0), (22, 3)], fill=O, outline=K)
    img.putpixel((10, 2), E)
    img.putpixel((21, 2), E)

    if p.get("has_shades", False):
        d.rectangle([10, 5, 21, 8], fill=(18, 18, 22, 255), outline=K)
        img.putpixel((12, 6), (255, 255, 255, 255))
        img.putpixel((18, 6), (255, 255, 255, 255))
    else:
        d.ellipse([11, 5, 14, 8], fill=(255, 255, 255, 255), outline=K)
        d.ellipse([17, 5, 20, 8], fill=(255, 255, 255, 255), outline=K)
        img.putpixel((12, 6), (20, 20, 20, 255))
        img.putpixel((18, 6), (20, 20, 20, 255))

    d.ellipse([10, 12, 21, 26], fill=O, outline=K)
    d.ellipse([12, 13, 19, 24], fill=W)

    # ── 3. Dangling Front & Hind Paws ──
    paw_swing = -1 if frame_idx in (0, 1) else 1
    d.rectangle([8 + paw_swing, 26, 12 + paw_swing, 30], fill=W, outline=K)
    d.rectangle([19 - paw_swing, 26, 23 - paw_swing, 30], fill=W, outline=K)

    return img


# ─── 9. CELEBRATE / JUMP / AI AGENT DONE ──────────────────────────────────
def _draw_celebrate_jump(p: dict, frame_idx: int) -> Image.Image:
    """
    Dynamic 4-frame jumping celebrate animation:
    Frame 0: Crouch & squash prep.
    Frame 1: Upward launch stretch with sparkling particles.
    Frame 2: High apex victory pose with big sparkling stars & cheerful blush.
    Frame 3: Soft graceful descent landing.
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    E = p["inner_ear"]
    K = p["outline"]

    fi = frame_idx % 4

    # Star & sparkle colors
    star_gold = (255, 220, 50, 255)
    star_pink = (255, 150, 180, 255)
    star_cyan = (130, 220, 255, 255)

    if fi == 0:
        # ── Frame 0: Crouch & Prep (Squash) ──
        d.ellipse([6, 17, 26, 28], fill=O, outline=K)
        d.ellipse([10, 18, 22, 26], fill=W)
        d.rectangle([7, 26, 12, 29], fill=W, outline=K)
        d.rectangle([20, 26, 25, 29], fill=W, outline=K)

        d.line([(6, 23), (3, 22), (2, 19), (4, 17)], fill=K, width=3)
        d.line([(6, 23), (3, 22), (2, 19), (4, 17)], fill=O, width=1)

        d.ellipse([7, 10, 25, 20], fill=O, outline=K)
        d.polygon([(8, 10), (7, 5), (12, 10)], fill=O, outline=K)
        d.polygon([(8, 9), (8, 6), (11, 9)], fill=E)
        d.polygon([(20, 10), (25, 5), (24, 10)], fill=O, outline=K)
        d.polygon([(21, 9), (24, 6), (24, 9)], fill=E)

        if p.get("has_shades", False):
            d.rectangle([9, 12, 23, 15], fill=(20, 20, 26, 255), outline=K)
            img.putpixel((11, 13), (255, 255, 255, 255))
            img.putpixel((18, 13), (255, 255, 255, 255))
        else:
            d.line([(10, 13), (12, 12), (14, 13)], fill=K, width=2)
            d.line([(18, 13), (20, 12), (22, 13)], fill=K, width=2)

        d.ellipse([11, 14, 16, 17], fill=W)
        d.ellipse([16, 14, 21, 17], fill=W)
        img.putpixel((16, 14), (240, 70, 90, 255))

        img.putpixel((5, 28), (200, 200, 210, 255))
        img.putpixel((27, 28), (200, 200, 210, 255))

    elif fi == 1:
        # ── Frame 1: Launch Upward (Stretch) ──
        d.ellipse([9, 10, 23, 23], fill=O, outline=K)
        d.ellipse([12, 11, 20, 20], fill=W)

        d.line([(16, 23), (16, 28), (17, 30)], fill=K, width=3)
        d.line([(16, 23), (16, 28), (17, 30)], fill=O, width=1)

        d.rectangle([10, 23, 13, 27], fill=W, outline=K)
        d.rectangle([19, 23, 22, 27], fill=W, outline=K)

        d.ellipse([7, 3, 25, 13], fill=O, outline=K)
        d.polygon([(8, 3), (7, 0), (12, 3)], fill=O, outline=K)
        d.polygon([(8, 2), (8, 0), (11, 2)], fill=E)
        d.polygon([(20, 3), (25, 0), (24, 3)], fill=O, outline=K)
        d.polygon([(21, 2), (24, 0), (24, 2)], fill=E)

        d.rectangle([5, 8, 8, 12], fill=W, outline=K)
        d.rectangle([24, 8, 27, 12], fill=W, outline=K)

        if p.get("has_shades", False):
            d.rectangle([9, 5, 23, 8], fill=(20, 20, 26, 255), outline=K)
            img.putpixel((11, 6), (255, 255, 255, 255))
            img.putpixel((18, 6), (255, 255, 255, 255))
        else:
            d.ellipse([10, 5, 13, 8], fill=(255, 255, 255, 255), outline=K)
            d.ellipse([19, 5, 22, 8], fill=(255, 255, 255, 255), outline=K)
            img.putpixel((11, 6), (20, 20, 20, 255))
            img.putpixel((20, 6), (20, 20, 20, 255))

        d.ellipse([11, 7, 16, 10], fill=W)
        d.ellipse([16, 7, 21, 10], fill=W)
        img.putpixel((16, 7), (240, 70, 90, 255))
        img.putpixel((16, 9), (230, 40, 60, 255))

        img.putpixel((3, 6), star_gold)
        img.putpixel((28, 6), star_cyan)

    elif fi == 2:
        # ── Frame 2: Apex High Celebrate (Paws Spread & Big Stars) ──
        d.ellipse([8, 8, 24, 20], fill=O, outline=K)
        d.ellipse([11, 9, 21, 18], fill=W)

        d.rectangle([3, 4, 7, 8], fill=W, outline=K)
        d.rectangle([25, 4, 29, 8], fill=W, outline=K)

        d.rectangle([9, 20, 13, 24], fill=W, outline=K)
        d.rectangle([19, 20, 23, 24], fill=W, outline=K)

        d.line([(16, 20), (13, 23), (12, 26), (14, 28)], fill=K, width=3)
        d.line([(16, 20), (13, 23), (12, 26), (14, 28)], fill=O, width=1)

        d.ellipse([7, 2, 25, 12], fill=O, outline=K)
        d.polygon([(8, 2), (7, 0), (12, 2)], fill=O, outline=K)
        d.polygon([(8, 1), (8, 0), (11, 1)], fill=E)
        d.polygon([(20, 2), (25, 0), (24, 2)], fill=O, outline=K)
        d.polygon([(21, 1), (24, 0), (24, 1)], fill=E)

        if p.get("has_shades", False):
            d.rectangle([9, 4, 23, 7], fill=(20, 20, 26, 255), outline=K)
            img.putpixel((11, 5), (255, 255, 255, 255))
            img.putpixel((18, 5), (255, 255, 255, 255))
        else:
            d.line([(10, 5), (12, 4), (14, 5)], fill=K, width=2)
            d.line([(18, 5), (20, 4), (22, 5)], fill=K, width=2)

        d.ellipse([11, 6, 16, 9], fill=W)
        d.ellipse([16, 6, 21, 9], fill=W)
        img.putpixel((16, 6), (240, 70, 90, 255))
        d.ellipse([14, 8, 18, 11], fill=(235, 45, 75, 255))

        img.putpixel((8, 8), (255, 160, 180, 255))
        img.putpixel((24, 8), (255, 160, 180, 255))

        d.line([(1, 3), (3, 3)], fill=star_gold)
        d.line([(2, 2), (2, 4)], fill=star_gold)
        img.putpixel((2, 3), (255, 255, 255, 255))

        d.line([(28, 3), (30, 3)], fill=star_gold)
        d.line([(29, 2), (29, 4)], fill=star_gold)
        img.putpixel((29, 3), (255, 255, 255, 255))

        img.putpixel((6, 0), star_pink)
        img.putpixel((26, 0), star_cyan)

    else:
        # ── Frame 3: Soft Glide Landing ──
        d.ellipse([8, 12, 24, 23], fill=O, outline=K)
        d.ellipse([11, 13, 21, 21], fill=W)

        d.rectangle([5, 14, 9, 18], fill=W, outline=K)
        d.rectangle([23, 14, 27, 18], fill=W, outline=K)
        d.rectangle([8, 22, 12, 26], fill=W, outline=K)
        d.rectangle([20, 22, 24, 26], fill=W, outline=K)

        d.ellipse([7, 5, 25, 15], fill=O, outline=K)
        d.polygon([(8, 5), (7, 1), (12, 5)], fill=O, outline=K)
        d.polygon([(8, 4), (8, 2), (11, 4)], fill=E)
        d.polygon([(20, 5), (25, 1), (24, 5)], fill=O, outline=K)
        d.polygon([(21, 4), (24, 2), (24, 4)], fill=E)

        if p.get("has_shades", False):
            d.rectangle([9, 7, 23, 10], fill=(20, 20, 26, 255), outline=K)
            img.putpixel((11, 8), (255, 255, 255, 255))
            img.putpixel((18, 8), (255, 255, 255, 255))
        else:
            d.line([(10, 8), (12, 7), (14, 8)], fill=K, width=2)
            d.line([(18, 8), (20, 7), (22, 8)], fill=K, width=2)

        d.ellipse([11, 9, 16, 12], fill=W)
        d.ellipse([16, 9, 21, 12], fill=W)
        img.putpixel((16, 9), (240, 70, 90, 255))

        img.putpixel((2, 10), star_cyan)
        img.putpixel((30, 10), star_pink)

    return img


# ─── 10. THINKING / AI AGENT PROCESSING ───────────────────────────────────────
def _draw_thinking(p: dict, frame_idx: int) -> Image.Image:
    """
    Authentic Comnyang AI Thinking Sprite:
    Sitting upright with big round curious eyes [O O] and a retro floating
    thought box with animated cycling dots [. -> .. -> ... -> glowing ...]
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    E = p["inner_ear"]
    K = p["outline"]

    fi = frame_idx % 4
    bob_y = 1 if fi in (1, 2) else 0

    # 1. Body & Paws (Sitting upright neatly)
    d.ellipse([7, 16, 24, 28], fill=O, outline=K)
    d.ellipse([11, 17, 20, 26], fill=W)
    d.rectangle([9, 26, 13, 29], fill=W, outline=K)
    d.rectangle([18, 26, 22, 29], fill=W, outline=K)

    # 2. Tail with cute curl
    tail_pts = [(7, 24), (4, 21), (3, 17 + bob_y), (5, 14 + bob_y)]
    for i in range(len(tail_pts) - 1):
        d.line([tail_pts[i], tail_pts[i + 1]], fill=K, width=3)
    for i in range(len(tail_pts) - 1):
        d.line([tail_pts[i], tail_pts[i + 1]], fill=O, width=1)

    # 3. Head (Facing forward/upward with big round curious eyes)
    head_left = 7
    head_top = 7 + bob_y
    d.ellipse([head_left, head_top, head_left + 17, head_top + 11], fill=O, outline=K)

    # Pointy perky ears
    d.polygon([(head_left, head_top + 1), (head_left, head_top - 5), (head_left + 5, head_top + 1)], fill=O, outline=K)
    d.polygon([(head_left + 1, head_top), (head_left + 1, head_top - 3), (head_left + 4, head_top)], fill=E)

    d.polygon([(head_left + 12, head_top + 1), (head_left + 17, head_top - 5), (head_left + 17, head_top + 1)], fill=O, outline=K)
    d.polygon([(head_left + 13, head_top), (head_left + 16, head_top - 3), (head_left + 16, head_top)], fill=E)

    # Big round curious eyes [O O] matching reference panel 11
    if p.get("has_shades", False):
        d.rectangle([head_left + 2, head_top + 3, head_left + 15, head_top + 6], fill=(20, 20, 26, 255), outline=K)
        img.putpixel((head_left + 4, head_top + 4), (255, 255, 255, 255))
        img.putpixel((head_left + 12, head_top + 4), (255, 255, 255, 255))
    else:
        # Left eye
        d.rectangle([head_left + 3, head_top + 3, head_left + 6, head_top + 6], fill=(255, 255, 255, 255), outline=K)
        img.putpixel((head_left + 4, head_top + 4), (20, 20, 20, 255))
        img.putpixel((head_left + 5, head_top + 4), (20, 20, 20, 255))
        img.putpixel((head_left + 4, head_top + 3), (255, 255, 255, 255))

        # Right eye
        d.rectangle([head_left + 11, head_top + 3, head_left + 14, head_top + 6], fill=(255, 255, 255, 255), outline=K)
        img.putpixel((head_left + 12, head_top + 4), (20, 20, 20, 255))
        img.putpixel((head_left + 13, head_top + 4), (20, 20, 20, 255))
        img.putpixel((head_left + 12, head_top + 3), (255, 255, 255, 255))

    # White muzzle & tiny pink nose
    d.ellipse([head_left + 5, head_top + 6, head_left + 9, head_top + 9], fill=W)
    d.ellipse([head_left + 9, head_top + 6, head_left + 13, head_top + 9], fill=W)
    img.putpixel((head_left + 9, head_top + 6), (225, 75, 55, 255))

    if p.get("has_collar", False):
        collar_c = p.get("collar", (56, 189, 248, 255))
        d.rectangle([head_left + 2, head_top + 10, head_left + 15, head_top + 11], fill=collar_c)
        img.putpixel((head_left + 9, head_top + 11), (255, 215, 0, 255))

    # 4. Floating Retro Thought Box [...] from reference image
    bx, by = head_left + 12, 1
    # Little connecting dot trail
    img.putpixel((head_left + 14, head_top - 2), (180, 190, 205, 255))
    img.putpixel((head_left + 16, head_top - 4), (180, 190, 205, 255))

    # Retro Thought Bubble Box with clean pixel borders
    box_bg = (245, 248, 255, 255)
    box_border = (80, 95, 120, 255)
    dot_color = (40, 50, 70, 255)
    dot_glow = (59, 130, 246, 255)

    d.rectangle([bx, by, bx + 10, by + 5], fill=box_bg, outline=box_border)

    # 4-Frame Dynamic Dot Cycle: . -> .. -> ... -> glowing ...
    if fi == 0:
        d.rectangle([bx + 2, by + 2, bx + 3, by + 3], fill=dot_glow)
    elif fi == 1:
        d.rectangle([bx + 2, by + 2, bx + 3, by + 3], fill=dot_color)
        d.rectangle([bx + 5, by + 2, bx + 6, by + 3], fill=dot_glow)
    elif fi == 2:
        d.rectangle([bx + 2, by + 2, bx + 3, by + 3], fill=dot_color)
        d.rectangle([bx + 5, by + 2, bx + 6, by + 3], fill=dot_color)
        d.rectangle([bx + 8, by + 2, bx + 9, by + 3], fill=dot_glow)
    else:
        d.rectangle([bx + 2, by + 2, bx + 3, by + 3], fill=dot_glow)
        d.rectangle([bx + 5, by + 2, bx + 6, by + 3], fill=dot_glow)
        d.rectangle([bx + 8, by + 2, bx + 9, by + 3], fill=dot_glow)

    return img


# ─── 11. PEEK MODE (SCREEN EDGE PEEKING) ──────────────────────────────────
def _draw_peek(p: dict, frame_idx: int, side: str = "right") -> Image.Image:
    """
    Cute edge-peeking animation when user is watching fullscreen video or gaming:
    - 'right': Peeking from right edge towards center-left.
    - 'left': Peeking from left edge towards center-right.
    - 'bottom': Peeking up from taskbar / bottom edge.
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    E = p["inner_ear"]
    K = p["outline"]

    fi = frame_idx % 4
    bob = 1 if fi in (1, 2) else 0

    if side == "right":
        # Peeking from the right edge toward the left
        d.ellipse([14, 10 + bob, 34, 28 + bob], fill=O, outline=K)

        head_x, head_y = 6 + bob, 8 + bob
        d.ellipse([head_x, head_y, head_x + 16, head_y + 13], fill=O, outline=K)

        # Ears
        d.polygon([(head_x + 1, head_y + 2), (head_x + 2, head_y - 4), (head_x + 6, head_y + 2)], fill=O, outline=K)
        d.polygon([(head_x + 2, head_y + 1), (head_x + 3, head_y - 2), (head_x + 5, head_y + 1)], fill=E)

        d.polygon([(head_x + 11, head_y + 2), (head_x + 15, head_y - 4), (head_x + 16, head_y + 2)], fill=O, outline=K)
        d.polygon([(head_x + 12, head_y + 1), (head_x + 14, head_y - 2), (head_x + 15, head_y + 1)], fill=E)

        # Eyes looking left towards content
        if p.get("has_shades", False):
            d.rectangle([head_x + 2, head_y + 4, head_x + 14, head_y + 7], fill=(20, 20, 26, 255), outline=K)
            img.putpixel((head_x + 4, head_y + 5), (255, 255, 255, 255))
            img.putpixel((head_x + 11, head_y + 5), (255, 255, 255, 255))
        else:
            d.ellipse([head_x + 3, head_y + 4, head_x + 6, head_y + 7], fill=(255, 255, 255, 255), outline=K)
            d.ellipse([head_x + 10, head_y + 4, head_x + 13, head_y + 7], fill=(255, 255, 255, 255), outline=K)
            img.putpixel((head_x + 3, head_y + 5), (20, 20, 20, 255))
            img.putpixel((head_x + 10, head_y + 5), (20, 20, 20, 255))
            img.putpixel((head_x + 4, head_y + 5), (255, 255, 255, 200))
            img.putpixel((head_x + 11, head_y + 5), (255, 255, 255, 200))

        # Muzzle
        d.ellipse([head_x + 4, head_y + 8, head_x + 8, head_y + 11], fill=W)
        d.ellipse([head_x + 8, head_y + 8, head_x + 12, head_y + 11], fill=W)
        img.putpixel((head_x + 8, head_y + 8), (225, 75, 55, 255))

        # Two cute paws gripping the edge
        paw_wave = 1 if fi == 2 else 0
        d.rectangle([head_x - 1, head_y + 12, head_x + 3, head_y + 15], fill=W, outline=K)
        d.rectangle([head_x + 2, head_y + 16 - paw_wave, head_x + 6, head_y + 19 - paw_wave], fill=W, outline=K)

    elif side == "left":
        # Peeking from the left edge toward the right
        d.ellipse([-2, 10 + bob, 18, 28 + bob], fill=O, outline=K)

        head_x, head_y = 10 - bob, 8 + bob
        d.ellipse([head_x, head_y, head_x + 16, head_y + 13], fill=O, outline=K)

        # Ears
        d.polygon([(head_x + 1, head_y + 2), (head_x + 2, head_y - 4), (head_x + 6, head_y + 2)], fill=O, outline=K)
        d.polygon([(head_x + 2, head_y + 1), (head_x + 3, head_y - 2), (head_x + 5, head_y + 1)], fill=E)

        d.polygon([(head_x + 11, head_y + 2), (head_x + 15, head_y - 4), (head_x + 16, head_y + 2)], fill=O, outline=K)
        d.polygon([(head_x + 12, head_y + 1), (head_x + 14, head_y - 2), (head_x + 15, head_y + 1)], fill=E)

        # Eyes looking right towards content
        if p.get("has_shades", False):
            d.rectangle([head_x + 2, head_y + 4, head_x + 14, head_y + 7], fill=(20, 20, 26, 255), outline=K)
            img.putpixel((head_x + 4, head_y + 5), (255, 255, 255, 255))
            img.putpixel((head_x + 11, head_y + 5), (255, 255, 255, 255))
        else:
            d.ellipse([head_x + 3, head_y + 4, head_x + 6, head_y + 7], fill=(255, 255, 255, 255), outline=K)
            d.ellipse([head_x + 10, head_y + 4, head_x + 13, head_y + 7], fill=(255, 255, 255, 255), outline=K)
            img.putpixel((head_x + 5, head_y + 5), (20, 20, 20, 255))
            img.putpixel((head_x + 12, head_y + 5), (20, 20, 20, 255))
            img.putpixel((head_x + 4, head_y + 5), (255, 255, 255, 200))
            img.putpixel((head_x + 11, head_y + 5), (255, 255, 255, 200))

        # Muzzle
        d.ellipse([head_x + 4, head_y + 8, head_x + 8, head_y + 11], fill=W)
        d.ellipse([head_x + 8, head_y + 8, head_x + 12, head_y + 11], fill=W)
        img.putpixel((head_x + 8, head_y + 8), (225, 75, 55, 255))

        # Two cute paws gripping the edge
        paw_wave = 1 if fi == 2 else 0
        d.rectangle([head_x + 13, head_y + 12, head_x + 17, head_y + 15], fill=W, outline=K)
        d.rectangle([head_x + 10, head_y + 16 - paw_wave, head_x + 14, head_y + 19 - paw_wave], fill=W, outline=K)

    else:
        # Peeking up from the bottom edge (Taskbar / screen bottom)
        d.ellipse([8, 14 - bob, 24, 34 - bob], fill=O, outline=K)

        head_x, head_y = 8, 8 - bob
        d.ellipse([head_x, head_y, head_x + 16, head_y + 12], fill=O, outline=K)

        # Ears perked up high
        d.polygon([(head_x + 1, head_y + 2), (head_x + 2, head_y - 5), (head_x + 6, head_y + 2)], fill=O, outline=K)
        d.polygon([(head_x + 2, head_y + 1), (head_x + 3, head_y - 3), (head_x + 5, head_y + 1)], fill=E)

        d.polygon([(head_x + 10, head_y + 2), (head_x + 14, head_y - 5), (head_x + 15, head_y + 2)], fill=O, outline=K)
        d.polygon([(head_x + 11, head_y + 1), (head_x + 13, head_y - 3), (head_x + 14, head_y + 1)], fill=E)

        # Big round eyes looking up
        if p.get("has_shades", False):
            d.rectangle([head_x + 2, head_y + 3, head_x + 14, head_y + 6], fill=(20, 20, 26, 255), outline=K)
            img.putpixel((head_x + 4, head_y + 4), (255, 255, 255, 255))
            img.putpixel((head_x + 11, head_y + 4), (255, 255, 255, 255))
        else:
            d.ellipse([head_x + 3, head_y + 3, head_x + 6, head_y + 6], fill=(255, 255, 255, 255), outline=K)
            d.ellipse([head_x + 10, head_y + 3, head_x + 13, head_y + 6], fill=(255, 255, 255, 255), outline=K)
            img.putpixel((head_x + 4, head_y + 4), (20, 20, 20, 255))
            img.putpixel((head_x + 11, head_y + 4), (20, 20, 20, 255))
            img.putpixel((head_x + 4, head_y + 3), (255, 255, 255, 220))
            img.putpixel((head_x + 11, head_y + 3), (255, 255, 255, 220))

        # Muzzle
        d.ellipse([head_x + 4, head_y + 6, head_x + 8, head_y + 9], fill=W)
        d.ellipse([head_x + 8, head_y + 6, head_x + 12, head_y + 9], fill=W)
        img.putpixel((head_x + 8, head_y + 6), (225, 75, 55, 255))

        # Two front paws resting on the bottom edge
        d.rectangle([head_x + 1, head_y + 11, head_x + 5, head_y + 14], fill=W, outline=K)
        d.rectangle([head_x + 11, head_y + 11, head_x + 15, head_y + 14], fill=W, outline=K)

    return img


# ─── 12. CAT STRETCH / YOGA POSTURE REMINDER ────────────────────────────────
def _draw_cat_stretch(p: dict, frame_idx: int) -> Image.Image:
    """
    Cute downward cat yoga stretch:
    Paws extended flat forward, spine sloping down, hips/butt elevated,
    perky tail arched high with animated flick, and blissful closed face.
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    E = p["inner_ear"]
    K = p["outline"]

    fi = frame_idx % 4

    # 1. Perky Tail Arched High with 4-frame animated flick
    tail_flicks = [
        [(5, 13), (3, 9), (2, 6), (4, 3), (6, 4)],
        [(5, 13), (3, 8), (3, 5), (5, 2), (7, 3)],
        [(5, 13), (4, 8), (4, 5), (6, 2), (8, 3)],
        [(5, 13), (3, 9), (2, 6), (4, 3), (6, 4)],
    ]
    pts = tail_flicks[fi]
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=K, width=3)
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=O, width=1)
    d.point(pts[-1], fill=W)

    # 2. Elevated Hind Legs & Butt
    d.ellipse([4, 11, 14, 23], fill=O, outline=K)
    d.rectangle([5, 19, 10, 27], fill=O, outline=K)
    d.rectangle([5, 25, 11, 27], fill=W, outline=K)
    d.line([(10, 18), (10, 24)], fill=S)

    # 3. Sloping Torso & Back
    body_pts = [(9, 12), (16, 17), (21, 22), (23, 26), (17, 27), (11, 25), (7, 19)]
    d.polygon(body_pts, fill=O, outline=K)

    # Spine tiger stripes
    d.line([(10, 13), (12, 16)], fill=S)
    d.line([(14, 16), (16, 20)], fill=S)
    d.line([(18, 20), (20, 23)], fill=S)

    # White belly & chest patch
    d.polygon([(14, 21), (20, 23), (22, 26), (16, 26)], fill=W)

    # 4. Front Paws (Stretched flat forward)
    d.rectangle([20, 24, 26, 27], fill=O, outline=K)
    d.rectangle([23, 25, 27, 27], fill=W, outline=K)

    reach = 29 if fi in (1, 2) else 28
    d.rectangle([18, 25, reach, 27], fill=O, outline=K)
    d.rectangle([reach - 4, 25, reach, 27], fill=W, outline=K)
    if fi in (1, 2):
        img.putpixel((reach, 26), (255, 160, 175, 255))

    # 5. Collar & Gold Bell / Chain
    if p.get("has_chain", False):
        d.line([(17, 20), (21, 22)], fill=(255, 215, 0, 255), width=2)
    else:
        collar_col = p.get("collar", (235, 55, 75, 255))
        d.line([(17, 20), (21, 22)], fill=collar_col, width=2)
        accent_col = p.get("accent", (255, 215, 35, 255))
        d.rectangle([19, 22, 21, 24], fill=accent_col, outline=K)

    # 6. Head & Kawaii Closed Face
    head_x = 16
    head_y = 14

    d.polygon([(head_x, head_y), (head_x - 2, head_y - 4), (head_x + 3, head_y - 1)], fill=O, outline=K)
    d.polygon([(head_x + 1, head_y - 1), (head_x - 1, head_y - 3), (head_x + 2, head_y - 1)], fill=E)

    d.polygon([(head_x + 7, head_y + 1), (head_x + 9, head_y - 3), (head_x + 11, head_y + 2)], fill=O, outline=K)
    d.polygon([(head_x + 8, head_y + 1), (head_x + 9, head_y - 2), (head_x + 10, head_y + 2)], fill=E)

    d.ellipse([head_x, head_y, head_x + 11, head_y + 10], fill=O, outline=K)
    d.ellipse([head_x + 4, head_y + 4, head_x + 11, head_y + 9], fill=W)

    if p.get("has_shades", False):
        d.rectangle([head_x + 3, head_y + 3, head_x + 11, head_y + 6], fill=(18, 18, 22, 255), outline=K)
        img.putpixel((head_x + 5, head_y + 4), (255, 255, 255, 255))
        img.putpixel((head_x + 9, head_y + 4), (255, 255, 255, 255))
    else:
        d.line([(head_x + 3, head_y + 4), (head_x + 5, head_y + 3)], fill=K)
        d.line([(head_x + 5, head_y + 3), (head_x + 7, head_y + 4)], fill=K)
        img.putpixel((head_x + 2, head_y + 6), (255, 140, 160, 255))
        img.putpixel((head_x + 3, head_y + 6), (255, 140, 160, 255))

    img.putpixel((head_x + 9, head_y + 5), (255, 120, 140, 255))

    # Stretch sparkles aura
    if fi in (1, 2):
        spark_y = 6 if fi == 1 else 5
        d.line([(12, spark_y), (14, spark_y)], fill=(255, 215, 50, 255))
        d.line([(13, spark_y - 1), (13, spark_y + 1)], fill=(255, 215, 50, 255))
        d.line([(18, spark_y + 3), (20, spark_y + 3)], fill=(255, 215, 50, 255))
        d.line([(19, spark_y + 2), (19, spark_y + 4)], fill=(255, 215, 50, 255))

    return img


# ─── 12. DRINK WATER / HYDRATION REMINDER ──────────────────────────────────
def _draw_drink_water(p: dict, frame_idx: int) -> Image.Image:
    """
    Cute cat drinking water beside a ceramic bowl with crystal blue water,
    splashes, lapping pink tongue, and satisfaction sparkle stars.
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    E = p["inner_ear"]
    K = p["outline"]

    fi = frame_idx % 4

    # 1. Ceramic Water Bowl with Water & Ripples
    bowl_x, bowl_y = 19, 21
    # Bowl shadow
    d.ellipse([bowl_x - 1, bowl_y + 4, bowl_x + 11, bowl_y + 8], fill=(30, 35, 45, 100))
    # Ceramic outer rim
    d.ellipse([bowl_x, bowl_y, bowl_x + 10, bowl_y + 7], fill=(230, 235, 245, 255), outline=K)
    # Bowl depth
    d.ellipse([bowl_x + 1, bowl_y + 1, bowl_x + 9, bowl_y + 6], fill=(50, 140, 230, 255))
    # Water surface highlight
    d.ellipse([bowl_x + 2, bowl_y + 2, bowl_x + 8, bowl_y + 5], fill=(100, 200, 255, 255))
    # Reflection shine
    img.putpixel((bowl_x + 3, bowl_y + 2), (255, 255, 255, 255))
    img.putpixel((bowl_x + 4, bowl_y + 2), (255, 255, 255, 255))

    # Water ripples & Splash Droplets on drinking frames
    if fi in (0, 1):
        d.line([(bowl_x + 4, bowl_y + 3), (bowl_x + 6, bowl_y + 3)], fill=(255, 255, 255, 255))
        if fi == 1:
            # Splash droplet flying up
            img.putpixel((bowl_x + 7, bowl_y - 2), (120, 215, 255, 255))
            img.putpixel((bowl_x + 8, bowl_y - 1), (80, 180, 255, 255))

    # 2. Cat Tail (Gently swishing in contentment)
    tail_offsets = [
        [(5, 24), (2, 22), (1, 18), (3, 15)],
        [(5, 24), (2, 23), (1, 19), (2, 16)],
        [(5, 24), (3, 23), (2, 20), (4, 17)],
        [(5, 24), (2, 22), (1, 18), (3, 15)],
    ]
    t_pts = tail_offsets[fi]
    for i in range(len(t_pts) - 1):
        d.line([t_pts[i], t_pts[i + 1]], fill=K, width=3)
    for i in range(len(t_pts) - 1):
        d.line([t_pts[i], t_pts[i + 1]], fill=O, width=1)
    d.point(t_pts[-1], fill=W)

    # 3. Sitting Cat Body (Hunched forward happily over bowl)
    d.ellipse([5, 14, 18, 27], fill=O, outline=K)
    # Hind leg curve
    d.ellipse([4, 19, 11, 27], fill=O, outline=K)
    d.rectangle([5, 25, 10, 27], fill=W, outline=K)
    # White belly & chest patch
    d.ellipse([10, 16, 17, 26], fill=W)

    # 4. Front Paws (Resting neatly near the bowl)
    d.rectangle([13, 24, 17, 27], fill=O, outline=K)
    d.rectangle([14, 25, 17, 27], fill=W, outline=K)
    d.rectangle([17, 24, 20, 27], fill=O, outline=K)
    d.rectangle([18, 25, 20, 27], fill=W, outline=K)

    # 5. Collar / Gold Chain
    if p.get("has_chain", False):
        d.line([(11, 16), (17, 16)], fill=(255, 215, 0, 255), width=2)
    else:
        collar_col = p.get("collar", (235, 55, 75, 255))
        d.line([(11, 16), (17, 16)], fill=collar_col, width=2)
        accent_col = p.get("accent", (255, 215, 35, 255))
        d.rectangle([14, 16, 16, 18], fill=accent_col, outline=K)

    # 6. Head & Kawaii Face (Dipping down to drink, lifting up satisfied)
    head_y_offsets = [12, 13, 11, 10]
    head_x_offsets = [13, 14, 12, 11]
    hx = head_x_offsets[fi]
    hy = head_y_offsets[fi]

    # Ears
    d.polygon([(hx, hy), (hx - 2, hy - 4), (hx + 3, hy - 1)], fill=O, outline=K)
    d.polygon([(hx + 1, hy - 1), (hx - 1, hy - 3), (hx + 2, hy - 1)], fill=E)

    d.polygon([(hx + 6, hy), (hx + 8, hy - 4), (hx + 10, hy)], fill=O, outline=K)
    d.polygon([(hx + 7, hy), (hx + 8, hy - 3), (hx + 9, hy)], fill=E)

    # Head circle
    d.ellipse([hx, hy, hx + 10, hy + 9], fill=O, outline=K)
    d.ellipse([hx + 3, hy + 3, hx + 10, hy + 8], fill=W)

    # Eyes / Glasses & Mouth
    if p.get("has_shades", False):
        d.rectangle([hx + 2, hy + 2, hx + 10, hy + 5], fill=(18, 18, 22, 255), outline=K)
        img.putpixel((hx + 4, hy + 3), (255, 255, 255, 255))
        img.putpixel((hx + 8, hy + 3), (255, 255, 255, 255))
    else:
        # Happy closed eyes ^ ^
        d.line([(hx + 3, hy + 4), (hx + 5, hy + 3)], fill=K)
        d.line([(hx + 5, hy + 3), (hx + 7, hy + 4)], fill=K)
        # Pink blush
        img.putpixel((hx + 2, hy + 6), (255, 140, 160, 255))
        img.putpixel((hx + 8, hy + 6), (255, 140, 160, 255))

    # Pink Tongue lapping water (frame 0 and 1)
    if fi in (0, 1):
        tongue_len = 3 if fi == 1 else 2
        d.rectangle([hx + 6, hy + 7, hx + 8, hy + 7 + tongue_len], fill=(255, 130, 160, 255), outline=K)
        # Wet water tip
        img.putpixel((hx + 7, hy + 7 + tongue_len), (120, 215, 255, 255))
    elif fi == 2:
        # Cute water droplet on chin
        img.putpixel((hx + 7, hy + 8), (100, 200, 255, 255))
    elif fi == 3:
        # Licking lips :3
        d.line([(hx + 6, hy + 7), (hx + 8, hy + 7)], fill=K)

    # Kawaii sparkle stars when satisfied (frames 2 and 3)
    if fi in (2, 3):
        sy = 4 if fi == 2 else 3
        d.line([(8, sy), (10, sy)], fill=(100, 200, 255, 255))
        d.line([(9, sy - 1), (9, sy + 1)], fill=(100, 200, 255, 255))
        d.line([(24, sy + 2), (26, sy + 2)], fill=(255, 220, 60, 255))
        d.line([(25, sy + 1), (25, sy + 3)], fill=(255, 220, 60, 255))

    return img


def _draw_cat_feeding(p: dict, frame_idx: int) -> Image.Image:
    """
    Comnyang Official Feeding Animation:
    Cat happily munching delicious fresh fish / snack from a ceramic dish,
    with crunch crumbs, tail wagging, cute chewing, licking chops, and floating love heart particles!
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p.get("fur_main", (245, 145, 35, 255))
    S = p.get("fur_shade", (210, 105, 20, 255))
    W = p.get("fur_belly", (255, 245, 235, 255))
    K = (18, 18, 22, 255)
    E = p.get("inner_ear", (255, 175, 185, 255))

    fi = frame_idx % 4

    # 1. Cute Ceramic Cat Food Dish (Bowl)
    DISH_RIM = (235, 240, 250, 255)
    DISH_BODY = (195, 205, 225, 255)
    FISH_GOLD = (255, 170, 40, 255)
    FISH_SHADE = (215, 120, 20, 255)
    HEART_RED = (255, 70, 105, 255)

    d.ellipse([19, 23, 30, 27], fill=DISH_BODY, outline=K)
    d.ellipse([20, 22, 29, 25], fill=DISH_RIM)

    # Food in bowl
    if fi == 0:
        d.ellipse([21, 21, 27, 24], fill=FISH_GOLD, outline=K)
        d.polygon([(26, 21), (30, 19), (29, 23)], fill=FISH_GOLD, outline=K)
        img.putpixel((22, 22), K)
    elif fi == 1:
        d.ellipse([22, 22, 27, 24], fill=FISH_GOLD, outline=K)
        d.polygon([(26, 22), (29, 20), (28, 24)], fill=FISH_SHADE)
        img.putpixel((20, 18), (255, 180, 50, 255))
        img.putpixel((22, 16), (230, 140, 30, 255))
    elif fi == 2:
        d.line([(22, 23), (26, 23)], fill=(240, 240, 245, 255))
        img.putpixel((24, 22), (240, 240, 245, 255))
        img.putpixel((24, 24), (240, 240, 245, 255))
    else:
        img.putpixel((25, 23), (255, 255, 255, 255))

    # 2. Tail (Swishing happily)
    tail_offsets = [
        [(5, 22), (3, 18), (2, 14), (4, 11)],
        [(5, 22), (2, 19), (1, 15), (2, 11)],
        [(5, 22), (3, 18), (4, 13), (6, 10)],
        [(5, 22), (4, 17), (5, 12), (7, 9)],
    ]
    t_pts = tail_offsets[fi]
    for i in range(len(t_pts) - 1):
        d.line([t_pts[i], t_pts[i + 1]], fill=K, width=3)
    for i in range(len(t_pts) - 1):
        d.line([t_pts[i], t_pts[i + 1]], fill=O, width=1)
    d.point(t_pts[-1], fill=W)

    # 3. Sitting Cat Body (Hunched happily over dish)
    d.ellipse([5, 14, 18, 27], fill=O, outline=K)
    d.ellipse([4, 19, 11, 27], fill=O, outline=K)
    d.rectangle([5, 25, 10, 27], fill=W, outline=K)
    d.ellipse([10, 16, 17, 26], fill=W)

    # 4. Front Paws
    d.rectangle([13, 24, 17, 27], fill=O, outline=K)
    d.rectangle([14, 25, 17, 27], fill=W, outline=K)
    d.rectangle([17, 24, 20, 27], fill=O, outline=K)
    d.rectangle([18, 25, 20, 27], fill=W, outline=K)

    # 5. Collar / Gold Chain
    if p.get("has_chain", False):
        d.line([(11, 16), (17, 16)], fill=(255, 215, 0, 255), width=2)
    else:
        collar_col = p.get("collar", (235, 55, 75, 255))
        d.line([(11, 16), (17, 16)], fill=collar_col, width=2)
        accent_col = p.get("accent", (255, 215, 35, 255))
        d.rectangle([14, 16, 16, 18], fill=accent_col, outline=K)

    # 6. Head & Kawaii Munching Face
    head_y_offsets = [12, 13, 11, 10]
    head_x_offsets = [13, 14, 12, 11]
    hx = head_x_offsets[fi]
    hy = head_y_offsets[fi]

    # Ears
    d.polygon([(hx, hy), (hx - 2, hy - 4), (hx + 3, hy - 1)], fill=O, outline=K)
    d.polygon([(hx + 1, hy - 1), (hx - 1, hy - 3), (hx + 2, hy - 1)], fill=E)
    d.polygon([(hx + 6, hy), (hx + 8, hy - 4), (hx + 10, hy)], fill=O, outline=K)
    d.polygon([(hx + 7, hy), (hx + 8, hy - 3), (hx + 9, hy)], fill=E)

    # Head circle
    d.ellipse([hx, hy, hx + 10, hy + 9], fill=O, outline=K)
    d.ellipse([hx + 3, hy + 3, hx + 10, hy + 8], fill=W)

    # Eyes & Mouth
    if p.get("has_shades", False):
        d.rectangle([hx + 2, hy + 2, hx + 10, hy + 5], fill=(18, 18, 22, 255), outline=K)
        img.putpixel((hx + 4, hy + 3), (255, 255, 255, 255))
        img.putpixel((hx + 8, hy + 3), (255, 255, 255, 255))
    else:
        d.line([(hx + 3, hy + 4), (hx + 5, hy + 3)], fill=K)
        d.line([(hx + 5, hy + 3), (hx + 7, hy + 4)], fill=K)
        img.putpixel((hx + 2, hy + 6), (255, 140, 160, 255))
        img.putpixel((hx + 8, hy + 6), (255, 140, 160, 255))

    # Mouth & Munching Action
    if fi == 0:
        d.rectangle([hx + 6, hy + 6, hx + 8, hy + 8], fill=(225, 75, 95, 255), outline=K)
    elif fi == 1:
        d.line([(hx + 5, hy + 7), (hx + 8, hy + 7)], fill=K)
        img.putpixel((hx + 9, hy + 8), (255, 170, 40, 255))
    elif fi == 2:
        d.line([(hx + 5, hy + 6), (hx + 7, hy + 7)], fill=K)
        d.line([(hx + 7, hy + 7), (hx + 9, hy + 6)], fill=K)
    elif fi == 3:
        d.rectangle([hx + 6, hy + 7, hx + 8, hy + 9], fill=(255, 130, 160, 255), outline=K)

    # 7. Floating Heart Particles ❤️
    if fi in (2, 3):
        heart_x = 22 if fi == 2 else 24
        heart_y = 4 if fi == 2 else 2
        d.rectangle([heart_x, heart_y, heart_x + 1, heart_y + 1], fill=HEART_RED)
        d.rectangle([heart_x + 3, heart_y, heart_x + 4, heart_y + 1], fill=HEART_RED)
        d.rectangle([heart_x, heart_y + 1, heart_x + 4, heart_y + 2], fill=HEART_RED)
        d.rectangle([heart_x + 1, heart_y + 3, heart_x + 3, heart_y + 3], fill=HEART_RED)
        img.putpixel((heart_x + 2, heart_y + 4), HEART_RED)

    return img


# ─── 14. SULK / NGAMBEK POSE (BACK TURNED & ANIME ANGER MARK 💢) ───────────
def _draw_sulk(p: dict, frame_idx: int) -> Image.Image:
    """
    Sulk / Ngambek pose:
    Cat turns its back in annoyance, ears turned away, twitching tail,
    and animated pulsing anime anger mark (💢).
    """
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    O = p["fur_main"]
    S = p["fur_shade"]
    W = p["fur_belly"]
    K = p["outline"]

    breath_y = -1 if frame_idx in (1, 2) else 0

    # 1. Agitated Tail (Curled up to right flank with twitch)
    tail_flick = [-2, 0, 2, 0][frame_idx % 4]
    d.line([(24, 25 + breath_y), (27, 22 + breath_y), (28, 17 + breath_y + tail_flick), (26, 14 + breath_y + tail_flick)], fill=O, width=2)
    d.line([(25, 26 + breath_y), (28, 22 + breath_y), (29, 17 + breath_y + tail_flick), (26, 13 + breath_y + tail_flick)], fill=K)

    # 2. Cat Body from Behind (Exact match to front idle body)
    body_top = 17 + breath_y
    d.ellipse([7, body_top, 24, 28 + breath_y], fill=O, outline=K)

    # Back spine fur stripes
    d.line([(12, body_top + 3), (12, body_top + 8)], fill=S)
    d.line([(15, body_top + 2), (15, body_top + 9)], fill=S, width=2)
    d.line([(19, body_top + 3), (19, body_top + 8)], fill=S)

    # Back paws (tucked flat on ground)
    paw_y = 27 + breath_y
    d.rectangle([8, paw_y, 12, 29 + breath_y], fill=O, outline=K)
    d.rectangle([19, paw_y, 23, 29 + breath_y], fill=O, outline=K)

    # 3. Head from Behind (Exact match to front idle head)
    head_y = 6 + breath_y

    # Ears from behind (Solid fur matching body, no pink inner ear)
    d.polygon([(7, head_y + 3), (7, head_y - 3), (12, head_y + 3)], fill=O, outline=K)
    d.polygon([(19, head_y + 3), (24, head_y - 3), (24, head_y + 3)], fill=O, outline=K)

    # Head ellipse
    d.ellipse([6, head_y, 25, head_y + 12], fill=O, outline=K)

    # Back of head fur stripes
    d.line([(13, head_y + 2), (13, head_y + 7)], fill=S)
    d.line([(15, head_y + 1), (15, head_y + 8)], fill=S, width=2)
    d.line([(18, head_y + 2), (18, head_y + 7)], fill=S)

    # 4. Animated Red Manga Anger Mark 💢 (Pulsing over top-right head)
    anger_red = (255, 35, 60, 255)
    pop = 1 if frame_idx in (0, 2) else 0

    ax, ay = 23 + pop, 1 - pop

    # 4-curve anime anger vein
    d.line([(ax, ay + 1), (ax + 1, ay)], fill=anger_red)
    d.line([(ax + 3, ay), (ax + 4, ay + 1)], fill=anger_red)
    d.line([(ax, ay + 3), (ax + 1, ay + 4)], fill=anger_red)
    d.line([(ax + 3, ay + 4), (ax + 4, ay + 3)], fill=anger_red)
    d.line([(ax + 2, ay + 1), (ax + 2, ay + 3)], fill=anger_red)
    d.line([(ax + 1, ay + 2), (ax + 3, ay + 2)], fill=anger_red)
    img.putpixel((ax + 2, ay + 2), (255, 190, 200, 255)) # highlight

    return img


# ─── WARDROBE ACCESSORIES DEFINITIONS & LAYER ENGINE ───────────────────────
ACCESSORIES = {
    "none": {"name": "🚫 Tanpa Aksesoris (None)", "icon": "🚫"},
    "wizard_hat": {"name": "🧙 Topi Penyihir (Wizard Hat)", "icon": "🧙"},
    "royal_crown": {"name": "👑 Mahkota Emas (Royal Crown)", "icon": "👑"},
    "cute_ribbon": {"name": "🎀 Pita Manis (Cute Ribbon)", "icon": "🎀"},
    "winter_scarf": {"name": "🧣 Syal Musim Dingin (Winter Scarf)", "icon": "🧣"},
    "sunglasses": {"name": "🕶️ Kacamata Hitam (Sunglasses)", "icon": "🕶️"},
    "flower_pin": {"name": "🌸 Jepit Bunga Sakura (Flower Pin)", "icon": "🌸"},
}


def _draw_accessory_layer(img: Image.Image, accessory: str, state: str, frame_idx: int, flip_left: bool = False):
    """Draws pixel-perfect accessory layer onto the native 32x32 cat canvas."""
    if not accessory or accessory == "none":
        return

    d = ImageDraw.Draw(img)
    K = (18, 18, 22, 255)
    fi = frame_idx % 4

    # Determine exact head & skull top anchor per state
    if state in ("walk_left", "walk_right", "run_W", "run_E", "walk"):
        bob_y = -1 if fi in (0, 2) else 0
        head_cx = 9 if flip_left else 23
        skull_top_y = 5 + bob_y
        eye_y = 8 + bob_y
        neck_y = 15 + bob_y
    elif state in ("work", "knead", "typing", "overheat", "heat", "hot"):
        bob_y = -1 if fi in (0, 2) else 0
        head_cx = 16
        skull_top_y = 4 + bob_y
        eye_y = 7 + bob_y
        neck_y = 15 + bob_y
    elif state == "sleep":
        head_cx = 20
        skull_top_y = 11
        eye_y = 14
        neck_y = 18
    elif state in ("stretch", "yoga", "posture"):
        head_cx = 24
        skull_top_y = 14
        eye_y = 17
        neck_y = 20
    elif state in ("celebrate", "jump", "done"):
        if fi in (1, 2):
            head_cx = 16
            skull_top_y = 1
            eye_y = 4
            neck_y = 10
        else:
            head_cx = 16
            skull_top_y = 5
            eye_y = 8
            neck_y = 14
    elif state.startswith("peek"):
        if state == "peek_left":
            head_cx = 22
            skull_top_y = 6
            eye_y = 9
            neck_y = 16
        elif state == "peek_bottom":
            head_cx = 16
            skull_top_y = 10
            eye_y = 13
            neck_y = 19
        else:
            head_cx = 10
            skull_top_y = 6
            eye_y = 9
            neck_y = 16
    else:  # idle_front, pet, thinking, feed, drag
        breath_y = -1 if fi == 1 else 0
        head_cx = 16
        skull_top_y = 5 + breath_y
        eye_y = 9 + breath_y
        neck_y = 16 + breath_y

    if accessory == "royal_crown":
        GOLD = (255, 210, 30, 255)
        GOLD_DARK = (205, 160, 15, 255)
        RUBY = (245, 45, 65, 255)
        SAPPHIRE = (45, 140, 255, 255)
        cx, cy = head_cx, skull_top_y

        # Base headband sitting on top of head (between ears)
        d.rectangle([cx - 4, cy - 1, cx + 4, cy], fill=GOLD_DARK, outline=K)
        # 3 Crown Spikes
        d.polygon([(cx - 4, cy - 1), (cx - 4, cy - 5), (cx - 2, cy - 2)], fill=GOLD, outline=K)
        d.polygon([(cx - 2, cy - 2), (cx, cy - 6), (cx + 2, cy - 2)], fill=GOLD, outline=K)
        d.polygon([(cx + 2, cy - 2), (cx + 4, cy - 5), (cx + 4, cy - 1)], fill=GOLD, outline=K)
        # Jewels
        img.putpixel((cx - 3, cy - 1), SAPPHIRE)
        img.putpixel((cx, cy - 1), RUBY)
        img.putpixel((cx + 3, cy - 1), SAPPHIRE)

    elif accessory == "wizard_hat":
        PURPLE = (110, 45, 185, 255)
        PURPLE_DARK = (75, 25, 135, 255)
        GOLD = (255, 215, 45, 255)
    # Render specific wardrobe accessory
    if accessory == "wizard_hat":
        # Purple pointed wizard hat with gold band and yellow star
        hat_col = (95, 45, 160, 255)
        hat_shade = (70, 30, 120, 255)
        star_gold = (255, 225, 50, 255)
        # Brim
        d.line([(head_cx - 8, skull_top_y), (head_cx + 8, skull_top_y)], fill=hat_shade, width=2)
        d.line([(head_cx - 7, skull_top_y - 1), (head_cx + 7, skull_top_y - 1)], fill=hat_col)
        # Cone
        d.polygon([(head_cx - 5, skull_top_y - 1), (head_cx + 5, skull_top_y - 1), (head_cx + 2, skull_top_y - 9), (head_cx - 1, skull_top_y - 9)], fill=hat_col, outline=K)
        # Gold band
        d.line([(head_cx - 4, skull_top_y - 2), (head_cx + 4, skull_top_y - 2)], fill=star_gold)
        # Star on tip
        img.putpixel((head_cx, max(0, skull_top_y - 10)), star_gold)

    elif accessory == "royal_crown":
        # Shiny gold crown with 3 peaks and ruby gems
        gold = (255, 215, 30, 255)
        gold_shade = (210, 160, 15, 255)
        ruby = (235, 35, 65, 255)
        # Base band
        d.rectangle([head_cx - 5, skull_top_y - 2, head_cx + 5, skull_top_y], fill=gold_shade, outline=K)
        d.line([(head_cx - 4, skull_top_y - 1), (head_cx + 4, skull_top_y - 1)], fill=gold)
        # 3 Crown Peaks
        d.polygon([(head_cx - 5, skull_top_y - 2), (head_cx - 4, skull_top_y - 6), (head_cx - 2, skull_top_y - 3)], fill=gold, outline=K)
        d.polygon([(head_cx - 2, skull_top_y - 2), (head_cx, skull_top_y - 7), (head_cx + 2, skull_top_y - 2)], fill=gold, outline=K)
        d.polygon([(head_cx + 2, skull_top_y - 3), (head_cx + 4, skull_top_y - 6), (head_cx + 5, skull_top_y - 2)], fill=gold, outline=K)
        # Gems
        img.putpixel((head_cx, skull_top_y - 4), ruby)
        img.putpixel((head_cx - 4, skull_top_y - 1), ruby)
        img.putpixel((head_cx + 4, skull_top_y - 1), ruby)

    elif accessory == "cute_ribbon":
        # Pink bow ribbon on right ear
        pink = (255, 110, 160, 255)
        pink_dark = (215, 65, 120, 255)
        rx, ry = head_cx + 5, skull_top_y - 1
        d.polygon([(rx, ry), (rx + 4, ry - 3), (rx + 4, ry + 3)], fill=pink, outline=K)
        d.polygon([(rx, ry), (rx - 4, ry - 3), (rx - 4, ry + 3)], fill=pink, outline=K)
        d.ellipse([rx - 1, ry - 1, rx + 1, ry + 1], fill=pink_dark, outline=K)

    elif accessory == "flower_pin":
        # Sakura pink flower with gold center on left ear
        sakura = (255, 185, 215, 255)
        sakura_edge = (245, 135, 175, 255)
        gold = (255, 220, 60, 255)
        fx, fy = head_cx - 5, skull_top_y - 1
        d.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=sakura, outline=sakura_edge)
        img.putpixel((fx, fy), gold)

    elif accessory == "sunglasses":
        # Cool retro black shades over eyes
        shades_col = (20, 20, 26, 255)
        shades_rim = (10, 10, 14, 255)
        d.rectangle([head_cx - 7, eye_y - 2, head_cx + 7, eye_y + 2], fill=shades_col, outline=shades_rim)
        # Glare reflections
        img.putpixel((head_cx - 5, eye_y - 1), (255, 255, 255, 220))
        img.putpixel((head_cx + 3, eye_y - 1), (255, 255, 255, 220))

    elif accessory == "winter_scarf":
        # Cozy warm red striped winter scarf around neck
        RED = (225, 45, 55, 255)
        WHITE = (250, 250, 255, 255)
        # Main wrap
        d.rectangle([head_cx - 7, neck_y - 1, head_cx + 7, neck_y + 2], fill=RED, outline=K)
        d.line([(head_cx - 3, neck_y), (head_cx - 3, neck_y + 2)], fill=WHITE)
        d.line([(head_cx + 3, neck_y), (head_cx + 3, neck_y + 2)], fill=WHITE)
        d.rectangle([head_cx + 3, neck_y + 3, head_cx + 5, neck_y + 6], fill=RED, outline=K)
        d.line([(head_cx + 3, neck_y + 4), (head_cx + 5, neck_y + 4)], fill=WHITE)
        img.putpixel((head_cx + 3, neck_y + 7), WHITE)
        img.putpixel((head_cx + 5, neck_y + 7), WHITE)


# ─── MAIN FRAME DISPATCHER (PUBLIC API) ────────────────────────────────────
def render_cat_frame(skin_key: str = "boss_oyen",
                     state: str = "idle",
                     frame_idx: int = 0,
                     look_dx: int = 0,
                     look_dy: int = 0,
                     accessory: str = "none") -> Image.Image:
    """
    Return a 128x128 RGBA PIL Image for the given skin / state / frame / accessory.
    Supports nearest-neighbor 4x scaling (32x32 -> 128x128) with dynamic eye follow and wardrobe layering.
    """
    global _CACHE
    cache_key = (skin_key, state, frame_idx % 4, look_dx, look_dy, accessory)
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    p = PALETTES.get(skin_key, PALETTES["boss_oyen"])
    fi = frame_idx % 4
    flip_left = False

    # Generate native 32x32 frame based on state
    if state in ("walk_left", "run_W"):
        native = _draw_walk_side(p, fi, flip_left=True)
        flip_left = True
    elif state in ("walk_right", "run_E", "walk"):
        native = _draw_walk_side(p, fi, flip_left=False)
    elif state in ("work", "knead", "typing"):
        native = _draw_knead_work(p, fi)
    elif state in ("overheat", "heat", "hot"):
        native = _draw_overheat(p, fi)
    elif state in ("sulk", "angry", "ngambek", "pout"):
        native = _draw_sulk(p, fi)
    elif state in ("paper_unroll", "scroll", "paper"):
        native = _draw_paper_unroll(p, fi)
    elif state in ("pet", "purr", "happy"):
        native = _draw_pet_purr(p, fi)
    elif state == "sleep":
        native = _draw_sleep_loaf(p, fi)
    elif state in ("stretch", "yoga", "posture"):
        native = _draw_cat_stretch(p, fi)
    elif state in ("drink_water", "drink", "water", "hydrate"):
        native = _draw_drink_water(p, fi)
    elif state in ("feed", "eat", "eating", "snack", "fish"):
        native = _draw_cat_feeding(p, fi)
    elif state in ("drag", "dangle", "mochi"):
        native = _draw_mochi_drag(p, fi)
    elif state in ("celebrate", "jump", "done"):
        native = _draw_celebrate_jump(p, fi)
    elif state in ("thinking", "alert"):
        native = _draw_thinking(p, fi)
    elif state in ("peek_right", "peek"):
        native = _draw_peek(p, fi, side="right")
    elif state in ("peek_left",):
        native = _draw_peek(p, fi, side="left")
    elif state in ("peek_bottom", "peek_down"):
        native = _draw_peek(p, fi, side="bottom")
    else:
        native = _draw_idle_front(p, fi, look_dx=look_dx, look_dy=look_dy)

    # Layer accessory onto native 32x32 frame
    if accessory and accessory != "none":
        _draw_accessory_layer(native, accessory, state, fi, flip_left=flip_left)

    # Scale 4x nearest-neighbor to crisp 128x128
    scaled = native.resize((128, 128), Image.Resampling.NEAREST)
    _CACHE[cache_key] = scaled
    return scaled


def pregenerate_all_sprites(output_dir: str = "assets/sprites") -> None:
    """Pre-generate all sprite frames to disk."""
    os.makedirs(output_dir, exist_ok=True)
    states = [
        "idle", "walk_left", "walk_right", "work", "overheat", "sulk",
        "paper_unroll", "pet", "sleep", "drag", "celebrate", "thinking",
        "peek_right", "peek_left", "peek_bottom"
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
