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
            string = ','.join([repr(v) for v in args]) + ','.join([f'{k}={repr(e)}' for k,e in kwargs.items()])
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
    _WIDTH_PX = 2048
    _HEIGHT_PX = 1532
    def __init__(self, ring_size=4, verbosity:str=None):
        """Initialize camera state, acquisition settings, and ring buffer.

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
        self.exposure = None

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
            return self._HEIGHT_PX
        elif self.binning == 2:
            return self._HEIGHT_PX//2+2
        elif self.binning == 3:
            return self._HEIGHT_PX//3+2
        elif self.binning == 4:
            return self._HEIGHT_PX//4+1
        else:
            raise ValueError('Binning value should only be 1, 2, 3, or 4!')
    @property
    def width(self):
        """Return frame width in pixels for the current hardware binning.

        Raises:
            ValueError: If ``self.binning`` is outside supported factors.
        """
        if self.binning in (1,2):
            return self._WIDTH_PX//self.binning
        elif self.binning == 3:
            return self._WIDTH_PX//self.binning-2
        elif self.binning == 4:
            return self._WIDTH_PX//self.binning-4
        else:
            raise ValueError('Binning value should only be 1, 2, 3, or 4!')
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
            uEye.is_InitCamera(self.hCam)
            self._opened = True
            self._prev_set_time = time.time()
        
        if set_defaults:
            self.set()
    @_verbose
    def set(self, colormode:str='MONO8', binning:int=1, exposure:float=0):
        """Apply primary acquisition settings and (re)allocate image memory.

        Args:
            colormode: uEye monochrome color mode suffix (for example ``MONO8``).
            binning: Hardware binning factor in each dimension.
            exposure: Exposure time in milliseconds. ``0`` queries current value.

        Raises:
            NameError: If the camera has not been opened.
        """
        if not self._opened:
            raise NameError('Camera not yet opened!')
        if self._streaming:
            self.stop_grab_thread()

        self._set_AOI( )
        # self._set_display_mode('IS_CM_DIB') # TODO does not work right? I am pretty sure this is not necessary to do anyway for the SC30
        self._set_color_mode( colormode.upper() )
        self._set_hardware_binning( int(binning) )
        self._set_exposure(exposure)
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
        uEye.is_AOI(self.hCam, 0,0, self._WIDTH_PX, self._HEIGHT_PX)
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
    def _set_exposure(self, ms:float):
        """Set or query exposure and cache the resulting value.

        Args:
            ms: Desired exposure in milliseconds; ``0`` reads current exposure.
        """
        self.exposure = uEye.is_Exposure(self.hCam, ms)
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
    import matplotlib.pyplot as plt
    sc30 = SC30Camera(verbosity='high')
    sc30.open(False)
    print(repr(sc30.get_camera_info()))
    sc30.set(binning=1, exposure=200)

    arr = sc30.capture_single_frame()
    print('Image mean value:', np.mean(arr))

    plt.matshow(arr, cmap='gray')
    plt.show()
