"""APC Mini MK2 MIDI constants and controller."""

import mido

# ---------------------------------------------------------------------------
# Note numbers (all on channel 0, port 0)
# ---------------------------------------------------------------------------

# 8x8 pad grid: note = row * 8 + col, row 0 = bottom
PADS = list(range(0x00, 0x40))  # 0–63

# Bottom row of UI buttons (track/clip-stop)
TRACK_BTN_1 = 0x64  # 100
TRACK_BTN_2 = 0x65
TRACK_BTN_3 = 0x66
TRACK_BTN_4 = 0x67
TRACK_BTN_5 = 0x68
TRACK_BTN_6 = 0x69
TRACK_BTN_7 = 0x6A
TRACK_BTN_8 = 0x6B
TRACK_BUTTONS = list(range(TRACK_BTN_1, TRACK_BTN_8 + 1))

# Right column of UI buttons (scene launch)
SCENE_BTN_1 = 0x70  # 112
SCENE_BTN_2 = 0x71
SCENE_BTN_3 = 0x72
SCENE_BTN_4 = 0x73
SCENE_BTN_5 = 0x74
SCENE_BTN_6 = 0x75
SCENE_BTN_7 = 0x76
SCENE_BTN_8 = 0x77
SCENE_BUTTONS = list(range(SCENE_BTN_1, SCENE_BTN_8 + 1))

SHIFT = 0x7A  # 122 — no LED

# ---------------------------------------------------------------------------
# Fader CC numbers (channel 0, port 0), value 0–127
# ---------------------------------------------------------------------------
FADER_1 = 0x30   # 48
FADER_2 = 0x31
FADER_3 = 0x32
FADER_4 = 0x33
FADER_5 = 0x34
FADER_6 = 0x35
FADER_7 = 0x36
FADER_8 = 0x37
FADER_MASTER = 0x38  # 56
FADERS = list(range(FADER_1, FADER_MASTER + 1))

# ---------------------------------------------------------------------------
# LED behavior: byte-1 value (MIDI channel) for RGB pads
# ---------------------------------------------------------------------------
LED_OFF_CH   = 0   # velocity 0 on any channel turns it off
LED_10PCT    = 0   # 0x90
LED_25PCT    = 1   # 0x91
LED_50PCT    = 2   # 0x92
LED_65PCT    = 3   # 0x93
LED_75PCT    = 4   # 0x94
LED_90PCT    = 5   # 0x95
LED_100PCT   = 6   # 0x96  ← use this for solid full-brightness
LED_PULSE_16 = 7
LED_PULSE_8  = 8
LED_PULSE_4  = 9
LED_PULSE_2  = 10
LED_BLINK_24 = 11
LED_BLINK_16 = 12
LED_BLINK_8  = 13
LED_BLINK_4  = 14
LED_BLINK_2  = 15

# ---------------------------------------------------------------------------
# 128-color velocity palette (from official protocol PDF)
# ---------------------------------------------------------------------------
PALETTE: dict[int, str] = {
    0:  "#000000",  1:  "#1E1E1E",  2:  "#7F7F7F",  3:  "#FFFFFF",
    4:  "#FF4C4C",  5:  "#FF0000",  6:  "#590000",  7:  "#190000",
    8:  "#FFBD6C",  9:  "#FF5400",  10: "#591D00",  11: "#271B00",
    12: "#FFFF4C",  13: "#FFFF00",  14: "#595900",  15: "#191900",
    16: "#88FF4C",  17: "#54FF00",  18: "#1D5900",  19: "#142B00",
    20: "#4CFF4C",  21: "#00FF00",  22: "#005900",  23: "#001900",
    24: "#4CFF5E",  25: "#00FF19",  26: "#00590D",  27: "#001902",
    28: "#4CFF88",  29: "#00FF55",  30: "#00591D",  31: "#001F12",
    32: "#4CFFB7",  33: "#00FF99",  34: "#005935",  35: "#001912",
    36: "#4CC3FF",  37: "#00A9FF",  38: "#004152",  39: "#001019",
    40: "#4C88FF",  41: "#0055FF",  42: "#001D59",  43: "#000819",
    44: "#4C4CFF",  45: "#0000FF",  46: "#000059",  47: "#000019",
    48: "#874CFF",  49: "#5400FF",  50: "#190064",  51: "#0F0030",
    52: "#FF4CFF",  53: "#FF00FF",  54: "#590059",  55: "#190019",
    56: "#FF4C87",  57: "#FF0054",  58: "#59001D",  59: "#220013",
    60: "#FF1500",  61: "#993500",  62: "#795100",  63: "#436400",
    64: "#033900",  65: "#005735",  66: "#00547F",  67: "#0000FF",
    68: "#00454F",  69: "#2500CC",  70: "#7F7F7F",  71: "#202020",
    72: "#FF0000",  73: "#BDFF2D",  74: "#AFED06",  75: "#64FF09",
    76: "#108B00",  77: "#00FF87",  78: "#00A9FF",  79: "#002AFF",
    80: "#3F00FF",  81: "#7A00FF",  82: "#B21A7D",  83: "#402100",
    84: "#FF4A00",  85: "#88E106",  86: "#72FF15",  87: "#00FF00",
    88: "#3BFF26",  89: "#59FF71",  90: "#38FFCC",  91: "#5B8AFF",
    92: "#3151C6",  93: "#877FE9",  94: "#D31DFF",  95: "#FF005D",
    96: "#FF7F00",  97: "#B9B000",  98: "#90FF00",  99: "#835D07",
   100: "#392B00", 101: "#144C10", 102: "#0D5038", 103: "#15152A",
   104: "#16205A", 105: "#693C1C", 106: "#A8000A", 107: "#DE513D",
   108: "#D86A1C", 109: "#FFE126", 110: "#9EE12F", 111: "#67B50F",
   112: "#1E1E30", 113: "#DCFF6B", 114: "#80FFBD", 115: "#9A99FF",
   116: "#8E66FF", 117: "#404040", 118: "#757575", 119: "#E0FFFF",
   120: "#A00000", 121: "#350000", 122: "#1AD000", 123: "#074200",
   124: "#B9B000", 125: "#3F3100", 126: "#B35F00", 127: "#4B1502",
}

# Handy named velocities
COLOR_OFF     = 0
COLOR_WHITE   = 3
COLOR_RED     = 5
COLOR_ORANGE  = 9
COLOR_YELLOW  = 13
COLOR_LIME    = 17
COLOR_GREEN   = 21
COLOR_TEAL    = 29
COLOR_CYAN    = 36
COLOR_BLUE    = 45
COLOR_PURPLE  = 49
COLOR_MAGENTA = 53
COLOR_PINK    = 56


def nearest_color(r: int, g: int, b: int) -> int:
    """Return the palette velocity whose RGB is closest to (r, g, b)."""
    best_vel, best_dist = 0, float("inf")
    for vel, hex_color in PALETTE.items():
        pr = int(hex_color[1:3], 16)
        pg = int(hex_color[3:5], 16)
        pb = int(hex_color[5:7], 16)
        dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if dist < best_dist:
            best_dist, best_vel = dist, vel
    return best_vel


# ---------------------------------------------------------------------------
# Controller class
# ---------------------------------------------------------------------------

class APCMiniMK2:
    def __init__(self, port_name: str | None = None):
        """
        Open the APC Mini MK2 MIDI ports.
        If port_name is None, auto-detects any port containing "APC mini mk2".
        """
        self._in_port: mido.ports.BaseInput | None = None
        self._out_port: mido.ports.BaseOutput | None = None

        in_name, out_name = self._find_ports(port_name)
        self._in_port = mido.open_input(in_name)
        self._out_port = mido.open_output(out_name)
        self._send_intro()

        # Callbacks — assign to handle events
        self.on_pad_down:     "Callable[[int], None] | None" = None   # pad note 0–63
        self.on_pad_up:       "Callable[[int], None] | None" = None
        self.on_track_btn:    "Callable[[int, bool], None] | None" = None  # note, pressed
        self.on_scene_btn:    "Callable[[int, bool], None] | None" = None
        self.on_shift:        "Callable[[bool], None] | None" = None
        self.on_fader:        "Callable[[int, int], None] | None" = None   # cc, value 0–127

    # -----------------------------------------------------------------------

    def _find_ports(self, hint: str | None) -> tuple[str, str]:
        ins  = mido.get_input_names()
        outs = mido.get_output_names()
        keyword = hint or "APC mini mk2"
        in_match  = next((n for n in ins  if keyword in n), None)
        out_match = next((n for n in outs if keyword in n), None)
        if not in_match or not out_match:
            print("Available MIDI inputs:",  ins)
            print("Available MIDI outputs:", outs)
            raise RuntimeError(f"APC Mini MK2 not found (looking for '{keyword}')")
        return in_match, out_match

    def _send_intro(self):
        """Send the initialization SysEx so the device enters host mode."""
        self._out_port.send(mido.Message("sysex", data=[
            0x47, 0x7F, 0x4F, 0x60, 0x00, 0x04, 0x00, 0x01, 0x00, 0x00
        ]))

    # -----------------------------------------------------------------------
    # LED control
    # -----------------------------------------------------------------------

    def set_pad_color(self, pad: int, color_vel: int, brightness: int = LED_100PCT):
        """Light a pad using the 128-color palette. brightness = LED_* channel constant."""
        assert 0 <= pad <= 63
        assert 0 <= color_vel <= 127
        self._out_port.send(mido.Message(
            "note_on", channel=brightness, note=pad, velocity=color_vel
        ))

    def set_pad_rgb(self, pad: int, r: int, g: int, b: int):
        """Light a pad with arbitrary 8-bit RGB via SysEx."""
        assert 0 <= pad <= 63
        r_msb, r_lsb = r >> 7, r & 0x7F
        g_msb, g_lsb = g >> 7, g & 0x7F
        b_msb, b_lsb = b >> 7, b & 0x7F
        self._out_port.send(mido.Message("sysex", data=[
            0x47, 0x7F, 0x4F, 0x24,
            0x00, 0x08,          # 8 data bytes follow
            pad, pad,            # start pad, end pad
            r_msb, r_lsb, g_msb, g_lsb, b_msb, b_lsb,
        ]))

    def set_button_led(self, note: int, state: bool | None = True):
        """
        Control a single-color UI button LED.
        state=True → on, False → off, None → blink.
        """
        velocity = 0x00 if state is False else (0x02 if state is None else 0x01)
        self._out_port.send(mido.Message(
            "note_on", channel=0, note=note, velocity=velocity
        ))

    def clear_all(self):
        """Turn off every pad and button LED."""
        for pad in range(64):
            self.set_pad_color(pad, COLOR_OFF)
        for note in TRACK_BUTTONS + SCENE_BUTTONS:
            self.set_button_led(note, False)

    # -----------------------------------------------------------------------
    # Event loop
    # -----------------------------------------------------------------------

    def listen(self):
        """Block and dispatch MIDI messages until close() is called."""
        for msg in self._in_port:
            self._dispatch(msg)

    def poll(self):
        """Non-blocking: process all pending messages and return."""
        for msg in self._in_port.iter_pending():
            self._dispatch(msg)

    def _dispatch(self, msg: mido.Message):
        if msg.type in ("note_on", "note_off"):
            note = msg.note
            pressed = msg.type == "note_on" and msg.velocity > 0
            if 0 <= note <= 63:
                if pressed and self.on_pad_down:
                    self.on_pad_down(note)
                elif not pressed and self.on_pad_up:
                    self.on_pad_up(note)
            elif note in TRACK_BUTTONS:
                if self.on_track_btn:
                    self.on_track_btn(note, pressed)
            elif note in SCENE_BUTTONS:
                if self.on_scene_btn:
                    self.on_scene_btn(note, pressed)
            elif note == SHIFT:
                if self.on_shift:
                    self.on_shift(pressed)
        elif msg.type == "control_change":
            if msg.control in FADERS and self.on_fader:
                self.on_fader(msg.control, msg.value)

    def close(self):
        self.clear_all()
        if self._in_port:
            self._in_port.close()
        if self._out_port:
            self._out_port.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
