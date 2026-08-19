"""
Pixel-Art Cat Sprite Generator & Manager (Handcrafted Matrix Engine)
Faithfully recreates the authentic retro pixel art directly using handcrafted 2D pixel grids.
Eliminates awkward geometric shapes to produce 100% pixel-perfect, cute, expressive sprites.
Zero external network required - 100% offline & local.
"""

from PIL import Image, ImageDraw
import os

PALETTES = {
    "boss_oyen": {
        "name": "Boss Oyen (Kacamata Hitam 🕶️)",
        "O": (255, 150, 45, 255),       # Warm vibrant orange
        "S": (215, 85, 10, 255),        # Dark orange stripes
        "E": (245, 110, 35, 255),       # Inner ear warm tone
        "B": (20, 20, 22, 255),         # Black sunglasses / pupils
        "W": (255, 255, 255, 255),      # White reflection shine
        "N": (230, 60, 30, 255),        # Cute nose dot
        "C": (0, 180, 216, 255),        # Turquoise collar
        "M": (255, 215, 0, 255),        # Gold bell
        "#": (32, 22, 18, 255),         # Crisp dark outline
        "has_sunglasses": True,
        "has_collar": False
    },
    "mochi": {
        "name": "Si Kalung Biru (Mochi Grey Kitten)",
        "O": (160, 170, 182, 255),      # Soft cool grey
        "S": (100, 110, 125, 255),      # Slate stripes
        "E": (255, 150, 175, 255),      # Pink inner ear
        "B": (25, 28, 35, 255),         # Dark cute eyes
        "W": (255, 255, 255, 255),      # White muzzle & chest
        "N": (255, 125, 155, 255),      # Rosy pink nose
        "C": (0, 180, 216, 255),        # Turquoise collar!
        "M": (255, 215, 0, 255),        # Gold medal
        "#": (25, 28, 35, 255),
        "has_sunglasses": False,
        "has_collar": True
    },
    "oyen": {
        "name": "Si Oyen (Orange Tabby)",
        "O": (255, 150, 45, 255),
        "S": (215, 85, 10, 255),
        "E": (255, 150, 170, 255),
        "B": (46, 204, 113, 255),       # Emerald green eyes
        "W": (255, 225, 160, 255),      # Cream belly
        "N": (230, 70, 40, 255),
        "C": (0, 180, 216, 255),
        "M": (255, 215, 0, 255),
        "#": (32, 22, 18, 255),
        "has_sunglasses": False,
        "has_collar": False
    },
    "shiro": {
        "name": "Si Putih (Snow White)",
        "O": (252, 253, 255, 255),      # Snow white
        "S": (215, 222, 235, 255),      # Soft shadow
        "E": (255, 165, 185, 255),
        "B": (52, 152, 219, 255),       # Sky blue eyes
        "W": (255, 255, 255, 255),
        "N": (255, 130, 155, 255),
        "C": (0, 180, 216, 255),
        "M": (255, 215, 0, 255),
        "#": (45, 50, 60, 255),
        "has_sunglasses": False,
        "has_collar": False
    },
    "tuxedo": {
        "name": "Si Tuxedo (Black & White)",
        "O": (42, 45, 54, 255),         # Charcoal black
        "S": (25, 28, 35, 255),
        "E": (255, 150, 170, 255),
        "B": (46, 204, 113, 255),       # Green eyes
        "W": (255, 255, 255, 255),      # White bib & paws
        "N": (255, 130, 150, 255),
        "C": (0, 180, 216, 255),
        "M": (255, 215, 0, 255),
        "#": (18, 20, 25, 255),
        "has_sunglasses": False,
        "has_collar": False
    },
    "calico": {
        "name": "Belang Tiga (Calico)",
        "O": (250, 250, 252, 255),      # White base
        "S": (230, 126, 34, 255),       # Orange patch
        "E": (255, 150, 170, 255),
        "B": (241, 196, 15, 255),       # Amber eyes
        "W": (52, 73, 94, 255),         # Dark patch
        "N": (255, 130, 150, 255),
        "C": (0, 180, 216, 255),
        "M": (255, 215, 0, 255),
        "#": (30, 30, 40, 255),
        "has_sunglasses": False,
        "has_collar": False
    },
    "grey": {
        "name": "Abu-Abu (Grey Tabby)",
        "O": (150, 162, 172, 255),      # Silver grey
        "S": (90, 102, 115, 255),       # Slate stripes
        "E": (255, 160, 180, 255),
        "B": (52, 152, 219, 255),       # Blue eyes
        "W": (225, 232, 240, 255),
        "N": (255, 130, 150, 255),
        "C": (0, 180, 216, 255),
        "M": (255, 215, 0, 255),
        "#": (35, 40, 50, 255),
        "has_sunglasses": False,
        "has_collar": False
    }
}

GRID_W = 24
GRID_H = 24
SCALE_FACTOR = 5  # Scaled cleanly to 120x120 pixels


# -------------------------------------------------------------
# HANDCRAFTED PIXEL MATRICES (Exact match to reference sheet!)
# -------------------------------------------------------------

# 1. IDLE (Standing side pose with paired legs & S-tail)
MATRIX_IDLE_SHADES_0 = [
    "........................",
    "....#.......#...........",
    "...#O#.....#O#.......#..",
    "...#OE#...#OE#......#O#.",
    "..#OOO#####OOO#....#OO#.",
    ".#OOOOOOOOOOOOO#..#OO#..",
    "##BBBB#...#BBBB##.#O#...",
    ".#BWBBO#.#BWBBO##O#.....",
    "##BBBB#...#BBBB#O#......",
    ".#OOOOOONOOOOOOOO#......",
    "..#OOOOOOOOOOOOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#######...#######....",
    "........................",
    "........................",
    "........................",
    "........................",
]

MATRIX_IDLE_SHADES_1 = [
    "........................",
    "....#.......#...........",
    "...#O#.....#O#......##..",
    "...#OE#...#OE#.....#OO#.",
    "..#OOO#####OOO#....#OO#.",
    ".#OOOOOOOOOOOOO#...#O#..",
    "##BBBB#...#BBBB##.#O#...",
    ".#BWBBO#.#BWBBO##O#.....",
    "##BBBB#...#BBBB#O#......",
    ".#OOOOOONOOOOOOOO#......",
    "..#OOOOOOOOOOOOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#######...#######....",
    "........................",
    "........................",
    "........................",
    "........................",
]

# Normal Eyes Idle Template
MATRIX_IDLE_EYES_0 = [
    "........................",
    "....#.......#...........",
    "...#O#.....#O#.......#..",
    "...#OE#...#OE#......#O#.",
    "..#OOO#####OOO#....#OO#.",
    ".#OOOOOOOOOOOOO#..#OO#..",
    "##OOOO#...#OOOO##.#O#...",
    ".#OBOOO#.#OBOOO##O#.....",
    "##OBOO#...#OBOO#O#......",
    ".#OOOOOONOOOOOOOO#......",
    "..#OOOOOOOOOOOOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#######...#######....",
    "........................",
    "........................",
    "........................",
    "........................",
]

MATRIX_IDLE_EYES_BLINK = [
    "........................",
    "....#.......#...........",
    "...#O#.....#O#.......#..",
    "...#OE#...#OE#......#O#.",
    "..#OOO#####OOO#....#OO#.",
    ".#OOOOOOOOOOOOO#..#OO#..",
    "##OOOO#...#OOOO##.#O#...",
    ".#O##OO#.#O##OO##O#.....",
    "##OOOO#...#OOOO#O#......",
    ".#OOOOOONOOOOOOOO#......",
    "..#OOOOOOOOOOOOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#OO#OO#...#OO#OO#....",
    "...#######...#######....",
    "........................",
    "........................",
    "........................",
    "........................",
]

# 2. WALK CYCLE (Stepping paired legs)
MATRIX_WALK_0 = [
    "........................",
    "....#.......#...........",
    "...#O#.....#O#.......#..",
    "...#OE#...#OE#......#O#.",
    "..#OOO#####OOO#....#OO#.",
    ".#OOOOOOOOOOOOO#..#OO#..",
    "##BBBB#...#BBBB##.#O#...",
    ".#BWBBO#.#BWBBO##O#.....",
    "##BBBB#...#BBBB#O#......",
    ".#OOOOOONOOOOOOOO#......",
    "..#OOOOOOOOOOOOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "....#OO#OO#...#OO#OO#...",
    "....#OO#OO#...#OO#OO#...",
    "....#OO#OO#...#OO#OO#...",
    "....#OO#OO#....#OO#OO#..",
    "....#######....#######..",
    "........................",
    "........................",
    "........................",
    "........................",
]

MATRIX_WALK_1 = [
    "........................",
    "....#.......#...........",
    "...#O#.....#O#......##..",
    "...#OE#...#OE#.....#OO#.",
    "..#OOO#####OOO#....#OO#.",
    ".#OOOOOOOOOOOOO#...#O#..",
    "##BBBB#...#BBBB##.#O#...",
    ".#BWBBO#.#BWBBO##O#.....",
    "##BBBB#...#BBBB#O#......",
    ".#OOOOOONOOOOOOOO#......",
    "..#OOOOOOOOOOOOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOSOOOSOOO#......",
    "...#OOOOOOOOOOOOO#......",
    "...#OO#OO#.....#OO#OO#..",
    "...#OO#OO#.....#OO#OO#..",
    "...#OO#OO#.....#OO#OO#..",
    "...#OO#OO#.....#OO#OO#..",
    "...#######.....#######..",
    "........................",
    "........................",
    "........................",
    "........................",
]

# 3. SLEEP / LOAF (Flat resting pose matching reference top-right)
MATRIX_SLEEP_0 = [
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "...................#....",
    "..................#O#...",
    "....#...#.........#O#...",
    "...#E#.#E#.......#OO#...",
    "..#OOO#OOO#.....#OO#....",
    ".#OOOOOOOOO#####OO#.....",
    ".#O#O#O#O#OOOOOOOO#..z..",
    ".#OOOOONOOOOOSSOOO#...z.",
    ".#OOOOOOOOOOOOOOOOO#..Z.",
    ".#WWWWWWWWWWWWWWWW#.....",
    ".##################.....",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
]

MATRIX_SLEEP_1 = [
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "...................#....",
    "..................#O#...",
    ".................#OO#...",
    "....#...#.......#OO#....",
    "...#E#.#E#.....#OO#..z..",
    "..#OOO#OOO#...#OO#....z.",
    ".#OOOOOOOOO###OO#.....Z.",
    ".#O#O#O#O#OOOOOOOO#.....",
    ".#OOOOONOOOOOSSOOO#.....",
    ".#OOOOOOOOOOOOOOOOO#....",
    ".#WWWWWWWWWWWWWWWW#.....",
    ".##################.....",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
]

# 4. PET / SITTING WITH HEART (Matching reference top-middle)
MATRIX_PET_0 = [
    ".........#.#............",
    "........#####...........",
    ".........###............",
    "..........#.............",
    "....#.......#...........",
    "...#E#.....#E#.......#..",
    "..#OOO#####OOO#.....#O#.",
    ".#OOOOOOOOOOOOO#...#OO#.",
    "##OOOOOOOOOOOOO##.#OO#..",
    ".#O^O#OOOOO#^OO##O#.....",
    "##OOO#OONOO#OOO#O#......",
    ".#OOOOOOOOOOOOOO#.......",
    "..#OOOOOWWWOOOOO#.......",
    "...#OOOOWWWOOOO#........",
    "...#OOOOOWWOOOO#........",
    "...#OOOOOSSOOOO#........",
    "...#OO#OO#OO#OO#........",
    "...#OO#OO#OO#OO#........",
    "...#OO#OO#OO#OO#........",
    "...#############........",
    "........................",
    "........................",
    "........................",
    "........................",
]

MATRIX_PET_1 = [
    "........#####...........",
    ".......#######..........",
    "........#####...........",
    ".........###............",
    "....#.......#...........",
    "...#E#.....#E#......##..",
    "..#OOO#####OOO#....#OO#.",
    ".#OOOOOOOOOOOOO#...#OO#.",
    "##OOOOOOOOOOOOO##.#O#...",
    ".#O^O#OOOOO#^OO##O#.....",
    "##OOO#OONOO#OOO#O#......",
    ".#OOOOOOOOOOOOOO#.......",
    "..#OOOOOWWWOOOOO#.......",
    "...#OOOOWWWOOOO#........",
    "...#OOOOOWWOOOO#........",
    "...#OOOOOSSOOOO#........",
    "...#OO#OO#OO#OO#........",
    "...#OO#OO#OO#OO#........",
    "...#OO#OO#OO#OO#........",
    "...#############........",
    "........................",
    "........................",
    "........................",
    "........................",
]

# 5. JUMP / CELEBRATE / STRETCH (Matching reference bottom-middle)
MATRIX_JUMP_0 = [
    "........................",
    "........................",
    ".....................#..",
    "....#.......#.......#O#.",
    "...#O#.....#O#......#O#.",
    "...#OE#...#OE#.....#OO#.",
    "..#OOO#####OOO#...#OO#..",
    ".#OOOOOOOOOOOOO#.#OO#...",
    "##BBBB#...#BBBB##O#.....",
    ".#BWBBO#.#BWBBO##O#..*..",
    "##BBBB#...#BBBB#O#......",
    ".#OOOOOONOOOOOO#........",
    "..#OOOOOOOOOOO#.........",
    "...#OOOOOOOOOO#.........",
    "...#OOOSOOOSOOO#........",
    "..#OO#OO#..#OO#OO#......",
    "..#OO#OO#...#OO#OO#.....",
    "..#OO#OO#....#OO#OO#....",
    "..######......######....",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
]

# 6. WORK / TYPING AT MINI LAPTOP
MATRIX_WORK_0 = [
    "........................",
    "....#.......#...........",
    "...#O#.....#O#..........",
    "...#OE#...#OE#..........",
    "..#OOO#####OOO#.........",
    ".#OOOOOOOOOOOOO#........",
    "##BBBB#...#BBBB##.......",
    ".#BWBBO#.#BWBBO#........",
    "##BBBB#...#BBBB#........",
    ".#OOOOOONOOOOOO#........",
    "..#OOOOOOOOOOO#.........",
    "...#OOOOOOOOO#..........",
    "...#OOOOOOOOO#..........",
    "...#OO#OO#OO#...........",
    "..############..........",
    "..#..........#..........",
    "..#.CG.CC.CG.#..........",
    "..#..........#..........",
    ".##############.........",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
]

# 7. THINKING (Tilted head looking up)
MATRIX_THINK_0 = [
    "...........d............",
    "..........d.............",
    ".........#.......#......",
    "........#O#.....#O#..#..",
    ".......#OE#...#OE#..#O#.",
    "......#OOO#####OOO##OO#.",
    ".....#OOOOOOOOOOOOOOO#..",
    "....##BBBB#...#BBBB##O#.",
    "....#BWBBO#.#BWBBO##O#..",
    "...##BBBB#...#BBBB#O#...",
    "....#OOOOOONOOOOOO#.....",
    ".....#OOOOOOOOOOOO#.....",
    "......#OOOOOSSOOOO#.....",
    "......#OOOOOSSOOOO#.....",
    "......#OOOOOOOOOOO#.....",
    "......#OO#OO#OO#OO#.....",
    "......#OO#OO#OO#OO#.....",
    "......#OO#OO#OO#OO#.....",
    "......#############.....",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
]

# 8. DRAG / DANGLING
MATRIX_DRAG_0 = [
    "........................",
    "....#.......#...........",
    "...#O#.....#O#..........",
    "...#OE#...#OE#..........",
    "..#OOO#####OOO#.........",
    ".#OOOOOOOOOOOOO#........",
    "##BBBB#...#BBBB##.......",
    ".#BWBBO#.#BWBBO#........",
    "##BBBB#...#BBBB#.....#..",
    ".#OOOOOONOOOOOO#....#O#.",
    "..#OOOOOOOOOOO#....#OO#.",
    "...#OOOOOOOOO#....#OO#..",
    "...#OOOOOSSOO#...#OO#...",
    "...#OOOOOSSOO#..#OO#....",
    "...#OOOOOOOOO##OO#......",
    "...#OO#OO#OO#OO#........",
    "...#OO#OO#OO#OO#........",
    "...#OO#OO#OO#OO#........",
    "...#OO#OO#OO#OO#........",
    "...#############........",
    "........................",
    "........................",
    "........................",
    "........................",
]


def render_matrix_to_image(matrix, palette, state="idle"):
    img = Image.new("RGBA", (GRID_W, GRID_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    has_sunglasses = palette.get("has_sunglasses", False)
    has_collar = palette.get("has_collar", False)

    for y, row in enumerate(matrix):
        for x, char in enumerate(row):
            if char == ".":
                continue
            elif char == "#":
                draw_col = palette["#"]
            elif char == "O":
                draw_col = palette["O"]
            elif char == "S":
                draw_col = palette["S"]
            elif char == "E":
                draw_col = palette["E"]
            elif char == "B":
                draw_col = palette["B"] if has_sunglasses else palette["B"]
            elif char == "W":
                draw_col = palette["W"]
            elif char == "N":
                draw_col = palette["N"]
            elif char == "z" or char == "Z":
                draw_col = (120, 180, 255, 220)
            elif char == "*":
                draw_col = (255, 215, 0, 255)
            elif char == "d":
                draw_col = (52, 152, 219, 255)
            elif char == "C":
                draw_col = (52, 152, 219, 255)
            elif char == "G":
                draw_col = (46, 204, 113, 255)
            elif char == "^":
                draw_col = palette["#"]
            else:
                draw_col = palette["O"]

            # Replace sunglasses with cute normal eyes if skin doesn't have sunglasses
            if not has_sunglasses and char == "B":
                draw_col = palette["B"]
            if not has_sunglasses and char == "W" and state not in ["pet", "sleep"]:
                draw_col = palette["O"]

            d.point((x, y), fill=draw_col)

    # Collar injection for collar skin
    if has_collar and state in ["idle", "walk", "walk_left", "walk_right", "thinking", "pet"]:
        d.line([(8, 10), (14, 10)], fill=palette["C"], width=1)
        d.point((11, 11), fill=palette["M"])

    # Scale with nearest-neighbor for crisp, authentic retro pixel-art
    scaled_size = (GRID_W * SCALE_FACTOR, GRID_H * SCALE_FACTOR)
    return img.resize(scaled_size, Image.Resampling.NEAREST)


def render_cat_frame(skin_key="boss_oyen", state="idle", frame_idx=0):
    palette = PALETTES.get(skin_key, PALETTES["boss_oyen"])
    has_shades = palette.get("has_sunglasses", False)

    if state == "sleep":
        mat = MATRIX_SLEEP_0 if (frame_idx % 2 == 0) else MATRIX_SLEEP_1
        return render_matrix_to_image(mat, palette, state)

    elif state in ["work", "knead", "typing"]:
        return render_matrix_to_image(MATRIX_WORK_0, palette, state)

    elif state in ["pet", "purr", "happy"]:
        mat = MATRIX_PET_0 if (frame_idx % 2 == 0) else MATRIX_PET_1
        return render_matrix_to_image(mat, palette, state)

    elif state in ["jump", "celebrate"]:
        return render_matrix_to_image(MATRIX_JUMP_0, palette, state)

    elif state in ["thinking", "alert"]:
        return render_matrix_to_image(MATRIX_THINK_0, palette, state)

    elif state in ["drag", "picked_up", "dangle"]:
        return render_matrix_to_image(MATRIX_DRAG_0, palette, state)

    elif state in ["land", "drop"]:
        mat = MATRIX_SLEEP_0 if (frame_idx in [0, 1]) else MATRIX_IDLE_SHADES_0
        return render_matrix_to_image(mat, palette, state)

    elif state in ["walk_left", "walk_right", "walk"]:
        mat = MATRIX_WALK_0 if (frame_idx % 2 == 0) else MATRIX_WALK_1
        img = render_matrix_to_image(mat, palette, state)
        if state == "walk_left":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        return img

    else:
        # Idle
        if has_shades:
            mat = MATRIX_IDLE_SHADES_0 if (frame_idx % 2 == 0) else MATRIX_IDLE_SHADES_1
        else:
            mat = MATRIX_IDLE_EYES_BLINK if (frame_idx == 2) else (MATRIX_IDLE_EYES_0 if frame_idx % 2 == 0 else MATRIX_IDLE_EYES_0)
        return render_matrix_to_image(mat, palette, state)


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
    print(f"[SpriteGen] Generated handcrafted pixel matrix sprites for {len(PALETTES)} characters in '{output_dir}'.")


if __name__ == "__main__":
    pregenerate_all_sprites()
