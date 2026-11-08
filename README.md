# light-player

See it in action:

https://github.com/user-attachments/assets/614779df-dfb3-4a71-81c4-ba0023e79ed5



Play your home assistant lights with a midi interface

made to be used with (installable via HACS):
https://github.com/zeyus/ha-osc

Pattern: `/light_player 0..100 0..255 0..255 0..255`

Action:
"turn on light"

```yaml
action: light.turn_on
metadata: {}
target:
  entity_id: light.dining
data:
  rgb_color:
    - '{{ trigger.args[1] }}'
    - '{{ trigger.args[2] }}'
    - '{{ trigger.args[3] }}'
  brightness_pct: '{{ trigger.args[0] }}'
```

## environment

Using direnv (`.envrc`), or whatever works for you:

```bash
OSC_SERVER="ip:port" # e.g. 192.168.1.50:8000
OSC_ENDPOINT="/light_player" # default, you can change it if you like
NOTE_RANGE_MIN=48 # C3
NOTE_RANGE_MAX=72 # C5
VELOCITY_MIN=30
VELOCITY_MAX=100
MIDI_INPUT_NAME="Midi device name"
```

## usage

```bash
# assuming direnv
direnv allow
uv sync

uv run light-player
```

## python-rtmidi on macos

There's a problem with python-rtmidi, but it's not too hard to get working, see: https://github.com/SpotlightKid/python-rtmidi/issues/217

You just need to replace the line `have_semaphore = cpp.has_header('semaphore.h')` in `build.meson` with `have_semaphore = host_machine.system().to_lower() != 'darwin' and cpp.has_header('semaphore.h')`


```bash
git clone https://github.com/SpotlightKid/python-rtmidi.git ../python-rtmidi
sed -i '' 's/have_semaphore = cpp.has_header("semaphore.h")/have_semaphore = host_machine.system().to_lower() != "darwin" and cpp.has_header("semaphore.h")/' ../python-rtmidi/build.meson
# then point UV to the local python-rtmidi repo
uv add python-rtmidi ../python-rtmidi
```

then you can run it as above.
