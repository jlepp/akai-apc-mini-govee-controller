"""Govee LAN UDP controller (no cloud, no external library)."""

import base64
import json
import socket
import time
from dataclasses import dataclass

GOVEE_DISCOVERY_ADDR = "239.255.255.250"
GOVEE_DISCOVERY_PORT = 4001   # send discovery here (multicast)
GOVEE_RESPONSE_PORT  = 4002   # devices respond here
GOVEE_CONTROL_PORT   = 4003   # send commands here


@dataclass
class GoveeDevice:
    ip: str
    device_id: str
    model: str
    name: str = ""


class GoveeController:
    def __init__(self, device: GoveeDevice):
        self.device = device
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.settimeout(0.5)

    # -----------------------------------------------------------------------
    # Discovery
    # -----------------------------------------------------------------------

    @staticmethod
    def discover(timeout: float = 3.0) -> list[GoveeDevice]:
        """
        Broadcast a LAN scan and collect responding Govee devices.
        Requires LAN Control to be enabled in the Govee Home app.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.5)
        try:
            sock.bind(("", GOVEE_RESPONSE_PORT))
        except OSError:
            # Port already in use — still try to send, may miss responses
            sock.bind(("", 0))

        scan_msg = json.dumps({
            "msg": {"cmd": "scan", "data": {"account_topic": "reserve"}}
        }).encode()

        # Send to multicast group and plain broadcast
        for addr in (GOVEE_DISCOVERY_ADDR, "255.255.255.255"):
            try:
                sock.sendto(scan_msg, (addr, GOVEE_DISCOVERY_PORT))
            except OSError:
                pass

        devices: list[GoveeDevice] = []
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                data, (ip, _) = sock.recvfrom(4096)
                msg = json.loads(data)
                if msg.get("msg", {}).get("cmd") == "scan":
                    d = msg["msg"]["data"]
                    devices.append(GoveeDevice(
                        ip=ip,
                        device_id=d.get("device", ""),
                        model=d.get("sku", ""),
                        name=d.get("deviceName", ""),
                    ))
            except (TimeoutError, OSError, json.JSONDecodeError):
                pass
        sock.close()
        return devices

    @staticmethod
    def connect_to(ip: str, device_id: str = "", model: str = "H619D") -> "GoveeController":
        """Create a controller for a device at a known IP without discovery."""
        return GoveeController(GoveeDevice(ip=ip, device_id=device_id, model=model))

    # -----------------------------------------------------------------------
    # Commands
    # -----------------------------------------------------------------------

    def _send(self, cmd: str, data: dict):
        payload = json.dumps({"msg": {"cmd": cmd, "data": data}}).encode()
        self._sock.sendto(payload, (self.device.ip, GOVEE_CONTROL_PORT))

    def turn_on(self):
        self._send("turn", {"value": 1})

    def turn_off(self):
        self._send("turn", {"value": 0})

    def set_brightness(self, level: int):
        """level: 1–100"""
        self._send("brightness", {"value": max(1, min(100, level))})

    def set_color(self, r: int, g: int, b: int):
        """Set RGB color (0–255 each). Turns on if off.
        WARNING: calling this puts the device in solid-color mode and breaks
        set_segment() — subsequent ptReal commands will be silently ignored.
        Recover by power-cycling (turn_off + turn_on) before using set_segment again."""
        self._send("colorwc", {
            "color": {"r": r, "g": g, "b": b},
            "colorTemInKelvin": 0,
        })

    def set_color_temp(self, kelvin: int):
        """Set white color temperature (2000–9000 K)."""
        self._send("colorwc", {
            "color": {"r": 0, "g": 0, "b": 0},
            "colorTemInKelvin": kelvin,
        })

    def get_status(self) -> dict | None:
        """Request current device state. Returns parsed response or None on timeout.
        Note: the device sends responses to port 4002, not back to our sending port,
        so this only works if our socket happens to be bound there."""
        self._send("devStatus", {})
        try:
            data, _ = self._sock.recvfrom(4096)
            return json.loads(data)
        except (TimeoutError, OSError, json.JSONDecodeError):
            return None

    def set_segment(self, seg: int, r: int, g: int, b: int):
        """Set one Govee segment's color via ptReal.

        The H619D does NOT accept raw hex LED data for ptReal (unlike some other
        Govee devices). It requires a base64-encoded 20-byte BLE packet:
          byte  0:     0x33        BLE command header
          bytes 1-2:   0x05 0x15   LED domain, color mode
          byte  3:     0x01        color subcommand
          bytes 4-6:   R G B
          bytes 7-11:  0x00 * 5   temperature (zero = use color, not white)
          bytes 12-18: bitmask     7-byte little-endian; bit N = segment N
          byte  19:    checksum    XOR of bytes 0-18

        Allow ~50ms between calls — rapid back-to-back commands get dropped.
        Do NOT call set_color() in the same session; it breaks ptReal mode."""
        bitmask = (1 << seg).to_bytes(7, "little")
        data = bytes([0x33, 0x05, 0x15, 0x01, r & 0xFF, g & 0xFF, b & 0xFF,
                      0x00, 0x00, 0x00, 0x00, 0x00]) + bitmask
        chk = 0
        for byte in data:
            chk ^= byte
        pkt = base64.b64encode(data + bytes([chk])).decode()
        self._send("ptReal", {"command": [pkt]})

    def close(self):
        self._sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
