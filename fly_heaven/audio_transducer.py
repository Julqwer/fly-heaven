"""Convert real audio into an engineered Drosophila auditory stimulus.

This is NOT a calibrated physical model of the antenna.

Approximation:
    JO-B proxy: 20-100 Hz vibration energy
    JO-A proxy: 100-1000 Hz vibration energy

Output is sampled in 10 ms bins for later neural stimulation.
"""

from pathlib import Path
import json

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt


ROOT = Path(__file__).resolve().parent

SOURCE = ROOT / "private_audio" / "video_games_mono.wav"
OUTPUT = ROOT / "private_audio" / "video_games_jo.npz"

BIN_MS = 10
JO_B_BAND = (20.0, 100.0)
JO_A_BAND = (100.0, 1000.0)


def load_audio(path):
    fs, audio = wavfile.read(path)

    if audio.ndim != 1:
        raise ValueError("Expected mono WAV")

    if np.issubdtype(audio.dtype, np.integer):
        scale = float(max(abs(np.iinfo(audio.dtype).min),
                          np.iinfo(audio.dtype).max))
        audio = audio.astype(np.float32) / scale
    else:
        audio = audio.astype(np.float32)

    if not np.isfinite(audio).all():
        raise ValueError("Non-finite audio samples")

    return fs, audio


def band_rms(audio, fs, low, high, samples_per_bin):
    sos = butter(
        4,
        [low, high],
        btype="bandpass",
        fs=fs,
        output="sos",
    )

    filtered = sosfilt(sos, audio).astype(np.float32)

    usable = (
        len(filtered) // samples_per_bin
    ) * samples_per_bin

    filtered = filtered[:usable]

    windows = filtered.reshape(
        -1,
        samples_per_bin,
    )

    rms = np.sqrt(
        np.mean(
            windows.astype(np.float64) ** 2,
            axis=1,
        )
    ).astype(np.float32)

    return rms


def robust_normalize(x):
    # Do not let one extreme transient define the whole song.
    ceiling = float(np.quantile(x, 0.99))

    if ceiling <= 0:
        return np.zeros_like(x)

    return np.clip(
        x / ceiling,
        0.0,
        1.0,
    ).astype(np.float32)


def main():
    fs, audio = load_audio(SOURCE)

    samples_per_bin = round(
        fs * BIN_MS / 1000
    )

    if samples_per_bin <= 0:
        raise ValueError("Invalid temporal bin")

    jo_b_raw = band_rms(
        audio,
        fs,
        *JO_B_BAND,
        samples_per_bin,
    )

    jo_a_raw = band_rms(
        audio,
        fs,
        *JO_A_BAND,
        samples_per_bin,
    )

    n = min(
        len(jo_a_raw),
        len(jo_b_raw),
    )

    jo_a_raw = jo_a_raw[:n]
    jo_b_raw = jo_b_raw[:n]

    jo_a = robust_normalize(jo_a_raw)
    jo_b = robust_normalize(jo_b_raw)

    time_s = (
        np.arange(n, dtype=np.float32)
        * BIN_MS
        / 1000.0
    )

    metadata = {
        "source": SOURCE.name,
        "sample_rate_hz": int(fs),
        "bin_ms": BIN_MS,
        "bins": int(n),
        "duration_s": float(n * BIN_MS / 1000),
        "jo_a_band_hz": JO_A_BAND,
        "jo_b_band_hz": JO_B_BAND,
        "normalization": "independent 99th-percentile RMS",
        "interpretation":
            "Engineered audio-derived mechanosensory proxy; "
            "not calibrated antennal biomechanics.",
    }

    np.savez_compressed(
        OUTPUT,
        time_s=time_s,
        jo_a=jo_a,
        jo_b=jo_b,
        jo_a_raw=jo_a_raw,
        jo_b_raw=jo_b_raw,
        metadata=json.dumps(metadata),
    )

    print()
    print("=== LANA -> FLY AUDIO ===")
    print("Source:", SOURCE.name)
    print("Sample rate:", fs, "Hz")
    print("Duration:", round(metadata["duration_s"], 2), "s")
    print("10 ms bins:", n)
    print()
    print("JO-B proxy:", JO_B_BAND, "Hz")
    print(
        "  mean =", round(float(jo_b.mean()), 4),
        "| max =", round(float(jo_b.max()), 4),
    )
    print()
    print("JO-A proxy:", JO_A_BAND, "Hz")
    print(
        "  mean =", round(float(jo_a.mean()), 4),
        "| max =", round(float(jo_a.max()), 4),
    )
    print()
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()
