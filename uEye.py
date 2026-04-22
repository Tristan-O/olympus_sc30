# uEye.py
from __future__ import annotations
import ctypes as ct
from pathlib import Path
import numpy as np
HIDS    = ct.c_int

# ---- Load DLL ----
try:
    # If needed: driver = ct.WinDLL(r"C:\Windows\System32\uc480_64.dll")
    driver = ct.WinDLL("uc480_64.dll")
except OSError as err:
    this_dir = Path(__file__).resolve().parent
    repo_driver_dir = this_dir / "Olympus-Drivers"
    msg = (
        "Could not find required DLL 'uc480_64.dll'.\n"
        "Install the camera driver for your model from this repository:\n"
        f"  SCx: {repo_driver_dir / 'SCx'}\n"
        f"  UC90: {repo_driver_dir / 'UC90'}\n"
        f"  DP7x: {repo_driver_dir / 'DP7x'}\n"
        f"  UCx_XCx_XMx: {repo_driver_dir / 'UCx_XCx_XMx'}\n"
        "Then restart the application."
    )
    print(msg)
    raise OSError(msg) from err


# Function prototypes
driver.is_InitCamera.argtypes      = [ct.POINTER(HIDS), ct.c_void_p]
driver.is_InitCamera.restype       = ct.c_int
driver.is_ExitCamera.argtypes      = [HIDS]
driver.is_ExitCamera.restype       = ct.c_int
driver.is_AOI.argtypes             = [HIDS, ct.c_uint, ct.c_void_p, ct.c_uint]
driver.is_AOI.restype              = ct.c_int
driver.is_SetColorMode.argtypes    = [HIDS, ct.c_int]
driver.is_SetColorMode.restype     = ct.c_int
driver.is_AllocImageMem.argtypes   = [HIDS, ct.c_int, ct.c_int, ct.c_int, ct.POINTER(ct.c_void_p), ct.POINTER(ct.c_int)]
driver.is_AllocImageMem.restype    = ct.c_int
driver.is_SetImageMem.argtypes     = [HIDS, ct.c_void_p, ct.c_int]
driver.is_SetImageMem.restype      = ct.c_int
driver.is_CaptureVideo.argtypes    = [HIDS, ct.c_int]
driver.is_CaptureVideo.restype     = ct.c_int
driver.is_StopLiveVideo.argtypes   = [HIDS, ct.c_int]
driver.is_StopLiveVideo.restype    = ct.c_int
driver.is_GetImageMem.argtypes     = [HIDS, ct.POINTER(ct.c_void_p)]
driver.is_GetImageMem.restype      = ct.c_int
driver.is_Exposure.argtypes        = [HIDS, ct.c_uint, ct.c_void_p, ct.c_uint]
driver.is_Exposure.restype         = ct.c_int
driver.is_SetHardwareGain.argtypes = [HIDS, ct.c_int, ct.c_int, ct.c_int, ct.c_int]
driver.is_SetHardwareGain.restype  = ct.c_int
driver.is_SetFrameRate.argtypes    = [HIDS, ct.c_double, ct.POINTER(ct.c_double)]
driver.is_SetFrameRate.restype     = ct.c_int
# driver.is_Exposure.restype  = ct.c_int
# driver.is_Exposure.argtypes = [HIDS, ct.c_uint, ct.c_void_p, ct.c_uint]


# ---- Parameters ---- #
# This list is not exhaustive. It's mostly just what I am using.

# Area of Interest set/get
IS_AOI_IMAGE_SET_AOI          = 0x0001
IS_AOI_IMAGE_GET_AOI          = 0x0002

# Color modes
IS_CM_MONO8             = 6
IS_CM_MONO12            = 26
IS_CM_MONO16            = 28
# IS_CM_SENSOR_RAW8       = 11 # I do not trust this code from copilot anymore
# IS_CM_SENSOR_RAW10      = 33 # I do not trust this code from copilot anymore
# IS_CM_SENSOR_RAW12      = 34 # I do not trust this code from copilot anymore
# IS_CM_BGR8_PACKED       = 0 # I do not trust this code from copilot anymore
# IS_CM_RGB8_PACKED       = 1 # I do not trust this code from copilot anymore
# IS_CM_BGRA8_PACKED      = 2 # I do not trust this code from copilot anymore
# IS_CM_RGBA8_PACKED      = 3 # I do not trust this code from copilot anymore
# IS_CM_BGR10_PACKED      = 8 # I do not trust this code from copilot anymore
# IS_CM_RGB10_PACKED      = 9 # I do not trust this code from copilot anymore
# IS_CM_BGR12_PACKED      = 10 # I do not trust this code from copilot anymore
# IS_CM_RGB12_PACKED      = 11 # I do not trust this code from copilot anymore
# IS_CM_BAYER_RG8         = 8 # I do not trust this code from copilot anymore
# IS_CM_BAYER_RG12        = 10 # I do not trust this code from copilot anymore
# IS_CM_BAYER_RG12_PACKED = 11 # I do not trust this code from copilot anymore

# Wait for completion (for image capturing)
IS_DONT_WAIT            = 0
IS_WAIT                 = 1

# Binning
IS_BINNING_DISABLE       = 0x00
IS_BINNING_2X_VERTICAL   = 0x0001
IS_BINNING_2X_HORIZONTAL = 0x0002
IS_BINNING_4X_VERTICAL   = 0x0004
IS_BINNING_4X_HORIZONTAL = 0x0008
IS_BINNING_3X_VERTICAL   = 0x0010
IS_BINNING_3X_HORIZONTAL = 0x0020
IS_BINNING_5X_VERTICAL   = 0x0040
IS_BINNING_5X_HORIZONTAL = 0x0080
IS_BINNING_6X_VERTICAL   = 0x0100
IS_BINNING_6X_HORIZONTAL = 0x0200
IS_BINNING_8X_VERTICAL   = 0x0400
IS_BINNING_8X_HORIZONTAL = 0x0800
IS_BINNING_2X = IS_BINNING_2X_VERTICAL | IS_BINNING_2X_HORIZONTAL
IS_BINNING_3X = IS_BINNING_3X_VERTICAL | IS_BINNING_3X_HORIZONTAL
IS_BINNING_4X = IS_BINNING_4X_VERTICAL | IS_BINNING_4X_HORIZONTAL
IS_BINNING_5X = IS_BINNING_5X_VERTICAL | IS_BINNING_5X_HORIZONTAL
IS_BINNING_6X = IS_BINNING_6X_VERTICAL | IS_BINNING_6X_HORIZONTAL
IS_BINNING_8X = IS_BINNING_8X_VERTICAL | IS_BINNING_8X_HORIZONTAL

# Exposure
IS_EXPOSURE_CMD_GET_EXPOSURE = 7
IS_EXPOSURE_CMD_SET_EXPOSURE = 12
IS_EXPOSURE_CMD_GET_CAPS = 1
IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE = 16

#  Sensor Types
IS_SENSOR_INVALID         = 0x0000

## CMOS Sensors
IS_SENSOR_UI141X_M        = 0x0001      # VGA rolling shutter, monochrome
IS_SENSOR_UI141X_C        = 0x0002      # VGA rolling shutter, color
IS_SENSOR_UI144X_M        = 0x0003      # SXGA rolling shutter, monochrome
IS_SENSOR_UI144X_C        = 0x0004      # SXGA rolling shutter, SXGA color
IS_SENSOR_UI154X_M        = 0x0030      # SXGA rolling shutter, monochrome
IS_SENSOR_UI154X_C        = 0x0031      # SXGA rolling shutter, color
IS_SENSOR_UI145X_C        = 0x0008      # UXGA rolling shutter, color
IS_SENSOR_UI146X_C        = 0x000a      # QXGA rolling shutter, color
IS_SENSOR_UI148X_M        = 0x000b      # 5MP rolling shutter, monochrome
IS_SENSOR_UI148X_C        = 0x000c      # 5MP rolling shutter, color
IS_SENSOR_UI121X_M        = 0x0010      # VGA global shutter, monochrome
IS_SENSOR_UI121X_C        = 0x0011      # VGA global shutter, VGA color
IS_SENSOR_UI122X_M        = 0x0012      # WVGA global shutter, monochrome
IS_SENSOR_UI122X_C        = 0x0013      # WVGA global shutter, color
IS_SENSOR_UI164X_C        = 0x0015      # SXGA rolling shutter, color
IS_SENSOR_UI155X_C        = 0x0017      # UXGA rolling shutter, color
IS_SENSOR_UI1223_M        = 0x0018      # WVGA global shutter, monochrome
IS_SENSOR_UI1223_C        = 0x0019      # WVGA global shutter, color
IS_SENSOR_UI149X_M        = 0x003E      # 10MP rolling shutter, monochrome
IS_SENSOR_UI149X_C        = 0x003F      # 10MP rolling shutter, color
IS_SENSOR_UI1225_M        = 0x0022      # WVGA global shutter, monochrome, LE model
IS_SENSOR_UI1225_C        = 0x0023      # WVGA global shutter, color, LE model
IS_SENSOR_UI1645_C        = 0x0025      # SXGA rolling shutter, color, LE model
IS_SENSOR_UI1555_C        = 0x0027      # UXGA rolling shutter, color, LE model
IS_SENSOR_UI1545_M        = 0x0028      # SXGA rolling shutter, monochrome, LE model
IS_SENSOR_UI1545_C        = 0x0029      # SXGA rolling shutter, color, LE model
IS_SENSOR_UI1455_C        = 0x002B      # UXGA rolling shutter, color, LE model
IS_SENSOR_UI1465_C        = 0x002D      # QXGA rolling shutter, color, LE model
IS_SENSOR_UI1485_M        = 0x002E      # 5MP rolling shutter, monochrome, LE model
IS_SENSOR_UI1485_C        = 0x002F      # 5MP rolling shutter, color, LE model
IS_SENSOR_UI1495_M        = 0x0040      # 10MP rolling shutter, monochrome, LE model
IS_SENSOR_UI1495_C        = 0x0041      # 10MP rolling shutter, color, LE model
IS_SENSOR_UI112X_M        = 0x004A      # 0768x576, HDR sensor, monochrome
IS_SENSOR_UI112X_C        = 0x004B      # 0768x576, HDR sensor, color
IS_SENSOR_UI1008_M        = 0x004C
IS_SENSOR_UI1008_C        = 0x004D
IS_SENSOR_UIF005_M        = 0x0076 
IS_SENSOR_UIF005_C        = 0x0077 
IS_SENSOR_UI1005_M        = 0x020A 
IS_SENSOR_UI1005_C        = 0x020B
IS_SENSOR_UI1240_M        = 0x0050      # SXGA global shutter, monochrome
IS_SENSOR_UI1240_C        = 0x0051      # SXGA global shutter, color
IS_SENSOR_UI1240_NIR      = 0x0062      # SXGA global shutter, NIR
IS_SENSOR_UI1240LE_M      = 0x0054      # SXGA global shutter, monochrome, single board
IS_SENSOR_UI1240LE_C      = 0x0055      # SXGA global shutter, color, single board
IS_SENSOR_UI1240LE_NIR    = 0x0064      # SXGA global shutter, NIR, single board
IS_SENSOR_UI1240ML_M      = 0x0066      # SXGA global shutter, monochrome, single board
IS_SENSOR_UI1240ML_C      = 0x0067      # SXGA global shutter, color, single board
IS_SENSOR_UI1240ML_NIR    = 0x0200      # SXGA global shutter, NIR, single board
IS_SENSOR_UI1243_M_SMI    = 0x0078
IS_SENSOR_UI1243_C_SMI    = 0x0079
IS_SENSOR_UI1543_M        = 0x0032      # SXGA rolling shutter, monochrome, single board
IS_SENSOR_UI1543_C        = 0x0033      # SXGA rolling shutter, color, single board
IS_SENSOR_UI1544_M        = 0x003A      # SXGA rolling shutter, monochrome, single board
IS_SENSOR_UI1544_C        = 0x003B      # SXGA rolling shutter, color, single board
IS_SENSOR_UI1543_M_WO     = 0x003C      # SXGA rolling shutter, monochrome, single board
IS_SENSOR_UI1543_C_WO     = 0x003D      # SXGA rolling shutter, color, single board
IS_SENSOR_UI1453_C        = 0x0035      # UXGA rolling shutter, color, single board
IS_SENSOR_UI1463_C        = 0x0037      # QXGA rolling shutter, color, single board
IS_SENSOR_UI1483_M        = 0x0038      # QSXG rolling shutter, monochrome, single board
IS_SENSOR_UI1483_C        = 0x0039      # QSXG rolling shutter, color, single board
IS_SENSOR_UI1493_M        = 0x004E      # 10Mp rolling shutter, monochrome, single board
IS_SENSOR_UI1493_C        = 0x004F      # 10MP rolling shutter, color, single board
IS_SENSOR_UI1463_M_WO     = 0x0044      # QXGA rolling shutter, monochrome, single board
IS_SENSOR_UI1463_C_WO     = 0x0045      # QXGA rolling shutter, color, single board
IS_SENSOR_UI1553_C_WN     = 0x0047      # UXGA rolling shutter, color, single board
IS_SENSOR_UI1483_M_WO     = 0x0048      # QSXGA rolling shutter, monochrome, single board
IS_SENSOR_UI1483_C_WO     = 0x0049      # QSXGA rolling shutter, color, single board
IS_SENSOR_UI1580_M        = 0x005A      # 5MP rolling shutter, monochrome
IS_SENSOR_UI1580_C        = 0x005B      # 5MP rolling shutter, color
IS_SENSOR_UI1580LE_M      = 0x0060      # 5MP rolling shutter, monochrome, single board
IS_SENSOR_UI1580LE_C      = 0x0061      # 5MP rolling shutter, color, single board
IS_SENSOR_UI1360M         = 0x0068      # 2.2MP global shutter, monochrome
IS_SENSOR_UI1360C         = 0x0069      # 2.2MP global shutter, color
IS_SENSOR_UI1360NIR       = 0x0212      # 2.2MP global shutter, NIR
IS_SENSOR_UI1370M         = 0x006A      # 4.2MP global shutter, monochrome
IS_SENSOR_UI1370C         = 0x006B      # 4.2MP global shutter, color
IS_SENSOR_UI1370NIR       = 0x0214      # 4.2MP global shutter, NIR
IS_SENSOR_UI1250_M        = 0x006C      # 2MP global shutter, monochrome
IS_SENSOR_UI1250_C        = 0x006D      # 2MP global shutter, color
IS_SENSOR_UI1250_NIR      = 0x006E      # 2MP global shutter, NIR
IS_SENSOR_UI1250LE_M      = 0x0070      # 2MP global shutter, monochrome, single board
IS_SENSOR_UI1250LE_C      = 0x0071      # 2MP global shutter, color, single board
IS_SENSOR_UI1250LE_NIR    = 0x0072      # 2MP global shutter, NIR, single board
IS_SENSOR_UI1250ML_M      = 0x0074      # 2MP global shutter, monochrome, single board
IS_SENSOR_UI1250ML_C      = 0x0075      # 2MP global shutter, color, single board
IS_SENSOR_UI1250ML_NIR    = 0x0202      # 2MP global shutter, NIR, single board
IS_SENSOR_XS              = 0x020B      # 5MP rolling shutter, color
IS_SENSOR_UI1493_M_AR     = 0x0204
IS_SENSOR_UI1493_C_AR     = 0x0205


## CCD Sensors
IS_SENSOR_UI223X_M        = 0x0080      # Sony CCD sensor - XGA monochrome
IS_SENSOR_UI223X_C        = 0x0081      # Sony CCD sensor - XGA color
IS_SENSOR_UI241X_M        = 0x0082      # Sony CCD sensor - VGA monochrome
IS_SENSOR_UI241X_C        = 0x0083      # Sony CCD sensor - VGA color
IS_SENSOR_UI234X_M        = 0x0084      # Sony CCD sensor - SXGA monochrome
IS_SENSOR_UI234X_C        = 0x0085      # Sony CCD sensor - SXGA color
IS_SENSOR_UI221X_M        = 0x0088      # Sony CCD sensor - VGA monochrome
IS_SENSOR_UI221X_C        = 0x0089      # Sony CCD sensor - VGA color
IS_SENSOR_UI231X_M        = 0x0090      # Sony CCD sensor - VGA monochrome
IS_SENSOR_UI231X_C        = 0x0091      # Sony CCD sensor - VGA color
IS_SENSOR_UI222X_M        = 0x0092      # Sony CCD sensor - CCIR / PAL monochrome
IS_SENSOR_UI222X_C        = 0x0093      # Sony CCD sensor - CCIR / PAL color
IS_SENSOR_UI224X_M        = 0x0096      # Sony CCD sensor - SXGA monochrome
IS_SENSOR_UI224X_C        = 0x0097      # Sony CCD sensor - SXGA color
IS_SENSOR_UI225X_M        = 0x0098      # Sony CCD sensor - UXGA monochrome
IS_SENSOR_UI225X_C        = 0x0099      # Sony CCD sensor - UXGA color
IS_SENSOR_UI214X_M        = 0x009A      # Sony CCD sensor - SXGA monochrome
IS_SENSOR_UI214X_C        = 0x009B      # Sony CCD sensor - SXGA color
IS_SENSOR_UI228X_M        = 0x009C      # Sony CCD sensor - QXGA monochrome
IS_SENSOR_UI228X_C        = 0x009D      # Sony CCD sensor - QXGA color
IS_SENSOR_UI241X_M_R2     = 0x0182      # Sony CCD sensor - VGA monochrome
IS_SENSOR_UI251X_M        = 0x0182      # Sony CCD sensor - VGA monochrome
IS_SENSOR_UI241X_C_R2     = 0x0183      # Sony CCD sensor - VGA color
IS_SENSOR_UI251X_C        = 0x0183      # Sony CCD sensor - VGA color
IS_SENSOR_UI2130_M        = 0x019E      # Sony CCD sensor - WXGA monochrome
IS_SENSOR_UI2130_C        = 0x019F      # Sony CCD sensor - WXGA color

# ---- Return Codes ---- #
IS_SUCCESS                      = 0
IS_NO_SUCCESS                   = 1
IS_INVALID_CAMERA_HANDLE        = 2
IS_INVALID_HANDLE               = 3
IS_INVALID_PARAMETER            = 4
IS_IO_REQUEST_FAILED            = 5
IS_CANT_OPEN_DEVICE             = 6
IS_CANT_COMMUNICATE_WITH_DRIVER = 7
IS_INVALID_CAMERA_TYPE         = 8
IS_INVALID_CAMERA_ID           = 9
IS_INVALID_MEMORY_ID           = 10
IS_INVALID_MEMORY_POINTER      = 11
IS_NOT_SUPPORTED               = 12
IS_BAD_STRUCTURE_TYPE          = 13
IS_BAD_STRUCTURE_SIZE          = 14

IS_INVALID_VALUE               = 15
IS_OUT_OF_MEMORY               = 16
IS_INVALID_MODE                = 17
IS_INVALID_VIDEO_IN            = 18
IS_INVALID_IMG_SIZE            = 19
IS_INVALID_ADDRESS             = 20
IS_INVALID_PIXEL_CLOCK         = 21
IS_INVALID_EXPOSURE_TIME       = 22
IS_INVALID_FRAME_RATE          = 23
IS_INVALID_SUBSAMPLING         = 24
IS_INVALID_BINNING             = 25
IS_INVALID_SIZE                = 26
IS_INVALID_IMAGE_FORMAT        = 27
IS_INVALID_TIMEOUT             = 28
IS_INVALID_BRIGHTNESS          = 29
IS_INVALID_HUE                 = 30
IS_INVALID_SATURATION          = 31
IS_INVALID_GAMMA               = 32
IS_INVALID_PARAMETER_VALUE     = 33
IS_INVALID_BUFFER_SIZE         = 34
IS_INVALID_PIXEL_FORMAT        = 35
IS_INVALID_COLOR_MODE          = 36
IS_INVALID_SENSOR_INFO         = 37
IS_INVALID_DEVICE_ID           = 38
IS_INVALID_SENSOR_TYPE         = 39
IS_INVALID_TRIGGER_MODE        = 40
IS_INVALID_TRIGGER_TIMEOUT     = 41
IS_INVALID_BAYER_CONVERSION    = 42
IS_INVALID_COLOR_CORRECTION    = 43
IS_INVALID_LUT                 = 44
IS_INVALID_SHARPNESS           = 45
IS_INVALID_AUTO_PARAMETER      = 46
IS_INVALID_CAMERA_INFO         = 47
IS_INVALID_CAMERA_SETTINGS     = 48
IS_INVALID_CAMERA_FEATURE      = 49

IS_NO_ACTIVE_IMG_MEM           = 50
IS_CANT_INIT_EVENT             = 51
IS_CANT_CLOSE_EVENT            = 52
IS_CANT_OPEN_DEVICE_REGISTRY   = 53
IS_CANT_READ_REGISTRY          = 54
IS_CANT_WRITE_REGISTRY         = 55
IS_CANT_CREATE_DIRECTORY       = 56
IS_CANT_CREATE_FILE            = 57
IS_CANT_OPEN_FILE              = 58
IS_CANT_READ_FILE              = 59
IS_CANT_WRITE_FILE             = 60
IS_CANT_LOCK_MEMORY            = 61
IS_CANT_UNLOCK_MEMORY          = 62
IS_CANT_ALLOCATE_MEMORY        = 63
IS_CANT_FREE_MEMORY            = 64
IS_CANT_MAP_MEMORY             = 65
IS_CANT_UNMAP_MEMORY           = 66
IS_CANT_ALLOCATE_IMAGE_MEM     = 67
IS_CANT_FREE_IMAGE_MEM         = 68
IS_CANT_SET_IMAGE_MEM          = 69
IS_CANT_GET_IMAGE_MEM          = 70
IS_CANT_GET_IMAGE_SIZE         = 71
IS_CANT_GET_IMAGE_FORMAT       = 72
IS_CANT_SET_IMAGE_FORMAT       = 73
IS_CANT_GET_COLOR_MODE         = 74
IS_CANT_SET_COLOR_MODE         = 75
IS_CANT_GET_PIXEL_CLOCK        = 76
IS_CANT_SET_PIXEL_CLOCK        = 77
IS_CANT_GET_EXPOSURE_TIME      = 78
IS_CANT_SET_EXPOSURE_TIME      = 79
IS_CANT_GET_FRAME_RATE         = 80
IS_CANT_SET_FRAME_RATE         = 81
IS_CANT_GET_GAIN               = 82
IS_CANT_SET_GAIN               = 83
IS_CANT_GET_AUTO_PARAMETER     = 84
IS_CANT_SET_AUTO_PARAMETER     = 85
IS_CANT_GET_LUT                = 86
IS_CANT_SET_LUT                = 87
IS_CANT_GET_SHARPNESS          = 88
IS_CANT_SET_SHARPNESS          = 89
IS_CANT_GET_BRIGHTNESS         = 90
IS_CANT_SET_BRIGHTNESS         = 91
IS_CANT_GET_SATURATION         = 92
IS_CANT_SET_SATURATION         = 93
IS_CANT_GET_HUE                = 94
IS_CANT_SET_HUE                = 95
IS_CANT_GET_GAMMA              = 96
IS_CANT_SET_GAMMA              = 97
IS_CANT_GET_CAMERA_INFO        = 98
IS_CANT_SET_CAMERA_INFO        = 99

IS_CAPTURE_RUNNING             = 100
IS_CAPTURE_STOPPED             = 101
IS_CAPTURE_FAILED              = 102
IS_CAPTURE_TIMEOUT             = 103
IS_CAPTURE_NO_FRAME            = 104
IS_CAPTURE_LOST_FRAME          = 105
IS_CAPTURE_FIFO_OVERFLOW       = 106
IS_CAPTURE_BUFFER_OVERFLOW     = 107
IS_CAPTURE_USB_TRANSFER_FAILED = 108
IS_CAPTURE_USB_BANDWIDTH_EXCEEDED = 109
IS_CAPTURE_USB_ENDPOINT_STALLED   = 110
IS_CAPTURE_USB_ENDPOINT_HALTED    = 111
IS_CAPTURE_USB_ENDPOINT_INVALID   = 112
IS_CAPTURE_USB_ENDPOINT_TIMEOUT   = 113
IS_CAPTURE_USB_ENDPOINT_OVERFLOW  = 114
IS_CAPTURE_USB_ENDPOINT_UNDERRUN  = 115
IS_CAPTURE_USB_ENDPOINT_ERROR     = 116
IS_CAPTURE_USB_ENDPOINT_ABORTED   = 117
IS_CAPTURE_USB_ENDPOINT_RESET     = 118
IS_CAPTURE_USB_ENDPOINT_DISABLED  = 119
IS_CAPTURE_USB_ENDPOINT_NOT_FOUND = 120
IS_CAPTURE_USB_ENDPOINT_NOT_SUPPORTED = 121
IS_CAPTURE_USB_ENDPOINT_NOT_READY = 122
IS_CAPTURE_USB_ENDPOINT_NOT_ENABLED = 123
IS_CAPTURE_USB_ENDPOINT_NOT_CONFIGURED = 124
IS_CAPTURE_USB_ENDPOINT_NOT_ACTIVE = 125
IS_CAPTURE_USB_ENDPOINT_NOT_IDLE = 126
IS_CAPTURE_USB_ENDPOINT_NOT_STALLED = 127
IS_CAPTURE_USB_ENDPOINT_NOT_HALTED = 128
IS_CAPTURE_USB_ENDPOINT_NOT_RESET = 129
IS_CAPTURE_USB_ENDPOINT_NOT_ABORTED = 130
IS_CAPTURE_USB_ENDPOINT_NOT_DISABLED = 131
IS_CAPTURE_USB_ENDPOINT_NOT_ERROR = 132
IS_CAPTURE_USB_ENDPOINT_NOT_TIMEOUT = 133
IS_CAPTURE_USB_ENDPOINT_NOT_OVERFLOW = 134
IS_CAPTURE_USB_ENDPOINT_NOT_UNDERRUN = 135
IS_CAPTURE_USB_ENDPOINT_NOT_TRANSFERRED = 136
IS_CAPTURE_USB_ENDPOINT_NOT_COMPLETED = 137
IS_CAPTURE_USB_ENDPOINT_NOT_STARTED = 138
IS_CAPTURE_USB_ENDPOINT_NOT_STOPPED = 139

# Duplicate official code
IS_CAPTURE_RUNNING_2           = 140

# OEM / SC30‑specific codes
IS_TRANSFER_ERROR              = 185   # SC30 USB transfer failure
IS_TIMED_OUT                   = 210   # SC30 timeout

# Misc internal driver states
IS_INVALID_STATE               = 200
IS_INVALID_EVENT               = 201
IS_INVALID_FUNCTION            = 202
IS_INVALID_BUFFER              = 203
IS_INVALID_DEVICE              = 204
IS_INVALID_FIRMWARE            = 205
IS_INVALID_DRIVER              = 206
IS_INVALID_HARDWARE            = 207
IS_INVALID_USB_CONFIGURATION   = 208
IS_INVALID_USB_INTERFACE       = 209
IS_DEVICE_NOT_READY            = 211
IS_DEVICE_BUSY                 = 212
IS_DEVICE_ERROR                = 213
IS_DEVICE_DISCONNECTED         = 214
IS_DEVICE_RECONNECTED          = 215
IS_DEVICE_RESET                = 216
IS_DEVICE_REBOOT               = 217
IS_DEVICE_SHUTDOWN             = 218
IS_DEVICE_SUSPENDED            = 219
IS_DEVICE_RESUMED              = 220

class uEyeError(Exception):
    returnStatuses = {
        IS_SUCCESS:   "Success",

        # General errors
        IS_NO_SUCCESS:   "No Success. Camera might be busy, try killing old processes.",
        IS_INVALID_CAMERA_HANDLE:   "Invalid Camera Handle",
        IS_INVALID_HANDLE:   "Invalid Handle",
        IS_INVALID_PARAMETER:   "Invalid Parameter",
        IS_IO_REQUEST_FAILED:   "IO Request Failed",
        IS_CANT_OPEN_DEVICE:   "Cant Open Device",
        IS_CANT_COMMUNICATE_WITH_DRIVER:   "Cant Communicate With Driver",
        IS_INVALID_CAMERA_TYPE:   "Invalid Camera Type",
        IS_INVALID_CAMERA_ID:   "Invalid Camera ID",
        IS_INVALID_MEMORY_ID:  "Invalid Memory ID",
        IS_INVALID_MEMORY_POINTER:  "Invalid Memory Pointer",
        IS_NOT_SUPPORTED:  "Not Supported",
        IS_BAD_STRUCTURE_TYPE:  "Bad Structure Type",
        IS_BAD_STRUCTURE_SIZE:  "Bad Structure Size",

        # Configuration / initialization
        IS_INVALID_VALUE:  "Invalid Value",
        IS_OUT_OF_MEMORY:  "Out Of Memory",
        IS_INVALID_MODE:  "Invalid Mode",
        IS_INVALID_VIDEO_IN:  "Invalid Video Input",
        IS_INVALID_IMG_SIZE:  "Invalid Image Size",
        IS_INVALID_ADDRESS:  "Invalid Address",
        IS_INVALID_PIXEL_CLOCK:  "Invalid Pixel Clock",
        IS_INVALID_EXPOSURE_TIME:  "Invalid Exposure Time",
        IS_INVALID_FRAME_RATE:  "Invalid Frame Rate",
        IS_INVALID_SUBSAMPLING:  "Invalid Subsampling",
        IS_INVALID_BINNING:  "Invalid Binning",
        IS_INVALID_SIZE:  "Not Calibrated",
        IS_INVALID_IMAGE_FORMAT:  "Invalid Size",
        IS_INVALID_TIMEOUT:  "Invalid Image Format",
        IS_INVALID_BRIGHTNESS:  "Invalid Timeout",
        IS_INVALID_HUE:  "Invalid Brightness",
        IS_INVALID_SATURATION:  "Invalid Hue",
        IS_INVALID_GAMMA:  "Invalid Saturation",
        IS_INVALID_PARAMETER_VALUE:  "Invalid Gamma",
        IS_INVALID_BUFFER_SIZE:  "Invalid Parameter Value",
        IS_INVALID_PIXEL_FORMAT:  "Invalid Buffer Size",
        IS_INVALID_COLOR_MODE:  "Invalid Pixel Format",
        IS_INVALID_SENSOR_INFO:  "Invalid Sensor Info",
        IS_INVALID_DEVICE_ID:  "Invalid Device ID",
        IS_INVALID_SENSOR_TYPE:  "Invalid Sensor Type",
        IS_INVALID_TRIGGER_MODE:  "Invalid Trigger Mode",
        IS_INVALID_TRIGGER_TIMEOUT:  "Invalid Trigger Timeout",
        IS_INVALID_BAYER_CONVERSION:  "Invalid Bayer Conversion",
        IS_INVALID_COLOR_CORRECTION:  "Invalid Color Correction",
        IS_INVALID_LUT:  "Invalid LUT",
        IS_INVALID_SHARPNESS:  "Invalid Sharpness",
        IS_INVALID_AUTO_PARAMETER:  "Invalid Auto Parameter",
        IS_INVALID_CAMERA_INFO:  "Invalid Camera Info",
        IS_INVALID_CAMERA_SETTINGS:  "Invalid Camera Settings",
        IS_INVALID_CAMERA_FEATURE:  "Invalid Camera Feature",

        # Image / memory errors
        IS_NO_ACTIVE_IMG_MEM:  "No Active Image Memory",
        IS_CANT_INIT_EVENT:  "Cant Init Event",
        IS_CANT_CLOSE_EVENT:  "Cant Close Event",
        IS_CANT_OPEN_DEVICE_REGISTRY:  "Cant Open Device Registry",
        IS_CANT_READ_REGISTRY:  "Cant Read Registry",
        IS_CANT_WRITE_REGISTRY:  "Cant Write Registry",
        IS_CANT_CREATE_DIRECTORY:  "Cant Create Directory",
        IS_CANT_CREATE_FILE:  "Cant Create File",
        IS_CANT_OPEN_FILE:  "Cant Open File",
        IS_CANT_READ_FILE:  "Cant Read File",
        IS_CANT_WRITE_FILE:  "Cant Write File",
        IS_CANT_LOCK_MEMORY:  "Cant Lock Memory",
        IS_CANT_UNLOCK_MEMORY:  "Cant Unlock Memory",
        IS_CANT_ALLOCATE_MEMORY:  "Cant Allocate Memory",
        IS_CANT_FREE_MEMORY:  "Cant Free Memory",
        IS_CANT_MAP_MEMORY:  "Cant Map Memory",
        IS_CANT_UNMAP_MEMORY:  "Cant Unmap Memory",
        IS_CANT_ALLOCATE_IMAGE_MEM:  "Cant Allocate Image Memory",
        IS_CANT_FREE_IMAGE_MEM:  "Cant Free Image Memory",
        IS_CANT_SET_IMAGE_MEM:  "Cant Set Image Memory",
        IS_CANT_GET_IMAGE_MEM:  "Cant Get Image Memory",
        IS_CANT_GET_IMAGE_SIZE:  "Cant Get Image Size",
        IS_CANT_GET_IMAGE_FORMAT:  "Cant Get Image Format",
        IS_CANT_SET_IMAGE_FORMAT:  "Cant Set Image Format",
        IS_CANT_GET_COLOR_MODE:  "Cant Get Color Mode",
        IS_CANT_SET_COLOR_MODE:  "Cant Set Color Mode",
        IS_CANT_GET_PIXEL_CLOCK:  "Cant Get Pixel Clock",
        IS_CANT_SET_PIXEL_CLOCK:  "Cant Set Pixel Clock",
        IS_CANT_GET_EXPOSURE_TIME:  "Cant Get Exposure Time",
        IS_CANT_SET_EXPOSURE_TIME:  "Cant Set Exposure Time",
        IS_CANT_GET_FRAME_RATE:  "Cant Get Frame Rate",
        IS_CANT_SET_FRAME_RATE:  "Cant Set Frame Rate",
        IS_CANT_GET_GAIN:  "Cant Get Gain",
        IS_CANT_SET_GAIN:  "Cant Set Gain",
        IS_CANT_GET_AUTO_PARAMETER:  "Cant Get Auto Parameter",
        IS_CANT_SET_AUTO_PARAMETER:  "Cant Set Auto Parameter",
        IS_CANT_GET_LUT:  "Cant Get LUT",
        IS_CANT_SET_LUT:  "Cant Set LUT",
        IS_CANT_GET_SHARPNESS:  "Cant Get Sharpness",
        IS_CANT_SET_SHARPNESS:  "Cant Set Sharpness",
        IS_CANT_GET_BRIGHTNESS:  "Cant Get Brightness",
        IS_CANT_SET_BRIGHTNESS:  "Cant Set Brightness",
        IS_CANT_GET_SATURATION:  "Cant Get Saturation",
        IS_CANT_SET_SATURATION:  "Cant Set Saturation",
        IS_CANT_GET_HUE:  "Cant Get Hue",
        IS_CANT_SET_HUE:  "Cant Set Hue",
        IS_CANT_GET_GAMMA:  "Cant Get Gamma",
        IS_CANT_SET_GAMMA:  "Cant Set Gamma",
        IS_CANT_GET_CAMERA_INFO:  "Cant Get Camera Info",
        IS_CANT_SET_CAMERA_INFO:  "Cant Set Camera Info",

        # Streaming / capture
        IS_CAPTURE_RUNNING: "Capture Running",
        IS_CAPTURE_STOPPED: "Capture Stopped",
        IS_CAPTURE_FAILED: "Capture Failed",
        IS_CAPTURE_TIMEOUT: "Capture Timeout",
        IS_CAPTURE_NO_FRAME: "Capture No Frame",
        IS_CAPTURE_LOST_FRAME: "Capture Lost Frame",
        IS_CAPTURE_FIFO_OVERFLOW: "Capture FIFO Overflow",
        IS_CAPTURE_BUFFER_OVERFLOW: "Capture Buffer Overflow",
        IS_CAPTURE_USB_TRANSFER_FAILED: "Capture USB Transfer Failed",
        IS_CAPTURE_USB_BANDWIDTH_EXCEEDED: "Capture USB Bandwidth Exceeded",
        IS_CAPTURE_USB_ENDPOINT_STALLED: "Capture USB Endpoint Stalled",
        IS_CAPTURE_USB_ENDPOINT_HALTED: "Capture USB Endpoint Halted",
        IS_CAPTURE_USB_ENDPOINT_INVALID: "Capture USB Endpoint Invalid",
        IS_CAPTURE_USB_ENDPOINT_TIMEOUT: "Capture USB Endpoint Timeout",
        IS_CAPTURE_USB_ENDPOINT_OVERFLOW: "Capture USB Endpoint Overflow",
        IS_CAPTURE_USB_ENDPOINT_UNDERRUN: "Capture USB Endpoint Underrun",
        IS_CAPTURE_USB_ENDPOINT_ERROR: "Capture USB Endpoint Error",
        IS_CAPTURE_USB_ENDPOINT_ABORTED: "Capture USB Endpoint Aborted",
        IS_CAPTURE_USB_ENDPOINT_RESET: "Capture USB Endpoint Reset",
        IS_CAPTURE_USB_ENDPOINT_DISABLED: "Capture USB Endpoint Disabled",
        IS_CAPTURE_USB_ENDPOINT_NOT_FOUND: "Capture USB Endpoint Not Found",
        IS_CAPTURE_USB_ENDPOINT_NOT_SUPPORTED: "Capture USB Endpoint Not Supported",
        IS_CAPTURE_USB_ENDPOINT_NOT_READY: "Capture USB Endpoint Not Ready",
        IS_CAPTURE_USB_ENDPOINT_NOT_ENABLED: "Capture USB Endpoint Not Enabled",
        IS_CAPTURE_USB_ENDPOINT_NOT_CONFIGURED: "Capture USB Endpoint Not Configured",
        IS_CAPTURE_USB_ENDPOINT_NOT_ACTIVE: "Capture USB Endpoint Not Active",
        IS_CAPTURE_USB_ENDPOINT_NOT_IDLE: "Capture USB Endpoint Not Idle",
        IS_CAPTURE_USB_ENDPOINT_NOT_STALLED: "Capture USB Endpoint Not Stalled",
        IS_CAPTURE_USB_ENDPOINT_NOT_HALTED: "Capture USB Endpoint Not Halted",
        IS_CAPTURE_USB_ENDPOINT_NOT_RESET: "Capture USB Endpoint Not Reset",
        IS_CAPTURE_USB_ENDPOINT_NOT_ABORTED: "Capture USB Endpoint Not Aborted",
        IS_CAPTURE_USB_ENDPOINT_NOT_DISABLED: "Capture USB Endpoint Not Disabled",
        IS_CAPTURE_USB_ENDPOINT_NOT_ERROR: "Capture USB Endpoint Not Error",
        IS_CAPTURE_USB_ENDPOINT_NOT_TIMEOUT: "Capture USB Endpoint Not Timeout",
        IS_CAPTURE_USB_ENDPOINT_NOT_OVERFLOW: "Capture USB Endpoint Not Overflow",
        IS_CAPTURE_USB_ENDPOINT_NOT_UNDERRUN: "Capture USB Endpoint Not Underrun",
        IS_CAPTURE_USB_ENDPOINT_NOT_TRANSFERRED: "Capture USB Endpoint Not Transferred",
        IS_CAPTURE_USB_ENDPOINT_NOT_COMPLETED: "Capture USB Endpoint Not Completed",
        IS_CAPTURE_USB_ENDPOINT_NOT_STARTED: "Capture USB Endpoint Not Started",
        IS_CAPTURE_USB_ENDPOINT_NOT_STOPPED: "Capture USB Endpoint Not Stopped",
        IS_CAPTURE_RUNNING_2: "Capture Running (Duplicate Official Code)",

        # OEM / undocumented / SC30‑relevant
        IS_TRANSFER_ERROR: "Transfer Error",   # SC30 USB transfer failed
        IS_TIMED_OUT: "Timed Out",        # SC30 operation timed out

        # Miscellaneous / internal
        IS_INVALID_STATE: "Invalid State",
        IS_INVALID_EVENT: "Invalid Event",
        IS_INVALID_FUNCTION: "Invalid Function",
        IS_INVALID_BUFFER: "Invalid Buffer",
        IS_INVALID_DEVICE: "Invalid Device",
        IS_INVALID_FIRMWARE: "Invalid Firmware",
        IS_INVALID_DRIVER: "Invalid Driver",
        IS_INVALID_HARDWARE: "Invalid Hardware",
        IS_INVALID_USB_CONFIGURATION: "Invalid USB Configuration",
        IS_INVALID_USB_INTERFACE: "Invalid USB Interface",
        IS_DEVICE_NOT_READY: "Device Not Ready",
        IS_DEVICE_BUSY: "Device Busy",
        IS_DEVICE_ERROR: "Device Error",
        IS_DEVICE_DISCONNECTED: "Device Disconnected",
        IS_DEVICE_RECONNECTED: "Device Reconnected",
        IS_DEVICE_RESET: "Device Reset",
        IS_DEVICE_REBOOT: "Device Reboot",
        IS_DEVICE_SHUTDOWN: "Device Shutdown",
        IS_DEVICE_SUSPENDED: "Device Suspended",
        IS_DEVICE_RESUMED: "Device Resumed",
    }
    def __init__(self, ret, *args, **kwargs):
        """Initialize an exception with a uEye return code.

        Args:
            ret: Numeric return status from a uEye API call.
            *args: Positional arguments forwarded to :class:`Exception`.
            **kwargs: Keyword arguments forwarded to :class:`Exception`.
        """
        super().__init__(*args, **kwargs)
        self.ret = ret
    def __str__(self):
        """Render a readable error message including symbolic status meaning."""
        return f'uEye Error, return code {self.ret}, which means "{self.returnStatuses.get(self.ret, "Unknown Error")}".'
    @classmethod
    def test(cls, code, ok_codes=(0,)):
        """Validate a return code and raise when it is not acceptable.

        Args:
            code: Return code from a driver call.
            ok_codes: Iterable of status codes treated as success.

        Raises:
            uEyeError: If ``code`` is not in ``ok_codes``.
        """
        if code not in ok_codes:
            raise cls(code)


# Structures
class CAMINFO(ct.Structure):
    _fields_ = [
        ("SerNo",     ct.c_char * 12),  # Serial number of the camera
        ("ID",        ct.c_char * 20),  # Manufacturer of the camera (e.g. IDS GmbH)
        ("Version",   ct.c_char * 10),  # For USB cameras, this value indicates the USB board hardware version (e.g. V2.10)
        ("Date",      ct.c_char * 12),  # System date of the final quality check (e.g. 01.08.2011 (DD.MM.YYYY))
        ("Select",    ct.c_ubyte),      # Customizable camera ID. This ID is stored in the camera and is persistent. When the camera is delivered, the value 1 is stored.
        ("Type",      ct.c_ubyte),      # Camera typeas an int
        ("Reserved",  ct.c_char * 8)]   # Reserved (unused)
    def to_dict(self):
        """Convert the raw C struct into a plain Python dictionary."""
        return dict(
            SerNo    = self.SerNo.decode(),
            ID       = self.ID.decode(),
            Version  = self.Version.decode(),
            Date     = self.Date.decode(),
            Select   = self.Select,
            Type     = self.Type,
            Reserved = self.Reserved.decode())
class SENSORINFO(ct.Structure):
    _fields_ = [
        ("SensorID", ct.c_ushort),
        ("strSensorName", ct.c_char * 32),
        ("nColorMode", ct.c_char),
        ("nMaxWidth", ct.c_uint),
        ("nMaxHeight", ct.c_uint),
        ("bMasterGain", ct.c_int),
        ("bRGain", ct.c_int),
        ("bGGain", ct.c_int),
        ("bBGain", ct.c_int),
        ("bGlobShutter", ct.c_int),
        ("wPixelSize", ct.c_ushort),
        ("nUpperLeftBayerPixel", ct.c_char),
        ("Reserved", ct.c_char * 13),
    ]
    def to_dict(self):
        """Convert sensor capabilities/info fields into a Python dictionary."""
        sensor_id_code = int(self.SensorID)
        sensor_id_names = {
            IS_SENSOR_INVALID: "IS_SENSOR_INVALID",
            IS_SENSOR_UI141X_M: "IS_SENSOR_UI141X_M",
            IS_SENSOR_UI141X_C: "IS_SENSOR_UI141X_C",
            IS_SENSOR_UI144X_M: "IS_SENSOR_UI144X_M",
            IS_SENSOR_UI144X_C: "IS_SENSOR_UI144X_C",
            IS_SENSOR_UI154X_M: "IS_SENSOR_UI154X_M",
            IS_SENSOR_UI154X_C: "IS_SENSOR_UI154X_C",
            IS_SENSOR_UI145X_C: "IS_SENSOR_UI145X_C",
            IS_SENSOR_UI146X_C: "IS_SENSOR_UI146X_C",
            IS_SENSOR_UI148X_M: "IS_SENSOR_UI148X_M",
            IS_SENSOR_UI148X_C: "IS_SENSOR_UI148X_C",
            IS_SENSOR_UI121X_M: "IS_SENSOR_UI121X_M",
            IS_SENSOR_UI121X_C: "IS_SENSOR_UI121X_C",
            IS_SENSOR_UI122X_M: "IS_SENSOR_UI122X_M",
            IS_SENSOR_UI122X_C: "IS_SENSOR_UI122X_C",
            IS_SENSOR_UI164X_C: "IS_SENSOR_UI164X_C",
            IS_SENSOR_UI155X_C: "IS_SENSOR_UI155X_C",
            IS_SENSOR_UI1223_M: "IS_SENSOR_UI1223_M",
            IS_SENSOR_UI1223_C: "IS_SENSOR_UI1223_C",
            IS_SENSOR_UI149X_M: "IS_SENSOR_UI149X_M",
            IS_SENSOR_UI149X_C: "IS_SENSOR_UI149X_C",
            IS_SENSOR_UI1225_M: "IS_SENSOR_UI1225_M",
            IS_SENSOR_UI1225_C: "IS_SENSOR_UI1225_C",
            IS_SENSOR_UI1645_C: "IS_SENSOR_UI1645_C",
            IS_SENSOR_UI1555_C: "IS_SENSOR_UI1555_C",
            IS_SENSOR_UI1545_M: "IS_SENSOR_UI1545_M",
            IS_SENSOR_UI1545_C: "IS_SENSOR_UI1545_C",
            IS_SENSOR_UI1455_C: "IS_SENSOR_UI1455_C",
            IS_SENSOR_UI1465_C: "IS_SENSOR_UI1465_C",
            IS_SENSOR_UI1485_M: "IS_SENSOR_UI1485_M",
            IS_SENSOR_UI1485_C: "IS_SENSOR_UI1485_C",
            IS_SENSOR_UI1495_M: "IS_SENSOR_UI1495_M",
            IS_SENSOR_UI1495_C: "IS_SENSOR_UI1495_C",
            IS_SENSOR_UI112X_M: "IS_SENSOR_UI112X_M",
            IS_SENSOR_UI112X_C: "IS_SENSOR_UI112X_C",
            IS_SENSOR_UI1008_M: "IS_SENSOR_UI1008_M",
            IS_SENSOR_UI1008_C: "IS_SENSOR_UI1008_C",
            IS_SENSOR_UIF005_M: "IS_SENSOR_UIF005_M",
            IS_SENSOR_UIF005_C: "IS_SENSOR_UIF005_C",
            IS_SENSOR_UI1005_M: "IS_SENSOR_UI1005_M",
            IS_SENSOR_XS: "IS_SENSOR_UI1005_C|IS_SENSOR_XS",
            IS_SENSOR_UI1240_M: "IS_SENSOR_UI1240_M",
            IS_SENSOR_UI1240_C: "IS_SENSOR_UI1240_C",
            IS_SENSOR_UI1240_NIR: "IS_SENSOR_UI1240_NIR",
            IS_SENSOR_UI1240LE_M: "IS_SENSOR_UI1240LE_M",
            IS_SENSOR_UI1240LE_C: "IS_SENSOR_UI1240LE_C",
            IS_SENSOR_UI1240LE_NIR: "IS_SENSOR_UI1240LE_NIR",
            IS_SENSOR_UI1240ML_M: "IS_SENSOR_UI1240ML_M",
            IS_SENSOR_UI1240ML_C: "IS_SENSOR_UI1240ML_C",
            IS_SENSOR_UI1240ML_NIR: "IS_SENSOR_UI1240ML_NIR",
            IS_SENSOR_UI1243_M_SMI: "IS_SENSOR_UI1243_M_SMI",
            IS_SENSOR_UI1243_C_SMI: "IS_SENSOR_UI1243_C_SMI",
            IS_SENSOR_UI1543_M: "IS_SENSOR_UI1543_M",
            IS_SENSOR_UI1543_C: "IS_SENSOR_UI1543_C",
            IS_SENSOR_UI1544_M: "IS_SENSOR_UI1544_M",
            IS_SENSOR_UI1544_C: "IS_SENSOR_UI1544_C",
            IS_SENSOR_UI1543_M_WO: "IS_SENSOR_UI1543_M_WO",
            IS_SENSOR_UI1543_C_WO: "IS_SENSOR_UI1543_C_WO",
            IS_SENSOR_UI1453_C: "IS_SENSOR_UI1453_C",
            IS_SENSOR_UI1463_C: "IS_SENSOR_UI1463_C",
            IS_SENSOR_UI1483_M: "IS_SENSOR_UI1483_M",
            IS_SENSOR_UI1483_C: "IS_SENSOR_UI1483_C",
            IS_SENSOR_UI1493_M: "IS_SENSOR_UI1493_M",
            IS_SENSOR_UI1493_C: "IS_SENSOR_UI1493_C",
            IS_SENSOR_UI1463_M_WO: "IS_SENSOR_UI1463_M_WO",
            IS_SENSOR_UI1463_C_WO: "IS_SENSOR_UI1463_C_WO",
            IS_SENSOR_UI1553_C_WN: "IS_SENSOR_UI1553_C_WN",
            IS_SENSOR_UI1483_M_WO: "IS_SENSOR_UI1483_M_WO",
            IS_SENSOR_UI1483_C_WO: "IS_SENSOR_UI1483_C_WO",
            IS_SENSOR_UI1580_M: "IS_SENSOR_UI1580_M",
            IS_SENSOR_UI1580_C: "IS_SENSOR_UI1580_C",
            IS_SENSOR_UI1580LE_M: "IS_SENSOR_UI1580LE_M",
            IS_SENSOR_UI1580LE_C: "IS_SENSOR_UI1580LE_C",
            IS_SENSOR_UI1360M: "IS_SENSOR_UI1360M",
            IS_SENSOR_UI1360C: "IS_SENSOR_UI1360C",
            IS_SENSOR_UI1360NIR: "IS_SENSOR_UI1360NIR",
            IS_SENSOR_UI1370M: "IS_SENSOR_UI1370M",
            IS_SENSOR_UI1370C: "IS_SENSOR_UI1370C",
            IS_SENSOR_UI1370NIR: "IS_SENSOR_UI1370NIR",
            IS_SENSOR_UI1250_M: "IS_SENSOR_UI1250_M",
            IS_SENSOR_UI1250_C: "IS_SENSOR_UI1250_C",
            IS_SENSOR_UI1250_NIR: "IS_SENSOR_UI1250_NIR",
            IS_SENSOR_UI1250LE_M: "IS_SENSOR_UI1250LE_M",
            IS_SENSOR_UI1250LE_C: "IS_SENSOR_UI1250LE_C",
            IS_SENSOR_UI1250LE_NIR: "IS_SENSOR_UI1250LE_NIR",
            IS_SENSOR_UI1250ML_M: "IS_SENSOR_UI1250ML_M",
            IS_SENSOR_UI1250ML_C: "IS_SENSOR_UI1250ML_C",
            IS_SENSOR_UI1250ML_NIR: "IS_SENSOR_UI1250ML_NIR",
            IS_SENSOR_UI1493_M_AR: "IS_SENSOR_UI1493_M_AR",
            IS_SENSOR_UI1493_C_AR: "IS_SENSOR_UI1493_C_AR",
            IS_SENSOR_UI223X_M: "IS_SENSOR_UI223X_M",
            IS_SENSOR_UI223X_C: "IS_SENSOR_UI223X_C",
            IS_SENSOR_UI241X_M: "IS_SENSOR_UI241X_M",
            IS_SENSOR_UI241X_C: "IS_SENSOR_UI241X_C",
            IS_SENSOR_UI234X_M: "IS_SENSOR_UI234X_M",
            IS_SENSOR_UI234X_C: "IS_SENSOR_UI234X_C",
            IS_SENSOR_UI221X_M: "IS_SENSOR_UI221X_M",
            IS_SENSOR_UI221X_C: "IS_SENSOR_UI221X_C",
            IS_SENSOR_UI231X_M: "IS_SENSOR_UI231X_M",
            IS_SENSOR_UI231X_C: "IS_SENSOR_UI231X_C",
            IS_SENSOR_UI222X_M: "IS_SENSOR_UI222X_M",
            IS_SENSOR_UI222X_C: "IS_SENSOR_UI222X_C",
            IS_SENSOR_UI224X_M: "IS_SENSOR_UI224X_M",
            IS_SENSOR_UI224X_C: "IS_SENSOR_UI224X_C",
            IS_SENSOR_UI225X_M: "IS_SENSOR_UI225X_M",
            IS_SENSOR_UI225X_C: "IS_SENSOR_UI225X_C",
            IS_SENSOR_UI214X_M: "IS_SENSOR_UI214X_M",
            IS_SENSOR_UI214X_C: "IS_SENSOR_UI214X_C",
            IS_SENSOR_UI228X_M: "IS_SENSOR_UI228X_M",
            IS_SENSOR_UI228X_C: "IS_SENSOR_UI228X_C",
            IS_SENSOR_UI241X_M_R2: "IS_SENSOR_UI241X_M_R2|IS_SENSOR_UI251X_M",
            IS_SENSOR_UI241X_C_R2: "IS_SENSOR_UI241X_C_R2|IS_SENSOR_UI251X_C",
            IS_SENSOR_UI2130_M: "IS_SENSOR_UI2130_M",
            IS_SENSOR_UI2130_C: "IS_SENSOR_UI2130_C",
        }
        sensor_id_name = sensor_id_names.get(sensor_id_code, f"UNKNOWN({sensor_id_code})")

        color_mode_code = int(self.nColorMode[0]) if self.nColorMode else 0
        # Sensor-info color mode codes from uEye header semantics.
        color_mode_names = {
            0: "INVALID",
            1: "MONOCHROME",
            2: "BAYER",
            4: "CBYCRY",
        }

        bayer_pixel_code = int(self.nUpperLeftBayerPixel[0]) if self.nUpperLeftBayerPixel else 0
        # Upper-left Bayer pixel identifiers from uEye sensor info.
        bayer_pixel_names = {
            0: "RED",
            1: "GREEN",
            2: "BLUE",
            3: "GREEN2",
        }

        return dict(
            SensorID=sensor_id_code,
            SensorIDCode=sensor_id_code,
            SensorIDHex=f"0x{sensor_id_code:04X}",
            SensorIDName=sensor_id_name,
            strSensorName=self.strSensorName.decode(errors='ignore').strip('\x00').strip(),
            nColorMode=color_mode_code,
            nColorModeName=color_mode_names.get(color_mode_code, f"UNKNOWN({color_mode_code})"),
            nMaxWidth=self.nMaxWidth,
            nMaxHeight=self.nMaxHeight,
            bMasterGain=bool(self.bMasterGain),
            bRGain=bool(self.bRGain),
            bGGain=bool(self.bGGain),
            bBGain=bool(self.bBGain),
            bGlobShutter=bool(self.bGlobShutter),
            wPixelSize=self.wPixelSize,
            nUpperLeftBayerPixel=bayer_pixel_code,
            nUpperLeftBayerPixelName=bayer_pixel_names.get(bayer_pixel_code, f"UNKNOWN({bayer_pixel_code})"),
            Reserved=self.Reserved[:],
        )
class UEYE_CAMERA_INFO(ct.Structure):
    _fields_ = [
        ("dwCameraID", ct.c_uint32),
        ("dwDeviceID", ct.c_uint32),
        ("dwSensorID", ct.c_uint32),
        ("dwInUse",    ct.c_uint32),
        ("SerNo",      ct.c_char * 16),
        ("Model",      ct.c_char * 16),
        ("dwStatus",   ct.c_uint32),
        ("dwReserved", ct.c_uint32 * 15)]
    def to_dict(self):
        """Convert camera-list entry fields to a Python dictionary."""
        return dict(
            dwCameraID  =self.dwCameraID,
            dwDeviceID  =self.dwDeviceID,
            dwSensorID  =self.dwSensorID,
            dwInUse     =self.dwInUse,
            SerNo       =self.SerNo.decode().strip(),
            Model       =self.Model.decode().strip(),
            dwStatus    =self.dwStatus,
            dwReserved  =self.dwReserved[:])
class IS_RECT(ct.Structure):
    _fields_ = [
        ("s32X",      ct.c_int),
        ("s32Y",      ct.c_int),
        ("s32Width",  ct.c_int),
        ("s32Height", ct.c_int)]
    def to_dict(self):
        """Convert AOI rectangle coordinates and size into a dictionary."""
        return dict(
            s32X=self.s32X,
            s32Y=self.s32Y,
            s32Width=self.s32Width,
            s32Height=self.s32Height)


# Helper functions
def is_GetNumberOfCameras()->int:
    """Return the number of connected uEye cameras detected by the driver.

    Returns:
        int: Number of connected camera devices.
    """
    pnNumCams = ct.c_uint()
    ret = driver.is_GetNumberOfCameras(ct.byref(pnNumCams))
    uEyeError.test(ret)

    return pnNumCams.value
def is_GetCameraList()->list[dict]:
    """Return information for each camera found by ``is_GetCameraList``.

    Returns:
        list[dict]: List of camera entries converted from ``UEYE_CAMERA_INFO``.

    Raises:
        ValueError: If no cameras are available.
    """
    pnNumCams = is_GetNumberOfCameras()
    if pnNumCams == 0:
        raise ValueError('No cameras found!')
    
    # 2. Allocate camera list of correct size
    class UEYE_CAMERA_LIST(ct.Structure):
        _fields_ = [
            ("dwCount", ct.c_ulong),
            ("uci", UEYE_CAMERA_INFO * pnNumCams), # NOTE this line uses pnNumCams
        ]

    cam_list = UEYE_CAMERA_LIST()
    cam_list.dwCount = ct.c_ulong(pnNumCams)

    ret = driver.is_GetCameraList(ct.byref(cam_list))
    uEyeError.test(ret)

    return [info.to_dict() for info in cam_list.uci] # slicing turns the array into a python list
def is_GetCameraInfo(hCam:HIDS)->dict:
    """Query detailed information for an initialized camera handle.

    Args:
        hCam: Camera handle created by :func:`is_InitCamera`.

    Returns:
        dict: Parsed ``CAMINFO`` fields.
    """

    info = CAMINFO()
    ret = driver.is_GetCameraInfo(hCam, ct.byref(info))
    uEyeError.test(ret)

    return info.to_dict()
def is_GetSensorInfo(hCam:HIDS)->dict:
    """Query sensor information for an initialized camera handle.

    Args:
        hCam: Camera handle created by :func:`is_InitCamera`.

    Returns:
        dict: Parsed ``SENSORINFO`` fields.
    """
    info = SENSORINFO()
    ret = driver.is_GetSensorInfo(hCam, ct.byref(info))
    uEyeError.test(ret)

    return info.to_dict()
def is_InitCamera(hCam:HIDS=None)->HIDS:
    """Initialize a camera and return its active handle.

    Args:
        hCam: Optional existing handle; defaults to ``HIDS(0)``.

    Returns:
        HIDS: Initialized camera handle.
    """
    if hCam is None:
        hCam = HIDS(0)
    ret = driver.is_InitCamera(ct.byref(hCam), None)
    uEyeError.test(ret, 
                   (IS_SUCCESS, IS_INVALID_HANDLE))
    return hCam
def is_ExitCamera(hCam:HIDS):
    """Close an initialized camera handle.

    Args:
        hCam: Camera handle to close.
    """
    ret = driver.is_ExitCamera(hCam)
    uEyeError.test(ret)
def is_FreezeVideo(hCam:HIDS, wait:bool=True):
    """Capture a single frame using freeze mode.

    Args:
        hCam: Camera handle.
        wait: If ``True``, block until capture completes.
    """
    # There's technically an option to add a timeout here if you want instead of wait/don't wait, not implemented.
    ret = driver.is_FreezeVideo(hCam, IS_WAIT if wait else IS_DONT_WAIT) # takes a picture. Waits until image acq is finished.
    uEyeError.test(ret)
def is_CaptureVideo(hCam:HIDS, wait:bool=True):
    """Start continuous video capture for a camera.

    Args:
        hCam: Camera handle.
        wait: If ``True``, block until start request is accepted.
    """
    ret = driver.is_CaptureVideo(hCam, IS_WAIT if wait else IS_DONT_WAIT)
    uEyeError.test(ret)
def is_StopLiveVideo(hCam:HIDS):
    """Stop continuous live video capture.

    Args:
        hCam: Camera handle.
    """
    ret = driver.is_StopLiveVideo(hCam)
    uEyeError.test(ret)
def is_AOI(hCam:HIDS, x_off:int=0, y_off:int=0, x_size:int=0, y_size:int=0):
    """Get or set the image area of interest (AOI).

    Passing all zeros performs a GET operation. Any non-zero field performs
    a SET operation with the provided rectangle.

    Args:
        hCam: Camera handle.
        x_off: AOI x-offset in pixels. (s32X)
        y_off: AOI y-offset in pixels. (s32Y)
        x_size: AOI width in pixels. (s32Width)
        y_size: AOI height in pixels. (s32Height)

    Returns:
        dict: AOI rectangle after the driver call.
    """
    aoi = IS_RECT(x_off, y_off, x_size, y_size)
    if not (x_off or y_off or x_size or y_size):
        # GET mode if all 0
        flag = IS_AOI_IMAGE_GET_AOI
    else: # SET mode
        flag = IS_AOI_IMAGE_SET_AOI
    ret = driver.is_AOI(hCam,
                        flag,
                        ct.byref(aoi), 
                        ct.sizeof(aoi))
    uEyeError.test(ret)
    return aoi.to_dict()
def is_SetColorMode(hCam:HIDS, mode:str='MONO8'):
    """Set monochrome color mode for the active camera.

    Args:
        hCam: Camera handle.
        mode: Color mode name, with or without ``IS_CM_`` prefix. Currently only support MONO8, MONO12, and MONO16.

    Raises:
        KeyError: If the provided mode name is unknown.
    """
    if not mode.upper().startswith('IS_CM_'):
        mode = 'IS_CM_' + mode.upper()

    codes = dict(
        IS_CM_MONO8  = IS_CM_MONO8,
        IS_CM_MONO12 = IS_CM_MONO12,
        IS_CM_MONO16 = IS_CM_MONO16)

    ret = driver.is_SetColorMode(hCam, 
                                 codes[mode.upper()])
    # NOTE that if you use IS_GET_COLOR_MODE, the return will just be the current setting and NOT and error code
    uEyeError.test(ret)
def is_SetBinning(hCam:HIDS, bin:int|tuple[int,int]):
    """Configure horizontal and vertical hardware binning. 
    NOTE that this will change the image size.

    Args:
        hCam: Camera handle.
        bin: Either one integer for symmetric binning or ``(x, y)`` tuple.
    """
    if isinstance(bin, int):
        bin = (bin,bin)
    
    code = IS_BINNING_DISABLE # 0x00

    if bin[0] == 2:
        code = code | IS_BINNING_2X_HORIZONTAL
    elif bin[0] == 3:
        code = code | IS_BINNING_3X_HORIZONTAL
    elif bin[0] == 4:
        code = code | IS_BINNING_4X_HORIZONTAL
    elif bin[0] == 5:
        code = code | IS_BINNING_5X_HORIZONTAL
    elif bin[0] == 6:
        code = code | IS_BINNING_6X_HORIZONTAL
    elif bin[0] == 8:
        code = code | IS_BINNING_8X_HORIZONTAL
    
    if bin[1] == 2:
        code = code | IS_BINNING_2X_VERTICAL
    elif bin[1] == 3:
        code = code | IS_BINNING_3X_VERTICAL
    elif bin[1] == 4:
        code = code | IS_BINNING_4X_VERTICAL
    elif bin[1] == 5:
        code = code | IS_BINNING_5X_VERTICAL
    elif bin[1] == 6:
        code = code | IS_BINNING_6X_VERTICAL
    elif bin[1] == 8:
        code = code | IS_BINNING_8X_VERTICAL
    
    ret = driver.is_SetBinning(hCam, code)
    uEyeError.test(ret)
def is_FreeImageMem(hCam:HIDS, pMem:ct.c_void_p, memID:ct.c_int):
    """Release an image-memory block allocated by the driver.

    Args:
        hCam: Camera handle.
        pMem: Pointer to image memory.
        memID: Driver memory identifier.
    """
    ret = driver.is_FreeImageMem(hCam, 
                                 pMem, 
                                 memID)
    uEyeError.test(ret)
def is_Exposure(hCam:HIDS, ms:float=0)->int:
    """Set or query camera exposure time. 
    NOTE that this does not fully implement IDS' is_Exposure, which is a complicated mess. 
    This only gets/sets the value. The other capabilities are provided in :func:`exposureGetCapabilities` and :func:`exposureGetRange`.

    Args:
        hCam: Camera handle.
        ms: Exposure in milliseconds. ``0`` performs a query.

    Returns:
        float: Current exposure value in milliseconds.
    """
    val = ct.c_double(ms)
    if ms:
        flag = IS_EXPOSURE_CMD_SET_EXPOSURE
    else:
        flag = IS_EXPOSURE_CMD_GET_EXPOSURE
    ret = driver.is_Exposure(hCam,
                             flag,
                             ct.byref(val),
                             ct.sizeof(val))
    uEyeError.test(ret)
    return val.value
def exposureGetCapabilities(hCam: HIDS) -> int:
    """Return exposure capability bit flags supported by the camera.

    Args:
        hCam: Camera handle.

    Returns:
        int: Capability bitmask from ``IS_EXPOSURE_CMD_GET_CAPS``.
    """
    caps = ct.c_uint()
    ret = driver.is_Exposure(hCam,
                      IS_EXPOSURE_CMD_GET_CAPS,
                      ct.byref(caps),
                      ct.sizeof(caps))
    uEyeError.test(ret)
    return caps.value
def exposureGetRange(hCam: HIDS) -> tuple[float, float, float]:
    """Return minimum, maximum, and increment exposure values.

    Args:
        hCam: Camera handle.

    Returns:
        tuple[float, float, float]: ``(min_ms, max_ms, increment_ms)``.
    """
    arr_type = ct.c_double * 3
    arr = arr_type()
    ret = driver.is_Exposure(hCam,
                      IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE,
                      ct.byref(arr),
                      ct.sizeof(arr))
    uEyeError.test(ret)
    return arr[0], arr[1], arr[2]
def is_SetHWGainFactor(hCam, master):
    """Placeholder for gain-factor API support. TODO

    Raises:
        NotImplementedError: Always, because this path is intentionally
            not implemented.
    """
    raise NotImplementedError
    ret = driver.is_SetHWGainFactor(hCam, master, -1, -1, -1)
    uEyeError.test(ret)
def is_AllocImageMem(hCam:HIDS, width:int, height:int, bpp:int, pMem:ct.c_void_p=None, memID:ct.c_int=None)->tuple[ct.c_void_p, ct.c_int]:
    """Allocate image memory for the active camera.

    Args:
        hCam: Camera handle.
        width: Frame width in pixels.
        height: Frame height in pixels.
        bpp: Bits per pixel.
        pMem: Optional pointer container to reuse.
        memID: Optional memory-id container to reuse.

    Returns:
        tuple[ct.c_void_p, ct.c_int]: Allocated memory pointer and memory ID.
    """
    if pMem is None:
        pMem = ct.c_void_p()
    if memID is None:
        memID = ct.c_int()
    ret = driver.is_AllocImageMem(hCam, 
                                  width, 
                                  height,
                                  bpp, # bits per pixel
                                  ct.byref(pMem),
                                  ct.byref(memID))
    uEyeError.test(ret)
    return pMem, memID
def is_SetImageMem(hCam:HIDS, pMem:ct.c_void_p, memID:ct.c_int):
    """Activate a previously allocated image-memory block for capture.

    Args:
        hCam: Camera handle.
        pMem: Pointer to the image memory.
        memID: Driver memory identifier.
    """
    ret = driver.is_SetImageMem(hCam, 
                                pMem, 
                                memID)
    uEyeError.test(ret)
def allocAndSetMem(hCam:HIDS, width:int, height:int, bpp:int)->tuple[ct.c_void_p, ct.c_int]:
    """Allocate image memory and immediately set it as active.

    Args:
        hCam: Camera handle.
        width: Frame width in pixels.
        height: Frame height in pixels.
        bpp: Bits per pixel.

    Returns:
        tuple[ct.c_void_p, ct.c_int]: Active memory pointer and memory ID.
    """
    pMem, memID = is_AllocImageMem(hCam, width, height, bpp)
    is_SetImageMem(hCam, pMem, memID)
    return pMem, memID
def is_GetImageMem(hCam:HIDS)->ct.c_void_p:
    """Return pointer to the currently active image memory.

    Args:
        hCam: Camera handle.

    Returns:
        ct.c_void_p: Pointer to image memory.

    Raises:
        ValueError: If the driver returns a null pointer.
    """
    ptr = ct.c_void_p()
    ret = driver.is_GetImageMem(hCam, 
                                ct.byref(ptr))
    uEyeError.test(ret)
    if not ptr.value:
            raise ValueError("Null image pointer received")
    return ptr
def getImageFromMem(hCam:HIDS, width:int, height:int):
    """Copy the current image-memory contents into a NumPy array.

    Args:
        hCam: Camera handle.
        width: Frame width in pixels.
        height: Frame height in pixels.

    Returns:
        numpy.ndarray: Copied frame data with shape ``(height, width)``.
    """
    ptr = is_GetImageMem(hCam)

    buf_type = ct.c_ubyte * (width*height)
    buf = buf_type.from_address(ptr.value)
    arr = np.ctypeslib.as_array(buf).reshape((height, width))

    return arr.copy()

if __name__ == '__main__':
    camlist = is_GetCameraList()
    print('number of cameras:', len(camlist))
    print(camlist)

    hCam = is_InitCamera()
    print(is_GetCameraInfo(hCam))
    print(is_GetSensorInfo(hCam))