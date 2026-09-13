"""Build the FLY HEAVEN sunset room."""

import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCENARIOS = HERE / "scenarios"
TEXTURES = HERE / "textures"
SPRITES = HERE / "assets" / "sprites"


def write_wad(path, entries):
    offset = 12
    body = bytearray()
    directory = bytearray()

    for name, data in entries:
        directory.extend(
            struct.pack(
                "<ii8s",
                offset,
                len(data),
                name.encode().ljust(8, b"\0"),
            )
        )
        body.extend(data)
        offset += len(data)

    path.write_bytes(
        struct.pack("<4sii", b"PWAD", len(entries), offset)
        + body
        + directory
    )


def room_text():
    lines = ['namespace = "ZDoom";']

    # 512 x 512 room
    for x, y in [
        (-256, -256),
        (-256,  256),
        ( 256,  256),
        ( 256, -256),
    ]:
        lines.append(f"vertex {{ x={x}.0; y={y}.0; }}")

    lines.append(
        'sector { '
        'heightfloor=0; '
        'heightceiling=160; '
        'texturefloor="SUNFLOOR"; '
        'textureceiling="SUNCEIL"; '
        'lightlevel=224; '
        '}'
    )

    # Player faces east (+X), so wall index 2 becomes the sunset wall.
    wall_textures = [
        "SUNWALL",
        "SUNWALL",
        "SUNWIN",
        "SUNWALL",
    ]

    for i, texture in enumerate(wall_textures):
        lines.append(
            f'sidedef {{ '
            f'sector=0; '
            f'texturemiddle="{texture}"; '
            f'}}'
        )

        lines.append(
            f"linedef {{ "
            f"v1={i}; "
            f"v2={(i + 1) % 4}; "
            f"sidefront={i}; "
            f"blocking=true; "
            f"}}"
        )

    # Fly viewpoint
    lines.append(
        'thing { '
        'x=0.0; y=0.0; angle=0; '
        'type=1; '
        'skill1=true; skill2=true; skill3=true; '
        'skill4=true; skill5=true; '
        'single=true; '
        '}'
    )

    # Visible fly actor in the 3D room
    lines.append(
        'thing { '
        'x=170.0; y=0.0; z=0.0; angle=180; '
        'type=3001; '
        'skill1=true; skill2=true; skill3=true; '
        'skill4=true; skill5=true; '
        'single=true; '
        '}'
    )

    return "\n".join(lines).encode()


def build():
    SCENARIOS.mkdir(parents=True, exist_ok=True)

    required = [
        "SUNWALL.png",
        "SUNFLOOR.png",
        "SUNCEIL.png",
        "SUNWIN.png",
    ]

    for name in required:
        if not (TEXTURES / name).exists():
            raise FileNotFoundError(TEXTURES / name)

    wad = SCENARIOS / "sunset_room.wad"
    cfg = SCENARIOS / "sunset_room.cfg"

    # TX_START / TX_END tells ZDoom these PNG lumps are textures.
    entries = [
        ("TX_START", b""),
        ("SUNWALL",  (TEXTURES / "SUNWALL.png").read_bytes()),
        ("SUNFLOOR", (TEXTURES / "SUNFLOOR.png").read_bytes()),
        ("SUNCEIL",  (TEXTURES / "SUNCEIL.png").read_bytes()),
        ("SUNWIN",   (TEXTURES / "SUNWIN.png").read_bytes()),
        ("TX_END", b""),

        ("DECORATE", b"""
actor FlyHeavenFly 3001
{
    Radius 8
    Height 56
    Health 1000000
    PainChance 255
    Scale 0.25

    +SHOOTABLE
    +NOBLOOD
    +NOGRAVITY
    +DONTTHRUST

    States
    {
    Spawn:
        // No automatic timer-driven action.
        FLYA A -1
        Stop

    Pain:
        // This state is triggered only by SMOKE.
        FLYA A 2
        FLYA B 2
        FLYA C 2
        FLYA D 2
        FLYA E 2
        FLYA F 2
        FLYA G 2
        FLYA H 2
        FLYA I 2
        FLYA J 2
        FLYA K 2
        FLYA L 2
        FLYA M 2
        FLYA N 2
        FLYA O 2
        FLYA P 2
        Goto Spawn
    }
}
"""),

        ("S_START", b""),
        ("FLYAA0", (SPRITES / "FLYAA0.png").read_bytes()),
        ("FLYAB0", (SPRITES / "FLYAB0.png").read_bytes()),
        ("FLYAC0", (SPRITES / "FLYAC0.png").read_bytes()),
        ("FLYAD0", (SPRITES / "FLYAD0.png").read_bytes()),
        ("FLYAE0", (SPRITES / "FLYAE0.png").read_bytes()),
        ("FLYAF0", (SPRITES / "FLYAF0.png").read_bytes()),
        ("FLYAG0", (SPRITES / "FLYAG0.png").read_bytes()),
        ("FLYAH0", (SPRITES / "FLYAH0.png").read_bytes()),
        ("FLYAI0", (SPRITES / "FLYAI0.png").read_bytes()),
        ("FLYAJ0", (SPRITES / "FLYAJ0.png").read_bytes()),
        ("FLYAK0", (SPRITES / "FLYAK0.png").read_bytes()),
        ("FLYAL0", (SPRITES / "FLYAL0.png").read_bytes()),
        ("FLYAM0", (SPRITES / "FLYAM0.png").read_bytes()),
        ("FLYAN0", (SPRITES / "FLYAN0.png").read_bytes()),
        ("FLYAO0", (SPRITES / "FLYAO0.png").read_bytes()),
        ("FLYAP0", (SPRITES / "FLYAP0.png").read_bytes()),
        ("S_END", b""),

        ("MAP01", b""),
        ("TEXTMAP", room_text()),
        ("ENDMAP", b""),
    ]

    write_wad(wad, entries)

    cfg.write_text(
        "\n".join(
            [
                "doom_scenario_path = sunset_room.wad",
                "doom_map = map01",
                "doom_skill = 3",
                "episode_start_time = 10",
                "episode_timeout = 0",
                "render_hud = false",
                "render_weapon = false",
                "mode = PLAYER",
                "",
            ]
        )
    )

    print("Rebuilt:", wad)
    print("Custom textures embedded.")
    print("Weapon rendering disabled.")


if __name__ == "__main__":
    build()
