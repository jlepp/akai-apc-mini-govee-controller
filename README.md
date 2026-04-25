# APC Mini MK2 → Govee Room Light Controller

A little Friday evening project to share with folks :). Control a Govee RGBIC LED strip room-by-room using an Akai APC Mini MK2 as a hardware light board. Press a pad to set any section of the room to any of 8 colors in real time.

## What it does

The 8×8 pad grid maps directly to your lights:

- **Rows** (bottom → top) = 8 colors: red, orange, yellow, green, cyan, blue, purple, magenta
- **Columns** (left → right) = 8 light segments around the room
- **Press any pad** → that wall segment changes to that row's color instantly
- **Scene buttons** (right column) → set every segment to one color at once
- **Master fader** → controls overall brightness

The APC pads stay lit in their row's color. The active color for each column glows at full brightness; the other rows dim down so you can see at a glance what color each segment is set to.

## Hardware

- [Akai APC Mini MK2](https://www.akaipro.com/apc-mini-mk2) — USB MIDI controller
- [Govee H619D](https://www.govee.com) RGBIC LED strip — running around 4 walls of a room
- A computer (tested on Windows 11)

## Physical layout

The H619D has two LED strands that start at the same corner, run in opposite directions around the room, and meet at the far end. This means each controllable segment lights two mirrored physical spots simultaneously. The 15 addressable segments are grouped into 8 columns:

| APC Column | Govee Segments | Location     |
|------------|----------------|--------------|
| 0          | 0, 1           | Start corner |
| 1          | 2, 3           |              |
| 2          | 4, 5           |              |
| 3          | 6, 7           |              |
| 4          | 8, 9           |              |
| 5          | 10, 11         |              |
| 6          | 12, 13         |              |
| 7          | 14             | End          |

## Setup

### Requirements

- Python 3.11+ (managed via [uv](https://github.com/astral-sh/uv))
- Govee Home app — enable **LAN Control** for your device
- APC Mini MK2 plugged in via USB

### Install

```bash
git clone https://github.com/your-username/akai-apc-mini.git
cd akai-apc-mini
uv sync
```

### Configure

Open `main.py` and set your Govee device's IP address:

```python
GOVEE_IP = "192.168.0.49"   # find this in your router or Govee app
```

### Run

```bash
uv run python main.py
```

Startup takes about 2 seconds while it sets all light segments to white and initializes the APC pads.

## Govee LAN API notes

A few non-obvious things about the H619D (aka Govee RGBIC Pro LED Strip Lights) that took some reverse engineering to figure out. I expect these will be similar for other Govee products, but I haven't tested them out yet:

**Segment control uses base64-encoded BLE packets, not raw hex.** The `ptReal` command expects a 20-byte BLE packet encoded as base64:

```
0x33 0x05 0x15 0x01  [R] [G] [B]  0x00×5  [7-byte LE segment bitmask]  [XOR checksum]
```

Who would have thought spending all that time reading the BLE standards back in the day would come in useful.

**`colorwc` breaks `ptReal`.** Sending a solid-color command (`colorwc`) puts the device into a mode where subsequent `ptReal` segment commands are silently ignored. The fix is a power cycle (`turn off` → `turn on`) followed by at least one `ptReal` command before doing segment control. This is why the program calls `activate_ptreal()` on startup.

**Rate limit commands.** Sending `ptReal` packets too fast causes the device to drop them. A 50ms gap between commands is enough.

**Responses come to port 4002**, not back to the sender's ephemeral port. Bind a separate socket to port 4002 if you need to read device responses. Quite useful for debugging.

## Project structure

```
apc_mini.py   — APC Mini MK2 MIDI constants and controller class
govee.py      — Govee LAN UDP controller (no cloud dependency)
main.py       — Wires APC pads to Govee segment groups
```

## Acknowledgements

Thanks to **Akai Professional** for publishing a clear and complete official MIDI communications protocol for the APC Mini MK2. It made implementing the LED control and pad mapping straightforward.
[APC Mini MK2 Communications Protocol v1.0 (PDF)](https://cdn.inmusicbrands.com/akai/attachments/APC%20mini%20mk2%20-%20Communication%20Protocol%20-%20v1.0.pdf)

Thanks to **wez's govee2mqtt project** and **egold555's Govee Reverse Engineering repo** for their community research into the Govee LAN protocol and BLE packet format — particularly the discovery that `ptReal` expects base64-encoded BLE packets rather than raw hex data.
[govee2mqtt](https://github.com/wez/govee2mqtt) · [Govee-Reverse-Engineering](https://github.com/egold555/Govee-Reverse-Engineering)

## License

MIT — see [LICENSE](LICENSE) Hope you find it useful, enjoy!
