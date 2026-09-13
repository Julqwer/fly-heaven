from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path("fly_heaven/visuals/fly")
OUT.mkdir(parents=True, exist_ok=True)

W, H = 320, 220
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img, "RGBA")

# wings (behind body)
d.ellipse([115, 48, 205, 112], fill=(220, 225, 235, 110), outline=(170, 175, 190, 140), width=2)
d.ellipse([150, 42, 240, 106], fill=(220, 225, 235, 100), outline=(170, 175, 190, 130), width=2)

# legs
leg = (40, 34, 37, 255)
for pts in [
    [(130,130), (95,150), (70,175)],
    [(145,138), (120,165), (102,192)],
    [(164,142), (150,170), (145,198)],
    [(182,136), (210,158), (238,180)],
    [(194,128), (228,146), (262,162)],
    [(168,126), (188,95), (205,72)],
]:
    d.line(pts, fill=leg, width=6)

# abdomen
d.ellipse([120, 92, 220, 170], fill=(58, 50, 54, 255))
# stripes
for x1, x2 in [(138,148), (160,170), (182,192)]:
    d.rectangle([x1, 100, x2, 162], fill=(92, 82, 64, 180))

# thorax
d.ellipse([96, 88, 160, 144], fill=(48, 42, 46, 255))

# head
d.ellipse([70, 92, 118, 132], fill=(42, 36, 40, 255))

# eyes
d.ellipse([60, 90, 86, 118], fill=(176, 54, 52, 255))
d.ellipse([82, 88, 108, 116], fill=(190, 62, 58, 255))

# antennae
d.line([(76,92), (60,78), (50,70)], fill=leg, width=3)
d.line([(94,90), (92,74), (100,62)], fill=leg, width=3)
d.ellipse([47,67,53,73], fill=leg)
d.ellipse([97,59,103,65], fill=leg)


path = OUT / "fly_base.png"
img.save(path)
print("Created:", path)
