"""
APC Mini MK2 -> Govee H619D per-segment light controller.

Grid:
  Rows (0 = bottom) -> 8 colors
  Columns (0 = left) -> 8 light segment groups

  Press any pad    -> apply that row's color to that column's segment group
  Scene buttons    -> set all segments to a preset color
  Master fader     -> brightness
"""

import sys
import time

from apc_mini import (
    APCMiniMK2,
    FADER_MASTER,
    SCENE_BTN_1, SCENE_BTN_2, SCENE_BTN_3, SCENE_BTN_4,
    SCENE_BTN_5, SCENE_BTN_6, SCENE_BTN_7, SCENE_BTN_8,
    SCENE_BUTTONS,
    COLOR_RED, COLOR_ORANGE, COLOR_YELLOW, COLOR_GREEN,
    COLOR_CYAN, COLOR_BLUE, COLOR_PURPLE, COLOR_MAGENTA,
    COLOR_WHITE,
    LED_100PCT, LED_75PCT, LED_25PCT,
)
from govee import GoveeController

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GOVEE_IP    = "192.168.0.49"
GOVEE_MODEL = "H619D"

# Total number of Govee segments (0-indexed). Calibrated: H619D has 15.
GOVEE_TOTAL_SEGMENTS = 15

# 8 APC columns -> Govee segment indices.
# The H619D has two strands starting at Bed Left corner, going clockwise
# and counterclockwise. Each segment number lights two mirrored physical spots.
# Walls clockwise: Window, Bed, Closet, Poster.
SEGMENT_GROUPS: list[list[int]] = [
    [0, 1],     # col 0 — Bed Left corner
    [2, 3],     # col 1
    [4, 5],     # col 2
    [6, 7],     # col 3
    [8, 9],     # col 4
    [10, 11],   # col 5
    [12, 13],   # col 6
    [14],       # col 7
]

# Row 0 (bottom) -> row 7 (top): APC pad color and RGB value.
ROW_COLORS = [
    COLOR_RED, COLOR_ORANGE, COLOR_YELLOW, COLOR_GREEN,
    COLOR_CYAN, COLOR_BLUE,  COLOR_PURPLE, COLOR_MAGENTA,
]
ROW_RGB: list[tuple[int, int, int]] = [
    (255,   0,   0),   # red
    (255, 100,   0),   # orange
    (255, 220,   0),   # yellow
    (  0, 255,   0),   # green
    (  0, 200, 255),   # cyan
    (  0,   0, 255),   # blue
    (160,   0, 255),   # purple
    (255,   0, 200),   # magenta
]

SCENE_COLORS: dict[int, tuple[int, int, int]] = {
    SCENE_BTN_1: ROW_RGB[0],
    SCENE_BTN_2: ROW_RGB[1],
    SCENE_BTN_3: ROW_RGB[2],
    SCENE_BTN_4: ROW_RGB[3],
    SCENE_BTN_5: ROW_RGB[4],
    SCENE_BTN_6: ROW_RGB[5],
    SCENE_BTN_7: ROW_RGB[6],
    SCENE_BTN_8: ROW_RGB[7],
}


def fader_to_brightness(value: int) -> int:
    return max(1, round(value / 127 * 100))


def connect_govee() -> GoveeController:
    print(f"Connecting to Govee at {GOVEE_IP}...")
    return GoveeController.connect_to(GOVEE_IP, model=GOVEE_MODEL)


def activate_ptreal(govee: GoveeController, r: int = 255, g: int = 255, b: int = 255):
    """Send one ptReal command per segment to put the device into segment mode.

    The H619D ignores ptReal commands if it was last controlled via colorwc (solid
    color mode). Sending any valid ptReal command breaks it out of that mode, so we
    seed all segments here on startup. Must also be called after any power cycle."""
    for s in range(GOVEE_TOTAL_SEGMENTS):
        govee.set_segment(s, r, g, b)
        time.sleep(0.05)  # device drops packets if commands arrive too fast


def apply_group(govee: GoveeController, col: int, r: int, g: int, b: int):
    """Send color to all Govee segments in this column's group."""
    for seg in SEGMENT_GROUPS[col]:
        govee.set_segment(seg, r, g, b)
        time.sleep(0.05)


def apply_all(govee: GoveeController, r: int, g: int, b: int):
    """Set every segment to the same color."""
    for s in range(GOVEE_TOTAL_SEGMENTS):
        govee.set_segment(s, r, g, b)
        time.sleep(0.05)


def paint_pads(apc: APCMiniMK2, segment_active_row: dict[int, int | None]):
    """Color pads by row. Active row per column = full brightness; others dimmed."""
    for col in range(8):
        active_row = segment_active_row[col]
        for row in range(8):
            pad = row * 8 + col
            if active_row is None:
                brightness = LED_75PCT
            elif row == active_row:
                brightness = LED_100PCT
            else:
                brightness = LED_25PCT
            apc.set_pad_color(pad, ROW_COLORS[row], brightness)

    # Scene buttons are single-color LEDs — set_pad_color() won't work on them.
    for note in SCENE_BUTTONS:
        apc.set_button_led(note, True)


def main():
    govee = connect_govee()
    govee.turn_on()
    time.sleep(0.5)  # give the device a moment to finish booting before ptReal commands

    print("Activating segment mode (setting all segments white)...")
    activate_ptreal(govee)

    print("Opening APC Mini MK2...")
    try:
        apc = APCMiniMK2()
    except RuntimeError as e:
        print(e)
        govee.close()
        sys.exit(1)

    # col -> row index of the currently applied color (None = not yet set)
    segment_active_row: dict[int, int | None] = {i: None for i in range(8)}
    # col -> (r, g, b)
    segment_colors: dict[int, tuple[int, int, int]] = {i: (255, 255, 255) for i in range(8)}

    paint_pads(apc, segment_active_row)
    print("Ready.")
    print("  Rows 0-7 (bottom->top)  = 8 colors")
    print("  Cols 0-7 (left->right)  = 8 light segment groups")
    print("  Press pad               -> set that segment to that color")
    print("  Scene buttons           -> set all segments to one color")
    print("  Master fader            -> brightness  |  Ctrl-C to exit\n")

    current_brightness = 100

    def on_pad_down(pad: int):
        row = pad // 8
        col = pad % 8
        r, g, b = ROW_RGB[row]
        segment_colors[col] = (r, g, b)
        segment_active_row[col] = row
        apply_group(govee, col, r, g, b)
        apc.set_pad_color(pad, COLOR_WHITE)  # flash white to acknowledge the press
        time.sleep(0.05)
        paint_pads(apc, segment_active_row)

    def on_scene_btn(note: int, pressed: bool):
        if not pressed:
            return
        r, g, b = SCENE_COLORS.get(note, (255, 255, 255))
        active_row = next((i for i, c in enumerate(ROW_RGB) if c == (r, g, b)), None)
        for col in range(8):
            segment_colors[col] = (r, g, b)
            segment_active_row[col] = active_row
        apply_all(govee, r, g, b)
        paint_pads(apc, segment_active_row)

    def on_fader(cc: int, value: int):
        nonlocal current_brightness
        if cc == FADER_MASTER:
            current_brightness = fader_to_brightness(value)
            govee.set_brightness(current_brightness)

    apc.on_pad_down  = on_pad_down
    apc.on_scene_btn = on_scene_btn
    apc.on_fader     = on_fader

    try:
        with apc:
            apc.listen()
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        govee.close()


if __name__ == "__main__":
    main()
