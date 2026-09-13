from pathlib import Path
from PIL import Image, ImageDraw
import math

OUT = Path("fly_heaven/visuals/smoking")
OUT.mkdir(parents=True, exist_ok=True)

W, H = 320, 180


def lerp(a, b, t):
    return a + (b - a) * t


def draw_cigarette(base, x, y, angle):
    cig = Image.new("RGBA", (90, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(cig)

    # paper
    d.rounded_rectangle(
        [8, 9, 66, 20],
        radius=5,
        fill=(238, 234, 220, 255),
    )

    # filter
    d.rounded_rectangle(
        [64, 9, 85, 20],
        radius=5,
        fill=(181, 118, 66, 255),
    )

    # ember
    d.ellipse(
        [4, 10, 13, 19],
        fill=(225, 82, 46, 255),
    )

    d.ellipse(
        [6, 12, 10, 17],
        fill=(255, 170, 92, 255),
    )

    cig = cig.rotate(
        angle,
        resample=Image.Resampling.BICUBIC,
        expand=True,
    )

    base.alpha_composite(
        cig,
        (
            int(x - cig.width / 2),
            int(y - cig.height / 2),
        ),
    )


def draw_leg(draw, hand_x, hand_y):
    # Fly foreleg entering from bottom-right.
    shoulder = (315, 176)

    elbow = (
        int((shoulder[0] + hand_x) / 2 + 16),
        int((shoulder[1] + hand_y) / 2 + 10),
    )

    leg = (46, 39, 42, 255)
    highlight = (78, 69, 73, 255)

    draw.line(
        [shoulder, elbow],
        fill=leg,
        width=10,
    )

    draw.line(
        [elbow, (hand_x, hand_y)],
        fill=leg,
        width=8,
    )

    draw.line(
        [shoulder, elbow],
        fill=highlight,
        width=3,
    )

    draw.ellipse(
        [elbow[0]-6, elbow[1]-6, elbow[0]+6, elbow[1]+6],
        fill=leg,
    )

    # tiny gripping "tarsus"
    draw.line(
        [(hand_x-4, hand_y-1), (hand_x+8, hand_y-5)],
        fill=leg,
        width=5,
    )


def draw_smoke(draw, phase):
    """Exhaled smoke originates at the fly's mouth, not the cigarette."""
    if phase <= 0:
        return

    # When the cigarette is raised, its burning tip reaches roughly here.
    # After the leg lowers, this point stays fixed as the mouth position.
    mouth_x, mouth_y = 101, 134

    puffs = [
        (mouth_x,     mouth_y,      10, 125),
        (mouth_x-8,   mouth_y-12,   15, 100),
        (mouth_x-18,  mouth_y-27,   21, 75),
        (mouth_x-31,  mouth_y-44,   28, 52),
    ]

    for i, (x, y, r, alpha) in enumerate(puffs):
        local = phase * 1.5 - i * 0.20

        if local <= 0:
            continue

        local = min(local, 1.0)

        # Smoke drifts away from the mouth and upward.
        xx = x - int(local * 10)
        yy = y - int(local * 14)
        rr = int(r * (0.75 + local * 0.65))
        aa = int(alpha * (1.0 - local * 0.68))

        draw.ellipse(
            [xx-rr, yy-rr, xx+rr, yy+rr],
            fill=(145, 145, 150, aa),
        )


# 16-frame cycle:
# 0-3   cigarette low
# 4-7   raise to mouth
# 8-9   inhale
# 10-12 lower
# 13-15 exhale smoke

frames = []

for i in range(16):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    low = (258, 148)
    mouth = (176, 139)

    if i <= 3:
        t = 0
    elif i <= 7:
        t = (i - 3) / 4
    elif i <= 9:
        t = 1
    elif i <= 12:
        t = 1 - (i - 9) / 3
    else:
        t = 0

    hand_x = int(lerp(low[0], mouth[0], t))
    hand_y = int(lerp(low[1], mouth[1], t))

    angle = lerp(-12, 4, t)

    draw_leg(draw, hand_x, hand_y)
    draw_cigarette(
        img,
        hand_x - 35,
        hand_y - 4,
        angle,
    )

    # Exhale.
    if i >= 13:
        draw_smoke(
            draw,
            (i - 12) / 3,
        )

    path = OUT / f"frame_{i:02d}.png"
    img.save(path)
    frames.append(img)

# GIF is only a convenient preview.
frames[0].save(
    OUT / "smoking_preview.gif",
    save_all=True,
    append_images=frames[1:],
    duration=110,
    loop=0,
    disposal=2,
)

print("Created 16 transparent frames")
print("Preview:", OUT / "smoking_preview.gif")
