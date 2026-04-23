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
driver.is_GetSensorInfo.argtypes   = [HIDS, ct.c_void_p]
driver.is_GetSensorInfo.restype    = ct.c_int
driver.is_Exposure.argtypes        = [HIDS, ct.c_uint, ct.c_void_p, ct.c_uint]
driver.is_Exposure.restype         = ct.c_int
driver.is_SetHardwareGain.argtypes = [HIDS, ct.c_int, ct.c_int, ct.c_int, ct.c_int]
driver.is_SetHardwareGain.restype  = ct.c_int
driver.is_SetFrameRate.argtypes    = [HIDS, ct.c_double, ct.POINTER(ct.c_double)]
driver.is_SetFrameRate.restype     = ct.c_int
driver.is_GetFramesPerSecond.argtypes = [HIDS, ct.POINTER(ct.c_double)]
driver.is_GetFramesPerSecond.restype  = ct.c_int
driver.is_GetFrameTimeRange.argtypes = [HIDS, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
driver.is_GetFrameTimeRange.restype  = ct.c_int
driver.is_PixelClock.argtypes      = [HIDS, ct.c_uint, ct.c_void_p, ct.c_uint]
driver.is_PixelClock.restype       = ct.c_int


# ---- Parameters ---- #
# This list is not exhaustive. It's mostly just what I am using.

class _code_str_pair:
    def __init__(self, codes:list[int], meanings:list[str]):
        self.codes = codes
        self.meanings = meanings
    @classmethod
    def from_dict(cls, d:dict):
        k = list(d.keys())
        v = list(d.values())
        if isinstance(k[0], str) and isinstance(v[0], int):
            codes, meanings = v, k
        elif isinstance(v[0], str) and isinstance(k[0], int):
            codes, meanings = k, v
        return cls(codes, meanings)
    def __getitem__(self, key:int|str):
        if isinstance(key, int):
            return self.meanings[self.codes.index(key)]
        if isinstance(key, str):
            try:
                return self.codes[self.meanings.index(key)]
            except:
                for c,m in zip(self.codes,self.meanings):
                    if m.startswith(key):
                        return c
        raise IndexError(f'Could not find key {key}')
    def get(self, code_or_meaning:int|str, default:str|int=None):
        if default is None:
            return self[code_or_meaning]
        else:
            try:
                return self[code_or_meaning]
            except KeyError or IndexError:
                return default


# Area of Interest set/get
AOI_CODES = _code_str_pair.from_dict(dict(
    IS_AOI_IMAGE_SET_AOI          = 0x0001,
    IS_AOI_IMAGE_GET_AOI          = 0x0002,
    IS_AOI_IMAGE_SET_POS          = 0x0003,
    IS_AOI_IMAGE_GET_POS          = 0x0004,
    IS_AOI_IMAGE_SET_SIZE         = 0x0005,
    IS_AOI_IMAGE_GET_SIZE         = 0x0006,
    IS_AOI_IMAGE_GET_POS_MIN      = 0x0007,
    IS_AOI_IMAGE_GET_SIZE_MIN     = 0x0008,
    IS_AOI_IMAGE_GET_POS_MAX      = 0x0009,
    IS_AOI_IMAGE_GET_SIZE_MAX     = 0x0010,
    IS_AOI_IMAGE_GET_POS_INC      = 0x0011,
    IS_AOI_IMAGE_GET_SIZE_INC     = 0x0012,
    IS_AOI_IMAGE_GET_POS_X_ABS    = 0x0013,
    IS_AOI_IMAGE_GET_POS_Y_ABS    = 0x0014,
    IS_AOI_IMAGE_GET_ORIGINAL_AOI = 0x0015
))

# Color modes
_IS_CM_ORDER_BGR  = 0x0000
_IS_CM_ORDER_RGB  = 0x0080
_IS_CM_FORMAT_PLANAR = 0x2000
COLOR_MODE_CODES = _code_str_pair.from_dict(dict(
    IS_COLORMODE_INVALID = 0,
    IS_COLORMODE_MONOCHROME = 1,
    IS_COLORMODE_BAYER = 2,
    IS_COLORMODE_CBYCRY = 4,
    IS_COLORMODE_JPEG = 8,

    IS_GET_COLOR_MODE = 0x8000,

    # Planar vs packed format
    IS_CM_FORMAT_PLANAR = 0x2000,
    IS_CM_FORMAT_MASK = 0x2000,

    # BGR vs. RGB order
    IS_CM_ORDER_BGR = 0x0000,
    IS_CM_ORDER_RGB = 0x0080,
    IS_CM_ORDER_MASK = 0x0080,

    IS_CM_PREFER_PACKED_SOURCE_FORMAT = 0x4000, # This flag indicates whether a packed source pixelformat should be used (also for the debayered pixel formats)

    IS_CM_SENSOR_RAW8 = 11, # Raw sensor data, occupies 8 bits
    IS_CM_SENSOR_RAW10 = 33, # Raw sensor data, occupies 16 bits
    IS_CM_SENSOR_RAW12 = 27, # Raw sensor data, occupies 16 bits
    IS_CM_SENSOR_RAW16 = 29, # Raw sensor data, occupies 16 bits

    IS_CM_MONO8  = 6, # Mono, occupies 8 bits
    IS_CM_MONO10 = 34, # Mono, occupies 16 bits
    IS_CM_MONO12 = 26, # Mono, occupies 16 bits
    IS_CM_MONO16 = 28, # Mono, occupies 16 bits

    IS_CM_BGR5_PACKED   = (3  | _IS_CM_ORDER_BGR), # BGR (5 5 5 1), 1 bit not used, occupies 16 bits
    IS_CM_BGR565_PACKED = (2  | _IS_CM_ORDER_BGR), # BGR (5 6 5), occupies 16 bits

    IS_CM_RGB8_PACKED = (1  | _IS_CM_ORDER_RGB), # RGB (8 8 8), occupies 24 bits
    IS_CM_BGR8_PACKED = (1  | _IS_CM_ORDER_BGR), # BGR (8 8 8), occupies 24 bits

    IS_CM_RGBA8_PACKED = (0  | _IS_CM_ORDER_RGB), # BGRA and RGBA (8 8 8 8), alpha not used, occupies 32 bits
    IS_CM_BGRA8_PACKED = (0  | _IS_CM_ORDER_BGR),

    IS_CM_RGBY8_PACKED = (24 | _IS_CM_ORDER_RGB), # BGRY and RGBY (8 8 8 8), occupies 32 bits
    IS_CM_BGRY8_PACKED = (24 | _IS_CM_ORDER_BGR),

    IS_CM_RGB10_PACKED = (25 | _IS_CM_ORDER_RGB), # BGR and RGB (10 10 10 2), 2 bits not used, occupies 32 bits, debayering is done from 12 bit raw 
    IS_CM_BGR10_PACKED = (25 | _IS_CM_ORDER_BGR),

    IS_CM_RGB10_UNPACKED = (35 | _IS_CM_ORDER_RGB), # BGR and RGB (10(16) 10(16) 10(16)), 6 MSB bits not used respectively, occupies 48 bits
    IS_CM_BGR10_UNPACKED = (35 | _IS_CM_ORDER_BGR),

    IS_CM_RGB12_UNPACKED = (30 | _IS_CM_ORDER_RGB), # BGR and RGB (12(16) 12(16) 12(16)), 4 MSB bits not used respectively, occupies 48 bits
    IS_CM_BGR12_UNPACKED = (30 | _IS_CM_ORDER_BGR),

    IS_CM_RGBA12_UNPACKED = (31 | _IS_CM_ORDER_RGB), # BGRA and RGBA (12(16) 12(16) 12(16) 16), 4 MSB bits not used respectively, alpha not used, occupies 64 bits
    IS_CM_BGRA12_UNPACKED = (31 | _IS_CM_ORDER_BGR),

    IS_CM_JPEG = 32,

    IS_CM_UYVY_PACKED = 12, # YUV422 (8 8), occupies 16 bits
    IS_CM_UYVY_MONO_PACKED = 13,
    IS_CM_UYVY_BAYER_PACKED = 14,

    IS_CM_CBYCRY_PACKED = 23, # YCbCr422 (8 8), occupies 16 bits

    IS_CM_RGB8_PLANAR = (1 | _IS_CM_ORDER_RGB | _IS_CM_FORMAT_PLANAR), # RGB planar (8 8 8), occupies 24 bits

    IS_CM_ALL_POSSIBLE = 0xFFFF,
    IS_CM_MODE_MASK = 0x007F,
))

# Wait for completion (for image capturing)
LIVE_FREEZE_CAPTURE_CODES = _code_str_pair.from_dict(dict(
    IS_GET_LIVE          = 0x8000,
    IS_WAIT              = 0x0001,
    IS_DONT_WAIT         = 0x0000,
    IS_FORCE_VIDEO_STOP  = 0x4000,
    IS_FORCE_VIDEO_START = 0x4000,
    IS_USE_NEXT_MEM      = 0x8000
))

# Binning
BINNING_CODES = _code_str_pair.from_dict(dict(
    IS_BINNING_DISABLE       = 0x0000,
    IS_BINNING_2X_VERTICAL   = 0x0001,
    IS_BINNING_2X_HORIZONTAL = 0x0002,
    IS_BINNING_4X_VERTICAL   = 0x0004,
    IS_BINNING_4X_HORIZONTAL = 0x0008,
    IS_BINNING_3X_VERTICAL   = 0x0010,
    IS_BINNING_3X_HORIZONTAL = 0x0020,
    IS_BINNING_5X_VERTICAL   = 0x0040,
    IS_BINNING_5X_HORIZONTAL = 0x0080,
    IS_BINNING_6X_VERTICAL   = 0x0100,
    IS_BINNING_6X_HORIZONTAL = 0x0200,
    IS_BINNING_8X_VERTICAL   = 0x0400,
    IS_BINNING_8X_HORIZONTAL = 0x0800
)) # IS_BINNING_2X = IS_BINNING_2X_VERTICAL | IS_BINNING_2X_HORIZONTAL, etc

# Pixel clock (MHz)
PIXEL_CLOCK_CODES = _code_str_pair.from_dict(dict(
    IS_PIXELCLOCK_CMD_GET_NUMBER  = 1,
    IS_PIXELCLOCK_CMD_GET_LIST    = 2,
    IS_PIXELCLOCK_CMD_GET_RANGE   = 3,
    IS_PIXELCLOCK_CMD_GET_DEFAULT = 4,
    IS_PIXELCLOCK_CMD_GET         = 5,
    IS_PIXELCLOCK_CMD_SET         = 6,

    IS_GET_PIXEL_CLOCK            = 0x8000,
    IS_GET_DEFAULT_PIXEL_CLK      = 0x8001,
    IS_GET_PIXEL_CLOCK_INC        = 0x8005,
))

# Framerate
FRAMERATE_CODES = _code_str_pair.from_dict(dict(
    IS_GET_FRAMERATE         = 0x8000,
    IS_GET_DEFAULT_FRAMERATE = 0x8001
))

# Exposure
EXPOSURE_CODES = _code_str_pair.from_dict(dict(
    IS_EXPOSURE_CMD_GET_CAPS                        = 1,
    IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE              = 6,
    IS_EXPOSURE_CMD_GET_EXPOSURE                    = 7,
    IS_EXPOSURE_CMD_SET_EXPOSURE                    = 12,
    IS_EXPOSURE_CMD_GET_LONG_EXPOSURE_RANGE_MIN     = 13,
    IS_EXPOSURE_CMD_GET_LONG_EXPOSURE_RANGE_MAX     = 14,
    IS_EXPOSURE_CMD_GET_LONG_EXPOSURE_RANGE_INC     = 15,
    IS_EXPOSURE_CMD_GET_LONG_EXPOSURE_RANGE         = 16,
    IS_EXPOSURE_CMD_GET_LONG_EXPOSURE_ENABLE        = 17,
    IS_EXPOSURE_CMD_SET_LONG_EXPOSURE_ENABLE        = 18,

    IS_EXPOSURE_CAP_EXPOSURE                        = 0x00000001,
    IS_EXPOSURE_CAP_FINE_INCREMENT                  = 0x00000002,
    IS_EXPOSURE_CAP_LONG_EXPOSURE                   = 0x00000004
))

# Sensor Types by ID
SENSOR_TYPE_CODES = _code_str_pair.from_dict({
    0x0000: 'IS_SENSOR_INVALID -  Not a valid sensor',

    ## CMOS Sensors
    0x0001: 'IS_SENSOR_UI141X_M -  CMOS, VGA rolling shutter, monochrome',
    0x0002: 'IS_SENSOR_UI141X_C -  CMOS, VGA rolling shutter, color',
    0x0003: 'IS_SENSOR_UI144X_M -  CMOS, SXGA rolling shutter, monochrome',
    0x0004: 'IS_SENSOR_UI144X_C -  CMOS, SXGA rolling shutter, SXGA color',
    0x0030: 'IS_SENSOR_UI154X_M -  CMOS, SXGA rolling shutter, monochrome',
    0x0031: 'IS_SENSOR_UI154X_C -  CMOS, SXGA rolling shutter, color',
    0x0008: 'IS_SENSOR_UI145X_C -  CMOS, UXGA rolling shutter, color',
    0x000a: 'IS_SENSOR_UI146X_C -  CMOS, QXGA rolling shutter, color',
    0x000b: 'IS_SENSOR_UI148X_M -  CMOS, 5MP rolling shutter, monochrome',
    0x000c: 'IS_SENSOR_UI148X_C -  CMOS, 5MP rolling shutter, color',
    0x0010: 'IS_SENSOR_UI121X_M -  CMOS, VGA global shutter, monochrome',
    0x0011: 'IS_SENSOR_UI121X_C -  CMOS, VGA global shutter, VGA color',
    0x0012: 'IS_SENSOR_UI122X_M -  CMOS, WVGA global shutter, monochrome',
    0x0013: 'IS_SENSOR_UI122X_C -  CMOS, WVGA global shutter, color',
    0x0015: 'IS_SENSOR_UI164X_C -  CMOS, SXGA rolling shutter, color',
    0x0017: 'IS_SENSOR_UI155X_C -  CMOS, UXGA rolling shutter, color',
    0x0018: 'IS_SENSOR_UI1223_M -  CMOS, WVGA global shutter, monochrome',
    0x0019: 'IS_SENSOR_UI1223_C -  CMOS, WVGA global shutter, color',
    0x003E: 'IS_SENSOR_UI149X_M -  CMOS, 10MP rolling shutter, monochrome',
    0x003F: 'IS_SENSOR_UI149X_C -  CMOS, 10MP rolling shutter, color',
    0x0022: 'IS_SENSOR_UI1225_M -  CMOS, WVGA global shutter, monochrome, LE model',
    0x0023: 'IS_SENSOR_UI1225_C -  CMOS, WVGA global shutter, color, LE model',
    0x0025: 'IS_SENSOR_UI1645_C -  CMOS, SXGA rolling shutter, color, LE model',
    0x0027: 'IS_SENSOR_UI1555_C -  CMOS, UXGA rolling shutter, color, LE model',
    0x0028: 'IS_SENSOR_UI1545_M -  CMOS, SXGA rolling shutter, monochrome, LE model',
    0x0029: 'IS_SENSOR_UI1545_C -  CMOS, SXGA rolling shutter, color, LE model',
    0x002B: 'IS_SENSOR_UI1455_C -  CMOS, UXGA rolling shutter, color, LE model',
    0x002D: 'IS_SENSOR_UI1465_C -  CMOS, QXGA rolling shutter, color, LE model',
    0x002E: 'IS_SENSOR_UI1485_M -  CMOS, 5MP rolling shutter, monochrome, LE model',
    0x002F: 'IS_SENSOR_UI1485_C -  CMOS, 5MP rolling shutter, color, LE model',
    0x0040: 'IS_SENSOR_UI1495_M -  CMOS, 10MP rolling shutter, monochrome, LE model',
    0x0041: 'IS_SENSOR_UI1495_C -  CMOS, 10MP rolling shutter, color, LE model',
    0x004A: 'IS_SENSOR_UI112X_M -  CMOS, 0768x576, HDR sensor, monochrome',
    0x004B: 'IS_SENSOR_UI112X_C -  CMOS, 0768x576, HDR sensor, color',
    0x004C: 'IS_SENSOR_UI1008_M -  CMOS',
    0x004D: 'IS_SENSOR_UI1008_C -  CMOS',
    0x0076: 'IS_SENSOR_UIF005_M -  CMOS',
    0x0077: 'IS_SENSOR_UIF005_C -  CMOS',
    0x020A: 'IS_SENSOR_UI1005_M -  CMOS',
    0x020B: 'IS_SENSOR_UI1005_C -  CMOS',
    0x0050: 'IS_SENSOR_UI1240_M -  CMOS, SXGA global shutter, monochrome',
    0x0051: 'IS_SENSOR_UI1240_C -  CMOS, SXGA global shutter, color',
    0x0062: 'IS_SENSOR_UI1240_NIR -  CMOS, SXGA global shutter, NIR',
    0x0054: 'IS_SENSOR_UI1240LE_M -  CMOS, SXGA global shutter, monochrome, single board',
    0x0055: 'IS_SENSOR_UI1240LE_C -  CMOS, SXGA global shutter, color, single board',
    0x0064: 'IS_SENSOR_UI1240LE_NIR -  CMOS, SXGA global shutter, NIR, single board',
    0x0066: 'IS_SENSOR_UI1240ML_M -  CMOS, SXGA global shutter, monochrome, single board',
    0x0067: 'IS_SENSOR_UI1240ML_C -  CMOS, SXGA global shutter, color, single board',
    0x0200: 'IS_SENSOR_UI1240ML_NIR -  CMOS, SXGA global shutter, NIR, single board',
    0x0078: 'IS_SENSOR_UI1243_M_SMI -  CMOS',
    0x0079: 'IS_SENSOR_UI1243_C_SMI -  CMOS',
    0x0032: 'IS_SENSOR_UI1543_M -  CMOS, SXGA rolling shutter, monochrome, single board',
    0x0033: 'IS_SENSOR_UI1543_C -  CMOS, SXGA rolling shutter, color, single board',
    0x003A: 'IS_SENSOR_UI1544_M -  CMOS, SXGA rolling shutter, monochrome, single board',
    0x003B: 'IS_SENSOR_UI1544_C -  CMOS, SXGA rolling shutter, color, single board',
    0x003C: 'IS_SENSOR_UI1543_M_WO -  CMOS, SXGA rolling shutter, monochrome, single board',
    0x003D: 'IS_SENSOR_UI1543_C_WO -  CMOS, SXGA rolling shutter, color, single board',
    0x0035: 'IS_SENSOR_UI1453_C -  CMOS, UXGA rolling shutter, color, single board',
    0x0037: 'IS_SENSOR_UI1463_C -  CMOS, QXGA rolling shutter, color, single board',
    0x0038: 'IS_SENSOR_UI1483_M -  CMOS, QSXG rolling shutter, monochrome, single board',
    0x0039: 'IS_SENSOR_UI1483_C -  CMOS, QSXG rolling shutter, color, single board',
    0x004E: 'IS_SENSOR_UI1493_M -  CMOS, 10Mp rolling shutter, monochrome, single board',
    0x004F: 'IS_SENSOR_UI1493_C -  CMOS, 10MP rolling shutter, color, single board',
    0x0044: 'IS_SENSOR_UI1463_M_WO -  CMOS, QXGA rolling shutter, monochrome, single board',
    0x0045: 'IS_SENSOR_UI1463_C_WO -  CMOS, QXGA rolling shutter, color, single board',
    0x0047: 'IS_SENSOR_UI1553_C_WN -  CMOS, UXGA rolling shutter, color, single board',
    0x0048: 'IS_SENSOR_UI1483_M_WO -  CMOS, QSXGA rolling shutter, monochrome, single board',
    0x0049: 'IS_SENSOR_UI1483_C_WO -  CMOS, QSXGA rolling shutter, color, single board',
    0x005A: 'IS_SENSOR_UI1580_M -  CMOS, 5MP rolling shutter, monochrome',
    0x005B: 'IS_SENSOR_UI1580_C -  CMOS, 5MP rolling shutter, color',
    0x0060: 'IS_SENSOR_UI1580LE_M -  CMOS, 5MP rolling shutter, monochrome, single board',
    0x0061: 'IS_SENSOR_UI1580LE_C -  CMOS, 5MP rolling shutter, color, single board',
    0x0068: 'IS_SENSOR_UI1360M -  CMOS, 2.2MP global shutter, monochrome',
    0x0069: 'IS_SENSOR_UI1360C -  CMOS, 2.2MP global shutter, color',
    0x0212: 'IS_SENSOR_UI1360NIR -  CMOS, 2.2MP global shutter, NIR',
    0x006A: 'IS_SENSOR_UI1370M -  CMOS, 4.2MP global shutter, monochrome',
    0x006B: 'IS_SENSOR_UI1370C -  CMOS, 4.2MP global shutter, color',
    0x0214: 'IS_SENSOR_UI1370NIR -  CMOS, 4.2MP global shutter, NIR',
    0x006C: 'IS_SENSOR_UI1250_M -  CMOS, 2MP global shutter, monochrome',
    0x006D: 'IS_SENSOR_UI1250_C -  CMOS, 2MP global shutter, color',
    0x006E: 'IS_SENSOR_UI1250_NIR -  CMOS, 2MP global shutter, NIR',
    0x0070: 'IS_SENSOR_UI1250LE_M -  CMOS, 2MP global shutter, monochrome, single board',
    0x0071: 'IS_SENSOR_UI1250LE_C -  CMOS, 2MP global shutter, color, single board',
    0x0072: 'IS_SENSOR_UI1250LE_NIR -  CMOS, 2MP global shutter, NIR, single board',
    0x0074: 'IS_SENSOR_UI1250ML_M -  CMOS, 2MP global shutter, monochrome, single board',
    0x0075: 'IS_SENSOR_UI1250ML_C -  CMOS, 2MP global shutter, color, single board',
    0x0202: 'IS_SENSOR_UI1250ML_NIR -  CMOS, 2MP global shutter, NIR, single board',
    0x020B: 'IS_SENSOR_XS -  CMOS, 5MP rolling shutter, color',
    0x0204: 'IS_SENSOR_UI1493_M_AR -  CMOS',
    0x0205: 'IS_SENSOR_UI1493_C_AR -  CMOS',

    ## CCD Sensors
    0x0080: 'IS_SENSOR_UI223X_M -  Sony CCD sensor - XGA monochrome',
    0x0081: 'IS_SENSOR_UI223X_C -  Sony CCD sensor - XGA color',
    0x0082: 'IS_SENSOR_UI241X_M -  Sony CCD sensor - VGA monochrome',
    0x0083: 'IS_SENSOR_UI241X_C -  Sony CCD sensor - VGA color',
    0x0084: 'IS_SENSOR_UI234X_M -  Sony CCD sensor - SXGA monochrome',
    0x0085: 'IS_SENSOR_UI234X_C -  Sony CCD sensor - SXGA color',
    0x0088: 'IS_SENSOR_UI221X_M -  Sony CCD sensor - VGA monochrome',
    0x0089: 'IS_SENSOR_UI221X_C -  Sony CCD sensor - VGA color',
    0x0090: 'IS_SENSOR_UI231X_M -  Sony CCD sensor - VGA monochrome',
    0x0091: 'IS_SENSOR_UI231X_C -  Sony CCD sensor - VGA color',
    0x0092: 'IS_SENSOR_UI222X_M -  Sony CCD sensor - CCIR / PAL monochrome',
    0x0093: 'IS_SENSOR_UI222X_C -  Sony CCD sensor - CCIR / PAL color',
    0x0096: 'IS_SENSOR_UI224X_M -  Sony CCD sensor - SXGA monochrome',
    0x0097: 'IS_SENSOR_UI224X_C -  Sony CCD sensor - SXGA color',
    0x0098: 'IS_SENSOR_UI225X_M -  Sony CCD sensor - UXGA monochrome',
    0x0099: 'IS_SENSOR_UI225X_C -  Sony CCD sensor - UXGA color',
    0x009A: 'IS_SENSOR_UI214X_M -  Sony CCD sensor - SXGA monochrome',
    0x009B: 'IS_SENSOR_UI214X_C -  Sony CCD sensor - SXGA color',
    0x009C: 'IS_SENSOR_UI228X_M -  Sony CCD sensor - QXGA monochrome',
    0x009D: 'IS_SENSOR_UI228X_C -  Sony CCD sensor - QXGA color',
    0x0182: 'IS_SENSOR_UI241X_M_R2 -  Sony CCD sensor - VGA monochrome',
    0x0182: 'IS_SENSOR_UI251X_M -  Sony CCD sensor - VGA monochrome',
    0x0183: 'IS_SENSOR_UI241X_C_R2 -  Sony CCD sensor - VGA color',
    0x0183: 'IS_SENSOR_UI251X_C -  Sony CCD sensor - VGA color',
    0x019E: 'IS_SENSOR_UI2130_M -  Sony CCD sensor - WXGA monochrome',
    0x019F: 'IS_SENSOR_UI2130_C -  Sony CCD sensor - WXGA color'
})

# IS_...() function return codes and their meanings
RETURN_CODES = _code_str_pair.from_dict({
    -1 : 'IS_NO_SUCCESS - General error message',
    0  : 'IS_SUCCESS - Function executed successfully',
    1  : 'IS_INVALID_CAMERA_HANDLE - Invalid camera handle',
    2  : 'IS_IO_REQUEST_FAILED - An IO request from the uEye driver failed. Possibly the versions of the ueye_api.dll (API) and the driver file (ueye_usb.sys or ueye_eth.sys) do not match.',
    3  : 'IS_CANT_OPEN_DEVICE - An attempt to initialize or select the camera failed (no camera connected or initialization error).',
    11 : 'IS_CANT_OPEN_REGISTRY - Error opening a Windows registry key',
    12 : 'IS_CANT_READ_REGISTRY - Error reading settings from the Windows registry',
    15 : 'IS_NO_IMAGE_MEM_ALLOCATED - The driver could not allocate memory.',
    16 : 'IS_CANT_CLEANUP_MEMORY - The driver could not release the allocated memory.',
    17 : 'IS_CANT_COMMUNICATE_WITH_DRIVER - Communication with the driver failed because no driver has been loaded.',
    18 : 'IS_FUNCTION_NOT_SUPPORTED_YET - The function is not supported yet.',
    30 : 'IS_INVALID_IMAGE_SIZE - Invalid image size',
    32 : 'IS_INVALID_CAPTURE_MODE - The function can not be executed in the current camera operating mode (free run, trigger or standby).',
    49 : 'IS_INVALID_MEMORY_POINTER - Invalid pointer or invalid memory ID',
    50 : 'IS_FILE_WRITE_OPEN_ERROR - File cannot be opened for writing or reading.',
    51 : 'IS_FILE_READ_OPEN_ERROR - The file cannot be opened.',
    52 : 'IS_FILE_READ_INVALID_BMP_ID - The specified file is not a valid bitmap file.',
    53 : 'IS_FILE_READ_INVALID_BMP_SIZE - The bitmap size is not correct (bitmap too large).',
    108: 'IS_NO_ACTIVE_IMG_MEM - No active image memory available. You must set the memory to active using the is_SetImageMem() function or create a sequence using the is_AddToSequence() function.',
    112: 'IS_SEQUENCE_LIST_EMPTY - The sequence list is empty and cannot be deleted.',
    113: 'IS_CANT_ADD_TO_SEQUENCE - The image memory is already included in the sequence and cannot be added again.',
    117: 'IS_SEQUENCE_BUF_ALREADY_LOCKED - The memory could not be locked. The pointer to the buffer is invalid.',
    118: 'IS_INVALID_DEVICE_ID - The device ID is invalid. Valid IDs start from 1 for USB cameras, and from 1001 for GigE cameras.',
    119: 'IS_INVALID_BOARD_ID - The board ID is invalid. Valid IDs range from 1 through 255.',
    120: 'IS_ALL_DEVICES_BUSY - All cameras are in use.',
    122: 'IS_TIMED_OUT - A timeout occurred. An image capturing process could not be terminated within the allowable period.',
    123: 'IS_NULL_POINTER - Invalid array',
    125: 'IS_INVALID_PARAMETER - One of the submitted parameters is outside the valid range or is not supported for this sensor or is not available in this mode.',
    127: 'IS_OUT_OF_MEMORY - No memory could be allocated.',
    129: 'IS_ACCESS_VIOLATION - An access violation has occurred.',
    139: 'IS_NO_USB20 - The camera is connected to a port which does not support the USB 2.0 high-speed standard.',
    140: 'IS_CAPTURE_RUNNING - A capturing operation is in progress and must be terminated first.',
    145: 'IS_IMAGE_NOT_PRESENT - The requested image is not available in the camera memory or is no longer valid.',
    148: 'IS_TRIGGER_ACTIVATED - The function cannot be used because the camera is waiting for a trigger signal.',
    151: 'IS_CRC_ERROR - A CRC error-correction problem occurred while reading the settings.',
    152: 'IS_NOT_YET_RELEASED - This function has not been enabled yet in this version.',
    153: 'IS_NOT_CALIBRATED - The camera does not contain any calibration data.',
    154: 'IS_WAITING_FOR_KERNEL - The system is waiting for the kernel driver to respond.',
    155: 'IS_NOT_SUPPORTED - The camera model used here does not support this function or setting.',
    156: 'IS_TRIGGER_NOT_ACTIVATED - The function is not possible as trigger is disabled.',
    157: 'IS_OPERATION_ABORTED - The operation was cancelled.',
    158: 'IS_BAD_STRUCTURE_SIZE - An internal structure has an incorrect size.',
    159: 'IS_INVALID_BUFFER_SIZE - The image memory has an inappropriate size to store the image in the desired format.',
    160: 'IS_INVALID_PIXEL_CLOCK - This setting is not available for the currently set pixel clock frequency.',
    161: 'IS_INVALID_EXPOSURE_TIME - This setting is not available for the currently set exposure time.',
    162: 'IS_AUTO_EXPOSURE_RUNNING - This setting cannot be changed while automatic exposure time control is enabled.',
    163: 'IS_CANNOT_CREATE_BB_SURF - The BackBuffer surface cannot be created.',
    164: 'IS_CANNOT_CREATE_BB_MIX - The BackBuffer mix surface cannot be created.',
    165: 'IS_BB_OVLMEM_NULL - The BackBuffer overlay memory cannot be locked.',
    166: 'IS_CANNOT_CREATE_BB_OVL - The BackBuffer overlay memory cannot be created.',
    167: 'IS_NOT_SUPP_IN_OVL_SURF_MODE - Not supported in BackBuffer Overlay mode.',
    168: 'IS_INVALID_SURFACE - Back buffer surface invalid.',
    169: 'IS_SURFACE_LOST - Back buffer surface not found.',
    170: 'IS_RELEASE_BB_OVL_DC - Error releasing the overlay device context.',
    171: 'IS_BB_TIMER_NOT_CREATED - The back buffer timer could not be created.',
    172: 'IS_BB_OVL_NOT_EN - The back buffer overlay was not enabled.',
    173: 'IS_ONLY_IN_BB_MODE - Only possible in BackBuffer mode.',
    174: 'IS_INVALID_COLOR_FORMAT - Invalid color format',
    175: 'IS_INVALID_WB_BINNING_MODE - Mono binning/mono sub-sampling do not support automatic white balance.',
    176: 'IS_INVALID_I2C_DEVICE_ADDRESS - Invalid I2C device address',
    177: 'IS_COULD_NOT_CONVERT - The current image could not be processed.',
    178: 'IS_TRANSFER_ERROR - Transfer error. Frequent transfer errors can mostly be avoided by reducing the pixel rate.',
    179: 'IS_PARAMETER_SET_NOT_PRESENT - Parameter set is not present.',
    180: 'IS_INVALID_CAMERA_TYPE - The camera type defined in the .ini file does not match the current camera model.',
    181: 'IS_INVALID_HOST_IP_HIBYTE - Invalid HIBYTE of host address',
    182: 'IS_CM_NOT_SUPP_IN_CURR_DISPLAYMODE - The color mode is not supported in the current display mode.',
    183: 'IS_NO_IR_FILTER - No IR filter available',
    184: 'IS_STARTER_FW_UPLOAD_NEEDED - The camera\'s starter firmware is not compatible with the driver and needs to be updated.',
    185: 'IS_DR_LIBRARY_NOT_FOUND - The DirectRenderer library could not be found.',
    186: 'IS_DR_DEVICE_OUT_OF_MEMORY - Not enough graphics memory available.',
    187: 'IS_DR_CANNOT_CREATE_SURFACE - The image surface or overlay surface could not be created.',
    188: 'IS_DR_CANNOT_CREATE_VERTEX_BUFFER - The vertex buffer could not be created.',
    189: 'IS_DR_CANNOT_CREATE_TEXTURE - The texture could not be created.',
    190: 'IS_DR_CANNOT_LOCK_OVERLAY_SURFACE - The overlay surface could not be locked.',
    191: 'IS_DR_CANNOT_UNLOCK_OVERLAY_SURFACE - The overlay surface could not be unlocked.',
    192: 'IS_DR_CANNOT_GET_OVERLAY_DC - Could not get the device context handle for the overlay.',
    193: 'IS_DR_CANNOT_RELEASE_OVERLAY_DC - Could not release the device context handle for the overlay.',
    194: 'IS_DR_DEVICE_CAPS_INSUFFICIENT - Function is not supported by the graphics hardware.',
    195: 'IS_INCOMPATIBLE_SETTING - Because of other incompatible settings the function is not possible.',
    196: 'IS_DR_NOT_ALLOWED_WHILE_DC_IS_ACTIVE - A device context handle is still open in the application.',
    197: 'IS_DEVICE_ALREADY_PAIRED - The device is already in use by the system or is being used by another system. (Camera was opened and paired to a device).',
    198: 'IS_SUBNETMASK_MISMATCH - The subnet mask of the camera and PC network card are different.',
    199: 'IS_SUBNET_MISMATCH - The subnet of the camera and PC network card are different.',
    200: 'IS_INVALID_IP_CONFIGURATION - The configuration of the IP address is invalid.',
    201: 'IS_DEVICE_NOT_COMPATIBLE - The device is not compatible to the drivers.',
    202: 'IS_NETWORK_FRAME_SIZE_INCOMPATIBLE - The settings for the image size of the camera are not compatible to the PC network card.',
    203: 'IS_NETWORK_CONFIGURATION_INVALID - The configuration of the network card is invalid.',
    204: 'IS_ERROR_CPU_IDLE_STATES_CONFIGURATION - The configuration of the CPU idle has failed.',
    205: 'IS_DEVICE_BUSY - The camera is busy and cannot transfer the requested image.',
    206: 'IS_SENSOR_INITIALIZATION_FAILED - The initialization of the sensor failed.',
    207: 'IS_IMAGE_BUFFER_NOT_DWORD_ALIGNED - The image buffer is not DWORD aligned.',
    208: 'IS_SEQ_BUFFER_IS_LOCKED - The image memory is locked.',
    209: 'IS_FILE_PATH_DOES_NOT_EXIST - The file path does not exist.',
    210: 'IS_INVALID_WINDOW_HANDLE - Invalid Window handle',
    211: 'IS_INVALID_IMAGE_PARAMETER - Invalid image parameter (position or size)'
})

class uEyeError(Exception):
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
        return f'uEye Error, return code {self.ret}, which means "{RETURN_CODES.get(self.ret, "Unknown Error")}".'
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
        sensor_id_name = SENSOR_TYPE_CODES.get(sensor_id_code, f"UNKNOWN({sensor_id_code})")

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
                   (RETURN_CODES.get('IS_SUCCESS'), 
                    RETURN_CODES.get('IS_INVALID_CAMERA_HANDLE')))
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
    ret = driver.is_FreezeVideo(hCam, 
                                LIVE_FREEZE_CAPTURE_CODES.get('IS_WAIT') if wait else LIVE_FREEZE_CAPTURE_CODES.get('IS_DONT_WAIT')) # takes a picture. Waits until image acq is finished.
    uEyeError.test(ret)
def is_CaptureVideo(hCam:HIDS, wait:bool=True):
    """Start continuous video capture for a camera.

    Args:
        hCam: Camera handle.
        wait: If ``True``, block until start request is accepted.
    """
    ret = driver.is_CaptureVideo(hCam,
                                 LIVE_FREEZE_CAPTURE_CODES.get('IS_WAIT') if wait else LIVE_FREEZE_CAPTURE_CODES.get('IS_DONT_WAIT'))
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
        flag = AOI_CODES.get('IS_AOI_IMAGE_GET_AOI')
    else: # SET mode
        flag = AOI_CODES.get('IS_AOI_IMAGE_SET_AOI')
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

    ret = driver.is_SetColorMode(hCam, 
                                 COLOR_MODE_CODES.get(mode.upper()))
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
    
    code = BINNING_CODES.get('IS_BINNING_DISABLE') # 0x00

    if bin[0] != 1:
        code = code | BINNING_CODES.get(f'IS_BINNING_{bin[0]}X_HORIZONTAL')
    if bin[1] != 1:
        code = code | BINNING_CODES.get(f'IS_BINNING_{bin[1]}X_VERTICAL')
    
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

def is_PixelClockList(hCam:HIDS)->list[int]:
    """Return all allowed pixel clock values for the current camera setup.

    Args:
        hCam: Camera handle.

    Returns:
        list[int]: Allowed pixel clock values in MHz.
    """
    n = ct.c_uint(0)
    ret = driver.is_PixelClock(hCam,
                               PIXEL_CLOCK_CODES.get('IS_PIXELCLOCK_CMD_GET_NUMBER'),
                               ct.byref(n),
                               ct.sizeof(n))
    uEyeError.test(ret)

    if n.value == 0:
        return []

    arr_type = ct.c_uint * n.value
    arr = arr_type()
    ret = driver.is_PixelClock(hCam,
                               PIXEL_CLOCK_CODES.get('IS_PIXELCLOCK_CMD_GET_LIST'),
                               ct.byref(arr),
                               ct.sizeof(arr))
    uEyeError.test(ret)
    return [int(v) for v in arr]
def is_PixelClock(hCam:HIDS, mhz:int|None=None)->int:
    """Get or set the camera pixel clock in MHz.

    Args:
        hCam: Camera handle.
        mhz: Requested pixel clock in MHz. If ``None``, read current value.

    Returns:
        int: Current pixel clock in MHz after the call.
    """
    val = ct.c_uint(0 if mhz is None else int(mhz))
    cmd = PIXEL_CLOCK_CODES.get('IS_PIXELCLOCK_CMD_GET') if mhz is None else PIXEL_CLOCK_CODES.get('IS_PIXELCLOCK_CMD_SET')
    ret = driver.is_PixelClock(hCam,
                               cmd,
                               ct.byref(val),
                               ct.sizeof(val))
    uEyeError.test(ret)

    if mhz is not None:
        val = ct.c_uint(0)
        ret = driver.is_PixelClock(hCam,
                                   PIXEL_CLOCK_CODES.get('IS_PIXELCLOCK_CMD_GET'),
                                   ct.byref(val),
                                   ct.sizeof(val))
        uEyeError.test(ret)

    return int(val.value)

def is_GetFrameTimeRange(hCam:HIDS)->tuple[float, float, float]:
    """Return frame-time limits for the current timing configuration.

    Args:
        hCam: Camera handle.

    Returns:
        tuple[float, float, float]: ``(min_time_s, max_time_s, increment_s)``.
    """
    min_t = ct.c_double(0)
    max_t = ct.c_double(0)
    inc_t = ct.c_double(0)
    ret = driver.is_GetFrameTimeRange(hCam,
                                      ct.byref(min_t),
                                      ct.byref(max_t),
                                      ct.byref(inc_t))
    uEyeError.test(ret)
    return float(min_t.value), float(max_t.value), float(inc_t.value)
def is_Framerate(hCam:HIDS, fps:float|None=None)->float:
    """Get or set the camera frame rate in frames per second.

    > To be able to set the default frame rate, you have to set a pixel clock equal to or higher than the default pixel clock.

    > In general, the pixel clock is set once when opening the camera and will not be changed. Note that, if you change the pixel clock, the setting ranges for frame rate and exposure time also changes. If you change a parameter, the following order is recommended:

    > 1. Change pixel clock.

    > 2. Query frame rate range and, if applicable, set new value.

    > 3. Query exposure time range and, if applicable, set new value.

    > If one parameter is changed, the following parameters have to be adjusted due to the dependencies.

    Args:
        hCam: Camera handle.
        fps: Requested frame rate. If ``None``, query the current frame rate.

    Returns:
        float: Current frame rate in fps after the call.
    """
    if fps is None:
        current = ct.c_double(0)
        ret = driver.is_GetFramesPerSecond(hCam, ct.byref(current))
        uEyeError.test(ret)
        return float(current.value)

    new_fps = ct.c_double(0)
    ret = driver.is_SetFrameRate(hCam,
                                 ct.c_double(float(fps)),
                                 ct.byref(new_fps))
    uEyeError.test(ret)
    return float(new_fps.value)
def getFramerateRangesByPixelClock(hCam:HIDS)->list[dict]:
    """Return frame-rate ranges for every supported pixel clock value.

    This helper temporarily switches the pixel clock to each allowed value,
    queries frame-time limits, and converts them to fps bounds.

    Args:
        hCam: Camera handle.

    Returns:
        list[dict]: Per-pixel-clock range information.
    """
    original_clock = is_PixelClock(hCam)
    clocks = is_PixelClockList(hCam)
    rows: list[dict] = []

    try:
        for mhz in clocks:
            applied = is_PixelClock(hCam, mhz)
            min_t, max_t, inc_t = is_GetFrameTimeRange(hCam)
            rows.append(dict(
                pixel_clock_mhz=applied,
                min_frame_time_s=min_t,
                max_frame_time_s=max_t,
                frame_time_increment_s=inc_t,
                max_fps=(1.0 / min_t) if min_t > 0 else 0.0,
                min_fps=(1.0 / max_t) if max_t > 0 else 0.0,
            ))
    finally:
        is_PixelClock(hCam, original_clock)

    return rows

def is_Exposure(hCam:HIDS, ms:float=0, long_exposure: bool=False)->int:
    """Set or query camera exposure time. 
    NOTE that this does not fully implement IDS' is_Exposure, which is a complicated mess. 
    This only gets/sets the value. The other capabilities are provided in
    :func:`exposureGetCapabilities` and :func:`exposureGetRange`.

    Args:
        hCam: Camera handle.
        ms: Exposure in milliseconds. ``0`` performs a query.
        long_exposure: If ``True``, request long-exposure mode before get/set.
            If ``False``, request normal exposure mode.

    Returns:
        float: Current exposure value in milliseconds.
    """
    if not exposureSetLongExposureEnabled(hCam, long_exposure):
        if long_exposure:
            raise ValueError('Long exposure mode is not supported on this camera/driver.')

    if ms:
        val = ct.c_double(float(ms))
        ret = driver.is_Exposure(hCam,
                                 EXPOSURE_CODES.get('IS_EXPOSURE_CMD_SET_EXPOSURE'),
                                 ct.byref(val),
                                 ct.sizeof(val))
        uEyeError.test(ret)

    current = ct.c_double(0)
    ret = driver.is_Exposure(hCam,
                             EXPOSURE_CODES.get('IS_EXPOSURE_CMD_GET_EXPOSURE'),
                             ct.byref(current),
                             ct.sizeof(current))
    uEyeError.test(ret)
    return current.value
def exposureGetCapabilities(hCam: HIDS) -> int:
    """Return exposure capability bit flags supported by the camera.

    Args:
        hCam: Camera handle.

    Returns:
        int: Capability bitmask from ``IS_EXPOSURE_CMD_GET_CAPS``.
    """
    caps = ct.c_uint()
    ret = driver.is_Exposure(hCam,
                      EXPOSURE_CODES.get('IS_EXPOSURE_CMD_GET_CAPS'),
                      ct.byref(caps),
                      ct.sizeof(caps))
    uEyeError.test(ret)

    caps_list = []
    for elem in ('IS_EXPOSURE_CAP_EXPOSURE', 'IS_EXPOSURE_CAP_FINE_INCREMENT', 'IS_EXPOSURE_CAP_LONG_EXPOSURE'):
        if EXPOSURE_CODES.get(elem) & caps.value:
            caps_list.append(elem)
    return caps_list
def exposureGetLongExposureEnabled(hCam: HIDS) -> bool | None:
    """Return whether long-exposure mode is enabled.

    Returns ``None`` if the queried camera/driver does not support this command.
    """
    enabled = ct.c_uint(0)
    ret = driver.is_Exposure(hCam,
                             EXPOSURE_CODES.get('IS_EXPOSURE_CMD_GET_LONG_EXPOSURE_ENABLE'),
                             ct.byref(enabled),
                             ct.sizeof(enabled))
    if ret in (RETURN_CODES.get('IS_NOT_SUPPORTED'), 
               RETURN_CODES.get('IS_INVALID_PARAMETER')):
        return None
    uEyeError.test(ret)
    return bool(enabled.value)
def exposureSetLongExposureEnabled(hCam: HIDS, enable: bool) -> bool:
    """Enable or disable long-exposure mode.

    Returns:
        bool: ``True`` if the command succeeded, otherwise ``False`` when the
        camera/driver does not support this command.
    """
    flag = ct.c_uint(1 if enable else 0)
    ret = driver.is_Exposure(hCam,
                             EXPOSURE_CODES.get('IS_EXPOSURE_CMD_SET_LONG_EXPOSURE_ENABLE'),
                             ct.byref(flag),
                             ct.sizeof(flag))
    if ret in (
        RETURN_CODES.get('IS_NOT_SUPPORTED'),
        RETURN_CODES.get('IS_INVALID_PARAMETER'),
    ):
        return False
    uEyeError.test(ret)
    return True
def exposureGetLongRange(hCam: HIDS) -> tuple[float, float, float] | None:
    """Return long-exposure min/max/increment values in milliseconds.

    Returns ``None`` if unsupported.
    """
    unsupported_codes = (RETURN_CODES.get('IS_NOT_SUPPORTED'), 
                         RETURN_CODES.get('IS_INVALID_PARAMETER'))

    prev_long_enabled = exposureGetLongExposureEnabled(hCam)
    long_mode_changed = False
    if prev_long_enabled is False:
        long_mode_changed = exposureSetLongExposureEnabled(hCam, True)

    try:
        arr_type = ct.c_double * 3
        arr = arr_type()
        ret = driver.is_Exposure(hCam,
                                 EXPOSURE_CODES.get('IS_EXPOSURE_CMD_GET_LONG_EXPOSURE_RANGE'),
                                 ct.byref(arr),
                                 ct.sizeof(arr))
        if ret == RETURN_CODES.get('IS_SUCCESS'):
            return arr[0], arr[1], arr[2]

        # Some driver versions/camera models only support individual min/max/inc commands.
        if ret not in unsupported_codes:
            vmin = ct.c_double(0)
            vmax = ct.c_double(0)
            vinc = ct.c_double(0)
            ret_min = driver.is_Exposure(hCam,
                                         EXPOSURE_CODES.get('IS_EXPOSURE_CMD_GET_LONG_EXPOSURE_RANGE_MIN'),
                                         ct.byref(vmin),
                                         ct.sizeof(vmin))
            ret_max = driver.is_Exposure(hCam,
                                         EXPOSURE_CODES.get('IS_EXPOSURE_CMD_GET_LONG_EXPOSURE_RANGE_MAX'),
                                         ct.byref(vmax),
                                         ct.sizeof(vmax))
            ret_inc = driver.is_Exposure(hCam,
                                         EXPOSURE_CODES.get('IS_EXPOSURE_CMD_GET_LONG_EXPOSURE_RANGE_INC'),
                                         ct.byref(vinc),
                                         ct.sizeof(vinc))
            if ret_min == RETURN_CODES.get('IS_SUCCESS') and ret_max == RETURN_CODES.get('IS_SUCCESS') and ret_inc == RETURN_CODES.get('IS_SUCCESS'):
                return vmin.value, vmax.value, vinc.value

            if ret_min in unsupported_codes or ret_max in unsupported_codes or ret_inc in unsupported_codes:
                return None

            # Raise the first non-success code for easier diagnosis.
            uEyeError.test(ret_min)
            uEyeError.test(ret_max)
            uEyeError.test(ret_inc)

        return None
    finally:
        if prev_long_enabled is False and long_mode_changed:
            exposureSetLongExposureEnabled(hCam, False)
def exposureGetRange(hCam: HIDS, long_exposure: bool=False) -> tuple[float, float, float]:
    """Return minimum, maximum, and increment exposure values.

    Args:
        hCam: Camera handle.

    Returns:
        long_exposure: If ``True``, query long-exposure range.

    Returns:
        tuple[float, float, float]: ``(min_ms, max_ms, increment_ms)``.

    Raises:
        ValueError: If long exposure range was requested but is unsupported.
    """
    if long_exposure:
        long_range = exposureGetLongRange(hCam)
        if long_range is None:
            raise ValueError('Long exposure range is not supported on this camera/driver.')
        return long_range

    arr_type = ct.c_double * 3
    arr = arr_type()
    ret = driver.is_Exposure(hCam,
                      EXPOSURE_CODES.get('IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE'),
                      ct.byref(arr),
                      ct.sizeof(arr))
    uEyeError.test(ret)
    return arr[0], arr[1], arr[2]
def getExposureLimitsByTiming(
    hCam: HIDS,
    pixel_clocks_mhz: list[int] | None = None,
    frame_rates_fps: list[float] | None = None,
    frame_rate_samples: int = 3,
) -> list[dict]:
    """Return short/long exposure limits over timing configurations.

    For each selected pixel clock and frame-rate point, this function sets the
    timing, then queries exposure ranges in short mode and (if supported) long
    mode.

    Args:
        hCam: Camera handle.
        pixel_clocks_mhz: Optional list of pixel clocks to evaluate. If
            omitted, all allowed pixel clock values are used.
        frame_rates_fps: Optional explicit frame-rate points (fps) to evaluate
            for each pixel clock. If omitted, points are generated from the
            available frame-time range.
        frame_rate_samples: Number of generated frame-rate points when
            ``frame_rates_fps`` is omitted. Minimum is ``2``.

    Returns:
        list[dict]: Timing/exposure rows with short and long limits.
    """
    if frame_rate_samples < 2:
        frame_rate_samples = 2

    original_clock = is_PixelClock(hCam)
    original_fps = is_Framerate(hCam)
    aoi = is_AOI(hCam)

    if pixel_clocks_mhz is None:
        pixel_clocks = is_PixelClockList(hCam)
    else:
        pixel_clocks = [int(v) for v in pixel_clocks_mhz]

    rows: list[dict] = []
    try:
        for px_mhz in pixel_clocks:
            applied_clock = is_PixelClock(hCam, px_mhz)

            if frame_rates_fps is None:
                min_t, max_t, _ = is_GetFrameTimeRange(hCam)
                max_fps = (1.0 / min_t) if min_t > 0 else 0.0
                min_fps = (1.0 / max_t) if max_t > 0 else 0.0
                if frame_rate_samples == 2:
                    fps_targets = [min_fps, max_fps]
                else:
                    fps_targets = [
                        min_fps + (max_fps - min_fps) * (i / (frame_rate_samples - 1))
                        for i in range(frame_rate_samples)
                    ]
            else:
                fps_targets = [float(v) for v in frame_rates_fps]

            for fps_target in fps_targets:
                applied_fps = is_Framerate(hCam, fps_target)

                short_min, short_max, short_inc = exposureGetRange(hCam, long_exposure=False)

                long_range = exposureGetLongRange(hCam)
                long_supported = long_range is not None
                if long_supported:
                    long_min, long_max, long_inc = long_range
                else:
                    long_min = None
                    long_max = None
                    long_inc = None

                rows.append(dict(
                    width_px=aoi.get('s32Width'),
                    height_px=aoi.get('s32Height'),
                    pixel_clock_mhz=applied_clock,
                    frame_rate_fps=applied_fps,
                    short_exposure_min_ms=short_min,
                    short_exposure_max_ms=short_max,
                    short_exposure_increment_ms=short_inc,
                    long_exposure_supported=long_supported,
                    long_exposure_min_ms=long_min,
                    long_exposure_max_ms=long_max,
                    long_exposure_increment_ms=long_inc,
                ))
    finally:
        try:
            is_PixelClock(hCam, original_clock)
            is_Framerate(hCam, original_fps)
        except Exception:
            # Preserve original cleanup path even if restore fails.
            pass

    return rows

def is_SetHWGainFactor(hCam, master):
    """Placeholder for gain-factor API support. TODO

    Raises:
        NotImplementedError: Always, because this path is intentionally
            not implemented.
    """
    raise NotImplementedError
    ret = driver.is_SetHWGainFactor(hCam, master, -1, -1, -1)
    uEyeError.test(ret)


if __name__ == '__main__':
    camlist = is_GetCameraList()
    print('number of cameras:', len(camlist))
    print(camlist)

    hCam = is_InitCamera()
    print(is_GetCameraInfo(hCam))
    print(is_GetSensorInfo(hCam))