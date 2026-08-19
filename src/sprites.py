"""
Pixel-Art Cat Sprite Generator & Manager (Exact Retro Reference Style)
Accurately models the exact paired-leg pillars [ | ] ___ [ | ], S-curved tail,
cheek whiskers, boxy torso, and sunglasses as shown in the reference image.
Zero external network required - 100% offline & local.
"""

from PIL import Image, ImageDraw
import os

PALETTES = {
    "boss_oyen": {
        "name": "Boss Oyen (Kacamata Hitam 🕶️)",
        "base": (255, 150, 50, 255),       # Warm saturated orange (exact match)
        "stripe": (210, 85, 10, 255),       # Dark orange stripes
        "belly": (255, 185, 100, 255),     # Light cream
        "inner_ear": (240, 110, 40, 255),
        "eye": (15, 15, 15, 255),
        "pupil": (15, 15, 15, 255),
        "nose": (220, 70, 20, 255),        # Reddish orange nose dot
        "outline": (30, 20, 15, 255),      # Crisp dark pixel outline
        "sunglasses": True,
        "collar": False,
        "white_paws": False
    },
    "mochi": {
        "name": "Si Kalung Biru (Mochi Grey Kitten)",
        "base": (160, 168, 178, 255),      # Soft cool grey
        "stripe": (105, 115, 128, 255),
        "belly": (255, 255, 255, 255),     # Pure white chest
        "inner_ear": (255, 150, 175, 255),
        "eye": (25, 25, 30, 255),
        "pupil": (25, 25, 30, 255),
        "nose": (255, 120, 150, 255),
        "outline": (25, 28, 35, 255),
        "sunglasses": False,
        "collar": True,
        "white_paws": True
    },
    "oyen": {
        "name": "Si Oyen (Orange Tabby)",
        "base": (255, 150, 50, 255),
        "stripe": (210, 85, 10, 255),
        "belly": (255, 220, 150, 255),
        "inner_ear": (255, 150, 170, 255),
        "eye": (46, 204, 113, 255),
        "pupil": (20, 20, 20, 255),
        "nose": (220, 70, 20, 255),
        "outline": (30, 20, 15, 255),
        "sunglasses": False,
        "collar": False,
        "white_paws": False
    },
    "shiro": {
        "name": "Si Putih (Snow White)",
        "base": (252, 253, 255, 255),
        "stripe": (215, 222, 232, 255),
        "belly": (255, 255, 255, 255),
        "inner_ear": (255, 165, 185, 255),
        "eye": (52, 152, 219, 255),
        "pupil": (20, 20, 20, 255),
        "nose": (255, 130, 155, 255),
        "outline": (45, 50, 60, 255),
        "sunglasses": False,
        "collar": False,
        "white_paws": False
    },
    "tuxedo": {
        "name": "Si Tuxedo (Black & White)",
        "base": (42, 45, 54, 255),
        "stripe": (25, 28, 35, 255),
        "belly": (255, 255, 255, 255),
        "inner_ear": (255, 150, 170, 255),
        "eye": (46, 204, 113, 255),
        "pupil": (20, 20, 20, 255),
        "nose": (255, 130, 150, 255),
        "outline": (18, 20, 25, 255),
        "sunglasses": False,
        "collar": False,
        "white_paws": True
    },
    "calico": {
        "name": "Belang Tiga (Calico)",
        "base": (250, 250, 252, 255),
        "stripe": (230, 126, 34, 255),
        "dark_patch": (52, 73, 94, 255),
        "belly": (255, 255, 255, 255),
        "inner_ear": (255, 150, 170, 255),
        "eye": (241, 196, 15, 255),
        "pupil": (20, 20, 20, 255),
        "nose": (255, 130, 150, 255),
        "outline": (30, 30, 40, 255),
        "sunglasses": False,
        "collar": False,
        "white_paws": True
    },
    "grey": {
        "name": "Abu-Abu (Grey Tabby)",
        "base": (150, 162, 172, 255),
        "stripe": (90, 102, 115, 255),
        "belly": (225, 232, 240, 255),
        "inner_ear": (255, 160, 180, 255),
        "eye": (52, 152, 219, 255),
        "pupil": (20, 20, 20, 255),
        "nose": (255, 130, 150, 255),
        "outline": (35, 40, 50, 255),
        "sunglasses": False,
        "collar": False,
        "white_paws": False
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


def draw_retro_sunglasses(draw, head_x, head_y, glint=True):
    """Draws pixel-perfect black sunglasses as in the user's reference image."""
    # Left & Right lens polygon
    draw.rectangle([head_x + 1, head_y + 4, head_x + 6, head_y + 8], fill=(15, 15, 15, 255))
    draw.rectangle([head_x + 8, head_y + 4, head_x + 13, head_y + 8], fill=(15, 15, 15, 255))
    # Center bridge
    draw.line([(head_x + 6, head_y + 5), (head_x + 8, head_y + 5)], fill=(15, 15, 15, 255), width=1)
    if glint:
        draw_pixel(draw, head_x + 2, head_y + 5, (255, 255, 255, 255))
        draw_pixel(draw, head_x + 9, head_y + 5, (255, 255, 255, 255))


def draw_paired_retro_legs(draw, base_color, outline_color, paw_color=None, offset_y=0, walk_phase=0):
    """
    Renders the exact paired legs [ | ] ___ [ | ] from the reference image:
    - Front leg pair: x=7..13 with center divider at x=10
    - Back leg pair: x=18..24 with center divider at x=21
    - Open underbelly gap: x=14..17
    - Flat bottom paws with black outline baseline
    """
    paw = paw_color if paw_color else base_color
    top_y = 19 + offset_y
    bot_y = 26 + offset_y

    # Underbelly bridge line above negative space
    draw.line([(13, top_y), (18, top_y)], fill=outline_color, width=1)

    if walk_phase == 0:
        # Standing / Idle exact pose:
        # 1. Front Legs Block (x=7 to 13)
        draw_rect(draw, 7, top_y, 13, bot_y, fill=paw, outline=outline_color)
        # Center vertical divider between front-left & front-right leg
        draw.line([(10, top_y + 1), (10, bot_y)], fill=outline_color, width=1)

        # 2. Back Legs Block (x=18 to 24)
        draw_rect(draw, 18, top_y, 24, bot_y, fill=paw, outline=outline_color)
        # Center vertical divider between back-left & back-right leg
        draw.line([(21, top_y + 1), (21, bot_y)], fill=outline_color, width=1)

    elif walk_phase == 1:
        # Step phase 1
        draw_rect(draw, 8, top_y, 14, bot_y, fill=paw, outline=outline_color)
        draw.line([(11, top_y + 1), (11, bot_y - 1)], fill=outline_color, width=1)

        draw_rect(draw, 17, top_y, 23, bot_y, fill=paw, outline=outline_color)
        draw.line([(20, top_y + 1), (20, bot_y)], fill=outline_color, width=1)

    elif walk_phase == 2:
        # Step phase 2
        draw_rect(draw, 6, top_y, 12, bot_y, fill=paw, outline=outline_color)
        draw.line([(9, top_y + 1), (9, bot_y)], fill=outline_color, width=1)

        draw_rect(draw, 19, top_y, 25, bot_y, fill=paw, outline=outline_color)
        draw.line([(22, top_y + 1), (22, bot_y - 1)], fill=outline_color, width=1)

    else:
        # Step phase 3
        draw_rect(draw, 7, top_y, 13, bot_y, fill=paw, outline=outline_color)
        draw.line([(10, top_y + 1), (10, bot_y)], fill=outline_color, width=1)

        draw_rect(draw, 18, top_y, 24, bot_y, fill=paw, outline=outline_color)
        draw.line([(21, top_y + 1), (21, bot_y)], fill=outline_color, width=1)


def render_exact_cat(palette, state="idle", frame_idx=0):
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
    # 1. STATE: SLEEP / LOAF
    # -------------------------------------------------------------
    if state == "sleep":
        bob = 1 if (frame_idx % 2 == 1) else 0
        y_off = 17 + bob

        # Slender Loaf Body resting flat on ground
        draw_rect(d, 6, y_off + 2, 25, y_off + 9, fill=base, outline=outline)
        d.line([(10, y_off + 8), (21, y_off + 8)], fill=belly, width=1)
        d.line([(15, y_off + 2), (15, y_off + 6)], fill=stripe, width=1)
        d.line([(20, y_off + 2), (20, y_off + 6)], fill=stripe, width=1)

        # Head flat
        draw_rect(d, 4, y_off, 14, y_off + 7, fill=base, outline=outline)
        d.polygon([(5, y_off), (7, y_off - 3), (9, y_off)], fill=base, outline=outline)
        d.polygon([(10, y_off), (12, y_off - 3), (14, y_off)], fill=base, outline=outline)
        draw_pixel(d, 7, y_off - 1, inner_ear)
        draw_pixel(d, 12, y_off - 1, inner_ear)

        # Tail curled
        d.line([(25, y_off + 7), (28, y_off + 5)], fill=outline, width=2)
        d.line([(28, y_off + 5), (28, y_off + 2)], fill=outline, width=2)

        if has_collar:
            d.line([(11, y_off + 2), (13, y_off + 6)], fill=(0, 180, 216, 255), width=2)

        if has_sunglasses:
            draw_retro_sunglasses(d, 3, y_off - 1, glint=False)
        else:
            d.line([(6, y_off + 3), (8, y_off + 3)], fill=outline, width=1)
            d.line([(10, y_off + 3), (12, y_off + 3)], fill=outline, width=1)
            draw_pixel(d, 9, y_off + 5, nose_col)

        # Zzz
        z = frame_idx % 4
        if z >= 1:
            draw_pixel(d, 23 + z, 13 - z * 2, (100, 160, 255, 220))
            draw_pixel(d, 24 + z, 13 - z * 2, (100, 160, 255, 220))
        if z >= 2:
            draw_pixel(d, 26, 6, (120, 180, 255, 255))
            draw_pixel(d, 27, 6, (120, 180, 255, 255))

    # -------------------------------------------------------------
    # 2. STATE: WORK / TYPING
    # -------------------------------------------------------------
    elif state in ["work", "knead", "typing"]:
        paw_left = (frame_idx % 2 == 0)

        # Mini Laptop
        draw_rect(d, 3, 23, 29, 27, fill=(65, 75, 90, 255), outline=outline)
        d.polygon([(5, 23), (8, 17), (24, 17), (27, 23)], fill=(120, 135, 155, 255), outline=outline)
        d.line([(11, 19), (21, 19)], fill=(46, 204, 113, 255), width=1)
        d.line([(10, 21), (18, 21)], fill=(52, 152, 219, 255), width=1)

        # Body
        draw_rect(d, 10, 10, 22, 23, fill=base, outline=outline)
        draw_rect(d, 13, 14, 19, 22, fill=belly)

        # Head
        head_x, head_y = 8, 3
        draw_rect(d, head_x, head_y, head_x + 15, head_y + 9, fill=base, outline=outline)
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 6, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 9, head_y), (head_x + 12, head_y - 3), (head_x + 14, head_y)], fill=base, outline=outline)
        draw_pixel(d, head_x + 3, head_y - 1, inner_ear)
        draw_pixel(d, head_x + 12, head_y - 1, inner_ear)

        # Cheek whiskers
        draw_pixel(d, head_x - 1, head_y + 4, outline)
        draw_pixel(d, head_x + 16, head_y + 4, outline)

        if has_collar:
            d.line([(head_x + 3, head_y + 9), (head_x + 13, head_y + 9)], fill=(0, 180, 216, 255), width=2)
            draw_pixel(d, head_x + 8, head_y + 10, (255, 215, 0, 255))

        if has_sunglasses:
            draw_retro_sunglasses(d, head_x + 1, head_y + 1, glint=True)
        else:
            d.line([(head_x + 3, head_y + 4), (head_x + 5, head_y + 5)], fill=outline, width=1)
            d.line([(head_x + 3, head_y + 6), (head_x + 5, head_y + 5)], fill=outline, width=1)
            d.line([(head_x + 12, head_y + 4), (head_x + 10, head_y + 5)], fill=outline, width=1)
            d.line([(head_x + 12, head_y + 6), (head_x + 10, head_y + 5)], fill=outline, width=1)
            draw_pixel(d, head_x + 7, head_y + 6, nose_col)

        # Tapping paws
        l_y = 21 if paw_left else 23
        r_y = 23 if paw_left else 21
        draw_rect(d, 8, l_y, 12, l_y + 3, fill=paw_col, outline=outline)
        draw_rect(d, 20, r_y, 24, r_y + 3, fill=paw_col, outline=outline)

    # -------------------------------------------------------------
    # 3. STATE: WALK (LEFT / RIGHT)
    # -------------------------------------------------------------
    elif state in ["walk_left", "walk_right", "walk"]:
        flip_x = (state == "walk_left")
        step = frame_idx % 4
        bob = 1 if (step in [1, 3]) else 0

        # Torso
        draw_rect(d, 7, 11 - bob, 24, 19 - bob, fill=base, outline=outline)
        d.line([(13, 11 - bob), (13, 16 - bob)], fill=stripe, width=1)
        d.line([(19, 11 - bob), (19, 16 - bob)], fill=stripe, width=1)

        # Head
        head_x, head_y = 4, 4 - bob
        draw_rect(d, head_x, head_y, head_x + 12, head_y + 9, fill=base, outline=outline)
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 5, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 7, head_y), (head_x + 9, head_y - 3), (head_x + 11, head_y)], fill=base, outline=outline)
        draw_pixel(d, head_x + 3, head_y - 1, inner_ear)
        draw_pixel(d, head_x + 9, head_y - 1, inner_ear)

        # Whiskers
        draw_pixel(d, head_x - 1, head_y + 3, outline)
        draw_pixel(d, head_x - 1, head_y + 6, outline)

        if has_collar:
            d.line([(head_x + 3, head_y + 9), (head_x + 10, head_y + 9)], fill=(0, 180, 216, 255), width=2)

        if has_sunglasses:
            draw_retro_sunglasses(d, head_x - 1, head_y + 1, glint=True)
        else:
            draw_pixel(d, head_x + 4, head_y + 5, pupil_col)
            draw_pixel(d, head_x + 8, head_y + 5, pupil_col)
            draw_pixel(d, head_x + 6, head_y + 7, nose_col)

        # S-Curved Tail
        tail_bob = 1 if step in [0, 2] else -1
        d.line([(24, 14 - bob), (27, 11 - bob)], fill=outline, width=2)
        d.line([(27, 11 - bob), (28, 6 - bob + tail_bob)], fill=outline, width=2)
        d.line([(28, 6 - bob + tail_bob), (26, 4 - bob + tail_bob)], fill=outline, width=2)

        # Paired Retro Legs with walk step
        draw_paired_retro_legs(d, base, outline, paw_col, offset_y=-bob, walk_phase=step)

        if flip_x:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # -------------------------------------------------------------
    # 4. STATE: PET / PURR / SITTING UPRIGHT WITH HEART
    # -------------------------------------------------------------
    elif state in ["pet", "purr", "happy"]:
        draw_rect(d, 10, 13, 22, 23, fill=base, outline=outline)
        draw_rect(d, 13, 16, 19, 22, fill=belly)

        head_x, head_y = 8, 5
        draw_rect(d, head_x, head_y, head_x + 15, head_y + 9, fill=base, outline=outline)
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 6, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 9, head_y), (head_x + 12, head_y - 3), (head_x + 14, head_y)], fill=base, outline=outline)
        draw_pixel(d, head_x + 3, head_y - 1, inner_ear)
        draw_pixel(d, head_x + 12, head_y - 1, inner_ear)

        # Whiskers
        draw_pixel(d, head_x - 1, head_y + 4, outline)
        draw_pixel(d, head_x + 16, head_y + 4, outline)

        if has_collar:
            d.line([(head_x + 3, head_y + 9), (head_x + 13, head_y + 9)], fill=(0, 180, 216, 255), width=2)
            draw_pixel(d, head_x + 8, head_y + 10, (255, 215, 0, 255))

        # Tail curled at side
        d.line([(22, 20), (26, 17)], fill=outline, width=2)
        d.line([(26, 17), (27, 11)], fill=outline, width=2)
        d.line([(27, 11), (25, 9)], fill=outline, width=2)

        if has_sunglasses:
            draw_retro_sunglasses(d, head_x + 1, head_y + 1, glint=True)
        else:
            d.line([(head_x + 3, head_y + 4), (head_x + 6, head_y + 4)], fill=outline, width=1)
            d.line([(head_x + 9, head_y + 4), (head_x + 12, head_y + 4)], fill=outline, width=1)
            draw_pixel(d, head_x + 2, head_y + 6, (255, 130, 160, 200))
            draw_pixel(d, head_x + 13, head_y + 6, (255, 130, 160, 200))
            draw_pixel(d, head_x + 7, head_y + 6, nose_col)

        # Paired sitting front paws
        draw_rect(d, 10, 23, 14, 27, fill=paw_col, outline=outline)
        draw_rect(d, 18, 23, 22, 27, fill=paw_col, outline=outline)

        # Floating Heart
        h_y = 3 - (frame_idx % 3)
        d.polygon([(15, h_y), (17, h_y - 2), (19, h_y), (17, h_y + 3)], fill=(255, 60, 90, 255))
        d.polygon([(13, h_y), (15, h_y - 2), (17, h_y), (15, h_y + 3)], fill=(255, 60, 90, 255))

    # -------------------------------------------------------------
    # 5. STATE: JUMP / CELEBRATE
    # -------------------------------------------------------------
    elif state in ["jump", "celebrate"]:
        jump_y = 5 if frame_idx in [1, 2] else 1

        draw_rect(d, 7, 11 - jump_y, 24, 18 - jump_y, fill=base, outline=outline)

        head_x, head_y = 4, 4 - jump_y
        draw_rect(d, head_x, head_y, head_x + 12, head_y + 9, fill=base, outline=outline)
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 5, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 7, head_y), (head_x + 9, head_y - 3), (head_x + 11, head_y)], fill=base, outline=outline)

        if has_collar:
            d.line([(head_x + 2, head_y + 9), (head_x + 10, head_y + 9)], fill=(0, 180, 216, 255), width=2)

        if has_sunglasses:
            draw_retro_sunglasses(d, head_x - 1, head_y + 1, glint=True)
        else:
            draw_rect(d, head_x + 3, head_y + 4, head_x + 5, head_y + 6, fill=eye_col)
            draw_rect(d, head_x + 7, head_y + 4, head_x + 9, head_y + 6, fill=eye_col)
            draw_pixel(d, head_x + 6, head_y + 7, nose_col)

        # Upright tail
        d.line([(24, 13 - jump_y), (27, 8 - jump_y)], fill=outline, width=2)
        d.line([(27, 8 - jump_y), (26, 3 - jump_y)], fill=outline, width=2)

        # Extended paired legs
        draw_rect(d, 8, 18 - jump_y, 14, 25 - jump_y, fill=paw_col, outline=outline)
        d.line([(11, 19 - jump_y), (11, 25 - jump_y)], fill=outline, width=1)
        draw_rect(d, 17, 18 - jump_y, 23, 25 - jump_y, fill=paw_col, outline=outline)
        d.line([(20, 19 - jump_y), (20, 25 - jump_y)], fill=outline, width=1)

        if frame_idx % 2 == 1:
            draw_pixel(d, 3, 5, (255, 215, 0, 255))
            draw_pixel(d, 28, 4, (255, 215, 0, 255))

    # -------------------------------------------------------------
    # 6. STATE: THINKING
    # -------------------------------------------------------------
    elif state in ["thinking", "alert"]:
        draw_rect(d, 7, 11, 24, 19, fill=base, outline=outline)

        # Tilted Head looking up
        head_x, head_y = 6, 4
        draw_rect(d, head_x, head_y, head_x + 12, head_y + 9, fill=base, outline=outline)
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 5, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 7, head_y), (head_x + 10, head_y - 2), (head_x + 12, head_y + 2)], fill=base, outline=outline)

        if has_collar:
            d.line([(head_x + 2, head_y + 9), (head_x + 10, head_y + 9)], fill=(0, 180, 216, 255), width=2)

        if has_sunglasses:
            draw_retro_sunglasses(d, head_x, head_y + 1, glint=True)
        else:
            draw_pixel(d, head_x + 4, head_y + 4, pupil_col)
            draw_pixel(d, head_x + 8, head_y + 4, pupil_col)
            draw_pixel(d, head_x + 6, head_y + 6, nose_col)

        # Tail
        d.line([(24, 14), (27, 11)], fill=outline, width=2)
        d.line([(27, 11), (28, 7)], fill=outline, width=2)

        # Paired legs
        draw_paired_retro_legs(d, base, outline, paw_col, offset_y=0, walk_phase=0)

        # Animated dots
        dot_count = (frame_idx % 3) + 1
        for i in range(dot_count):
            draw_pixel(d, 10 + i * 3, 1, (52, 152, 219, 255))

    # -------------------------------------------------------------
    # 7. STATE: DRAG (Dangling with 4 vertical hanging legs)
    # -------------------------------------------------------------
    elif state in ["drag", "picked_up", "dangle"]:
        leg_step = frame_idx % 4

        # Suspended Body
        draw_rect(d, 10, 9, 22, 21, fill=base, outline=outline)
        draw_rect(d, 13, 12, 19, 19, fill=belly)

        # Head at top
        head_x, head_y = 8, 1
        draw_rect(d, head_x, head_y, head_x + 15, head_y + 8, fill=base, outline=outline)
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 2), (head_x + 5, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 10, head_y), (head_x + 12, head_y - 2), (head_x + 14, head_y)], fill=base, outline=outline)

        if has_collar:
            d.line([(head_x + 3, head_y + 8), (head_x + 13, head_y + 8)], fill=(0, 180, 216, 255), width=2)

        if has_sunglasses:
            draw_retro_sunglasses(d, head_x + 1, head_y + 1, glint=True)
        else:
            draw_pixel(d, head_x + 4, head_y + 3, pupil_col)
            draw_pixel(d, head_x + 11, head_y + 3, pupil_col)
            draw_pixel(d, head_x + 7, head_y + 5, nose_col)

        # Tail swaying
        tail_x = 24 if leg_step in [0, 1] else 26
        d.line([(22, 15), (tail_x, 11)], fill=outline, width=2)
        d.line([(tail_x, 11), (tail_x - 1, 6)], fill=outline, width=2)

        # 4 Straight vertical legs dangling
        if leg_step == 0:
            draw_rect(d, 10, 21, 12, 27, fill=paw_col, outline=outline)
            draw_rect(d, 13, 21, 15, 26, fill=paw_col, outline=outline)
            draw_rect(d, 17, 21, 19, 28, fill=paw_col, outline=outline)
            draw_rect(d, 20, 21, 22, 27, fill=paw_col, outline=outline)
        elif leg_step == 1:
            draw_rect(d, 10, 21, 12, 26, fill=paw_col, outline=outline)
            draw_rect(d, 13, 21, 15, 28, fill=paw_col, outline=outline)
            draw_rect(d, 17, 21, 19, 26, fill=paw_col, outline=outline)
            draw_rect(d, 20, 21, 22, 28, fill=paw_col, outline=outline)
        elif leg_step == 2:
            draw_rect(d, 10, 21, 12, 28, fill=paw_col, outline=outline)
            draw_rect(d, 13, 21, 15, 26, fill=paw_col, outline=outline)
            draw_rect(d, 17, 21, 19, 27, fill=paw_col, outline=outline)
            draw_rect(d, 20, 21, 22, 26, fill=paw_col, outline=outline)
        else:
            draw_rect(d, 10, 21, 12, 27, fill=paw_col, outline=outline)
            draw_rect(d, 13, 21, 15, 27, fill=paw_col, outline=outline)
            draw_rect(d, 17, 21, 19, 27, fill=paw_col, outline=outline)
            draw_rect(d, 20, 21, 22, 27, fill=paw_col, outline=outline)

        if frame_idx % 2 == 1:
            draw_pixel(d, 5, 12, (200, 225, 255, 200))
            draw_pixel(d, 27, 12, (200, 225, 255, 200))

    # -------------------------------------------------------------
    # 8. STATE: LAND / DROP
    # -------------------------------------------------------------
    elif state in ["land", "drop"]:
        if frame_idx in [0, 1]:
            draw_rect(d, 7, 15, 24, 24, fill=base, outline=outline)
            draw_rect(d, 5, 9, 18, 16, fill=base, outline=outline)
            if has_sunglasses:
                draw_retro_sunglasses(d, 5, 9, glint=True)
            else:
                d.line([(8, 12), (11, 13)], fill=outline, width=1)
                d.line([(15, 12), (12, 13)], fill=outline, width=1)
            draw_rect(d, 7, 24, 13, 27, fill=paw_col, outline=outline)
            draw_rect(d, 18, 24, 24, 27, fill=paw_col, outline=outline)
        else:
            draw_rect(d, 7, 11, 24, 19, fill=base, outline=outline)
            head_x, head_y = 4, 4
            draw_rect(d, head_x, head_y, head_x + 12, head_y + 9, fill=base, outline=outline)
            draw_paired_retro_legs(d, base, outline, paw_col, offset_y=0, walk_phase=0)

    # -------------------------------------------------------------
    # 9. DEFAULT: IDLE (Exact match to reference image standing pose!)
    # -------------------------------------------------------------
    else:
        blink = (frame_idx == 2)
        tail_phase = 1 if (frame_idx in [1, 2]) else -1

        # Torso: x=7..24, y=11..19
        draw_rect(d, 7, 11, 24, 19, fill=base, outline=outline)
        # Tabby stripes on back
        d.line([(14, 11), (14, 15)], fill=stripe, width=1)
        d.line([(20, 11), (20, 15)], fill=stripe, width=1)

        # Head: x=4..16, y=4..13 (matching reference image)
        head_x, head_y = 4, 4
        draw_rect(d, head_x, head_y, head_x + 12, head_y + 9, fill=base, outline=outline)
        # Pointy cat ears
        d.polygon([(head_x + 1, head_y), (head_x + 3, head_y - 3), (head_x + 5, head_y)], fill=base, outline=outline)
        d.polygon([(head_x + 7, head_y), (head_x + 9, head_y - 3), (head_x + 11, head_y)], fill=base, outline=outline)
        draw_pixel(d, head_x + 3, head_y - 1, inner_ear)
        draw_pixel(d, head_x + 9, head_y - 1, inner_ear)

        # 3 Cheek whiskers on left and right (exact match to reference!)
        draw_pixel(d, head_x - 1, head_y + 2, outline)
        draw_pixel(d, head_x - 1, head_y + 5, outline)
        draw_pixel(d, head_x - 1, head_y + 8, outline)

        draw_pixel(d, head_x + 13, head_y + 2, outline)
        draw_pixel(d, head_x + 13, head_y + 5, outline)
        draw_pixel(d, head_x + 13, head_y + 8, outline)

        if has_collar:
            d.line([(head_x + 3, head_y + 9), (head_x + 11, head_y + 9)], fill=(0, 180, 216, 255), width=2)
            draw_pixel(d, head_x + 7, head_y + 10, (255, 215, 0, 255))

        # Upright S-Curved Tail rising from back rump
        tail_bend = 1 if tail_phase > 0 else 0
        d.line([(23, 14), (26, 12)], fill=outline, width=2)
        d.line([(26, 12), (27, 7 + tail_bend)], fill=outline, width=2)
        d.line([(27, 7 + tail_bend), (25, 4 + tail_bend)], fill=outline, width=2)

        # Face: Sunglasses or Eyes & Reddish Nose Dot
        if has_sunglasses:
            draw_retro_sunglasses(d, head_x - 1, head_y + 1, glint=(frame_idx in [0, 1, 3]))
            # Nose dot below sunglasses
            draw_pixel(d, head_x + 6, head_y + 7, nose_col)
        else:
            if blink:
                d.line([(head_x + 3, head_y + 4), (head_x + 5, head_y + 4)], fill=outline, width=1)
                d.line([(head_x + 7, head_y + 4), (head_x + 9, head_y + 4)], fill=outline, width=1)
            else:
                draw_pixel(d, head_x + 4, head_y + 5, pupil_col)
                draw_pixel(d, head_x + 8, head_y + 5, pupil_col)
            draw_pixel(d, head_x + 6, head_y + 7, nose_col)

        # EXACT PAIRED LEGS: [ | ] ___ [ | ]
        draw_paired_retro_legs(d, base, outline, paw_col, offset_y=0, walk_phase=0)

    scaled_size = (SPRITE_GRID_SIZE * SCALE_FACTOR, SPRITE_GRID_SIZE * SCALE_FACTOR)
    crisp_img = img.resize(scaled_size, Image.Resampling.NEAREST)
    return crisp_img


def render_cat_frame(skin_key="boss_oyen", state="idle", frame_idx=0):
    palette = PALETTES.get(skin_key, PALETTES["boss_oyen"])
    return render_exact_cat(palette, state, frame_idx)


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
    print(f"[SpriteGen] Generated all exact retro reference sprites for {len(PALETTES)} characters in '{output_dir}'.")


if __name__ == "__main__":
    pregenerate_all_sprites()
