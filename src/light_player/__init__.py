import os
import mido
from pythonosc import udp_client
import asyncio

OSC_SERVER = os.environ.get("OSC_SERVER", "")
OSC_ENDPOINT = os.environ.get("OSC_ENDPOINT", "/light_player")
# default range: C3 to C5 (MIDI notes 48 to 72)
NOTE_RANGE = (
    int(os.environ.get("NOTE_RANGE_MIN", "48")),
    int(os.environ.get("NOTE_RANGE_MAX", "72")),
)
VELOCITY_CLAMP = (
    int(os.environ.get("VELOCITY_MIN", "30")),
    int(os.environ.get("VELOCITY_MAX", "100")),
)  # MIDI (input) velocity range

MIDI_INPUT_NAME = os.environ.get("MIDI_INPUT_NAME")  # default input name

async def midi_listener(handler: callable):
    with mido.open_input(MIDI_INPUT_NAME) as inport:
        # test print midi messages
        for msg in inport:
            print(msg)
            await handler(msg)

def midi_note_to_rgb_and_brightness(msg: mido.Message):
    if msg.type == "note_on":
        note = msg.note
        velocity = msg.velocity
        # Clamp note to the defined range
        note = max(NOTE_RANGE[0], min(NOTE_RANGE[1], note))
        # Clamp velocity to the defined range
        velocity = max(VELOCITY_CLAMP[0], min(VELOCITY_CLAMP[1], velocity))
        # Map note to (R, G, B)
        # using the rainbow (lowest note = red, highest note = violet)
        hue = (note - NOTE_RANGE[0]) / (NOTE_RANGE[1] - NOTE_RANGE[0])  # normalized to [0, 1]
        S = 1.0  # full saturation
        V = 1.0  # full value
        # Convert HSV to RGB
        i = int(hue * 6)
        f = hue * 6 - i
        p = V * (1 - S)
        q = V * (1 - f * S)
        t = V * (1 - (1 - f) * S)
        i = i % 6
        r, g, b = 0, 0, 0
        if i == 0:
            r, g, b = V, t, p
        elif i == 1:
            r, g, b = q, V, p
        elif i == 2:
            r, g, b = p, V, t
        elif i == 3:
            r, g, b = p, q, V
        elif i == 4:
            r, g, b = t, p, V
        elif i == 5:
            r, g, b = V, p, q
        rgb = (int(r * 255), int(g * 255), int(b * 255))
        # Map velocity to brightness (0-100)
        brightness = int((velocity - VELOCITY_CLAMP[0]) / (VELOCITY_CLAMP[1] - VELOCITY_CLAMP[0]) * 100)
        return brightness, rgb

async def osc_sender(msg: mido.Message):
    client = udp_client.SimpleUDPClient(OSC_SERVER.split(":")[0], int(OSC_SERVER.split(":")[1]))
    if msg.type == "note_on":
        brightness, rgb = midi_note_to_rgb_and_brightness(msg)
        client.send_message(OSC_ENDPOINT, [brightness, rgb[0], rgb[1], rgb[2]])
        print(f"Sent OSC message: {OSC_ENDPOINT} [{brightness, rgb[0], rgb[1], rgb[2]}]")

def main() -> None:
    asyncio.run(async_main())

async def async_main() -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(midi_listener(osc_sender))
    loop.run_forever()

if __name__ == "__main__":
    asyncio.run(async_main())
