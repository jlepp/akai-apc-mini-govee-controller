# APC Mini MK2 + Govee H619D — Project Notes

## Govee LAN API

- LAN control must be enabled in the Govee Home app per device.
- Discovery: send a `scan` UDP packet to multicast `239.255.255.250:4001`; devices respond on port `4002`.
- Commands: send JSON to `{device_ip}:4003`. Responses come back to port `4002` (not the sender's ephemeral port — bind a separate socket to 4002 to receive them).
- Basic commands (`turn`, `brightness`, `colorwc`) work reliably.
- `colorwc` puts the device into solid-color mode. Sending `colorwc` then `ptReal` does NOT work — `ptReal` is silently ignored after `colorwc`.
- To recover: power-cycle the device (`turn off` then `turn on`) before using `ptReal`.

## Govee H619D Specifics

- Discovered at `192.168.0.49`.
- **Physical layout**: two LED strands that start together at the Bed Left corner, split and run in opposite directions (one clockwise, one counterclockwise around the room), and meet at the far end. Each segment number lights two mirrored physical spots — one on each strand.
- **Walls** (clockwise): Window, Bed, Closet, Poster.
- **Segment count**: 15 segments (indices 0–14), addressed via bitmask.
- `ptReal` with raw hex-encoded LED data (e.g. `0x74 0x00 0x00 + RGB*n`) does NOT work on this device. The correct format uses **base64-encoded BLE packets**.

### ptReal BLE packet format

```
byte  0:    0x33        (BLE command header)
bytes 1-2:  0x05 0x15   (LED domain, color mode)
byte  3:    0x01        (color subcommand)
bytes 4-6:  R G B       (color, 0-255 each)
bytes 7-11: 0x00 * 5    (temperature, zero for colored light)
bytes 12-18: bitmask    (7-byte little-endian; bit N = segment N)
byte  19:   XOR checksum of bytes 0-18
```

Encode the 20-byte packet as base64 and send as:
```json
{"msg": {"cmd": "ptReal", "data": {"command": ["<base64>"]}}}
```

To set segment `N`: `bitmask = (1 << N).to_bytes(7, 'little')`.

### Segment group mapping (calibrated)

| APC col | Govee segments | Physical location        |
|---------|----------------|--------------------------|
| 0       | 0, 1           |                          |
| 1       | 2, 3           |                          |
| 2       | 4, 5           |                          |
| 3       | 6, 7           |                          |
| 4       | 8, 9           |                          |
| 5       | 10, 11         |                          |
| 6       | 12, 13         |                          |
| 7       | 14             |                          |

Physical positions for cols 1–7 have not been fully mapped — the mirrored strand layout makes individual wall assignment ambiguous.

### ptReal mode rules

- Always call `activate_ptreal()` on startup (sets all 15 segments via ptReal to enter segment mode).
- Never mix `colorwc` with `ptReal` in the same session — use `set_segment()` for everything including scene/all-color commands.
- Add ~50ms delay between successive `ptReal` commands to avoid dropping packets.
- The `brightness` command is safe to use alongside `ptReal`.

---

## Akai APC Mini MK2

- Auto-detected by port name containing `"APC mini mk2"`.
- MIDI port 0, channel 0.
- **8×8 pad grid**: note = `row * 8 + col`, row 0 = bottom row (notes 0–7), row 7 = top (notes 56–63).
- **Scene launch buttons** (right column, notes 0x70–0x77 = 112–119): single-color LEDs — use `set_button_led(note, True/False)`, NOT `set_pad_color`. They do not support RGB.
- **Track buttons** (bottom row, notes 0x64–0x6B): single-color LEDs.
- **Faders**: CC numbers 0x30–0x38 (48–56); master fader = 0x38.
- **Pad colors**: set via `note_on` with `channel` = brightness level and `velocity` = palette index (0–127). Full brightness = channel 6 (`LED_100PCT`).
- Initialization requires a SysEx message: `47 7F 4F 60 00 04 00 01 00 00`.
- The 128-color palette maps velocity → hex RGB; see `apc_mini.py` for full table.

---

## Running the Project

```bash
uv run python main.py
```

Dependencies (`mido`, `python-rtmidi`) are declared in `pyproject.toml` and managed by uv. Startup takes ~2s while `activate_ptreal()` seeds all 15 Govee segments.

---

## Project Layout

| File         | Purpose                                      |
|--------------|----------------------------------------------|
| `apc_mini.py`| APC Mini MK2 MIDI constants + controller class |
| `govee.py`   | Govee LAN UDP controller                     |
| `main.py`    | Wires APC pads → Govee segment groups        |
