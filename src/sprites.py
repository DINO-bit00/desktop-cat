"""
Pixel-Art Cat Sprite Generator & Manager (Slender / Classic Retro Style)
Redesigned with slender body proportions, defined legs, angular ears,
and crisp 1px pixel outlines matching the authentic retro pixel-art aesthetic.
Zero external network required - 100% offline & local.
"""

from PIL import Image, ImageDraw
import os

PALETTES = {
    "boss_oyen": {
        "name": "Boss Oyen (Kacamata Hitam 🕶️)",
        "base": (255, 154, 60, 255),       # Rich vibrant orange
        "stripe": (214, 90, 15, 255),       # Darker tabby stripes
        "belly": (254, 215, 140, 255),     # Light cream belly
        "inner_ear": (235, 110, 40, 255),  # Deep warm inner ear
        "eye": (20, 20, 20, 255),
        "pupil": (20, 20, 20, 255),
        "nose": (40, 25, 20, 255),
        "outline": (35, 25, 20, 255),      # Sharp dark brown outline
        "sunglasses": True,
        "collar": False,
        "white_paws": False
    },
    "mochi": {
        "name": "Si Kalung Biru (Mochi Grey Kitten)",
        "base": (160, 168, 178, 255),      # Soft cool grey
        "stripe": (105, 115, 128, 255),    # Dark slate stripes
        "belly": (255, 255, 255, 255),     # Pure white chest patch
        "inner_ear": (255, 150, 175, 255), # Soft pink inner ear
        "eye": (30, 30, 35, 255),
        "pupil": (30, 30, 35, 255),
        "nose": (255, 130, 155, 255),      # Pink nose
        "outline": (30, 32, 40, 255),      # Slate black outline
        "sunglasses": False,
        "collar": True,                    # Turquoise collar
        "white_paws": True
    },
    "oyen": {
        "name": "Si Oyen (Orange Tabby)",
        "base": (255, 154, 60, 255),       # Classic orange
        "stripe": (214, 90, 15, 255),
        "belly": (255, 225, 160, 255),
        "inner_ear": (255, 160, 180, 255),
        "eye": (46, 204, 113, 255),        # Emerald green eyes
        "pupil": (20, 20, 20, 255),
        "nose": (255, 120, 140, 255),
        "outline": (35, 25, 20, 255),
        "sunglasses": False,
        "collar": False,
        "white_paws": True
    },
    "shiro": {
        "name": "Si Putih (Snow White)",
        "base": (252, 253, 255, 255),      # Pure white
        "stripe": (218, 225, 235, 255),    # Soft shadow
        "belly": (255, 255, 255, 255),
        "inner_ear": (255, 165, 185, 255), # Pastel pink
        "eye": (52, 152, 219, 255),        # Sky blue eyes
        "pupil": (20, 20, 20, 255),
        "nose": (255, 130, 155, 255),
        "outline": (50, 55, 65, 255),
        "sunglasses": False,
        "collar": False,
        "white_paws": True
    },
    "tuxedo": {
        "name": "Si Tuxedo (Black & White)",
        "base": (45, 48, 58, 255),         # Charcoal black
        "stripe": (30, 32, 40, 255),
        "belly": (255, 255, 255, 255),     # White chest & paws
        "inner_ear": (255, 160, 180, 255),
        "eye": (46, 204, 113, 255),        # Green eyes
        "pupil": (20, 20, 20, 255),
        "nose": (255, 140, 160, 255),
        "outline": (20, 22, 28, 255),
        "sunglasses": False,
        "collar": False,
        "white_paws": True
    },
    "calico": {
        "name": "Belang Tiga (Calico)",
        "base": (250, 250, 252, 255),      # White base
        "stripe": (230, 126, 34, 255),     # Orange patch
        "dark_patch": (52, 73, 94, 255),   # Dark patch
        "belly": (255, 255, 255, 255),
        "inner_ear": (255, 160, 180, 255),
        "eye": (241, 196, 15, 255),        # Amber gold
        "pupil": (20, 20, 20, 255),
        "nose": (255, 130, 150, 255),
        "outline": (35, 35, 45, 255),
        "sunglasses": False,
        "collar": False,
        "white_paws": True
    },
    "grey": {
        "name": "Abu-Abu (Grey Tabby)",
        "base": (150, 162, 172, 255),      # Silver grey
        "stripe": (90, 102, 115, 255),     # Slate stripes
        "belly": (225, 232, 240, 255),
        "inner_ear": (255, 165, 185, 255),
        "eye": (52, 152, 219, 255),        # Blue eyes
        "pupil": (20, 20, 20, 255),
        "nose": (255, 130, 150, 255),
        "outline": (40, 45, 55, 255),
        "sunglasses": False,
        "collar": False,
        "white_paws": True
    }
}

SPRITE_GRID_SIZE = 32  # 32x32 pixel base canvas
SCALE_FACTOR = 4       # Output size 128x128 crisp pixel art


def create_blank_canvas():
    return Image.new("RGBA", (SPRITE_GRID_SIZE, SPRITE_GRID_SIZE), (0, 0, 0, 0))


def draw_pixel(draw, x, y, color):
    if 0 <= x < SPRITE_GRID_SIZE and 0 <= y < SPRITE_GRID_SIZE:
        draw.point((x, y), fill=color)


def draw_rect(draw, x1, y1, x2, y2, fill, outline=None):
    draw.rectangle([x1, y1, x2, y2], fill=fill, outline=outline)


def draw_sunglasses(draw, head_x, head_y, glint=True):
    """Draws pixel-art black sunglasses in slender style."""
    # Left lens
    draw.rectangle([head_x + 1, head_y + 4, head_x + 5, head_y + 7], fill=(15, 15, 15, 255))
    # Right lens
    draw.rectangle([head_x + 7, head_y + 4, head_x + 11, head_y + 7], fill=(15, 15, 15, 255))
    # Bridge
    draw.line([(head_x + 5, head_y + 4), (head_x + 7, head_y + 4)], fill=(15, 15, 15, 255), width=1)
    if glint:
        draw_pixel(draw, head_x + 2, head_y + 5, (255, 255, 255, 255))
        draw_pixel(draw, head_x + 8, head_y + 5, (255, 255, 255, 255))


def render_slender_cat(palette, state="idle", frame_idx=0):
    img = create_blank_canvas()
    d = ImageDraw.Draw(img)

    base = palette["base"]
    stripe = palette.get("stripe", base)
    belly = palette["belly"]
    inner_ear = palette["inner_ear"]
    eye_col = palette["eye"]
    pupil_col = palette["pupil"]
    nose_col = palette["nose"]
    outline = palette["outline"]
    paw_col = (255, 255, 255, 255) if palette.get("white_paws") else base
    has_sunglasses = palette.get("sunglasses", False)
    has_collar = palette.get("collar", False)

    # -------------------------------------------------------------
    # 1. STATE: SLEEP / LOAF (Flat resting on floor)
    # -------------------------------------------------------------
    if state == "sleep":
        bob = 1 if (frame_idx % 2 == 1) else 0
        y_off = 17 + bob

        # Slender Loaf Body
        draw_rect(d, 6, y_off + 2, 25, y_off + 9, fill=base, outline=outline)
        # Belly underside
        d.line([(10, y_off + 8), (20, y_off + 8)], fill=belly, width=1)
        # Body stripes
        d.line([(14, y_off + 2), (14, y_off + 6)], fill=stripe, width=1)
        d.line([(19, y_off + 2), (19, y_off + 6)], fill=stripe, width=1)

        # Head resting flat on left
        draw_rect(d, 4, y_off, 14, y_off + 7, fill=base, outline=outline)
        # Pointy ears
        d.polygon([(5, y_off), (7, y_off - 3), (9, y_off)], fill=base, outline=outline)
        d.polygon([(10, y_off), (12, y_off - 3), (14, y_off)], fill=base, outline=outline)
        draw_pixel(d, 7, y_off - 1, inner_ear)
        draw_pixel(d, 12, y_off - 1, inner_ear)

        # Tail curled back
        d.line([(25, y_off + 7), (28, y_off + 5)], fill=outline, width=2)
        d.line([(28, y_off + 5), (28, y_off + 3)], fill=outline, width=2)

        if has_collar:
            d.line([(11, y_off + 2), (13, y_off + 6)], fill=(0, 180, 216, 255), width=2)

        # Sleeping eyes (- -) or shades
        if has_sunglasses:
            draw_sunglasses(d, 4, y_off, glint=False)
        else:
            d.line([(6, y_off + 3), (8, y_off + 3)], fill=outline, width=1)
            d.line([(10, y_off + 3), (12, y_off + 3)], fill=outline, width=1)
            draw_pixel(d, 9, y_off + 5, nose_col)

        # Floating Zzz particles
        z = frame_idx % 4
        if z >= 1:
            draw_pixel(d, 23 + z, 13 - z * 2, (100, 160, 255, 220))
            draw_pixel(d, 24 + z, 13 - z * 2, (100, 160, 255, 220))
        if z >= 2:
            draw_pixel(d, 26, 6, (120, 180, 255, 255))
            draw_pixel(d, 27, 6, (120, 180, 255, 255))

    # -------------------------------------------------------------
    # 2. STATE: WORK / KNEADING / TYPING
    # -------------------------------------------------------------
    elif state in ["work", "knead", "typing"]:
        paw_left = (frame_idx % 2 == 0)

        # Mini Laptop on Desk
        draw_rect(d, 3, 23, 29, 27, fill=(65, 75, 90, 255), outline=outline)
        d.polygon([(5, 23), (8, 17), (24, 17), (27, 23)], fill=(120, 135, 155, 255), outline=outline)
        # Code glow
        d.line([(11, 19), (21, 19)], fill=(46, 204, 113, 255), width=1)
        d.line([(10, 21), (18, 21)], fill=(52, 152, 219, 255), width=1)

        # Slender Cat Body
        draw_rect(d, 10, 10, 22, 23, fill=base, outline=outline)
        draw_rect(d, 13, 14, 19, 22, fill=belly)

        # Head
        head_x, head_y = 9, 3
        draw_rect(d, head_x, head_y, head_x + 14, head_y + 9, fill=base, outline=outline)
        # Pointy Ears
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 6, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 8, head_y), (head_x + 11, head_y - 3), (head_x + 13, head_y)], fill=base, outline=outline)
        draw_pixel(d, head_x + 3, head_y - 1, inner_ear)
        draw_pixel(d, head_x + 11, head_y - 1, inner_ear)

        # Cheeks
        draw_pixel(d, head_x - 1, head_y + 4, outline)
        draw_pixel(d, head_x + 15, head_y + 4, outline)

        if has_collar:
            d.line([(head_x + 2, head_y + 9), (head_x + 12, head_y + 9)], fill=(0, 180, 216, 255), width=2)
            draw_pixel(d, head_x + 7, head_y + 10, (255, 215, 0, 255))

        if has_sunglasses:
            draw_sunglasses(d, head_x + 1, head_y + 1, glint=True)
        else:
            # Concentrated eyes (> <)
            d.line([(head_x + 3, head_y + 4), (head_x + 5, head_y + 5)], fill=outline, width=1)
            d.line([(head_x + 3, head_y + 6), (head_x + 5, head_y + 5)], fill=outline, width=1)
            d.line([(head_x + 11, head_y + 4), (head_x + 9, head_y + 5)], fill=outline, width=1)
            d.line([(head_x + 11, head_y + 6), (head_x + 9, head_y + 5)], fill=outline, width=1)
            draw_pixel(d, head_x + 7, head_y + 6, nose_col)

        # Fast Tapping Paws
        l_y = 21 if paw_left else 23
        r_y = 23 if paw_left else 21
        draw_rect(d, 8, l_y, 12, l_y + 3, fill=paw_col, outline=outline)
        draw_rect(d, 20, r_y, 24, r_y + 3, fill=paw_col, outline=outline)

        if frame_idx % 2 == 1:
            draw_pixel(d, 26, 4, (52, 152, 219, 255))

    # -------------------------------------------------------------
    # 3. STATE: WALK (LEFT / RIGHT)
    # -------------------------------------------------------------
    elif state in ["walk_left", "walk_right", "walk"]:
        flip_x = (state == "walk_left")
        step = frame_idx % 4
        bob = 1 if (step in [1, 3]) else 0

        # Slender Torso
        draw_rect(d, 10, 11 - bob, 22, 18 - bob, fill=base, outline=outline)
        d.line([(14, 11 - bob), (14, 15 - bob)], fill=stripe, width=1)
        d.line([(18, 11 - bob), (18, 15 - bob)], fill=stripe, width=1)

        # Head (facing right)
        head_x, head_y = 14, 4 - bob
        draw_rect(d, head_x, head_y, head_x + 12, head_y + 8, fill=base, outline=outline)
        # Pointy ears
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 5, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 7, head_y), (head_x + 9, head_y - 3), (head_x + 11, head_y)], fill=base, outline=outline)
        draw_pixel(d, head_x + 3, head_y - 1, inner_ear)
        draw_pixel(d, head_x + 9, head_y - 1, inner_ear)

        if has_collar:
            d.line([(head_x + 1, head_y + 8), (head_x + 8, head_y + 8)], fill=(0, 180, 216, 255), width=2)

        if has_sunglasses:
            draw_rect(d, head_x + 4, head_y + 3, head_x + 10, head_y + 6, fill=(15, 15, 15, 255))
            draw_pixel(d, head_x + 5, head_y + 4, (255, 255, 255, 255))
        else:
            draw_pixel(d, head_x + 8, head_y + 4, eye_col)
            draw_pixel(d, head_x + 11, head_y + 5, nose_col)

        # Upright S-Curved Tail
        tail_tip = 1 if step in [0, 2] else -1
        d.line([(9, 13 - bob), (6, 12 - bob)], fill=outline, width=2)
        d.line([(6, 12 - bob), (5, 6 - bob + tail_tip)], fill=outline, width=2)
        d.line([(5, 6 - bob + tail_tip), (7, 4 - bob + tail_tip)], fill=outline, width=2)

        # Distinct 4 Straight Pixel Legs with open space
        if step == 0:
            draw_rect(d, 12, 18 - bob, 14, 25, fill=paw_col, outline=outline)  # Front leg forward
            draw_rect(d, 15, 18 - bob, 17, 24, fill=paw_col, outline=outline)  # Front leg back
            draw_rect(d, 18, 18 - bob, 20, 25, fill=paw_col, outline=outline)  # Hind leg forward
            draw_rect(d, 21, 18 - bob, 23, 24, fill=paw_col, outline=outline)  # Hind leg back
        elif step == 1:
            draw_rect(d, 13, 18 - bob, 15, 24, fill=paw_col, outline=outline)
            draw_rect(d, 16, 18 - bob, 18, 25, fill=paw_col, outline=outline)
            draw_rect(d, 19, 18 - bob, 21, 24, fill=paw_col, outline=outline)
            draw_rect(d, 22, 18 - bob, 24, 25, fill=paw_col, outline=outline)
        elif step == 2:
            draw_rect(d, 14, 18 - bob, 16, 25, fill=paw_col, outline=outline)
            draw_rect(d, 17, 18 - bob, 19, 24, fill=paw_col, outline=outline)
            draw_rect(d, 20, 18 - bob, 22, 25, fill=paw_col, outline=outline)
            draw_rect(d, 23, 18 - bob, 25, 24, fill=paw_col, outline=outline)
        else:
            draw_rect(d, 13, 18 - bob, 15, 24, fill=paw_col, outline=outline)
            draw_rect(d, 16, 18 - bob, 18, 25, fill=paw_col, outline=outline)
            draw_rect(d, 19, 18 - bob, 21, 24, fill=paw_col, outline=outline)
            draw_rect(d, 22, 18 - bob, 24, 25, fill=paw_col, outline=outline)

        if flip_x:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # -------------------------------------------------------------
    # 4. STATE: PET / PURR / SITTING UPRIGHT WITH HEART
    # -------------------------------------------------------------
    elif state in ["pet", "purr", "happy"]:
        # Slender Sitting Upright Posture (matching top-middle of reference image!)
        # Torso
        draw_rect(d, 10, 13, 22, 24, fill=base, outline=outline)
        # White chest bib
        draw_rect(d, 13, 16, 19, 23, fill=belly)

        # Head
        head_x, head_y = 9, 5
        draw_rect(d, head_x, head_y, head_x + 14, head_y + 9, fill=base, outline=outline)
        # Pointy ears
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 6, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 8, head_y), (head_x + 11, head_y - 3), (head_x + 13, head_y)], fill=base, outline=outline)
        draw_pixel(d, head_x + 3, head_y - 1, inner_ear)
        draw_pixel(d, head_x + 11, head_y - 1, inner_ear)

        # Cheeks
        draw_pixel(d, head_x - 1, head_y + 4, outline)
        draw_pixel(d, head_x + 15, head_y + 4, outline)

        if has_collar:
            d.line([(head_x + 2, head_y + 9), (head_x + 12, head_y + 9)], fill=(0, 180, 216, 255), width=2)
            draw_pixel(d, head_x + 7, head_y + 10, (255, 215, 0, 255))

        # Tail curled upright at side
        d.line([(22, 20), (25, 18)], fill=outline, width=2)
        d.line([(25, 18), (26, 12)], fill=outline, width=2)
        d.line([(26, 12), (24, 10)], fill=outline, width=2)

        # Happy eyes
        if has_sunglasses:
            draw_sunglasses(d, head_x + 1, head_y + 1, glint=True)
        else:
            # Closed happy smiling lines (_ _)
            d.line([(head_x + 3, head_y + 4), (head_x + 6, head_y + 4)], fill=outline, width=1)
            d.line([(head_x + 8, head_y + 4), (head_x + 11, head_y + 4)], fill=outline, width=1)
            # Blushing pink
            draw_pixel(d, head_x + 2, head_y + 6, (255, 130, 160, 200))
            draw_pixel(d, head_x + 12, head_y + 6, (255, 130, 160, 200))
            draw_pixel(d, head_x + 7, head_y + 6, nose_col)

        # Straight Front Paws
        draw_rect(d, 11, 23, 14, 27, fill=paw_col, outline=outline)
        draw_rect(d, 18, 23, 21, 27, fill=paw_col, outline=outline)

        # Floating Pixel Heart above head (exactly like reference image!)
        h_y = 3 - (frame_idx % 3)
        d.polygon([(14, h_y), (16, h_y - 2), (18, h_y), (16, h_y + 3)], fill=(255, 60, 90, 255))
        d.polygon([(12, h_y), (14, h_y - 2), (16, h_y), (14, h_y + 3)], fill=(255, 60, 90, 255))

    # -------------------------------------------------------------
    # 5. STATE: JUMP / CELEBRATE / STRETCH ARCH
    # -------------------------------------------------------------
    elif state in ["jump", "celebrate"]:
        jump_y = 5 if frame_idx in [1, 2] else 1

        # Playful Arching Slender Body (matching bottom-middle of reference!)
        draw_rect(d, 10, 11 - jump_y, 22, 17 - jump_y, fill=base, outline=outline)

        head_x, head_y = 14, 4 - jump_y
        draw_rect(d, head_x, head_y, head_x + 12, head_y + 8, fill=base, outline=outline)
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 5, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 7, head_y), (head_x + 9, head_y - 3), (head_x + 11, head_y)], fill=base, outline=outline)

        if has_collar:
            d.line([(head_x + 1, head_y + 8), (head_x + 8, head_y + 8)], fill=(0, 180, 216, 255), width=2)

        if has_sunglasses:
            draw_sunglasses(d, head_x, head_y + 1, glint=True)
        else:
            # Wide excited open eyes
            draw_rect(d, head_x + 3, head_y + 3, head_x + 5, head_y + 5, fill=eye_col)
            draw_rect(d, head_x + 7, head_y + 3, head_x + 9, head_y + 5, fill=eye_col)
            draw_pixel(d, head_x + 6, head_y + 6, nose_col)

        # High Upright Tail
        d.line([(10, 12 - jump_y), (8, 6 - jump_y)], fill=outline, width=2)
        d.line([(8, 6 - jump_y), (10, 2 - jump_y)], fill=outline, width=2)

        # Extended legs
        draw_rect(d, 12, 17 - jump_y, 14, 25 - jump_y, fill=paw_col, outline=outline)
        draw_rect(d, 18, 17 - jump_y, 20, 25 - jump_y, fill=paw_col, outline=outline)

        # Sparkles around
        if frame_idx % 2 == 1:
            draw_pixel(d, 4, 6, (255, 215, 0, 255))
            draw_pixel(d, 27, 4, (255, 215, 0, 255))
            draw_pixel(d, 28, 5, (255, 215, 0, 255))

    # -------------------------------------------------------------
    # 6. STATE: THINKING
    # -------------------------------------------------------------
    elif state in ["thinking", "alert"]:
        draw_rect(d, 10, 13, 22, 24, fill=base, outline=outline)
        draw_rect(d, 13, 16, 19, 23, fill=belly)

        # Tilted Head
        head_x, head_y = 11, 4
        draw_rect(d, head_x, head_y, head_x + 13, head_y + 9, fill=base, outline=outline)
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 5, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 8, head_y), (head_x + 11, head_y - 2), (head_x + 13, head_y + 2)], fill=base, outline=outline)

        if has_collar:
            d.line([(head_x + 2, head_y + 9), (head_x + 11, head_y + 9)], fill=(0, 180, 216, 255), width=2)

        if has_sunglasses:
            draw_sunglasses(d, head_x + 1, head_y + 1, glint=True)
        else:
            # Big curious dot eyes looking up
            draw_pixel(d, head_x + 4, head_y + 3, pupil_col)
            draw_pixel(d, head_x + 9, head_y + 3, pupil_col)
            draw_pixel(d, head_x + 6, head_y + 6, nose_col)

        # Front paws
        draw_rect(d, 11, 23, 14, 27, fill=paw_col, outline=outline)
        draw_rect(d, 18, 23, 21, 27, fill=paw_col, outline=outline)

        # Animated dots above
        dot_count = (frame_idx % 3) + 1
        for i in range(dot_count):
            draw_pixel(d, 14 + i * 3, 1, (52, 152, 219, 255))

    # -------------------------------------------------------------
    # 7. STATE: DRAG (Dangling with slender wiggling legs)
    # -------------------------------------------------------------
    elif state in ["drag", "picked_up", "dangle"]:
        leg_step = frame_idx % 4

        # Slender Suspended Body
        draw_rect(d, 11, 9, 21, 21, fill=base, outline=outline)
        draw_rect(d, 13, 12, 19, 19, fill=belly)

        # Head at top
        head_x, head_y = 9, 1
        draw_rect(d, head_x, head_y, head_x + 14, head_y + 8, fill=base, outline=outline)
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 2), (head_x + 5, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 9, head_y), (head_x + 11, head_y - 2), (head_x + 13, head_y)], fill=base, outline=outline)

        if has_collar:
            d.line([(head_x + 2, head_y + 8), (head_x + 12, head_y + 8)], fill=(0, 180, 216, 255), width=2)

        if has_sunglasses:
            draw_sunglasses(d, head_x + 1, head_y + 1, glint=True)
        else:
            # Surprised wide dot eyes
            draw_pixel(d, head_x + 4, head_y + 3, pupil_col)
            draw_pixel(d, head_x + 10, head_y + 3, pupil_col)
            draw_pixel(d, head_x + 7, head_y + 5, nose_col)

        # Tail swaying
        tail_x = 24 if leg_step in [0, 1] else 26
        d.line([(21, 15), (tail_x, 11)], fill=outline, width=2)
        d.line([(tail_x, 11), (tail_x - 1, 6)], fill=outline, width=2)

        # 4 Slender dangling legs wiggling
        if leg_step == 0:
            draw_rect(d, 11, 21, 13, 27, fill=paw_col, outline=outline)
            draw_rect(d, 15, 21, 17, 26, fill=paw_col, outline=outline)
            draw_rect(d, 19, 21, 21, 28, fill=paw_col, outline=outline)
        elif leg_step == 1:
            draw_rect(d, 11, 21, 13, 26, fill=paw_col, outline=outline)
            draw_rect(d, 15, 21, 17, 28, fill=paw_col, outline=outline)
            draw_rect(d, 19, 21, 21, 26, fill=paw_col, outline=outline)
        elif leg_step == 2:
            draw_rect(d, 11, 21, 13, 28, fill=paw_col, outline=outline)
            draw_rect(d, 15, 21, 17, 26, fill=paw_col, outline=outline)
            draw_rect(d, 19, 21, 21, 27, fill=paw_col, outline=outline)
        else:
            draw_rect(d, 11, 21, 13, 27, fill=paw_col, outline=outline)
            draw_rect(d, 15, 21, 17, 27, fill=paw_col, outline=outline)
            draw_rect(d, 19, 21, 21, 27, fill=paw_col, outline=outline)

        if frame_idx % 2 == 1:
            draw_pixel(d, 5, 12, (200, 225, 255, 200))
            draw_pixel(d, 27, 12, (200, 225, 255, 200))

    # -------------------------------------------------------------
    # 8. STATE: LAND / DROP (Squish & Spring bounce)
    # -------------------------------------------------------------
    elif state in ["land", "drop"]:
        if frame_idx in [0, 1]:
            # Squished flat posture
            draw_rect(d, 8, 16, 24, 24, fill=base, outline=outline)
            draw_rect(d, 7, 10, 20, 17, fill=base, outline=outline)
            if has_sunglasses:
                draw_sunglasses(d, 7, 10, glint=True)
            else:
                d.line([(9, 13), (12, 14)], fill=outline, width=1)
                d.line([(17, 13), (14, 14)], fill=outline, width=1)
            draw_rect(d, 8, 24, 12, 27, fill=paw_col, outline=outline)
            draw_rect(d, 20, 24, 24, 27, fill=paw_col, outline=outline)
        else:
            # Springing back
            draw_rect(d, 10, 12, 22, 20, fill=base, outline=outline)
            draw_rect(d, 6, 6, 18, 14, fill=base, outline=outline)
            draw_rect(d, 12, 20, 14, 26, fill=paw_col, outline=outline)
            draw_rect(d, 19, 20, 21, 26, fill=paw_col, outline=outline)

    # -------------------------------------------------------------
    # 9. DEFAULT: IDLE (Slender Standing Stance with S-Tail & Defined Legs)
    # -------------------------------------------------------------
    else:
        blink = (frame_idx == 2)
        tail_phase = 1 if (frame_idx in [1, 2]) else -1

        # Slender Torso (Matching exact reference image: center, left-middle, etc.)
        draw_rect(d, 10, 11, 22, 19, fill=base, outline=outline)
        d.line([(14, 11), (14, 15)], fill=stripe, width=1)
        d.line([(18, 11), (18, 15)], fill=stripe, width=1)

        # Head (Slender box shape with pointy ears & cheek whiskers)
        head_x, head_y = 5, 5
        draw_rect(d, head_x, head_y, head_x + 12, head_y + 9, fill=base, outline=outline)
        # Pointy ears
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 5, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 7, head_y), (head_x + 9, head_y - 3), (head_x + 11, head_y)], fill=base, outline=outline)
        draw_pixel(d, head_x + 3, head_y - 1, inner_ear)
        draw_pixel(d, head_x + 9, head_y - 1, inner_ear)

        # Cheek whiskers (protruding 1-2px)
        draw_pixel(d, head_x - 1, head_y + 4, outline)
        draw_pixel(d, head_x + 13, head_y + 4, outline)

        if has_collar:
            d.line([(head_x + 4, head_y + 9), (head_x + 11, head_y + 9)], fill=(0, 180, 216, 255), width=2)
            draw_pixel(d, head_x + 7, head_y + 10, (255, 215, 0, 255))

        # Upright S-Curved Tail rising from back
        tail_bend = 1 if tail_phase > 0 else 0
        d.line([(22, 14), (25, 12)], fill=outline, width=2)
        d.line([(25, 12), (26, 7 + tail_bend)], fill=outline, width=2)
        d.line([(26, 7 + tail_bend), (24, 5 + tail_bend)], fill=outline, width=2)

        # Face Rendering:
        if has_sunglasses:
            draw_sunglasses(d, head_x, head_y + 1, glint=(frame_idx in [0, 1, 3]))
        else:
            if blink:
                # Closed line eyes (- -)
                d.line([(head_x + 3, head_y + 4), (head_x + 5, head_y + 4)], fill=outline, width=1)
                d.line([(head_x + 7, head_y + 4), (head_x + 9, head_y + 4)], fill=outline, width=1)
            else:
                # Expressive clean dot eyes (• •)
                draw_pixel(d, head_x + 4, head_y + 4, pupil_col)
                draw_pixel(d, head_x + 8, head_y + 4, pupil_col)
            draw_pixel(d, head_x + 6, head_y + 6, nose_col)

        # 4 Defined Straight Pixel Legs with open space between front & back
        draw_rect(d, 12, 19, 14, 26, fill=paw_col, outline=outline)  # Front leg left
        draw_rect(d, 15, 19, 17, 26, fill=paw_col, outline=outline)  # Front leg right
        draw_rect(d, 19, 19, 21, 26, fill=paw_col, outline=outline)  # Back leg left
        draw_rect(d, 22, 19, 24, 26, fill=paw_col, outline=outline)  # Back leg right

    scaled_size = (SPRITE_GRID_SIZE * SCALE_FACTOR, SPRITE_GRID_SIZE * SCALE_FACTOR)
    crisp_img = img.resize(scaled_size, Image.Resampling.NEAREST)
    return crisp_img


def render_cat_frame(skin_key="boss_oyen", state="idle", frame_idx=0):
    palette = PALETTES.get(skin_key, PALETTES["boss_oyen"])
    return render_slender_cat(palette, state, frame_idx)


def pregenerate_all_sprites(output_dir="assets/sprites"):
    os.makedirs(output_dir, exist_ok=True)
    states = ["idle", "walk_left", "walk_right", "sleep", "work", "pet", "jump", "thinking", "drag", "land"]
    for skin in PALETTES.keys():
        skin_dir = os.path.join(output_dir, skin)
        os.makedirs(skin_dir, exist_ok=True)
        for state in states:
            for frame in range(4):
                img = render_cat_frame(skin, state, frame)
                path = os.path.join(skin_dir, f"{state}_{frame}.png")
                img.save(path)
    print(f"[SpriteGen] Generated all pixel art sprites in slender/retro style for {len(PALETTES)} characters in '{output_dir}'.")


if __name__ == "__main__":
    pregenerate_all_sprites()
