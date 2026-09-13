"""FLY HEAVEN — live code / neural event visualizer.

This is a presentation layer only. It does not control the simulation.
It tails /tmp/fly_heaven.log and synchronizes the display to real runtime
messages emitted by fly_heaven.run_heaven.

Run:
    python -m fly_heaven.live_code
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import time
from collections import deque
from pathlib import Path


LOG_PATH = Path(os.environ.get("FLY_HEAVEN_LOG", "/tmp/fly_heaven.log"))
REFRESH_HZ = 12.0

ESC = "\x1b["
RESET = f"{ESC}0m"
BOLD = f"{ESC}1m"
DIM = f"{ESC}2m"
CYAN = f"{ESC}38;5;51m"
MAGENTA = f"{ESC}38;5;213m"
PINK = f"{ESC}38;5;205m"
ORANGE = f"{ESC}38;5;214m"
GREEN = f"{ESC}38;5;82m"
YELLOW = f"{ESC}38;5;226m"
RED = f"{ESC}38;5;203m"
GRAY = f"{ESC}38;5;245m"
WHITE = f"{ESC}38;5;255m"
BLUE = f"{ESC}38;5;117m"

SMOKE_RE = re.compile(
    r"SMOKE #(\d+).*?song\s+([0-9.]+)s.*?loop\s+(\d+)\s+\|\s+(TRAINING|FROZEN)"
)
LOOP_RE = re.compile(r"Video Games loop\s+(\d+)")
EFF_RE = re.compile(r"mean KC->MBON05 efficacy:\s*([0-9.]+)")


CODE_STEPS = [
    ("AUDIO INPUT", [
        "position_s, bin_index, loop_number = current_song_position()",
        "stimulation = song.stimulation(bin_index)",
        "# Video Games -> JO-A / JO-B current drive",
    ]),
    ("FULL CONNECTOME", [
        "counts, _ = brain.step(",
        "    darkness, duration_ms=BIN_MS,",
        "    learning=not weights_frozen,",
        "    stimulation=stimulation,",
        ")",
    ]),
    ("MOTOR READOUT", [
        "mn9_spikes = int(counts[mn9].sum())",
        "smoke = decoder.update(",
        "    time_s=wall_time,",
        "    mn9_spikes=mn9_spikes,",
        ")",
    ]),
    ("SELF-INITIATED ACTION", [
        "if smoke:",
        "    stats[\"smokes\"] += 1",
        "    smoke_requests.put_nowait(True)",
        "    # MN9 -> visible SMOKE",
    ]),
    ("APPETITIVE CONSEQUENCE", [
        "reward_stimulation.append((",
        "    circuit[\"dan\"],",
        "    CIGARETTE_REWARD_CURRENT,",
        "))",
        "# PAM07 reward pulse: 200 ms",
    ]),
    ("PLASTICITY", [
        "brain.step(",
        "    darkness, duration_ms=BIN_MS,",
        "    learning=training_this_smoke,",
        "    stimulation=reward_stimulation,",
        ")",
    ]),
]


class State:
    def __init__(self):
        self.loop = 0
        self.smokes = 0
        self.song_s = 0.0
        self.phase = "WAITING"
        self.reward_until = 0.0
        self.trigger_until = 0.0
        self.efficacy = None
        self.last_event = "waiting for FLY HEAVEN..."
        self.events = deque(maxlen=7)
        self.started = time.monotonic()
        self.code_step = 0

    def push(self, text: str):
        stamp = time.strftime("%H:%M:%S")
        self.events.appendleft(f"{stamp}  {text}")
        self.last_event = text


def strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def fit(s: str, width: int) -> str:
    plain = strip_ansi(s)
    if len(plain) <= width:
        return s + " " * (width - len(plain))
    keep = max(0, width - 1)
    # Safe for our own colored lines: truncate plain display content only.
    return plain[:keep] + "…"


def color_code(line: str) -> str:
    out = line
    replacements = [
        ("brain.step", f"{CYAN}brain.step{RESET}"),
        ("song.stimulation", f"{MAGENTA}song.stimulation{RESET}"),
        ("decoder.update", f"{PINK}decoder.update{RESET}"),
        ("mn9_spikes", f"{ORANGE}mn9_spikes{RESET}"),
        ("smoke", f"{ORANGE}smoke{RESET}"),
        ("PAM07", f"{GREEN}PAM07{RESET}"),
        ("CIGARETTE_REWARD_CURRENT", f"{GREEN}CIGARETTE_REWARD_CURRENT{RESET}"),
        ("training_this_smoke", f"{YELLOW}training_this_smoke{RESET}"),
        ("reward_stimulation", f"{GREEN}reward_stimulation{RESET}"),
    ]
    for old, new in replacements:
        out = out.replace(old, new)
    return out


def parse_line(line: str, state: State):
    if not line:
        return

    m = LOOP_RE.search(line)
    if m:
        state.loop = int(m.group(1))
        state.push(f"🎵 Video Games loop {state.loop}")
        return

    m = SMOKE_RE.search(line)
    if m:
        state.smokes = int(m.group(1))
        state.song_s = float(m.group(2))
        state.loop = int(m.group(3))
        state.phase = m.group(4)
        state.trigger_until = time.monotonic() + 1.3
        state.code_step = 3
        state.push(
            f"🚬 SMOKE #{state.smokes}  |  song {state.song_s:.2f}s  |  {state.phase}"
        )
        return

    if "PAM07 reward" in line:
        state.reward_until = time.monotonic() + 1.4
        state.code_step = 4
        state.push("↳ PAM07 appetitive reward — 200 ms")
        return

    if "TRAINING COMPLETE" in line:
        state.phase = "FROZEN"
        state.code_step = 5
        state.push("🧠 training complete — weights frozen")
        return

    m = EFF_RE.search(line)
    if m:
        state.efficacy = float(m.group(1))
        state.push(f"KC→MBON05 mean efficacy = {state.efficacy:.6f}")
        return

    if "Leaving FLY HEAVEN" in line:
        state.push("session stopping")
        return


def tail_new_lines(handle, state: State):
    while True:
        pos = handle.tell()
        line = handle.readline()
        if not line:
            handle.seek(pos)
            break
        parse_line(line.rstrip("\n"), state)


def draw_box(lines, width, title=None):
    width = max(12, width)
    top_title = f" {title} " if title else ""
    spare = max(0, width - 2 - len(top_title))
    left = spare // 2
    right = spare - left
    out = ["┌" + "─" * left + top_title + "─" * right + "┐"]
    for line in lines:
        out.append("│" + fit(line, width - 2) + "│")
    out.append("└" + "─" * (width - 2) + "┘")
    return out


def render(state: State):
    cols, rows = shutil.get_terminal_size((120, 36))
    cols = max(cols, 84)
    rows = max(rows, 28)

    now = time.monotonic()
    reward_on = now < state.reward_until
    trigger_on = now < state.trigger_until

    # When there is no discrete event, cycle through the actual control-flow code.
    if not trigger_on and not reward_on:
        elapsed = now - state.started
        state.code_step = int(elapsed / 1.6) % len(CODE_STEPS)

    section, code = CODE_STEPS[state.code_step]

    header = [
        f"{BOLD}{PINK}FLY HEAVEN{RESET}  {DIM}// live neural code trace{RESET}",
        f"{GRAY}Video Games → JO → MaleCNS → MN9 → SMOKE → PAM07 → plasticity{RESET}",
    ]

    reward_badge = (
        f"{BOLD}{GREEN}████  PAM07 REWARD ON  ████{RESET}"
        if reward_on
        else f"{DIM}PAM07 reward idle{RESET}"
    )

    trigger_badge = (
        f"{BOLD}{ORANGE}MN9 TRIGGER → SELF-INITIATED SMOKE{RESET}"
        if trigger_on
        else f"{DIM}MN9 decoder listening…{RESET}"
    )

    phase_color = YELLOW if state.phase == "TRAINING" else BLUE
    eff = "—" if state.efficacy is None else f"{state.efficacy:.6f}"

    stats_lines = [
        f"song loop      {BOLD}{state.loop}{RESET}",
        f"last song pos  {BOLD}{state.song_s:7.2f} s{RESET}",
        f"SMOKEs         {BOLD}{ORANGE}{state.smokes}{RESET}",
        f"plasticity     {BOLD}{phase_color}{state.phase}{RESET}",
        f"KC→MBON05 η̄    {BOLD}{eff}{RESET}",
        "",
        trigger_badge,
        reward_badge,
    ]

    code_lines = [
        f"{BOLD}{CYAN}{section}{RESET}",
        "",
    ]
    for i, line in enumerate(code):
        bullet = f"{PINK}›{RESET} " if i == 0 else "  "
        code_lines.append(bullet + color_code(line))

    event_lines = list(state.events) or ["no runtime events yet"]
    while len(event_lines) < 7:
        event_lines.append("")

    gap = 2
    left_w = max(48, int(cols * 0.62))
    right_w = cols - left_w - gap
    if right_w < 28:
        left_w = cols - 30
        right_w = 28

    code_box = draw_box(code_lines + [""] * max(0, 9 - len(code_lines)), left_w, "EXECUTING PATH")
    stats_box = draw_box(stats_lines, right_w, "LIVE STATE")

    event_w = min(cols, 110)
    event_box = draw_box(
        [f"{GRAY}{e}{RESET}" for e in event_lines],
        event_w,
        "REAL EVENTS FROM run_heaven.py",
    )

    canvas = []
    canvas.extend(header)
    canvas.append("")

    h = max(len(code_box), len(stats_box))
    for i in range(h):
        l = code_box[i] if i < len(code_box) else " " * left_w
        r = stats_box[i] if i < len(stats_box) else " " * right_w
        canvas.append(l + " " * gap + r)

    canvas.append("")
    canvas.extend(event_box)
    canvas.append("")
    canvas.append(
        f"{DIM}presentation layer only • runtime events are read from {LOG_PATH} • Ctrl+C to close monitor{RESET}"
    )

    sys.stdout.write(f"{ESC}H{ESC}2J")
    sys.stdout.write("\n".join(canvas[:rows]))
    sys.stdout.flush()


def main():
    # Hide cursor and set terminal title.
    sys.stdout.write(f"{ESC}?25l{ESC}]0;FLY HEAVEN // LIVE CODE\x07")
    sys.stdout.flush()

    state = State()
    handle = None

    try:
        while True:
            if handle is None:
                try:
                    handle = LOG_PATH.open("r", encoding="utf-8", errors="replace")
                    # Read existing content so the dashboard can recover state.
                    for line in handle:
                        parse_line(line.rstrip("\n"), state)
                except FileNotFoundError:
                    pass

            if handle is not None:
                tail_new_lines(handle, state)

            render(state)
            time.sleep(1.0 / REFRESH_HZ)

    except KeyboardInterrupt:
        pass
    finally:
        if handle is not None:
            handle.close()
        sys.stdout.write(f"{RESET}{ESC}?25h\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
