"""
Original Cozy Desktop Pet Pixel-Art Engine (NyangBuddy Signature Edition)
Custom crafted with high-charm cozy chibi proportions, expressive anime-pixel eyes,
lively 4-frame fluid motion, fluffy tails, and vibrant calibrated color palettes.
Zero external network required - 100% offline & local.
"""

from PIL import Image, ImageDraw
import os

PALETTES = {
    "boss_oyen": {
        "name": "Boss Oyen (Kacamata Hitam 🕶️)",
        "base": (255, 146, 43, 255),       # Honey golden orange
        "stripe": (217, 72, 15, 255),       # Warm terracotta stripes
        "belly": (255, 224, 160, 255),     # Warm cream bib
        "inner_ear": (255, 135, 110, 255), # Coral pink
        "eye": (25, 25, 30, 255),          # Deep dark
        "pupil": (25, 25, 30, 255),
        "nose": (240, 62, 62, 255),        # Red-pink nose
        "outline": (43, 27, 23, 255),      # Chocolate outline
        "blush": (255, 107, 107, 180),
        "sunglasses": True,
        "collar": False
    },
    "mochi": {
        "name": "Si Kalung Biru (Mochi Chibi 🐾)",
        "base": (173, 181, 189, 255),      # Soft pastel grey
        "stripe": (108, 117, 125, 255),    # Slate shadow
        "belly": (248, 249, 250, 255),     # Pure white chest
        "inner_ear": (255, 165, 180, 255), # Sweet pink
        "eye": (33, 37, 41, 255),          # Sparkling dark eyes
        "pupil": (33, 37, 41, 255),
        "nose": (255, 135, 155, 255),
        "outline": (33, 37, 41, 255),
        "blush": (255, 140, 160, 200),
        "sunglasses": False,
        "collar": True,                    # Turquoise collar + gold bell!
        "collar_color": (34, 184, 207, 255),
        "bell_color": (252, 196, 25, 255)
    },
    "oyen": {
        "name": "Si Oyen (Orange Tabby 🐱)",
        "base": (255, 146, 43, 255),
        "stripe": (217, 72, 15, 255),
        "belly": (255, 224, 160, 255),
        "inner_ear": (255, 140, 160, 255),
        "eye": (46, 204, 113, 255),        # Emerald green anime eyes
        "pupil": (20, 20, 20, 255),
        "nose": (255, 107, 107, 255),
        "outline": (43, 27, 23, 255),
        "blush": (255, 107, 107, 180),
        "sunglasses": False,
        "collar": False
    },
    "shiro": {
        "name": "Si Putih (Snow White ❄️)",
        "base": (250, 252, 255, 255),      # Snow white
        "stripe": (222, 226, 230, 255),
        "belly": (255, 255, 255, 255),
        "inner_ear": (255, 175, 195, 255), # Powder pink
        "eye": (51, 154, 240, 255),        # Sapphire blue eyes
        "pupil": (20, 20, 30, 255),
        "nose": (255, 140, 165, 255),
        "outline": (52, 58, 64, 255),
        "blush": (255, 155, 175, 190),
        "sunglasses": False,
        "collar": False
    },
    "tuxedo": {
        "name": "Si Tuxedo (Black & White 🎩)",
        "base": (45, 48, 56, 255),         # Elegant charcoal
        "stripe": (30, 32, 38, 255),
        "belly": (248, 249, 250, 255),     # Crisp white tuxedo bib
        "inner_ear": (255, 155, 175, 255),
        "eye": (46, 204, 113, 255),        # Green eyes
        "pupil": (15, 15, 20, 255),
        "nose": (255, 140, 160, 255),
        "outline": (20, 22, 26, 255),
        "blush": (255, 120, 145, 180),
        "sunglasses": False,
        "collar": False
    },
    "calico": {
        "name": "Belang Tiga (Calico 🎨)",
        "base": (248, 249, 250, 255),      # White body
        "stripe": (230, 119, 0, 255),      # Orange spots
        "dark_patch": (52, 58, 64, 255),   # Dark slate spots
        "belly": (255, 255, 255, 255),
        "inner_ear": (255, 160, 180, 255),
        "eye": (250, 176, 5, 255),         # Golden amber eyes
        "pupil": (20, 20, 20, 255),
        "nose": (255, 130, 150, 255),
        "outline": (40, 42, 48, 255),
        "blush": (255, 130, 150, 180),
        "sunglasses": False,
        "collar": False
    },
    "grey": {
        "name": "Abu-Abu (Grey Tabby 🩶)",
        "base": (173, 181, 189, 255),
        "stripe": (108, 117, 125, 255),
        "belly": (233, 236, 239, 255),
        "inner_ear": (255, 165, 185, 255),
        "eye": (51, 154, 240, 255),        # Blue eyes
        "pupil": (20, 20, 30, 255),
        "nose": (255, 135, 155, 255),
        "outline": (45, 50, 58, 255),
        "blush": (255, 140, 160, 180),
        "sunglasses": False,
        "collar": False
    }
}

CANVAS_SIZE = 32
SCALE_FACTOR = 4  # Produces crisp 128x128 pixel art


def create_blank():
    return Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))


def draw_pixel(d, x, y, col):
    if 0 <= x < CANVAS_SIZE and 0 <= y < CANVAS_SIZE:
        d.point((x, y), fill=col)


def draw_rect(d, x1, y1, x2, y2, fill, outline=None):
    d.rectangle([x1, y1, x2, y2], fill=fill, outline=outline)


def draw_cute_head(d, palette, x=7, y=5, bob=0, eyes_state="open", tilt=0):
    """Draws a cute, rounded chibi cat head with pointy ears, cheeks, and face."""
    base = palette["base"]
    inner_ear = palette["inner_ear"]
    outline = palette["outline"]
    stripe = palette.get("stripe", base)
    nose = palette["nose"]
    blush = palette.get("blush", (255, 140, 160, 180))
    has_sunglasses = palette.get("sunglasses", False)

    hx = x + tilt
    hy = y + bob

    # 1. Pointy Ears (Left & Right)
    # Left Ear
    d.polygon([(hx + 1, hy + 2), (hx + 3, hy - 3), (hx + 5, hy + 1)], fill=base, outline=outline)
    d.polygon([(hx + 2, hy + 1), (hx + 3, hy - 2), (hx + 4, hy + 1)], fill=inner_ear)
    # Right Ear
    d.polygon([(hx + 11, hy + 1), (hx + 13, hy - 3), (hx + 15, hy + 2)], fill=base, outline=outline)
    d.polygon([(hx + 12, hy + 1), (hx + 13, hy - 2), (hx + 14, hy + 1)], fill=inner_ear)

    # 2. Main Head Shape (Rounded chibi rectangle)
    draw_rect(d, hx + 1, hy, hx + 15, hy + 10, fill=base, outline=outline)
    # Cheek tufts
    d.polygon([(hx - 1, hy + 6), (hx + 1, hy + 4), (hx + 1, hy + 8)], fill=base, outline=outline)
    d.polygon([(hx + 17, hy + 6), (hx + 15, hy + 4), (hx + 15, hy + 8)], fill=base, outline=outline)

    # Forehead Tabby Stripe
    draw_pixel(d, hx + 8, hy + 1, stripe)
    draw_pixel(d, hx + 8, hy + 2, stripe)
    draw_pixel(d, hx + 6, hy + 1, stripe)
    draw_pixel(d, hx + 10, hy + 1, stripe)

    # 3. Eyes & Accessories
    if has_sunglasses and eyes_state != "sleep":
        # Cool retro black shades
        draw_rect(d, hx + 2, hy + 4, hx + 7, hy + 7, fill=(18, 18, 22, 255), outline=outline)
        draw_rect(d, hx + 9, hy + 4, hx + 14, hy + 7, fill=(18, 18, 22, 255), outline=outline)
        d.line([(hx + 7, hy + 5), (hx + 9, hy + 5)], fill=(18, 18, 22, 255), width=1)
        # White gleam / reflection slash
        draw_pixel(d, hx + 3, hy + 5, (255, 255, 255, 255))
        draw_pixel(d, hx + 10, hy + 5, (255, 255, 255, 255))
        # Nose
        draw_pixel(d, hx + 8, hy + 8, nose)

    elif eyes_state == "open":
        # Sparkly Anime Pixel Eyes (2x3 with highlight dot)
        eye_col = palette["eye"]
        # Left eye
        draw_rect(d, hx + 4, hy + 4, hx + 5, hy + 6, fill=eye_col)
        draw_pixel(d, hx + 4, hy + 4, (255, 255, 255, 255))  # shine
        # Right eye
        draw_rect(d, hx + 11, hy + 4, hx + 12, hy + 6, fill=eye_col)
        draw_pixel(d, hx + 11, hy + 4, (255, 255, 255, 255))  # shine

        # Nose & Kitty Mouth (:3)
        draw_pixel(d, hx + 8, hy + 6, nose)
        draw_pixel(d, hx + 7, hy + 7, outline)
        draw_pixel(d, hx + 9, hy + 7, outline)

        # Cheeks blush
        draw_pixel(d, hx + 3, hy + 7, blush)
        draw_pixel(d, hx + 13, hy + 7, blush)

    elif eyes_state == "blink" or eyes_state == "sleep":
        # Sweet sleeping / blinking curved lines (- -)
        d.line([(hx + 3, hy + 5), (hx + 6, hy + 5)], fill=outline, width=1)
        d.line([(hx + 10, hy + 5), (hx + 13, hy + 5)], fill=outline, width=1)
        draw_pixel(d, hx + 8, hy + 6, nose)
        draw_pixel(d, hx + 3, hy + 6, blush)
        draw_pixel(d, hx + 13, hy + 6, blush)

    elif eyes_state == "happy":
        # Happy closed eyes (^ ^)
        d.polygon([(hx + 3, hy + 6), (hx + 5, hy + 4), (hx + 7, hy + 6)], fill=None, outline=outline)
        d.polygon([(hx + 10, hy + 6), (hx + 12, hy + 4), (hx + 14, hy + 6)], fill=None, outline=outline)
        draw_pixel(d, hx + 8, hy + 6, nose)
        draw_pixel(d, hx + 3, hy + 6, blush)
        draw_pixel(d, hx + 13, hy + 6, blush)

    # 4. Collar & Bell (For Mochi)
    if palette.get("collar", False):
        col_c = palette.get("collar_color", (34, 184, 207, 255))
        bell_c = palette.get("bell_color", (252, 196, 25, 255))
        d.line([(hx + 4, hy + 10), (hx + 12, hy + 10)], fill=col_c, width=2)
        draw_rect(d, hx + 7, hy + 10, hx + 9, hy + 12, fill=bell_c, outline=outline)


def draw_cute_tail(d, palette, phase=0, base_x=22, base_y=20):
    """Draws a fluffy, expressive animated tail."""
    outline = palette["outline"]
    base = palette["base"]
    stripe = palette.get("stripe", base)

    offsets = [
        [(0, 0), (2, -3), (3, -7), (2, -10), (0, -11)],
        [(0, 0), (3, -3), (5, -6), (4, -9), (2, -11)],
        [(0, 0), (2, -3), (3, -7), (2, -10), (0, -11)],
        [(0, 0), (1, -3), (1, -6), (0, -9), (-2, -11)],
    ]
    pts = offsets[phase % 4]
    poly_pts = [(base_x + dx, base_y + dy) for dx, dy in pts]

    for i in range(len(poly_pts) - 1):
        d.line([poly_pts[i], poly_pts[i + 1]], fill=base, width=3)
        d.line([poly_pts[i], poly_pts[i + 1]], fill=outline, width=1)

    # Tail tip
    tip_x, tip_y = poly_pts[-1]
    draw_pixel(d, tip_x, tip_y, stripe)


def render_cat_sprite(palette, state="idle", frame_idx=0):
    img = create_blank()
    d = ImageDraw.Draw(img)

    base = palette["base"]
    belly = palette["belly"]
    outline = palette["outline"]
    stripe = palette.get("stripe", base)
    has_sunglasses = palette.get("sunglasses", False)

    # -------------------------------------------------------------
    # 1. IDLE STATE (Cozy standing loaf with gentle breathing & tail wag)
    # -------------------------------------------------------------
    if state == "idle":
        bob = 1 if (frame_idx in [1, 2]) else 0
        blink = "blink" if (frame_idx == 2 and not has_sunglasses) else "open"

        # Tail
        draw_cute_tail(d, palette, phase=frame_idx, base_x=21, base_y=20 - bob)

        # Body (Chubby cozy loaf)
        draw_rect(d, 8, 14 - bob, 22, 23 - bob, fill=base, outline=outline)
        # White belly bib
        draw_rect(d, 11, 16 - bob, 19, 22 - bob, fill=belly)
        # Tabby back stripes
        draw_pixel(d, 20, 15 - bob, stripe)
        draw_pixel(d, 20, 17 - bob, stripe)

        # Front & Back Paws
        draw_rect(d, 9, 23 - bob, 12, 26, fill=(255, 255, 255, 255), outline=outline)
        draw_rect(d, 18, 23 - bob, 21, 26, fill=(255, 255, 255, 255), outline=outline)

        # Head
        draw_cute_head(d, palette, x=7, y=5, bob=bob, eyes_state=blink)

    # -------------------------------------------------------------
    # 2. WALK STATE (Cute toddle animation)
    # -------------------------------------------------------------
    elif state in ["walk_left", "walk_right", "walk"]:
        step = frame_idx % 4
        bob = 1 if (step in [1, 3]) else 0

        draw_cute_tail(d, palette, phase=step, base_x=21, base_y=19 - bob)

        # Body
        draw_rect(d, 8, 13 - bob, 22, 22 - bob, fill=base, outline=outline)
        draw_rect(d, 11, 15 - bob, 18, 21 - bob, fill=belly)

        # Animated Stepping Paws
        if step == 0:
            draw_rect(d, 10, 22 - bob, 13, 26, fill=(255, 255, 255, 255), outline=outline)
            draw_rect(d, 17, 22 - bob, 20, 24, fill=(255, 255, 255, 255), outline=outline)
        elif step == 1:
            draw_rect(d, 8, 22 - bob, 11, 25, fill=(255, 255, 255, 255), outline=outline)
            draw_rect(d, 19, 22 - bob, 22, 26, fill=(255, 255, 255, 255), outline=outline)
        elif step == 2:
            draw_rect(d, 7, 22 - bob, 10, 24, fill=(255, 255, 255, 255), outline=outline)
            draw_rect(d, 18, 22 - bob, 21, 26, fill=(255, 255, 255, 255), outline=outline)
        else:
            draw_rect(d, 9, 22 - bob, 12, 26, fill=(255, 255, 255, 255), outline=outline)
            draw_rect(d, 18, 22 - bob, 21, 25, fill=(255, 255, 255, 255), outline=outline)

        # Head
        draw_cute_head(d, palette, x=6, y=4, bob=bob, eyes_state="open")

        if state == "walk_left":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # -------------------------------------------------------------
    # 3. SLEEP STATE (Curled up cozy sleeping loaf with Zzz)
    # -------------------------------------------------------------
    elif state == "sleep":
        bob = 1 if (frame_idx % 2 == 1) else 0

        # Curled body on floor
        draw_rect(d, 5, 17 + bob, 26, 26, fill=base, outline=outline)
        draw_rect(d, 9, 21 + bob, 22, 25, fill=belly)

        # Curled tail hugging side
        d.polygon([(25, 23 + bob), (28, 20 + bob), (27, 17 + bob), (24, 18 + bob)], fill=base, outline=outline)

        # Head resting flat on paws
        draw_cute_head(d, palette, x=4, y=14 + bob, bob=0, eyes_state="sleep")

        # Floating Zzz particles
        z = frame_idx % 4
        if z >= 1:
            draw_pixel(d, 23 + z, 11 - z * 2, (100, 160, 255, 220))
            draw_pixel(d, 24 + z, 11 - z * 2, (100, 160, 255, 220))
        if z >= 2:
            draw_pixel(d, 26, 5, (120, 180, 255, 255))
            draw_pixel(d, 27, 5, (120, 180, 255, 255))

    # -------------------------------------------------------------
    # 4. PET / HAPPY STATE (Purring with heart above head)
    # -------------------------------------------------------------
    elif state in ["pet", "purr", "happy"]:
        bob = 1 if (frame_idx % 2 == 1) else 0

        # Tail
        draw_cute_tail(d, palette, phase=frame_idx, base_x=22, base_y=19)

        # Body
        draw_rect(d, 8, 14, 22, 23, fill=base, outline=outline)
        draw_rect(d, 11, 16, 19, 22, fill=belly)

        # Front paws together
        draw_rect(d, 10, 23, 14, 26, fill=(255, 255, 255, 255), outline=outline)
        draw_rect(d, 16, 23, 20, 26, fill=(255, 255, 255, 255), outline=outline)

        # Head with happy ^ ^ eyes
        draw_cute_head(d, palette, x=7, y=5, bob=bob, eyes_state="happy")

        # Floating Red Heart
        hy = 3 - (frame_idx % 3)
        d.polygon([(14, hy), (16, hy - 2), (18, hy), (16, hy + 3)], fill=(255, 75, 110, 255))
        d.polygon([(12, hy), (14, hy - 2), (16, hy), (14, hy + 3)], fill=(255, 75, 110, 255))

    # -------------------------------------------------------------
    # 5. JUMP / CELEBRATE STATE (Joyful leap with star sparkles)
    # -------------------------------------------------------------
    elif state in ["jump", "celebrate"]:
        jump_y = 6 if frame_idx in [1, 2] else 2

        # Tail up
        d.polygon([(22, 18 - jump_y), (27, 12 - jump_y), (25, 7 - jump_y)], fill=base, outline=outline)

        # Body stretched high
        draw_rect(d, 8, 12 - jump_y, 22, 21 - jump_y, fill=base, outline=outline)
        draw_rect(d, 11, 14 - jump_y, 19, 20 - jump_y, fill=belly)

        # Joyful extended paws
        draw_rect(d, 6, 20 - jump_y, 10, 25 - jump_y, fill=(255, 255, 255, 255), outline=outline)
        draw_rect(d, 20, 20 - jump_y, 24, 25 - jump_y, fill=(255, 255, 255, 255), outline=outline)

        # Head looking up happily
        draw_cute_head(d, palette, x=7, y=3 - jump_y, eyes_state="happy")

        # Star sparkles ✨
        if frame_idx % 2 == 1:
            draw_pixel(d, 4, 6, (255, 215, 0, 255))
            draw_pixel(d, 28, 4, (255, 215, 0, 255))
            draw_pixel(d, 29, 5, (255, 215, 0, 255))

    # -------------------------------------------------------------
    # 6. WORK / TYPING STATE (Mini Laptop with glowing screen)
    # -------------------------------------------------------------
    elif state in ["work", "knead", "typing"]:
        paw_toggle = (frame_idx % 2 == 0)

        # Body
        draw_rect(d, 9, 13, 23, 23, fill=base, outline=outline)
        draw_rect(d, 12, 15, 20, 22, fill=belly)

        # Mini Laptop on Desk
        draw_rect(d, 2, 23, 30, 27, fill=(73, 80, 87, 255), outline=outline)
        d.polygon([(4, 23), (7, 16), (25, 16), (28, 23)], fill=(134, 142, 150, 255), outline=outline)
        # Glowing code lines
        d.line([(10, 18), (22, 18)], fill=(81, 207, 102, 255), width=1)
        d.line([(8, 20), (18, 20)], fill=(51, 154, 240, 255), width=1)

        # Head
        draw_cute_head(d, palette, x=8, y=4, eyes_state="open")

        # Tapping front paws
        ly = 20 if paw_toggle else 22
        ry = 22 if paw_toggle else 20
        draw_rect(d, 7, ly, 11, ly + 3, fill=(255, 255, 255, 255), outline=outline)
        draw_rect(d, 21, ry, 25, ry + 3, fill=(255, 255, 255, 255), outline=outline)

    # -------------------------------------------------------------
    # 7. THINKING STATE (Curious tilted head with thought dots)
    # -------------------------------------------------------------
    elif state in ["thinking", "alert"]:
        draw_cute_tail(d, palette, phase=frame_idx, base_x=21, base_y=20)
        draw_rect(d, 8, 14, 22, 23, fill=base, outline=outline)
        draw_rect(d, 11, 16, 19, 22, fill=belly)
        draw_rect(d, 9, 23, 12, 26, fill=(255, 255, 255, 255), outline=outline)
        draw_rect(d, 18, 23, 21, 26, fill=(255, 255, 255, 255), outline=outline)

        # Head with tilt
        draw_cute_head(d, palette, x=9, y=4, eyes_state="open", tilt=1)

        # Thought dots
        dots = (frame_idx % 3) + 1
        for i in range(dots):
            draw_pixel(d, 12 + i * 3, 1, (51, 154, 240, 255))

    # -------------------------------------------------------------
    # 8. DRAG STATE (Dangling cutely in mid-air)
    # -------------------------------------------------------------
    elif state in ["drag", "picked_up", "dangle"]:
        leg_step = frame_idx % 4

        # Suspended elongated body
        draw_rect(d, 10, 10, 22, 22, fill=base, outline=outline)
        draw_rect(d, 13, 13, 19, 20, fill=belly)

        # Head looking surprised
        draw_cute_head(d, palette, x=7, y=2, eyes_state="open")

        # Dangling paws wiggling
        if leg_step == 0:
            draw_rect(d, 9, 22, 12, 28, fill=(255, 255, 255, 255), outline=outline)
            draw_rect(d, 20, 22, 23, 27, fill=(255, 255, 255, 255), outline=outline)
        elif leg_step == 1:
            draw_rect(d, 9, 22, 12, 26, fill=(255, 255, 255, 255), outline=outline)
            draw_rect(d, 20, 22, 23, 29, fill=(255, 255, 255, 255), outline=outline)
        elif leg_step == 2:
            draw_rect(d, 9, 22, 12, 29, fill=(255, 255, 255, 255), outline=outline)
            draw_rect(d, 20, 22, 23, 26, fill=(255, 255, 255, 255), outline=outline)
        else:
            draw_rect(d, 9, 22, 12, 27, fill=(255, 255, 255, 255), outline=outline)
            draw_rect(d, 20, 22, 23, 27, fill=(255, 255, 255, 255), outline=outline)

    # -------------------------------------------------------------
    # 9. LAND STATE (Squish & Spring bounce)
    # -------------------------------------------------------------
    elif state in ["land", "drop"]:
        if frame_idx in [0, 1]:
            draw_rect(d, 6, 16, 26, 25, fill=base, outline=outline)
            draw_rect(d, 9, 18, 23, 24, fill=belly)
            draw_cute_head(d, palette, x=6, y=8, eyes_state="happy")
        else:
            draw_rect(d, 8, 14, 22, 23, fill=base, outline=outline)
            draw_cute_head(d, palette, x=7, y=5, eyes_state="open")

    # Scaled to crisp 128x128
    scaled_size = (CANVAS_SIZE * SCALE_FACTOR, CANVAS_SIZE * SCALE_FACTOR)
    return img.resize(scaled_size, Image.Resampling.NEAREST)


def render_cat_frame(skin_key="boss_oyen", state="idle", frame_idx=0):
    palette = PALETTES.get(skin_key, PALETTES["boss_oyen"])
    return render_cat_sprite(palette, state, frame_idx)


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

    print(f"[SpriteGen] Generated all signature cozy pixel-art sprites for {len(PALETTES)} characters in '{output_dir}'.")


if __name__ == "__main__":
    pregenerate_all_sprites()
