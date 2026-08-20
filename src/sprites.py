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


# ─── 11. CAT STRETCH / YOGA POSTURE REMINDER ────────────────────────────────
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
    elif state in ("stretch", "yoga", "posture"):
        native = _draw_cat_stretch(p, fi)
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
