from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path("fly_heaven/visuals/fly/fly_base.png")
CIG = Path("fly_heaven/textures/CIGAA0.png")
OUT = Path("fly_heaven/assets/sprites")

OUT.mkdir(parents=True, exist_ok=True)

base = Image.open(BASE).convert("RGBA")
cig0 = Image.open(CIG).convert("RGBA")

# Cigarette size relative to fly.
target_w = 70
scale = target_w / cig0.width
cig0 = cig0.resize(
    (target_w, int(cig0.height * scale)),
    Image.Resampling.NEAREST,
)

letters = "ABCDEFGHIJKLMNOP"

# Cigarette Y through the animation:
# low -> mouth -> low
ys = [
    128, 124, 120, 116,
    112, 108, 104, 102,
    102, 102,
    106, 112,
    118, 124, 128, 128,
]

for i, letter in enumerate(letters):

    frame = base.copy()
    d = ImageDraw.Draw(frame, "RGBA")

    cig_y = ys[i]

    # Filter/right end sits near fly's mouth.
    cig_x = 10

    # Front leg holding the cigarette.
    # Thorax -> bent joint -> filter.
    filter_x = cig_x + cig0.width - 5
    filter_y = cig_y + cig0.height // 2

    d.line(
        [(120, 118), (100, 108), (filter_x, filter_y)],
        fill=(40, 34, 37, 255),
        width=5,
    )

    frame.alpha_composite(cig0, (cig_x, cig_y))

    # Smoke after the cigarette leaves the mouth.
    # Solid grey because old ZDoom dithers semi-transparency.
    if i >= 10:
        smoke_phase = i - 10

        puffs = [
            (66 - smoke_phase * 3, 98 - smoke_phase * 4, 8),
            (54 - smoke_phase * 4, 88 - smoke_phase * 5, 10),
            (42 - smoke_phase * 5, 76 - smoke_phase * 6, 12),
            (30 - smoke_phase * 6, 63 - smoke_phase * 7, 10),
        ]

        for x, y, r in puffs:
            d.ellipse(
                [x-r, y-r, x+r, y+r],
                fill=(185, 185, 185, 255),
            )

    out = OUT / f"FLYA{letter}0.png"
    frame.save(out)

print("FIXED SMOKING ANIMATION READY")
print("16 frames, fixed 320x220 canvas")
