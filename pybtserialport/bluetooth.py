import ctypes

from . import core

__c_api_version__ = core.bt.BT_Version()

class SerialPortBinding(object):
    """A serial port binding for a local bluetooth device object"""
    def __init__(self, addr, channel_id, *args, **kwargs):
        if channel_id > 0:
            v = addr.encode('utf-8')
            self.handle = core.bt.BTSerialPortBinding_Create(v, channel_id);
            self.owned = True
        else:
            raise core.bt.BTError("Channel Id has to be greater than 0")

    def connect(self):
        core.bt.BTSerialPortBinding_Connect(self.handle)

    # def write(self, buf):
    #     core.bt.BTSerialPortBinding_Write(self.handle, buf, len(buf))

    def __del__(self):
        try:
            self.owned
        except AttributeError:
            # we were partially constructed.  We're going to let it leak
            # in that case
            return
        if self.owned:
            if self.handle and core:
                try:
                    core.bt
                except AttributeError:
                    # uh, leak?  We're owned, and have a handle
                    # but for some reason the dll isn't active
                    return

                core.bt.BTSerialPortBinding_Destroy(self.handle)
                self.owned = False
                self.handle = None   

class DeviceINQ(object):
    """A Device Inquirer for local bluetooth devices object"""
    def __init__(self,  *args, **kwargs):
        """Create a new device inquirer"""
        self.handle = core.bt.BTDeviceINQ_Create()
        self.owned = True

    def __del__(self):
        try:
            self.owned
        except AttributeError:
            # we were partially constructed.  We're going to let it leak
            # in that case
            return
        if self.owned:
            if self.handle and core:
                try:
                    core.bt
                except AttributeError:
                    # uh, leak?  We're owned, and have a handle
                    # but for some reason the dll isn't active
                    return

                core.bt.BTDeviceINQ_Destroy(self.handle)
                self.owned = False
                self.handle = None

    def inquire(self):
        """Search for local bluetooth devices"""
        p_num_results = ctypes.c_uint64(0)
        devices = ctypes.pointer(ctypes.c_void_p())
        core.bt.BTDeviceINQ_Inquire(
            self.handle,
            devices,
            ctypes.byref(p_num_results))
        return self._get_devices(devices, p_num_results.value)

    def search(self, addr):
        """Service Discovery Search"""
        p_channel_id = ctypes.c_int(0)
        v = addr.encode('utf-8')
        core.bt.BTDeviceINQ_SdpSearch(self.handle, v, p_channel_id)
        return p_channel_id.value

    def _get_devices(self, d, num_results):
        # take the pointer, yield the result objects and free
        devices = ctypes.cast(d, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p * num_results)))
        dvcs = ctypes.cast(devices, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))       
        try:
            for i in range(num_results):
                yield Device(devices[i])
            if dvcs:
                core.bt.BT_DestroyDevices(dvcs, num_results);
        except:
            core.bt.BT_DestroyDevices(dvcs, num_results);

class Device(object):
    """A container for device entries"""
    def __init__(self, handle, owned=False):
        """No need to instantiate these yourself"""
        if handle:
            self.handle = handle
        self.owned = owned

    @property
    def name(self):
        return core.bt.BTDevice_GetName(self.handle)

    @property
    def address(self):
        return core.bt.BTDevice_GetAddress(self.handle)

    @property
    def is_connected(self):
        return bool(core.bt.BTDevice_IsConnected(self.handle))

    @property
    def is_authenticated(self):
        return bool(core.bt.BTDevice_IsAuthenticated(self.handle))

