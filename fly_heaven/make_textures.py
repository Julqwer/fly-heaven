from pathlib import Path
from PIL import Image, ImageDraw
import random

OUT = Path(__file__).resolve().parent / "textures"
OUT.mkdir(parents=True, exist_ok=True)

random.seed(42)


def plaster():
    w = h = 128
    img = Image.new("RGB", (w, h))
    px = img.load()

    for y in range(h):
        for x in range(w):
            noise = random.randint(-5, 5)
            px[x, y] = (
                max(0, min(255, 184 + noise)),
                max(0, min(255, 126 + noise)),
                max(0, min(255, 100 + noise)),
            )

    img.save(OUT / "SUNWALL.png")


def ceiling():
    w = h = 128
    img = Image.new("RGB", (w, h))
    px = img.load()

    for y in range(h):
        for x in range(w):
            noise = random.randint(-3, 3)
            px[x, y] = (
                222 + noise,
                193 + noise,
                164 + noise,
            )

    img.save(OUT / "SUNCEIL.png")


def wooden_floor():
    w = h = 128
    img = Image.new("RGB", (w, h), (105, 65, 46))
    draw = ImageDraw.Draw(img)

    plank_h = 32

    for row, y in enumerate(range(0, h, plank_h)):
        offset = 32 if row % 2 else 0

        for x in range(-offset, w, 64):
            tone = random.randint(-8, 8)

            draw.rectangle(
                [x, y, x + 63, y + plank_h - 1],
                fill=(118 + tone, 72 + tone, 48 + tone),
            )

            draw.line(
                [x, y, x + 63, y],
                fill=(72, 44, 33),
                width=2,
            )

            draw.line(
                [x, y, x, y + plank_h],
                fill=(70, 42, 30),
                width=2,
            )

    img.save(OUT / "SUNFLOOR.png")


def sunset():
    w, h = 256, 128
    img = Image.new("RGB", (w, h))
    px = img.load()

    top = (72, 58, 112)
    middle = (220, 105, 96)
    bottom = (247, 171, 103)

    for y in range(h):
        t = y / (h - 1)

        if t < 0.55:
            u = t / 0.55
            a, b = top, middle
        else:
            u = (t - 0.55) / 0.45
            a, b = middle, bottom

        color = tuple(
            int(a[i] * (1 - u) + b[i] * u)
            for i in range(3)
        )

        for x in range(w):
            px[x, y] = color

    draw = ImageDraw.Draw(img)

    # Sun
    draw.ellipse(
        [174, 51, 210, 87],
        fill=(255, 218, 151),
    )

    # Distant landscape silhouette
    horizon = [
        (-10, 105),
        (25, 92),
        (52, 99),
        (85, 80),
        (118, 101),
        (145, 89),
        (172, 105),
        (210, 94),
        (270, 105),
        (270, 140),
        (-10, 140),
    ]

    draw.polygon(
        horizon,
        fill=(61, 46, 61),
    )

    img.save(OUT / "SUNSET.png")


plaster()
ceiling()
wooden_floor()
sunset()

print("Created textures in:", OUT)

for file in sorted(OUT.glob("*.png")):
    print(" -", file.name)
