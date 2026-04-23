from __future__ import annotations
import numpy as np
import threading
import time
from functools import wraps
try:
    from . import uEye
except ImportError:
    # Allow direct script execution outside package context.
    import uEye


# ---- SC30 Driver ----
def _verbose(func):
    """Decorate instance methods to optionally log call details.

    Logging is controlled by ``self.verbosity``. When set to ``'high'``,
    function name and provided arguments are printed before invocation.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """Invoke ``func`` while emitting verbose call information."""
        if self.verbosity is None:
            pass
        elif self.verbosity == 'high':
            string1 = ', '.join([repr(v) for v in args]) 
            string2 = ', '.join([f'{k}={repr(e)}' for k,e in kwargs.items()])

            if string1 and string2:
                string = string1 + ', ' + string2
            else:
                string = string1 + string2

            print(f"INFO: Calling {self.__class__.__name__}.{func.__name__}({string})")

        return func(self, *args, **kwargs)
    return wrapper
class SC30Camera:
    """
    Clean SC30 driver:
    - No GET functions (SC30 firmware stubs them)
    - Full exception mapping
    - Exposure, gain, framerate setters
    - Ring buffer capture
    """
    _SENSOR_WIDTH_PX = 2048
    _SENSOR_HEIGHT_PX = 1532
    _PIXEL_SIZE_UM = 3.20
    _TIMING_FUNC_OF_PIXEL_CLOCK_MHZ = { # prev determined programatically
        5: {'frame_time_increment_s': 0.0004878,
            'max_fps': 1.3057455415318484,
            'max_frame_time_s': 1.7487629999999998,
            'min_fps': 0.5718327755104609,
            'min_frame_time_s': 0.765846},
        6: {'frame_time_increment_s': 0.0004065,
            'max_fps': 1.5668946498382181,
            'max_frame_time_s': 1.4573025,
            'min_fps': 0.686199330612553,
            'min_frame_time_s': 0.638205},
        7: {'frame_time_increment_s': 0.0003484285714285714,
            'max_fps': 1.8280437581445879,
            'max_frame_time_s': 1.2491164285714285,
            'min_fps': 0.8005658857146453,
            'min_frame_time_s': 0.5470328571428571},
        8: {'frame_time_increment_s': 0.000304875,
            'max_fps': 2.0891928664509574,
            'max_frame_time_s': 1.0929768750000002,
            'min_fps': 0.9149324408167372,
            'min_frame_time_s': 0.47865375000000004},
        9: {'frame_time_increment_s': 0.000271,
            'max_fps': 2.3503419747573275,
            'max_frame_time_s': 0.9715349999999999,
            'min_fps': 1.0292989959188295,
            'min_frame_time_s': 0.42546999999999996},
        10: {'frame_time_increment_s': 0.0002439,
            'max_fps': 2.611491083063697,
            'max_frame_time_s': 0.8743814999999999,
            'min_fps': 1.1436655510209217,
            'min_frame_time_s': 0.382923},
        11: {'frame_time_increment_s': 0.00022172727272727272,
            'max_fps': 2.8726401913700665,
            'max_frame_time_s': 0.7948922727272727,
            'min_fps': 1.2580321061230137,
            'min_frame_time_s': 0.3481118181818182},
        12: {'frame_time_increment_s': 0.00020325,
            'max_fps': 3.1337892996764363,
            'max_frame_time_s': 0.72865125,
            'min_fps': 1.372398661225106,
            'min_frame_time_s': 0.3191025},
        13: {'frame_time_increment_s': 0.00018761538461538462,
            'max_fps': 3.394938407982806,
            'max_frame_time_s': 0.6726011538461539,
            'min_fps': 1.486765216327198,
            'min_frame_time_s': 0.29455615384615386},
        14: {'frame_time_increment_s': 0.0001742142857142857,
            'max_fps': 3.6560875162891757,
            'max_frame_time_s': 0.6245582142857142,
            'min_fps': 1.6011317714292905,
            'min_frame_time_s': 0.27351642857142855},
        15: {'frame_time_increment_s': 0.0001626,
            'max_fps': 3.917236624595545,
            'max_frame_time_s': 0.582921,
            'min_fps': 1.7154983265313823,
            'min_frame_time_s': 0.255282},
        16: {'frame_time_increment_s': 0.0001524375,
            'max_fps': 4.178385732901915,
            'max_frame_time_s': 0.5464884375000001,
            'min_fps': 1.8298648816334744,
            'min_frame_time_s': 0.23932687500000002},
        17: {'frame_time_increment_s': 0.0001434705882352941,
            'max_fps': 4.439534841208285,
            'max_frame_time_s': 0.5143420588235293,
            'min_fps': 1.944231436735567,
            'min_frame_time_s': 0.22524882352941175},
        18: {'frame_time_increment_s': 0.0001355,
            'max_fps': 4.700683949514655,
            'max_frame_time_s': 0.48576749999999996,
            'min_fps': 2.058597991837659,
            'min_frame_time_s': 0.21273499999999998},
        19: {'frame_time_increment_s': 0.00012836842105263158,
            'max_fps': 4.961833057821024,
            'max_frame_time_s': 0.4602007894736842,
            'min_fps': 2.172964546939751,
            'min_frame_time_s': 0.2015384210526316},
        20: {'frame_time_increment_s': 0.00012195,
            'max_fps': 5.222982166127394,
            'max_frame_time_s': 0.43719074999999996,
            'min_fps': 2.2873311020418434,
            'min_frame_time_s': 0.1914615},
        21: {'frame_time_increment_s': 0.00011614285714285714,
            'max_fps': 5.484131274433763,
            'max_frame_time_s': 0.41637214285714286,
            'min_fps': 2.4016976571439352,
            'min_frame_time_s': 0.1823442857142857},
        22: {'frame_time_increment_s': 0.00011086363636363636,
            'max_fps': 5.745280382740133,
            'max_frame_time_s': 0.39744613636363635,
            'min_fps': 2.5160642122460275,
            'min_frame_time_s': 0.1740559090909091},
        23: {'frame_time_increment_s': 0.00010604347826086956,
            'max_fps': 6.006429491046503,
            'max_frame_time_s': 0.38016586956521736,
            'min_fps': 2.63043076734812,
            'min_frame_time_s': 0.16648826086956522},
        24: {'frame_time_increment_s': 0.000101625,
            'max_fps': 6.2675785993528725,
            'max_frame_time_s': 0.364325625,
            'min_fps': 2.744797322450212,
            'min_frame_time_s': 0.15955125},
        25: {'frame_time_increment_s': 9.756e-05,
            'max_fps': 6.528727707659243,
            'max_frame_time_s': 0.34975259999999997,
            'min_fps': 2.8591638775523043,
            'min_frame_time_s': 0.15316919999999998},
        26: {'frame_time_increment_s': 9.380769230769231e-05,
            'max_fps': 6.789876815965612,
            'max_frame_time_s': 0.33630057692307697,
            'min_fps': 2.973530432654396,
            'min_frame_time_s': 0.14727807692307693},
        27: {'frame_time_increment_s': 9.033333333333334e-05,
            'max_fps': 7.051025924271982,
            'max_frame_time_s': 0.323845,
            'min_fps': 3.0878969877564884,
            'min_frame_time_s': 0.14182333333333333},
        28: {'frame_time_increment_s': 8.710714285714285e-05,
            'max_fps': 7.312175032578351,
            'max_frame_time_s': 0.3122791071428571,
            'min_fps': 3.202263542858581,
            'min_frame_time_s': 0.13675821428571427},
        29: {'frame_time_increment_s': 8.410344827586207e-05,
            'max_fps': 7.573324140884721,
            'max_frame_time_s': 0.30151086206896555,
            'min_fps': 3.3166300979606724,
            'min_frame_time_s': 0.13204241379310344},
        30: {'frame_time_increment_s': 8.13e-05,
            'max_fps': 7.83447324919109,
            'max_frame_time_s': 0.2914605,
            'min_fps': 3.4309966530627647,
            'min_frame_time_s': 0.127641},
        31: {'frame_time_increment_s': 7.867741935483872e-05,
            'max_fps': 8.09562235749746,
            'max_frame_time_s': 0.2820585483870968,
            'min_fps': 3.5453632081648565,
            'min_frame_time_s': 0.12352354838709678},
        32: {'frame_time_increment_s': 7.621875e-05,
            'max_fps': 8.35677146580383,
            'max_frame_time_s': 0.27324421875000005,
            'min_fps': 3.6597297632669488,
            'min_frame_time_s': 0.11966343750000001},
        33: {'frame_time_increment_s': 7.390909090909091e-05,
            'max_fps': 8.6179205741102,
            'max_frame_time_s': 0.2649640909090909,
            'min_fps': 3.7740963183690415,
            'min_frame_time_s': 0.11603727272727273},
        34: {'frame_time_increment_s': 7.173529411764706e-05,
            'max_fps': 8.87906968241657,
            'max_frame_time_s': 0.2571710294117647,
            'min_fps': 3.888462873471134,
            'min_frame_time_s': 0.11262441176470588},
        35: {'frame_time_increment_s': 6.968571428571428e-05,
            'max_fps': 9.14021879072294,
            'max_frame_time_s': 0.24982328571428572,
            'min_fps': 4.002829428573226,
            'min_frame_time_s': 0.10940657142857142},
        36: {'frame_time_increment_s': 6.775e-05,
            'max_fps': 9.40136789902931,
            'max_frame_time_s': 0.24288374999999998,
            'min_fps': 4.117195983675318,
            'min_frame_time_s': 0.10636749999999999},
        37: {'frame_time_increment_s': 6.591891891891892e-05,
            'max_fps': 9.662517007335678,
            'max_frame_time_s': 0.23631932432432431,
            'min_fps': 4.2315625387774105,
            'min_frame_time_s': 0.10349270270270271},
        38: {'frame_time_increment_s': 6.418421052631579e-05,
            'max_fps': 9.923666115642048,
            'max_frame_time_s': 0.2301003947368421,
            'min_fps': 4.345929093879502,
            'min_frame_time_s': 0.1007692105263158},
        39: {'frame_time_increment_s': 6.253846153846153e-05,
            'max_fps': 10.18481522394842,
            'max_frame_time_s': 0.2242003846153846,
            'min_fps': 4.460295648981595,
            'min_frame_time_s': 0.0981853846153846},
        40: {'frame_time_increment_s': 6.0975e-05,
            'max_fps': 10.445964332254787,
            'max_frame_time_s': 0.21859537499999998,
            'min_fps': 4.574662204083687,
            'min_frame_time_s': 0.09573075},
        41: {'frame_time_increment_s': 5.948780487804878e-05,
            'max_fps': 10.707113440561157,
            'max_frame_time_s': 0.21326378048780487,
            'min_fps': 4.689028759185779,
            'min_frame_time_s': 0.09339585365853659},
        42: {'frame_time_increment_s': 5.807142857142857e-05,
            'max_fps': 10.968262548867527,
            'max_frame_time_s': 0.20818607142857143,
            'min_fps': 4.8033953142878705,
            'min_frame_time_s': 0.09117214285714285},
        43: {'frame_time_increment_s': 5.672093023255814e-05,
            'max_fps': 11.229411657173896,
            'max_frame_time_s': 0.20334453488372092,
            'min_fps': 4.917761869389963,
            'min_frame_time_s': 0.08905186046511628}}
    def __init__(self, ring_size=4, verbosity:str=None):
        """Initialize camera state, acquisition settings, and ring buffer.
        The camera/sensor information can be found [here](https://www.1stvision.com/cameras/IDS/IDS-manuals/uEye_Manual/sensor-data-ui-146x.html).
        (UI1465_C, QXGA rolling shutter, color, LE model)

        Application notes from IDS:

        - Master gain is digitally calculated on the sensor and may cause artifacts. Instead use RGB gains first (e.g. by setting a minimum value in the Auto white balance function).

        - The sensor does not allow changes of exposure time while in trigger mode. If is_Exposure() is called in trigger mode, the sensor will temporarily switch to freerun. This results in a longer delay time (depending on the frame rate) at function call.

        - Sensor speed does not increase for effective horizontal resolution <256 pixels.

        - Changing the frame rate in trigger mode has no effect. The maximum possible exposure time cannot be increased in this way.

        - With horizontal 4x binning, a dark column appears at the right-hand image border, which is caused by the sensor.
            - I have observed this. Though it remains when switching from 4x back to 1x.

        - For hardware reasons, the sensor can not perform more than 3x vertical binning. When 4x or 6x binning is activated in the uEye software, the driver uses a combination of binning and subsampling instead. Therefore, the image will not become brighter when 4x or 6x horizontal binning is activated.

        - The brightness of the first and last line might deviate due to the sensor.

        Args:
            ring_size: Number of frame slots to retain in the circular buffer.
            verbosity: ``None`` for silent operation or ``'high'`` for logging.

        Raises:
            ValueError: If ``verbosity`` is not a supported value.
        """
        self.hCam    = uEye.HIDS(0)
        self.binning = 1
        self.depth   = 1
        self.bpp     = 8
        self._exposure_ms = None
        self._long_exposure_enabled = False
        self._sensor_info = None

        self.verbosity = verbosity
        if self.verbosity is None:
            pass
        elif self.verbosity == 'high':
            pass
        else:
            raise ValueError(f'Verbosity setting {verbosity} unknown')

        self.memory_allocated = False
        self._opened    = False
        self._streaming = False
        self._prev_set_time = 0

        # Ring buffer
        self.ring_size   = ring_size
        self._ring       = [None] * ring_size
        self._ring_idx   = 0
        self._ring_lock  = threading.Lock()
        self._grab_thread = None
        self._grab_stop   = threading.Event()
    @property
    def height(self):
        """Return frame height in pixels for the current hardware binning.

        Raises:
            ValueError: If ``self.binning`` is outside supported factors.
        """
        if self.binning == 1:
            return self._SENSOR_HEIGHT_PX
        elif self.binning == 2:
            return self._SENSOR_HEIGHT_PX//2+2
        elif self.binning == 3:
            return self._SENSOR_HEIGHT_PX//3+2
        elif self.binning == 4:
            return self._SENSOR_HEIGHT_PX//4+1
        else:
            raise ValueError('Binning value should only be 1, 2, 3, or 4!')
    @property
    def width(self):
        """Return frame width in pixels for the current hardware binning.

        Raises:
            ValueError: If ``self.binning`` is outside supported factors.
        """
        if self.binning in (1,2):
            return self._SENSOR_WIDTH_PX//self.binning
        elif self.binning == 3:
            return self._SENSOR_WIDTH_PX//self.binning-2
        elif self.binning == 4:
            return self._SENSOR_WIDTH_PX//self.binning-4
        else:
            raise ValueError('Binning value should only be 1, 2, 3, or 4!')
    @property
    def exposure_ms(self):
        """Return current exposure in milliseconds, if known."""
        return self._exposure_ms
    @property
    def exposure_s(self):
        """Return current exposure in seconds, if known."""
        if self._exposure_ms is None:
            return None
        return self._exposure_ms / 1000.0
    @_verbose
    def get_camera_info(self):
        """
        Return camera identification and metadata from the uEye driver.

        Returns:
            dict: Parsed camera information fields.
        """
        return uEye.is_GetCameraInfo(self.hCam)
    @_verbose
    def open(self, set_defaults:bool=True):
        """Initialize the camera handle and optionally apply default settings.

        Args:
            set_defaults: If ``True``, call :meth:`set` with default arguments.
        """
        if not self._opened:
            # Init camera
            self.hCam = uEye.is_InitCamera(self.hCam)
            self._opened = True
            self._prev_set_time = time.time()
            self._set_AOI( ) # this should only happen once, I believe
        
        if set_defaults:
            self.set()
    @_verbose
    def set(self, colormode:str='MONO8', binning:int=1, exposure_ms:float=0, long_exposure: bool|None=None):
        """Apply primary acquisition settings and (re)allocate image memory.

        Args:
            colormode: uEye monochrome color mode suffix (for example ``MONO8``).
            binning: Hardware binning factor in each dimension.
            exposure_ms: Exposure time in milliseconds. ``0`` queries current value.
            long_exposure: Exposure mode selection. ``True`` forces long
                exposure, ``False`` forces normal exposure, and ``None`` lets
                the SC30 wrapper decide automatically.

        Raises:
            NameError: If the camera has not been opened.
        """
        if not self._opened:
            raise NameError('Camera not yet opened!')
        if self._streaming:
            self.stop_grab_thread()

        # self._set_display_mode('IS_CM_DIB') # TODO does not work right? I am pretty sure this is not necessary to do anyway for the SC30
        self._set_color_mode( colormode.upper() )
        for i in range(int(binning)):
            self._set_hardware_binning( i+1 ) # camera seems to prefer to increment binning slowly? Doesn't like going from 1 to 4 after acquiring an image.
        self._set_exposure(exposure_ms, long_exposure=long_exposure)
        self._allocate_memory()
        self._prev_set_time = time.time()
    @_verbose
    def close(self):
        """Stop acquisition, free buffers, and close the camera handle safely."""
        if not self._opened:
            return

        self.stop_grab_thread()

        if self._streaming:
            uEye.is_StopLiveVideo(self.hCam)
            self._streaming = False
        
        if self.memory_allocated:
            self._free_memory()

        uEye.is_ExitCamera(self.hCam)
        self._opened = False
    @_verbose
    def _get_AOI(self)->dict:
        """Return the currently configured area of interest from the camera."""
        return uEye.is_AOI(self.hCam)
    @_verbose
    def _set_AOI(self):
        """Set area of interest to full sensor extents."""
        uEye.is_AOI(self.hCam, 0,0, self._SENSOR_WIDTH_PX, self._SENSOR_HEIGHT_PX)
    @_verbose
    def _set_color_mode(self, mode:str='MONO8'):
        """Configure color mode and derive internal pixel-depth metadata.

        Args:
            mode: uEye color mode name.

        Raises:
            NotImplementedError: If a non-monochrome mode would require debayering.
        """
        uEye.is_SetColorMode(self.hCam, mode)

        if '8' in mode:
            self.bpp = 8
        elif '12' in mode:
            self.bpp = 12
        elif '16' in mode:
            self.bpp = 16

        if 'MONO' in mode:
            self.depth = 1
        else:
            self.depth = 3
            raise NotImplementedError('Debayering has not been implemented.')
    @_verbose
    def _set_hardware_binning(self, factor: int):
        """Configure symmetric hardware binning.

        Args:
            factor: Supported factor ``1``, ``2``, ``3``, or ``4``.

        Raises:
            ValueError: If ``factor`` is outside the supported set.
        """

        if factor not in (1,2,3,4):
            raise ValueError("Binning factor must be 1, 2, 3, or 4")

        # Apply hardware binning
        uEye.is_SetBinning(self.hCam, factor)
        self.binning = factor
    @_verbose
    def _allocate_memory(self):
        """Allocate and activate camera image memory for current frame format."""
        # Free old image memory if present
        if self.memory_allocated:
            self._free_memory()

        # Allocate memory
        self.pMem, self.mem_id = uEye.allocAndSetMem(self.hCam, 
                                                     self.width, 
                                                     self.height,
                                                     self.bpp) # bits per pixel
        self.memory_allocated = True
    @_verbose
    def _free_memory(self):
        """Release active image memory previously allocated on the camera."""
        uEye.is_FreeImageMem(self.hCam, 
                             self.pMem, 
                             self.mem_id)

        self.pMem = None
        self.mem_id = None
        self.memory_allocated = False
    @_verbose
    def _auto_long_exposure(self, ms: float) -> bool:
        """Decide whether long exposure should be used for a requested value."""
        if ms <= 0:
            return self._long_exposure_enabled

        caps = uEye.exposureGetCapabilities(self.hCam)
        if not ('IS_EXPOSURE_CAP_LONG_EXPOSURE' in caps):
            return False

        _, max_short_ms, _ = uEye.exposureGetRange(self.hCam, long_exposure=False)
        return ms > max_short_ms
    @_verbose
    def _set_exposure(self, ms:float=0, long_exposure: bool|None=None):
        """Set or query exposure and cache the resulting value.

        Args:
            ms: Desired exposure in milliseconds; ``0`` reads current exposure.
            long_exposure: ``True`` forces long mode, ``False`` forces short
                mode, and ``None`` uses automatic mode selection.
        """
        if long_exposure is None:
            long_exposure = self._auto_long_exposure(float(ms or 0))

        if ms:
            self._exposure_ms = uEye.is_Exposure(self.hCam, ms, long_exposure=long_exposure)
        self._exposure_ms = uEye.is_Exposure(self.hCam, 0, long_exposure=long_exposure)
        self._long_exposure_enabled = bool(long_exposure)
        return self.exposure_ms
    @_verbose
    def _grab_frame(self):
        """Read the latest image memory into a detached NumPy array."""
        # "is_GetImageMem() returns the pointer to the starting address of the active image memory. 
        #  If you use ring buffering, is_GetImageMem() returns the starting address of the image memory last used for image capturing."
        return uEye.getImageFromMem(self.hCam, self.width, self.height)
    @_verbose
    def capture_single_frame(self):
        """
        Capture one still image without entering continuous live-view mode.

        Returns:
            numpy.ndarray: Two-dimensional frame array with shape
                ``(height, width)``.
        """
        # Freeze (single-frame capture)
        # ret = uEye.driver.is_ForceTrigger(self.hCam)
        # uEye.uEyeError.test(ret)
        time.sleep(max(0, 1 - (time.time() - self._prev_set_time))) # wait for 1 second after setting before acquiring any images (this time has not been optimized, just seems necessary)
        uEye.is_FreezeVideo(self.hCam, wait=True) # takes a picture. Waits until image acq is finished.

        return self._grab_frame()
    @_verbose
    def start_streaming(self):
        """Start continuous camera capture mode in the driver."""
        # Start streaming
        uEye.is_CaptureVideo(self.hCam, wait=True)

        self._streaming = True
    # ---- Ring buffer ----
    @_verbose
    def _grab_loop(self, interval_s):
        """Continuously grab frames into the ring buffer until stopped.

        Args:
            interval_s: Sleep interval between successful frame reads.
        """
        while not self._grab_stop.is_set():
            try:
                frame = self._grab_frame()
            except Exception:
                continue

            with self._ring_lock:
                self._ring[self._ring_idx] = frame
                self._ring_idx = (self._ring_idx + 1) % self.ring_size

            if interval_s > 0:
                time.sleep(interval_s)
    @_verbose
    def start_grab_thread(self, interval_s=0.0):
        """Start a background thread that keeps the ring buffer fresh.

        Args:
            interval_s: Optional delay between frame acquisitions.
        """
        if self._grab_thread and self._grab_thread.is_alive():
            return
        self._grab_stop.clear()
        self._grab_thread = threading.Thread(
            target=self._grab_loop,
            args=(interval_s,),
            daemon=True
        )
        self._grab_thread.start()
    @_verbose
    def stop_grab_thread(self):
        """Stop and join the grab thread, then stop live capture if needed."""
        if self._grab_thread and self._grab_thread.is_alive():
            self._grab_stop.set()
            self._grab_thread.join()
        self._grab_thread = None
        if self._streaming:
            uEye.is_StopLiveVideo(self.hCam, wait=True)
            self._streaming = False
    @_verbose
    def get_latest_frame(self):
        """Return the newest non-empty frame from the ring buffer.

        Returns:
            numpy.ndarray | None: Most recent captured frame, or ``None`` if
                no frame has been stored yet.
        """
        with self._ring_lock:
            for i in range(self.ring_size):
                idx = (self._ring_idx - 1 - i) % self.ring_size
                frame = self._ring[idx]
                if frame is not None:
                    return frame
        return None

'''
# API                          Return Value
# is_GetCameraList ( ... )     0
# is_InitCamera ( ... )        0
# is_GetBusSpeed ( ... )       4
# is_SetErrorReport ( ... )    0
# is_GetSensorInfo ( ... )     0
# is_GetCameraInfo ( ... )     0
# is_PixelClock ( ... )        0
# is_PixelClock ( ... )        0
# is_SetColorMode ( ... )      174
# is_SetColorMode ( ... )      0
# is_SetBinning ( ... )        831
# is_PixelClock ( ... )        0
# is_PixelClock ( ... )        0
# is_SetBinning ( ... )        0
# is_PixelClock ( ... )        0
# is_AOI ( ... )               0
# is_HotPixel ( ... )          0
# is_HotPixel ( ... )          0
# is_Blacklevel ( ... )        0
# is_SetHWGainFactor ( ... )   4294967295
# is_SetHWGainFactor ( ... )   100
# is_SetHWGainFactor ( ... )   100
# is_InitEvent ( ... )         0
# is_EnableEvent ( ... )       0
# is_GetCameraInfo ( ... )     0
# is_DeviceInfo ( ... )        0
# is_GetDLLVersion ( ... )     73205847
# is_PixelClock ( ... )        0
# is_PixelClock ( ... )        0
# is_SetBinning ( ... )        0
# is_PixelClock ( ... )        0
# is_AOI ( ... )               0
# is_SetHWGainFactor ( ... )    100
# is_SetHWGainFactor ( ... )    100
# is_SetHWGainFactor ( ... )    100
# is_PixelClock ( ... )        0'''

if __name__ == '__main__':
    sc30 = SC30Camera(verbosity='high')
    sc30.open(False)
    print(sc30.get_camera_info())
    sc30.set(binning=1, exposure_ms=200)

    arr = sc30.capture_single_frame()
    print('Image mean value:', np.mean(arr))

    import matplotlib.pyplot as plt
    plt.matshow(arr, cmap='gray')
    plt.show()
