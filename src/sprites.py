"""
Pixel-Art Cat Sprite Generator & Manager
Generates crisp, cute pixel-art frames dynamically for various animation states and skins.
Zero external network required - 100% offline & local.
"""

from PIL import Image, ImageDraw
import os

# Color Palettes for different cat skins
PALETTES = {
    "oyen": {
        "name": "Si Oyen (Orange Tabby)",
        "base": (255, 159, 67, 255),       # Vibrant orange
        "stripe": (211, 84, 0, 255),        # Deep orange/brown stripes
        "belly": (254, 235, 178, 255),     # Cream/yellowish white
        "inner_ear": (255, 175, 189, 255), # Soft pink
        "eye": (46, 204, 113, 255),        # Emerald green
        "pupil": (20, 20, 20, 255),        # Dark pupil
        "nose": (255, 120, 140, 255),      # Rosy pink
        "outline": (45, 30, 20, 255),      # Soft dark brown outline
        "white_paws": True
    },
    "calico": {
        "name": "Belang Tiga (Calico)",
        "base": (248, 249, 250, 255),      # White
        "stripe": (230, 126, 34, 255),     # Orange patch
        "dark_patch": (52, 73, 94, 255),   # Dark grey/black patch
        "belly": (255, 255, 255, 255),
        "inner_ear": (255, 175, 189, 255),
        "eye": (241, 196, 15, 255),        # Amber gold
        "pupil": (20, 20, 20, 255),
        "nose": (255, 120, 140, 255),
        "outline": (35, 35, 45, 255),
        "white_paws": True
    },
    "tuxedo": {
        "name": "Si Tuxedo (Black & White)",
        "base": (40, 42, 54, 255),         # Dark charcoal black
        "stripe": (25, 25, 35, 255),
        "belly": (245, 246, 250, 255),     # White bib
        "inner_ear": (255, 175, 189, 255),
        "eye": (46, 204, 113, 255),        # Bright green
        "pupil": (20, 20, 20, 255),
        "nose": (255, 140, 160, 255),
        "outline": (15, 15, 20, 255),
        "white_paws": True
    },
    "grey": {
        "name": "Abu-Abu (Grey Tabby)",
        "base": (149, 165, 166, 255),      # Soft silver grey
        "stripe": (87, 101, 116, 255),     # Slate stripes
        "belly": (223, 228, 234, 255),     # Light grey/white
        "inner_ear": (255, 175, 189, 255),
        "eye": (52, 152, 219, 255),        # Sky blue
        "pupil": (20, 20, 20, 255),
        "nose": (255, 140, 160, 255),
        "outline": (40, 45, 50, 255),
        "white_paws": True
    },
    "shiro": {
        "name": "Si Putih (Snow White)",
        "base": (250, 252, 255, 255),      # Snow white
        "stripe": (215, 225, 235, 255),    # Soft shadow
        "belly": (255, 255, 255, 255),
        "inner_ear": (255, 170, 185, 255),
        "eye": (52, 152, 219, 255),        # Ocean blue
        "pupil": (20, 20, 20, 255),
        "nose": (255, 140, 160, 255),
        "outline": (60, 65, 75, 255),
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


def draw_rect(draw, x1, y1, x2, y2, color):
    draw.rectangle([x1, y1, x2, y2], fill=color)


def render_cat_frame(skin_key="oyen", state="idle", frame_idx=0):
    palette = PALETTES.get(skin_key, PALETTES["oyen"])
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
    paw_col = (250, 250, 250, 255) if palette.get("white_paws") else base

    # -------------------------------------------------------------
    # 1. STATE: SLEEP
    # -------------------------------------------------------------
    if state == "sleep":
        # Curled up cat sleeping at bottom
        bob = 1 if (frame_idx % 2 == 1) else 0
        y_off = 16 + bob

        # Body curled
        d.ellipse([7, y_off, 25, y_off + 11], fill=base, outline=outline)
        # Belly curve
        d.ellipse([11, y_off + 3, 21, y_off + 10], fill=belly)
        # Tail curled around
        d.arc([5, y_off + 2, 13, y_off + 11], start=90, end=270, fill=outline, width=2)
        # Closed eyes (sleep curves - -)
        d.line([19, y_off + 3, 21, y_off + 3], fill=outline, width=1)
        d.line([23, y_off + 3, 25, y_off + 3], fill=outline, width=1)
        # Ears flat
        d.polygon([(16, y_off), (18, y_off - 2), (20, y_off)], fill=base, outline=outline)
        d.polygon([(22, y_off), (24, y_off - 2), (26, y_off)], fill=base, outline=outline)
        # Nose
        draw_pixel(d, 22, y_off + 4, nose_col)

        # Floating "Z z z" particles
        z_offset = frame_idx % 4
        if z_offset >= 1:
            draw_pixel(d, 25 + z_offset, 13 - z_offset * 2, (100, 160, 255, 200))
            draw_pixel(d, 26 + z_offset, 13 - z_offset * 2, (100, 160, 255, 200))
            draw_pixel(d, 25 + z_offset, 14 - z_offset * 2, (100, 160, 255, 200))
        if z_offset >= 2:
            draw_pixel(d, 27, 6, (120, 180, 255, 255))
            draw_pixel(d, 28, 6, (120, 180, 255, 255))

    # -------------------------------------------------------------
    # 2. STATE: WORK / KNEAD / TYPING (Inspired by Comnyang!)
    # -------------------------------------------------------------
    elif state in ["work", "knead", "typing"]:
        # Cat facing desk/laptop with paws moving up and down
        paw_left_up = (frame_idx % 2 == 0)
        paw_right_up = not paw_left_up

        # Mini Laptop / Desk at bottom
        d.rectangle([4, 25, 28, 29], fill=(70, 80, 95, 255), outline=outline)
        # Laptop screen (angled)
        d.polygon([(6, 25), (10, 18), (22, 18), (26, 25)], fill=(120, 140, 160, 255), outline=outline)
        # Screen glow (code lines)
        d.line([(12, 20), (19, 20)], fill=(46, 204, 113, 255), width=1)
        d.line([(11, 22), (18, 22)], fill=(52, 152, 219, 255), width=1)

        # Cat Body behind laptop
        d.ellipse([9, 10, 23, 26], fill=base, outline=outline)
        # Belly
        d.ellipse([12, 15, 20, 25], fill=belly)

        # Head
        d.ellipse([8, 4, 24, 17], fill=base, outline=outline)
        # Ears
        d.polygon([(9, 7), (12, 1), (15, 6)], fill=base, outline=outline)
        d.polygon([(11, 6), (12, 3), (14, 6)], fill=inner_ear)
        d.polygon([(17, 6), (20, 1), (23, 7)], fill=base, outline=outline)
        d.polygon([(18, 6), (20, 3), (21, 6)], fill=inner_ear)

        # Focused / determined eyes (> < or concentrated dots)
        d.line([(11, 9), (14, 10)], fill=outline, width=1)
        d.line([(11, 11), (14, 10)], fill=outline, width=1)
        d.line([(21, 9), (18, 10)], fill=outline, width=1)
        d.line([(21, 11), (18, 10)], fill=outline, width=1)

        # Nose & Muzzle
        draw_pixel(d, 16, 12, nose_col)

        # Fast Kneading Paws on keyboard
        l_y = 23 if paw_left_up else 25
        r_y = 23 if paw_right_up else 25
        d.ellipse([8, l_y, 13, l_y + 4], fill=paw_col, outline=outline)
        d.ellipse([19, r_y, 24, r_y + 4], fill=paw_col, outline=outline)

        # Focus sweatdrop or energy sparks
        if frame_idx % 2 == 1:
            draw_pixel(d, 25, 4, (52, 152, 219, 255))
            draw_pixel(d, 25, 5, (52, 152, 219, 255))

    # -------------------------------------------------------------
    # 3. STATE: WALK (LEFT / RIGHT)
    # -------------------------------------------------------------
    elif state in ["walk_left", "walk_right", "walk"]:
        flip_x = (state == "walk_left")
        step = frame_idx % 4
        bob = 1 if (step in [1, 3]) else 0

        # Body
        d.ellipse([7, 11 - bob, 22, 23 - bob], fill=base, outline=outline)
        # Stripes
        d.line([(12, 11 - bob), (12, 16 - bob)], fill=stripe, width=1)
        d.line([(16, 11 - bob), (16, 16 - bob)], fill=stripe, width=1)

        # Head
        d.ellipse([16, 6 - bob, 27, 17 - bob], fill=base, outline=outline)
        # Ears
        d.polygon([(17, 7 - bob), (20, 2 - bob), (22, 7 - bob)], fill=base, outline=outline)
        d.polygon([(19, 6 - bob), (20, 4 - bob), (21, 6 - bob)], fill=inner_ear)
        d.polygon([(23, 7 - bob), (26, 2 - bob), (28, 7 - bob)], fill=base, outline=outline)
        d.polygon([(24, 6 - bob), (26, 4 - bob), (27, 6 - bob)], fill=inner_ear)

        # Eye looking forward
        d.rectangle([23, 10 - bob, 25, 12 - bob], fill=eye_col)
        draw_pixel(d, 24, 11 - bob, pupil_col)
        # Nose
        draw_pixel(d, 27, 12 - bob, nose_col)

        # Tail waving back
        tail_bob = 2 if step in [0, 2] else 0
        d.arc([1, 8 - tail_bob, 9, 20 - tail_bob], start=120, end=300, fill=outline, width=2)
        d.arc([1, 8 - tail_bob, 9, 20 - tail_bob], start=120, end=300, fill=base, width=1)

        # Legs stepping
        if step == 0:
            d.rectangle([9, 22 - bob, 11, 27], fill=paw_col, outline=outline)
            d.rectangle([14, 22 - bob, 16, 26], fill=paw_col, outline=outline)
            d.rectangle([18, 22 - bob, 20, 27], fill=paw_col, outline=outline)
        elif step == 1:
            d.rectangle([10, 22 - bob, 12, 26], fill=paw_col, outline=outline)
            d.rectangle([13, 22 - bob, 15, 27], fill=paw_col, outline=outline)
            d.rectangle([19, 22 - bob, 21, 26], fill=paw_col, outline=outline)
        elif step == 2:
            d.rectangle([11, 22 - bob, 13, 27], fill=paw_col, outline=outline)
            d.rectangle([15, 22 - bob, 17, 26], fill=paw_col, outline=outline)
            d.rectangle([17, 22 - bob, 19, 27], fill=paw_col, outline=outline)
        else:
            d.rectangle([9, 22 - bob, 11, 26], fill=paw_col, outline=outline)
            d.rectangle([14, 22 - bob, 16, 27], fill=paw_col, outline=outline)
            d.rectangle([18, 22 - bob, 20, 26], fill=paw_col, outline=outline)

        if flip_x:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # -------------------------------------------------------------
    # 4. STATE: PET / PURR (Happy hearts and blushing)
    # -------------------------------------------------------------
    elif state in ["pet", "purr", "happy"]:
        # Cat smiling with closed eyes, blushed cheeks, floating heart
        # Body
        d.ellipse([7, 13, 25, 27], fill=base, outline=outline)
        d.ellipse([11, 16, 21, 26], fill=belly)

        # Head
        d.ellipse([7, 6, 25, 19], fill=base, outline=outline)
        # Ears perked
        d.polygon([(8, 7), (11, 1), (14, 7)], fill=base, outline=outline)
        d.polygon([(10, 6), (11, 3), (13, 6)], fill=inner_ear)
        d.polygon([(18, 7), (21, 1), (24, 7)], fill=base, outline=outline)
        d.polygon([(19, 6), (21, 3), (22, 6)], fill=inner_ear)

        # Happy closed eyes (^ ^)
        d.line([(10, 12), (12, 10)], fill=outline, width=1)
        d.line([(12, 10), (14, 12)], fill=outline, width=1)
        d.line([(18, 12), (20, 10)], fill=outline, width=1)
        d.line([(20, 10), (22, 12)], fill=outline, width=1)

        # Blushing pink cheeks (*^_^*)
        d.ellipse([9, 13, 12, 15], fill=(255, 120, 150, 180))
        d.ellipse([(20, 13), (23, 15)], fill=(255, 120, 150, 180))

        # Nose & cute mouth (:3)
        draw_pixel(d, 16, 13, nose_col)
        draw_pixel(d, 15, 14, outline)
        draw_pixel(d, 17, 14, outline)

        # Front paws
        d.ellipse([10, 24, 14, 28], fill=paw_col, outline=outline)
        d.ellipse([18, 24, 22, 28], fill=paw_col, outline=outline)

        # Floating Heart
        h_y = 5 - (frame_idx % 3) * 2
        # Draw pixel heart
        d.polygon([(4, h_y), (6, h_y - 2), (8, h_y), (6, h_y + 3)], fill=(255, 75, 110, 255))
        d.polygon([(2, h_y), (4, h_y - 2), (6, h_y), (4, h_y + 3)], fill=(255, 75, 110, 255))

    # -------------------------------------------------------------
    # 5. STATE: JUMP / CELEBRATE (Success / Timer Finish)
    # -------------------------------------------------------------
    elif state in ["jump", "celebrate"]:
        jump_y = 6 if frame_idx in [1, 2] else 2

        # Cat in mid-air
        d.ellipse([8, 10 - jump_y, 24, 24 - jump_y], fill=base, outline=outline)
        d.ellipse([12, 13 - jump_y, 20, 23 - jump_y], fill=belly)

        # Head high
        d.ellipse([8, 3 - jump_y, 24, 16 - jump_y], fill=base, outline=outline)
        # Ears up
        d.polygon([(8, 4 - jump_y), (11, -jump_y), (14, 4 - jump_y)], fill=base, outline=outline)
        d.polygon([(18, 4 - jump_y), (21, -jump_y), (24, 4 - jump_y)], fill=base, outline=outline)

        # Wide starry or happy eyes
        d.rectangle([11, 7 - jump_y, 14, 10 - jump_y], fill=eye_col)
        d.rectangle([18, 7 - jump_y, 21, 10 - jump_y], fill=eye_col)
        draw_pixel(d, 12, 8 - jump_y, (255, 255, 255, 255))
        draw_pixel(d, 19, 8 - jump_y, (255, 255, 255, 255))
        # Open mouth (yay!)
        d.ellipse([15, 11 - jump_y, 17, 14 - jump_y], fill=(255, 100, 120, 255), outline=outline)

        # Paws stretched out
        d.ellipse([6, 15 - jump_y, 10, 19 - jump_y], fill=paw_col, outline=outline)
        d.ellipse([22, 15 - jump_y, 26, 19 - jump_y], fill=paw_col, outline=outline)
        d.ellipse([9, 23 - jump_y, 13, 27 - jump_y], fill=paw_col, outline=outline)
        d.ellipse([19, 23 - jump_y, 23, 27 - jump_y], fill=paw_col, outline=outline)

        # Sparkles around
        if frame_idx % 2 == 1:
            # Sparkle 1
            draw_pixel(d, 4, 6, (255, 215, 0, 255))
            draw_pixel(d, 3, 7, (255, 215, 0, 255))
            draw_pixel(d, 5, 7, (255, 215, 0, 255))
            draw_pixel(d, 4, 8, (255, 215, 0, 255))
            # Sparkle 2
            draw_pixel(d, 27, 8, (255, 215, 0, 255))
            draw_pixel(d, 26, 9, (255, 215, 0, 255))
            draw_pixel(d, 28, 9, (255, 215, 0, 255))
            draw_pixel(d, 27, 10, (255, 215, 0, 255))

    # -------------------------------------------------------------
    # 6. STATE: THINKING (Watching AI / background process)
    # -------------------------------------------------------------
    elif state in ["thinking", "alert"]:
        # Cat looking up attentively with subtle head tilt
        # Body
        d.ellipse([7, 13, 25, 27], fill=base, outline=outline)
        d.ellipse([11, 16, 21, 26], fill=belly)

        # Head tilted
        d.ellipse([9, 5, 25, 18], fill=base, outline=outline)
        # Ears twitching
        ear_twitch = 1 if frame_idx % 2 == 1 else 0
        d.polygon([(9, 6), (12, 1 - ear_twitch), (15, 6)], fill=base, outline=outline)
        d.polygon([(11, 5), (12, 3 - ear_twitch), (14, 5)], fill=inner_ear)
        d.polygon([(19, 6), (22, 1), (25, 6)], fill=base, outline=outline)
        d.polygon([(20, 5), (22, 3), (24, 5)], fill=inner_ear)

        # Big curious eyes looking up
        d.rectangle([12, 7, 15, 11], fill=eye_col, outline=outline)
        d.rectangle([19, 7, 22, 11], fill=eye_col, outline=outline)
        draw_pixel(d, 13, 8, pupil_col)
        draw_pixel(d, 20, 8, pupil_col)
        # Glisten
        draw_pixel(d, 14, 8, (255, 255, 255, 255))
        draw_pixel(d, 21, 8, (255, 255, 255, 255))

        # Nose
        draw_pixel(d, 17, 13, nose_col)

        # Paws
        d.ellipse([10, 24, 14, 28], fill=paw_col, outline=outline)
        d.ellipse([18, 24, 22, 28], fill=paw_col, outline=outline)

        # Animated Question/Lightbulb bubble above head
        dot_count = (frame_idx % 3) + 1
        for i in range(dot_count):
            draw_pixel(d, 14 + i * 3, 2, (52, 152, 219, 255))

    # -------------------------------------------------------------
    # 8. STATE: DRAG / PICKED UP (Dangling in mid-air when moved)
    # -------------------------------------------------------------
    elif state in ["drag", "picked_up", "dangle"]:
        # Cat picked up by scruff / dangling with paws kicking and tail swaying
        leg_phase = frame_idx % 4
        tail_phase = frame_idx % 4

        # Tail swaying with momentum
        if tail_phase == 0:
            d.arc([3, 14, 13, 26], start=120, end=300, fill=outline, width=2)
            d.arc([3, 14, 13, 26], start=120, end=300, fill=base, width=1)
        elif tail_phase == 2:
            d.arc([19, 14, 29, 26], start=240, end=60, fill=outline, width=2)
            d.arc([19, 14, 29, 26], start=240, end=60, fill=base, width=1)
        else:
            d.arc([11, 16, 21, 28], start=220, end=320, fill=outline, width=2)
            d.arc([11, 16, 21, 28], start=220, end=320, fill=base, width=1)

        # Elongated dangling body
        d.ellipse([10, 8, 22, 24], fill=base, outline=outline)
        d.ellipse([12, 11, 20, 22], fill=belly)

        # Head (Surprised dangling face)
        d.ellipse([8, 2, 24, 14], fill=base, outline=outline)
        # Ears pulled up
        d.polygon([(9, 4), (11, -1), (14, 4)], fill=base, outline=outline)
        d.polygon([(10, 3), (11, 1), (13, 3)], fill=inner_ear)
        d.polygon([(18, 4), (21, -1), (23, 4)], fill=base, outline=outline)
        d.polygon([(19, 3), (21, 1), (22, 3)], fill=inner_ear)

        # Big surprised wide eyes (o o)
        d.rectangle([10, 5, 14, 9], fill=eye_col, outline=outline)
        d.rectangle([18, 5, 22, 9], fill=eye_col, outline=outline)
        draw_pixel(d, 12, 6, pupil_col)
        draw_pixel(d, 20, 6, pupil_col)
        draw_pixel(d, 11, 6, (255, 255, 255, 255))
        draw_pixel(d, 19, 6, (255, 255, 255, 255))

        # Cute small open mouth (:o)
        draw_pixel(d, 16, 10, nose_col)
        d.ellipse([15, 11, 17, 13], fill=(255, 120, 140, 255), outline=outline)

        # Front paws hanging up/forward
        d.ellipse([6, 9, 10, 14], fill=paw_col, outline=outline)
        d.ellipse([22, 9, 26, 14], fill=paw_col, outline=outline)

        # Back legs kicking / dangling
        if leg_phase == 0:
            d.ellipse([10, 21, 13, 26], fill=paw_col, outline=outline)
            d.ellipse([19, 23, 22, 28], fill=paw_col, outline=outline)
        elif leg_phase == 1:
            d.ellipse([10, 23, 13, 28], fill=paw_col, outline=outline)
            d.ellipse([19, 23, 22, 28], fill=paw_col, outline=outline)
        elif leg_phase == 2:
            d.ellipse([10, 23, 13, 28], fill=paw_col, outline=outline)
            d.ellipse([19, 21, 22, 26], fill=paw_col, outline=outline)
        else:
            d.ellipse([9, 22, 12, 27], fill=paw_col, outline=outline)
            d.ellipse([20, 22, 23, 27], fill=paw_col, outline=outline)

        # Wind / motion marks when moving
        if frame_idx % 2 == 1:
            draw_pixel(d, 4, 12, (200, 220, 255, 180))
            draw_pixel(d, 27, 12, (200, 220, 255, 180))

    # -------------------------------------------------------------
    # 9. STATE: LAND / DROP (Squish & settle when placed)
    # -------------------------------------------------------------
    elif state in ["land", "drop"]:
        if frame_idx in [0, 1]:
            # Squished flat landing
            d.ellipse([5, 14, 27, 27], fill=base, outline=outline)
            d.ellipse([9, 17, 23, 26], fill=belly)
            # Head squished
            d.ellipse([8, 8, 24, 19], fill=base, outline=outline)
            # Closed happy squinting eyes (> <)
            d.line([(11, 12), (14, 13)], fill=outline, width=1)
            d.line([(11, 14), (14, 13)], fill=outline, width=1)
            d.line([(21, 12), (18, 13)], fill=outline, width=1)
            d.line([(21, 14), (18, 13)], fill=outline, width=1)
            # Paws flat
            d.ellipse([7, 23, 12, 27], fill=paw_col, outline=outline)
            d.ellipse([20, 23, 25, 27], fill=paw_col, outline=outline)
        else:
            # Rebound back to normal
            d.ellipse([7, 12, 25, 26], fill=base, outline=outline)
            d.ellipse([11, 15, 21, 25], fill=belly)
            d.ellipse([7, 5, 25, 18], fill=base, outline=outline)
            d.rectangle([11, 8, 15, 12], fill=eye_col, outline=outline)
            d.rectangle([17, 8, 21, 12], fill=eye_col, outline=outline)
            d.ellipse([10, 23, 14, 27], fill=paw_col, outline=outline)
            d.ellipse([18, 23, 22, 27], fill=paw_col, outline=outline)

    # -------------------------------------------------------------
    # 10. DEFAULT: IDLE (Sitting, blinking, tail wagging)
    # -------------------------------------------------------------
    else:
        blink = (frame_idx == 2)
        tail_dir = 1 if (frame_idx in [1, 2]) else -1

        # Tail
        tail_x = 24 if tail_dir > 0 else 26
        d.arc([18, 12, tail_x, 26], start=240, end=60, fill=outline, width=2)
        d.arc([18, 12, tail_x, 26], start=240, end=60, fill=base, width=1)

        # Body
        d.ellipse([7, 12, 25, 26], fill=base, outline=outline)
        # Belly
        d.ellipse([11, 15, 21, 25], fill=belly)
        # Stripes
        d.line([(10, 15), (12, 15)], fill=stripe, width=1)
        d.line([(20, 15), (22, 15)], fill=stripe, width=1)

        # Head
        d.ellipse([7, 5, 25, 18], fill=base, outline=outline)
        # Ears
        d.polygon([(8, 6), (11, 1), (14, 6)], fill=base, outline=outline)
        d.polygon([(10, 5), (11, 3), (13, 5)], fill=inner_ear)
        d.polygon([(18, 6), (21, 1), (24, 6)], fill=base, outline=outline)
        d.polygon([(19, 5), (21, 3), (22, 5)], fill=inner_ear)

        # Eyes (Blinking vs Open)
        if blink:
            # Closed calm eyes (- -)
            d.line([(11, 10), (15, 10)], fill=outline, width=1)
            d.line([(17, 10), (21, 10)], fill=outline, width=1)
        else:
            d.rectangle([11, 8, 15, 12], fill=eye_col, outline=outline)
            d.rectangle([17, 8, 21, 12], fill=eye_col, outline=outline)
            # Pupil & shine
            draw_pixel(d, 13, 9, pupil_col)
            draw_pixel(d, 19, 9, pupil_col)
            draw_pixel(d, 12, 9, (255, 255, 255, 255))
            draw_pixel(d, 18, 9, (255, 255, 255, 255))

        # Nose & cute mouth
        draw_pixel(d, 16, 12, nose_col)
        draw_pixel(d, 15, 13, outline)
        draw_pixel(d, 17, 13, outline)

        # Front paws
        d.ellipse([10, 23, 14, 27], fill=paw_col, outline=outline)
        d.ellipse([18, 23, 22, 27], fill=paw_col, outline=outline)

    # Scale with nearest-neighbor for crisp retro pixel art
    scaled_size = (SPRITE_GRID_SIZE * SCALE_FACTOR, SPRITE_GRID_SIZE * SCALE_FACTOR)
    crisp_img = img.resize(scaled_size, Image.Resampling.NEAREST)
    return crisp_img


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
    print(f"[SpriteGen] All pixel art sprites generated in '{output_dir}'.")


if __name__ == "__main__":
    pregenerate_all_sprites()
