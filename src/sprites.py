"""
Dual-Mode Desktop Pet Pixel-Art Engine (Front-Sitting & Retro-Side-Walk)
- Idle & Interactive States: Full Frontal Sitting Boss Cat with Thug Shades, Muzzle Puffs, and 4 Bottom Paws (Image 1)
- Walking State: Classic 8-Bit Retro Side-Profile Walking Cat with Puffy Tail & Stride (Image 2)
Zero external network required - 100% offline & local.
"""

from PIL import Image, ImageDraw
import os

PALETTES = {
    "boss_oyen": {
        "name": "Boss Oyen (Kacamata Hitam 🕶️)",
        "base": (255, 140, 50, 255),       # Vibrant saturated orange (exact match to Image 1)
        "shadow": (225, 105, 30, 255),     # Darker orange shadow
        "belly": (255, 240, 220, 255),     # White/cream muzzle & chest
        "inner_ear": (255, 255, 255, 255), # White inner ear
        "eye": (20, 20, 25, 255),          # Black shades
        "pupil": (20, 20, 25, 255),
        "nose": (165, 75, 45, 255),        # Brown nose
        "outline": (35, 22, 18, 255),      # Crisp dark brown outline
        "paw": (255, 255, 255, 255),       # Pure white paws
        "chain": (255, 205, 20, 255),      # Gold chain
        "chain_shine": (255, 245, 150, 255),
        "sunglasses": True,
        "collar": False
    },
    "mochi": {
        "name": "Si Kalung Biru (Mochi Chibi 🐾)",
        "base": (175, 185, 195, 255),      # Cool grey
        "shadow": (125, 135, 148, 255),
        "belly": (255, 255, 255, 255),     # White muzzle
        "inner_ear": (255, 170, 190, 255), # Pink inner ear
        "eye": (30, 35, 42, 255),
        "pupil": (30, 35, 42, 255),
        "nose": (255, 130, 155, 255),      # Pink nose
        "outline": (30, 35, 42, 255),
        "paw": (255, 255, 255, 255),
        "chain": (0, 185, 220, 255),       # Turquoise collar
        "chain_shine": (255, 220, 50, 255),# Gold bell
        "sunglasses": False,
        "collar": True
    },
    "oyen": {
        "name": "Si Oyen (Orange Tabby 🐱)",
        "base": (255, 140, 50, 255),
        "shadow": (225, 105, 30, 255),
        "belly": (255, 240, 220, 255),
        "inner_ear": (255, 255, 255, 255),
        "eye": (46, 204, 113, 255),        # Emerald eyes
        "pupil": (20, 20, 20, 255),
        "nose": (165, 75, 45, 255),
        "outline": (35, 22, 18, 255),
        "paw": (255, 255, 255, 255),
        "chain": (255, 205, 20, 255),
        "chain_shine": (255, 245, 150, 255),
        "sunglasses": False,
        "collar": False
    },
    "shiro": {
        "name": "Si Putih (Snow White ❄️)",
        "base": (252, 253, 255, 255),      # White
        "shadow": (218, 225, 235, 255),
        "belly": (255, 255, 255, 255),
        "inner_ear": (255, 175, 195, 255), # Pink
        "eye": (52, 152, 219, 255),        # Blue eyes
        "pupil": (20, 20, 30, 255),
        "nose": (255, 140, 165, 255),
        "outline": (45, 52, 60, 255),
        "paw": (255, 255, 255, 255),
        "chain": (230, 55, 80, 255),       # Red collar
        "chain_shine": (255, 215, 0, 255),
        "sunglasses": False,
        "collar": False
    },
    "tuxedo": {
        "name": "Si Tuxedo (Black & White 🎩)",
        "base": (42, 45, 52, 255),         # Charcoal black
        "shadow": (28, 30, 35, 255),
        "belly": (255, 255, 255, 255),     # White bib
        "inner_ear": (255, 165, 185, 255),
        "eye": (46, 204, 113, 255),
        "pupil": (15, 15, 20, 255),
        "nose": (255, 135, 155, 255),
        "outline": (20, 22, 26, 255),
        "paw": (255, 255, 255, 255),
        "chain": (255, 205, 20, 255),
        "chain_shine": (255, 245, 150, 255),
        "sunglasses": False,
        "collar": False
    },
    "calico": {
        "name": "Belang Tiga (Calico 🎨)",
        "base": (250, 250, 252, 255),
        "shadow": (230, 120, 25, 255),
        "belly": (255, 255, 255, 255),
        "inner_ear": (255, 160, 180, 255),
        "eye": (245, 180, 10, 255),
        "pupil": (20, 20, 20, 255),
        "nose": (255, 130, 150, 255),
        "outline": (35, 38, 45, 255),
        "paw": (255, 255, 255, 255),
        "chain": (255, 205, 20, 255),
        "chain_shine": (255, 245, 150, 255),
        "sunglasses": False,
        "collar": False
    },
    "grey": {
        "name": "Abu-Abu (Grey Tabby 🩶)",
        "base": (165, 175, 185, 255),
        "shadow": (115, 125, 138, 255),
        "belly": (240, 243, 246, 255),
        "inner_ear": (255, 165, 185, 255),
        "eye": (52, 152, 219, 255),
        "pupil": (20, 20, 30, 255),
        "nose": (255, 130, 150, 255),
        "outline": (40, 45, 52, 255),
        "paw": (255, 255, 255, 255),
        "chain": (255, 205, 20, 255),
        "chain_shine": (255, 245, 150, 255),
        "sunglasses": False,
        "collar": False
    }
}

CANVAS_SIZE = 32
SCALE_FACTOR = 4  # Generates 128x128 pixel art


def create_blank():
    return Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))


def draw_pixel(d, x, y, col):
    if 0 <= x < CANVAS_SIZE and 0 <= y < CANVAS_SIZE:
        d.point((x, y), fill=col)


def draw_rect(d, x1, y1, x2, y2, fill, outline=None):
    d.rectangle([x1, y1, x2, y2], fill=fill, outline=outline)


# -------------------------------------------------------------------------
# 1. FRONT-FACING SITTING POSE (Exact match to Image 1: Boss Cat Sitting)
# -------------------------------------------------------------------------
def render_front_facing_cat(palette, bob=0, eyes_state="shades", heart=False, sparkle=False, laptop=False):
    img = create_blank()
    d = ImageDraw.Draw(img)

    base = palette["base"]
    shadow = palette["shadow"]
    inner_ear = palette["inner_ear"]
    belly = palette["belly"]
    nose = palette["nose"]
    outline = palette["outline"]
    paw = palette["paw"]
    chain = palette["chain"]
    chain_shine = palette["chain_shine"]
    has_shades = palette.get("sunglasses", False)

    y_off = bob

    # 1. Outer Body & Thighs (Left & Right sitting curves)
    # Left outer thigh
    draw_rect(d, 4, 15 + y_off, 9, 27, fill=base, outline=outline)
    d.line([(4, 15 + y_off), (4, 25)], fill=outline, width=1)
    # Right outer thigh
    draw_rect(d, 22, 15 + y_off, 27, 27, fill=base, outline=outline)
    d.line([(27, 15 + y_off), (27, 25)], fill=outline, width=1)

    # 2. Central Torso & Front Legs (2 straight pillars going down)
    # Left front leg pillar
    draw_rect(d, 9, 14 + y_off, 14, 27, fill=base, outline=outline)
    # Right front leg pillar
    draw_rect(d, 17, 14 + y_off, 22, 27, fill=base, outline=outline)
    # Center divider between front legs
    draw_rect(d, 15, 14 + y_off, 16, 27, fill=shadow, outline=outline)

    # 3. Bottom 4 White Paws in a Row [ Rear Left ] [ Front Left ] [ Front Right ] [ Rear Right ]
    # Rear Left Paw (x=4..8)
    draw_rect(d, 4, 25, 8, 28, fill=paw, outline=outline)
    draw_pixel(d, 6, 26, outline)
    # Front Left Paw (x=9..14)
    draw_rect(d, 9, 25, 14, 28, fill=paw, outline=outline)
    draw_pixel(d, 11, 26, outline)
    draw_pixel(d, 12, 26, outline)
    # Front Right Paw (x=17..22)
    draw_rect(d, 17, 25, 22, 28, fill=paw, outline=outline)
    draw_pixel(d, 19, 26, outline)
    draw_pixel(d, 20, 26, outline)
    # Rear Right Paw (x=23..27)
    draw_rect(d, 23, 25, 27, 28, fill=paw, outline=outline)
    draw_pixel(d, 25, 26, outline)

    # 4. White Chest Triangle & Gold Chain / Necklace
    # White chest patch under chin
    d.polygon([(11, 13 + y_off), (20, 13 + y_off), (16, 17 + y_off)], fill=belly)

    if not laptop:
        # Gold Chain Necklace across chest
        d.line([(9, 14 + y_off), (12, 16 + y_off)], fill=chain, width=2)
        d.line([(12, 16 + y_off), (19, 16 + y_off)], fill=chain, width=2)
        d.line([(19, 16 + y_off), (22, 14 + y_off)], fill=chain, width=2)

        # Big Gold "S" Pendant / Medal hanging in center!
        draw_rect(d, 13, 17 + y_off, 18, 22 + y_off, fill=chain, outline=outline)
        # S letter pattern in shine
        draw_pixel(d, 14, 18 + y_off, chain_shine)
        draw_pixel(d, 15, 18 + y_off, chain_shine)
        draw_pixel(d, 16, 18 + y_off, chain_shine)
        draw_pixel(d, 14, 19 + y_off, chain_shine)
        draw_pixel(d, 15, 20 + y_off, chain_shine)
        draw_pixel(d, 16, 20 + y_off, chain_shine)
        draw_pixel(d, 16, 21 + y_off, chain_shine)
        draw_pixel(d, 15, 21 + y_off, chain_shine)
        draw_pixel(d, 14, 21 + y_off, chain_shine)

    # 5. Big Round Head (Chubby cheeks, pointy ears)
    # Left Ear (with white/inner patch)
    d.polygon([(4, 6 + y_off), (7, 1 + y_off), (11, 6 + y_off)], fill=base, outline=outline)
    d.polygon([(5, 5 + y_off), (7, 2 + y_off), (9, 5 + y_off)], fill=inner_ear)
    # Right Ear
    d.polygon([(20, 6 + y_off), (24, 1 + y_off), (27, 6 + y_off)], fill=base, outline=outline)
    d.polygon([(22, 5 + y_off), (24, 2 + y_off), (26, 5 + y_off)], fill=inner_ear)

    # Main Head Circle
    draw_rect(d, 4, 6 + y_off, 27, 16 + y_off, fill=base, outline=outline)
    draw_rect(d, 3, 8 + y_off, 28, 14 + y_off, fill=base, outline=outline)

    # 6. Face Features: Thug Shades, Muzzle Puffs, Nose
    if has_shades or eyes_state == "shades":
        # Thug Life Sunglasses across face
        draw_rect(d, 3, 7 + y_off, 28, 11 + y_off, fill=(18, 18, 22, 255), outline=outline)
        # Stepped Pixel Glint (White stairs shine on left and right lens)
        # Left Lens Glint
        draw_pixel(d, 6, 8 + y_off, (255, 255, 255, 255))
        draw_pixel(d, 7, 8 + y_off, (255, 255, 255, 255))
        draw_pixel(d, 8, 9 + y_off, (255, 255, 255, 255))
        draw_pixel(d, 9, 9 + y_off, (255, 255, 255, 255))
        # Right Lens Glint
        draw_pixel(d, 19, 8 + y_off, (255, 255, 255, 255))
        draw_pixel(d, 20, 8 + y_off, (255, 255, 255, 255))
        draw_pixel(d, 21, 9 + y_off, (255, 255, 255, 255))
        draw_pixel(d, 22, 9 + y_off, (255, 255, 255, 255))

    elif eyes_state == "open":
        eye_col = palette["eye"]
        # Big anime eyes
        draw_rect(d, 7, 8 + y_off, 10, 11 + y_off, fill=eye_col)
        draw_pixel(d, 8, 8 + y_off, (255, 255, 255, 255))
        draw_rect(d, 21, 8 + y_off, 24, 11 + y_off, fill=eye_col)
        draw_pixel(d, 22, 8 + y_off, (255, 255, 255, 255))

    elif eyes_state == "happy":
        d.line([(7, 10 + y_off), (9, 8 + y_off)], fill=outline, width=2)
        d.line([(9, 8 + y_off), (11, 10 + y_off)], fill=outline, width=2)
        d.line([(20, 10 + y_off), (22, 8 + y_off)], fill=outline, width=2)
        d.line([(22, 8 + y_off), (24, 10 + y_off)], fill=outline, width=2)

    elif eyes_state == "sleep":
        d.line([(7, 10 + y_off), (11, 10 + y_off)], fill=outline, width=2)
        d.line([(20, 10 + y_off), (24, 10 + y_off)], fill=outline, width=2)

    # Cute Brown Nose
    draw_rect(d, 14, 10 + y_off, 17, 12 + y_off, fill=nose, outline=outline)

    # White Rounded Whisker Muzzle Puffs (:3)
    draw_rect(d, 10, 12 + y_off, 15, 15 + y_off, fill=belly, outline=outline)
    draw_rect(d, 16, 12 + y_off, 21, 15 + y_off, fill=belly, outline=outline)
    draw_pixel(d, 12, 13 + y_off, outline)
    draw_pixel(d, 19, 13 + y_off, outline)

    # Optional Overlays:
    if heart:
        # Floating pixel heart
        hy = 2 - (bob % 2)
        d.polygon([(14, hy), (16, hy - 2), (18, hy), (16, hy + 3)], fill=(255, 60, 90, 255))
        d.polygon([(12, hy), (14, hy - 2), (16, hy), (14, hy + 3)], fill=(255, 60, 90, 255))

    if sparkle:
        draw_pixel(d, 3, 4, (255, 215, 0, 255))
        draw_pixel(d, 28, 4, (255, 215, 0, 255))
        draw_pixel(d, 29, 5, (255, 215, 0, 255))

    if laptop:
        # Mini Laptop
        draw_rect(d, 6, 20, 25, 27, fill=(65, 75, 90, 255), outline=outline)
        d.polygon([(8, 20), (10, 15), (21, 15), (23, 20)], fill=(120, 135, 155, 255), outline=outline)
        d.line([(12, 17), (19, 17)], fill=(46, 204, 113, 255), width=1)

    # Resize cleanly to 128x128
    scaled_size = (CANVAS_SIZE * SCALE_FACTOR, CANVAS_SIZE * SCALE_FACTOR)
    return img.resize(scaled_size, Image.Resampling.NEAREST)


# -------------------------------------------------------------------------
# 2. SIDE-FACING WALKING POSE (Exact match to Image 2: 8-Bit Retro Walking)
# -------------------------------------------------------------------------
def render_side_walking_cat(palette, step=0):
    img = create_blank()
    d = ImageDraw.Draw(img)

    base = palette["base"]
    shadow = palette["shadow"]
    inner_ear = palette["inner_ear"]
    belly = palette["belly"]
    outline = palette["outline"]
    paw = palette["paw"]
    chain = palette["chain"]

    bob = 1 if (step in [1, 3]) else 0
    by = 13 - bob

    # 1. Upright Puffy Tail (Image 2 style)
    tail_step = 1 if step in [0, 2] else 0
    d.polygon([(21, by + 4), (25, by - 2 + tail_step), (28, by - 5 + tail_step), (25, by - 7 + tail_step), (22, by - 1)], fill=base, outline=outline)

    # 2. Rectangular Retro Torso
    draw_rect(d, 8, by, 22, by + 8, fill=base, outline=outline)
    d.line([(12, by + 1), (12, by + 4)], fill=shadow, width=1)
    d.line([(17, by + 1), (17, by + 4)], fill=shadow, width=1)

    # 3. Head (Facing Left/Side as in Image 2)
    # Pointy Ears
    d.polygon([(6, by - 5), (8, by - 9), (11, by - 5)], fill=base, outline=outline)
    d.polygon([(7, by - 6), (8, by - 8), (10, by - 6)], fill=inner_ear)
    d.polygon([(12, by - 5), (14, by - 9), (17, by - 5)], fill=base, outline=outline)
    d.polygon([(13, by - 6), (14, by - 8), (16, by - 6)], fill=inner_ear)

    # Head Box
    draw_rect(d, 5, by - 5, 17, by + 2, fill=base, outline=outline)

    # Eye (Dark square dot)
    draw_rect(d, 8, by - 3, 9, by - 2, fill=(35, 22, 18, 255))
    draw_rect(d, 13, by - 3, 14, by - 2, fill=(35, 22, 18, 255))

    # White Muzzle Patch on Snout (Image 2)
    draw_rect(d, 5, by - 1, 10, by + 2, fill=belly, outline=outline)

    # Dark Collar / Chain under neck
    draw_rect(d, 7, by + 2, 15, by + 4, fill=chain, outline=outline)
    d.line([(7, by + 2), (7, by + 7)], fill=outline, width=2)

    # 4. Clean 8-Bit Walking Legs with Stride (Image 2 style)
    # 4 defined stepping columns
    if step == 0:
        # Front Left forward, Front Right back, Rear Left forward, Rear Right back
        draw_rect(d, 8, by + 8, 10, 27, fill=paw, outline=outline)
        draw_rect(d, 12, by + 8, 14, 25, fill=paw, outline=outline)
        draw_rect(d, 17, by + 8, 19, 27, fill=paw, outline=outline)
        draw_rect(d, 20, by + 8, 22, 25, fill=paw, outline=outline)
    elif step == 1:
        # Passing phase
        draw_rect(d, 9, by + 8, 11, 26, fill=paw, outline=outline)
        draw_rect(d, 13, by + 8, 15, 26, fill=paw, outline=outline)
        draw_rect(d, 18, by + 8, 20, 26, fill=paw, outline=outline)
        draw_rect(d, 21, by + 8, 23, 26, fill=paw, outline=outline)
    elif step == 2:
        # Opposite stride
        draw_rect(d, 7, by + 8, 9, 25, fill=paw, outline=outline)
        draw_rect(d, 11, by + 8, 13, 27, fill=paw, outline=outline)
        draw_rect(d, 16, by + 8, 18, 25, fill=paw, outline=outline)
        draw_rect(d, 20, by + 8, 22, 27, fill=paw, outline=outline)
    else:
        # Passing phase 2
        draw_rect(d, 9, by + 8, 11, 26, fill=paw, outline=outline)
        draw_rect(d, 13, by + 8, 15, 26, fill=paw, outline=outline)
        draw_rect(d, 18, by + 8, 20, 26, fill=paw, outline=outline)
        draw_rect(d, 21, by + 8, 23, 26, fill=paw, outline=outline)

    scaled_size = (CANVAS_SIZE * SCALE_FACTOR, CANVAS_SIZE * SCALE_FACTOR)
    return img.resize(scaled_size, Image.Resampling.NEAREST)


# -------------------------------------------------------------------------
# 3. SLEEPING LOAF POSE
# -------------------------------------------------------------------------
def render_sleep_cat(palette, frame_idx=0):
    img = create_blank()
    d = ImageDraw.Draw(img)

    base = palette["base"]
    belly = palette["belly"]
    outline = palette["outline"]
    inner_ear = palette["inner_ear"]

    bob = 1 if (frame_idx % 2 == 1) else 0

    # Flat loaf body
    draw_rect(d, 4, 16 + bob, 27, 26, fill=base, outline=outline)
    draw_rect(d, 8, 20 + bob, 22, 25, fill=belly)

    # Curled tail
    d.polygon([(26, 22 + bob), (29, 18 + bob), (28, 15 + bob), (25, 17 + bob)], fill=base, outline=outline)

    # Sleeping head on left
    draw_rect(d, 4, 12 + bob, 15, 20 + bob, fill=base, outline=outline)
    d.polygon([(5, 12 + bob), (7, 8 + bob), (9, 12 + bob)], fill=base, outline=outline)
    d.polygon([(6, 11 + bob), (7, 9 + bob), (8, 11 + bob)], fill=inner_ear)
    d.polygon([(11, 12 + bob), (13, 8 + bob), (15, 12 + bob)], fill=base, outline=outline)

    # Closed sleeping eyes (- -)
    d.line([(6, 15 + bob), (9, 15 + bob)], fill=outline, width=2)
    d.line([(11, 15 + bob), (14, 15 + bob)], fill=outline, width=2)

    # Zzz
    z = frame_idx % 4
    if z >= 1:
        draw_pixel(d, 23 + z, 10 - z * 2, (100, 160, 255, 220))
        draw_pixel(d, 24 + z, 10 - z * 2, (100, 160, 255, 220))
    if z >= 2:
        draw_pixel(d, 26, 4, (120, 180, 255, 255))
        draw_pixel(d, 27, 4, (120, 180, 255, 255))

    scaled_size = (CANVAS_SIZE * SCALE_FACTOR, CANVAS_SIZE * SCALE_FACTOR)
    return img.resize(scaled_size, Image.Resampling.NEAREST)


def render_cat_frame(skin_key="boss_oyen", state="idle", frame_idx=0):
    palette = PALETTES.get(skin_key, PALETTES["boss_oyen"])

    if state == "idle":
        bob = 1 if (frame_idx in [1, 2]) else 0
        return render_front_facing_cat(palette, bob=bob, eyes_state="shades" if palette.get("sunglasses") else "open")

    elif state in ["walk_left", "walk_right", "walk"]:
        img = render_side_walking_cat(palette, step=frame_idx % 4)
        if state == "walk_right":
            # Image 2 is walking left, so flip for walk_right
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        return img

    elif state == "sleep":
        return render_sleep_cat(palette, frame_idx)

    elif state in ["pet", "purr", "happy"]:
        bob = 1 if (frame_idx % 2 == 1) else 0
        return render_front_facing_cat(palette, bob=bob, eyes_state="happy", heart=True)

    elif state in ["jump", "celebrate"]:
        bob = 2 if (frame_idx in [1, 2]) else 0
        return render_front_facing_cat(palette, bob=-bob, eyes_state="happy", sparkle=True)

    elif state in ["work", "knead", "typing"]:
        bob = 1 if (frame_idx % 2 == 1) else 0
        return render_front_facing_cat(palette, bob=bob, laptop=True)

    elif state in ["thinking", "alert"]:
        return render_front_facing_cat(palette, bob=0, eyes_state="open")

    elif state in ["drag", "picked_up", "dangle"]:
        return render_front_facing_cat(palette, bob=-3, eyes_state="open")

    elif state in ["land", "drop"]:
        return render_front_facing_cat(palette, bob=2, eyes_state="happy")

    else:
        return render_front_facing_cat(palette, bob=0)


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

    print(f"[SpriteGen] Generated Dual-Mode (Front-Sitting & Retro-Side-Walk) sprites for {len(PALETTES)} characters in '{output_dir}'.")


if __name__ == "__main__":
    pregenerate_all_sprites()
