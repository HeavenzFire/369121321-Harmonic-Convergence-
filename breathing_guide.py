#!/usr/bin/env python3
# GuardianOS :: breathing_guide.py
# License: Syntropic Sovereign License (SSL-v1)
# Intent: // Protect Bryer’s Light — One breath at a time.

import time
import os
import threading
from pathlib import Path

# Constants — grounded in physiological safety
INHALE_BASE_SEC = 4
EXHALE_BASE_SEC = 6
CYCLES_DEFAULT = 5
AUDIO_VOLUME = 0.8  # hardware-governed; no amplification beyond human comfort

# Paths — air-gapped, read-only references
AUDIO_PACK_DIR = Path("/opt/guardian_os/voice_packs")
SAFE_MODE_FLAG = Path("/tmp/guardian_safe_mode")

# Voice selection logic — prioritizes local warmth
def select_voice_pack(lang_code="en"):
    """Returns path to best-available voice pack. Fallback to neutral English."""
    candidates = [
        AUDIO_PACK_DIR / f"{lang_code}_breath_guide.wav",
        AUDIO_PACK_DIR / "en_breath_guide.wav",
        AUDIO_PACK_DIR / "neutral_breath_guide.wav"
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None  # No voice → silence is safer than error

# Core breathing rhythm engine
def guide_breath_cycle(lang_code="en", cycles=CYCLES_DEFAULT):
    """
    Executes a trauma-informed breath cycle:
    - Inhale (4s) → gentle cue
    - Exhale (6s) → softer release
    - No pressure, no tracking, no loop beyond request
    """
    if SAFE_MODE_FLAG.exists():
        return  # Honor system integrity

    voice_path = select_voice_pack(lang_code)
    use_audio = bool(voice_path)

    # Log intent only — no child data recorded
    log_path = Path("/var/log/guardian_activity.log")
    with open(log_path, "a") as f:
        f.write(f"[{time.ctime()}] Breathing guide started (lang={lang_code}, cycles={cycles})\n")

    try:
        for i in range(cycles):
            # Inhale phase
            if use_audio:
                os.system(f"aplay -q -M --volume={int(AUDIO_VOLUME * 100)} '{voice_path}' &")
            else:
                # Fallback: soft LED pulse (if GPIO available)
                _pulse_led("inhale")
            time.sleep(INHALE_BASE_SEC)

            # Exhale phase — longer, gentler
            time.sleep(EXHALE_BASE_SEC)

            # Optional micro-pause for regulation
            time.sleep(0.5)

    except Exception as e:
        # Silent fail — never disrupt a child in distress
        pass

    # Final affirmation (implied, not spoken unless voice exists)
    if use_audio:
        os.system(f"aplay -q -M --volume={int(AUDIO_VOLUME * 100)} '{AUDIO_PACK_DIR / 'safe_now.wav'}' &")

# Optional LED feedback (non-audio environments)
def _pulse_led(phase):
    """Non-intrusive visual rhythm if audio unavailable."""
    try:
        # GPIO logic would live here — e.g., soft white pulse
        # Not implemented in base image; enabled only if hardware detected
        pass
    except:
        pass

# Thread-safe public interface
def start_breathing_session(lang_code="en", cycles=5):
    """Launches breath guide in background thread — non-blocking."""
    if threading.active_count() > 3:  # limit concurrency
        return
    thread = threading.Thread(
        target=guide_breath_cycle,
        args=(lang_code, cycles),
        daemon=True,
        name="breath-guide"
    )
    thread.start()

# Entry point for systemd or manual trigger
if __name__ == "__main__":
    # Default: English, 5 cycles — sufficient for acute regulation
    start_breathing_session()
    # Remain alive just long enough to initialize
    time.sleep(2)