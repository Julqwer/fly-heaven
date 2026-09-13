from pathlib import Path
from PIL import Image

room_path = Path("fly_heaven/sunset_room_preview.png")
fly_path = Path("fly_heaven/visuals/fly/fly_base.png")
out_path = Path("fly_heaven/fly_in_room_preview.png")

room = Image.open(room_path).convert("RGBA")
fly = Image.open(fly_path).convert("RGBA")

# уменьшаем муху
target_w = 170
scale = target_w / fly.width
target_h = int(fly.height * scale)
fly = fly.resize((target_w, target_h), Image.NEAREST)

# позиция: на полу, чуть правее центра
x = room.width // 2 - fly.width // 2
y = room.height - fly.height - 35

layer = Image.new("RGBA", room.size, (0, 0, 0, 0))
layer.alpha_composite(fly, (x, y))

final = Image.alpha_composite(room, layer)
final.save(out_path)
print("Saved:", out_path)
