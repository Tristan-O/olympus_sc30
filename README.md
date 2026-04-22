# olympus_sc30

Python driver wrapper for Olympus SC30 cameras using the IDS/uEye C API.

This submodule provides:

- A low-level ctypes layer in `uEye.py`.
- A higher-level `SC30Camera` class in `Olympus_SC30.py`.

## Contents

- `Olympus_SC30.py`: high-level camera class (`SC30Camera`) for open/configure/capture/stream workflows.
- `uEye.py`: low-level DLL bindings, status/error mapping, and helper functions.
- `__init__.py`: package exports.
- `Olympus-Drivers/`: vendor driver files and notes.

## Requirements

- Windows (the code loads `uc480_64.dll` via `ctypes.WinDLL`).
- Olympus/IDS uEye runtime installed so `uc480_64.dll` is discoverable in PATH or system directories.
- Python 3.10+ recommended.
- `numpy` installed.

## Install and import

From the repository root:

```bash
pip install -r requirements.txt
```

Use as a package import:

```python
from olympus_sc30 import SC30Camera
```

## Quick start

```python
from olympus_sc30 import SC30Camera

cam = SC30Camera(verbosity="high")

try:
    cam.open(set_defaults=False)
    cam.set(colormode="MONO8", binning=1, exposure=100)

    frame = cam.capture_single_frame()
    print(frame.shape, frame.dtype)
finally:
    cam.close()
```

## Streaming and latest frame

```python
from olympus_sc30 import SC30Camera

cam = SC30Camera(ring_size=8)

try:
    cam.open()
    cam.start_streaming()
    cam.start_grab_thread(interval_s=0.01)

    frame = cam.get_latest_frame()
    if frame is not None:
        print(frame.shape)
finally:
    cam.stop_grab_thread()
    cam.close()
```

## SC30Camera API summary

Main methods:

- `open(set_defaults=True)`
- `set(colormode="MONO8", binning=1, exposure=0)`
- `capture_single_frame()`
- `start_streaming()`
- `start_grab_thread(interval_s=0.0)`
- `get_latest_frame()`
- `stop_grab_thread()`
- `close()`
- `get_camera_info()`

Important notes:

- Supported color modes are monochrome only (`MONO8`, `MONO12`, `MONO16`).
- Non-monochrome paths intentionally raise `NotImplementedError`.
- Supported binning factors are `1`, `2`, `3`, and `4`.
- Exposure is in milliseconds.

## Error handling

Driver return codes are checked and converted to `uEyeError` exceptions with readable status text.

Example:

```python
from olympus_sc30 import uEye

try:
    h = uEye.is_InitCamera()
except uEye.uEyeError as err:
    print(err)
```

## Troubleshooting

- `OSError: [WinError 126]` on import usually means `uc480_64.dll` is not installed or not found in PATH.
- `No cameras found!` means the device is not visible to the uEye driver.
- Capture/start failures can happen if another process already owns the camera handle.

## Development notes

- The low-level wrapper intentionally exposes only the uEye calls currently used by this project.
- Return-code mappings in `uEye.py` include SC30-specific codes for easier diagnosis.
- The package is focused on practical acquisition for this repository rather than full uEye API coverage.
