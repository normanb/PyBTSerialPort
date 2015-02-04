import os
import ctypes
from ctypes.util import find_library

class BTError(Exception):
    "Bluetooth exception, indicates a Bluetooth related error."
    pass

def check_return(result, func, cargs):
    "Error checking for Error calls"
    if result != 0:
        msg = 'Last error in "%s": %s' % (func.__name__, bt.Error_GetLastErrorMsg())
        bt.Error_Reset()
        raise BTError(msg)
    return True

def check_void(result, func, cargs):
    "Error checking for void* return"
    if not bool(result):
        msg = 'Error in "%s": %s' % (func.__name__, bt.Error_GetLastErrorMsg())
        bt.Error_Reset()
        raise BTError(msg)
    return result

def check_void_done(result, func, cargs):
    "Error checking for void* returns that might be empty with no error"
    if bt.Error_GetErrorCount():
        msg = 'Error in "%s": %s' % (func.__name__, bt.Error_GetLastErrorMsg())
        bt.Error_Reset()
        raise BTError(msg)
    return result

def check_value(result, func, cargs):
    "Error checking proper value returns"
    count = bt.Error_GetErrorCount()
    if count != 0:
        msg = 'Error in "%s": %s' % (func.__name__, bt.Error_GetLastErrorMsg())
        bt.Error_Reset()
        raise BTError(msg)
    return result

def check_value_free(result, func, cargs):
    "Error checking proper value returns"
    count = bt.Error_GetErrorCount()
    if count != 0:
        msg = 'Error in "%s": %s' % (func.__name__, bt.Error_GetLastErrorMsg())
    return result

def free_returned_char_p(result, func, cargs):
    retvalue = ctypes.string_at(result)
    p = ctypes.cast(result, ctypes.POINTER(ctypes.c_void_p))
    bt.BT_Free(p)
    return retvalue

def free_error_msg_ptr(result, func, cargs):
    retvalue = ctypes.string_at(result)
    p = ctypes.cast(result, ctypes.POINTER(ctypes.c_void_p))
    bt.BT_Free(p)
    return retvalue

if os.name == 'nt':

    def _load_library(dllname, loadfunction, dllpaths=('', )):
        """Load a DLL via ctypes load function. Return None on failure.
        Try loading the DLL from the current package directory first,
        then from the Windows DLL search path.
        """
        try:
            dllpaths = (os.path.abspath(os.path.dirname(__file__)),
                        ) + dllpaths
        except NameError:
            pass # no __file__ attribute on PyPy and some frozen distributions
        for path in dllpaths:
            if path:
                # temporarily add the path to the PATH environment variable
                # so Windows can find additional DLL dependencies.
                try:
                    oldenv = os.environ['PATH']
                    os.environ['PATH'] = path + ';' + oldenv
                except KeyError:
                    oldenv = None
            try:
                return loadfunction(os.path.join(path, dllname))
            except (WindowsError, OSError):
                pass
            finally:
                if path and oldenv is not None:
                    os.environ['PATH'] = oldenv
        return None

    bt = _load_library('bluetoothserialport_c.dll', ctypes.cdll.LoadLibrary)
    if not bt:
        raise OSError("could not find or load bluetoothserialport_c.dll")

elif os.name == 'posix':
    platform = os.uname()[0]
    lib_name = find_library('bluetoothserialport_c')
    if lib_name is None:
        raise OSError("Could not find bluetoothserialport_c library file")

    bt = ctypes.CDLL(lib_name)
else:
    raise BTError('Unsupported OS "%s"' % os.name)

bt.Error_GetLastErrorNum.restype = ctypes.c_int

bt.Error_GetLastErrorMsg.argtypes = []
bt.Error_GetLastErrorMsg.restype = ctypes.POINTER(ctypes.c_char)
bt.Error_GetLastErrorMsg.errcheck = free_error_msg_ptr

bt.Error_GetLastErrorMethod.derestype = ctypes.POINTER(ctypes.c_char)
bt.Error_GetLastErrorMethod.errcheck = free_returned_char_p

bt.Error_GetErrorCount.argtypes = []
bt.Error_GetErrorCount.restype=ctypes.c_int

bt.Error_Reset.argtypes = []
bt.Error_Reset.restype = None

bt.BTDeviceINQ_Create.argtypes = []
bt.BTDeviceINQ_Create.restype = ctypes.c_void_p
bt.BTDeviceINQ_Create.errcheck = check_void

bt.BTDeviceINQ_Inquire.argtypes = [ctypes.c_void_p, 
                                   ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)),
                                   ctypes.POINTER(ctypes.c_uint64)]
bt.BTDeviceINQ_Inquire.restype = ctypes.c_int
bt.BTDeviceINQ_Inquire.errcheck = check_return

bt.BTDeviceINQ_SdpSearch.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
bt.BTDeviceINQ_SdpSearch.restype = ctypes.c_int
bt.BTDeviceINQ_SdpSearch.errcheck = check_return

bt.BTDeviceINQ_Destroy.argtypes = [ctypes.c_void_p]
bt.BTDeviceINQ_Destroy.restype = None
bt.BTDeviceINQ_Destroy.errcheck = check_void_done

bt.BTSerialPortBinding_Create.argtypes = [ctypes.c_char_p, ctypes.c_int]
bt.BTSerialPortBinding_Create.restype = ctypes.c_void_p
bt.BTSerialPortBinding_Create.errcheck = check_void

bt.BTSerialPortBinding_Connect.argtypes = [ctypes.c_void_p]
bt.BTSerialPortBinding_Connect.restype = ctypes.c_int
bt.BTSerialPortBinding_Connect.errcheck = check_return

bt.BTSerialPortBinding_Close.argtypes = [ctypes.c_void_p]
bt.BTSerialPortBinding_Close.restype = ctypes.c_int
bt.BTSerialPortBinding_Close.errcheck = check_return

bt.BTSerialPortBinding_Write.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
bt.BTSerialPortBinding_Write.restype = ctypes.c_int
bt.BTSerialPortBinding_Write.errcheck = check_return

bt.BTSerialPortBinding_Destroy.argtypes = [ctypes.c_void_p]
bt.BTSerialPortBinding_Destroy.restype = None
bt.BTSerialPortBinding_Destroy.errcheck = check_void_done

bt.BT_Free.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
bt.BT_Free.restype = None

bt.BTDevice_GetName.argtypes = [ctypes.c_void_p]
bt.BTDevice_GetName.restype = ctypes.POINTER(ctypes.c_char)
bt.BTDevice_GetName.errcheck = free_returned_char_p

bt.BTDevice_GetAddress.argtypes = [ctypes.c_void_p]
bt.BTDevice_GetAddress.restype = ctypes.POINTER(ctypes.c_char)
bt.BTDevice_GetAddress.errcheck = free_returned_char_p

bt.BTDevice_IsConnected.argtypes = [ctypes.c_void_p]
bt.BTDevice_IsConnected.restype = ctypes.c_int
bt.BTDevice_IsConnected.errcheck = check_value

bt.BTDevice_IsAuthenticated.argtypes = [ctypes.c_void_p]
bt.BTDevice_IsAuthenticated.restype = ctypes.c_int
bt.BTDevice_IsAuthenticated.errcheck = check_value

bt.BT_DestroyDevices.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)), ctypes.c_uint32]
bt.BT_DestroyDevices.restype = None
bt.BT_DestroyDevices.errcheck = check_void_done

bt.BT_Version.argtypes = []
bt.BT_Version.restype = ctypes.POINTER(ctypes.c_char)
bt.BT_Version.errcheck = free_returned_char_p













