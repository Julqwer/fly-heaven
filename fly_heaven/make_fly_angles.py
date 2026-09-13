from pathlib import Path
from PIL import Image

src = Path("fly_heaven/assets/fly/fly_base.png")
out_dir = Path("fly_heaven/assets/fly/angles")
out_dir.mkdir(parents=True, exist_ok=True)

img = Image.open(src).convert("RGBA")
w, h = img.size
canvas_size = max(w, h) * 2

angles = [
    ("0",   0),
    ("1",  45),
    ("2",  90),
    ("3", 135),
    ("4", 180),
    ("5", 225),
    ("6", 270),
    ("7", 315),
]

for name, angle in angles:
    rotated = img.rotate(
        -angle,
        resample=Image.Resampling.NEAREST,
        expand=True
    )
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    x = (canvas_size - rotated.width) // 2
    y = (canvas_size - rotated.height) // 2
    canvas.alpha_composite(rotated, (x, y))
    canvas.save(out_dir / f"fly_{name}.png")

print("Saved to:", out_dir)
for p in sorted(out_dir.glob("*.png")):
    print(" -", p.name)
