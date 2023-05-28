##
 # MeterFeeder Library Wrapper
 # 
 # by soliax, randogoth
 ##
 
from platform import os
from sys import platform
from ctypes import *

cdll = LibraryLoader(CDLL)

class MeterFeederWrapper:

    def __init__(self):
        if platform == "linux" or platform == "linux2":
            # Linux
            self._meterfeeder = cdll.LoadLibrary(os.getcwd() + '/MeterFeeder/builds/linux/libmeterfeeder.so')
        elif platform == "darwin":
            # OS X
            self._meterfeeder = cdll.LoadLibrary(os.getcwd() + '/MeterFeeder/builds/mac/libmeterfeeder.dylib')
        elif platform == "win32":
            # Windows
            self._meterfeeder = cdll.LoadLibrary(os.getcwd() + '/MeterFeeder/builds/windows/meterfeeder.dll')

        # Declare function bridging
        self._meterfeeder.MF_Initialize.argtypes = c_char_p,
        self._meterfeeder.MF_Initialize.restype = c_int
        
        self._meterfeeder.MF_GetNumberGenerators.restype = c_int

        self._meterfeeder.MF_GetListGenerators.argtypes = [POINTER(c_char_p)]

        self._meterfeeder.MF_GetBytes.argtypes = c_int, POINTER(c_ubyte), c_char_p, c_char_p,

        self._meterfeeder.MF_RandInt32.argtypes = c_char_p, c_char_p,
        self._meterfeeder.MF_RandInt32.restype = c_int

        self._meterfeeder.MF_RandUniform.argtypes = c_char_p, c_char_p,
        self._meterfeeder.MF_RandUniform.restype = c_double

        self._meterfeeder.MF_RandNormal.argtypes = c_char_p, c_char_p,
        self._meterfeeder.MF_RandNormal.restype = c_double

        self._meterfeeder.MF_Clear.argtypes = c_char_p, c_char_p,
        self._meterfeeder.MF_Clear.restype = c_bool

        self._meterfeeder.MF_Reset.argtypes = c_char_p,
        self._meterfeeder.MF_Reset.restype = c_int

        self._medErrorReason = create_string_buffer(256)

        # Initialize Meter Feeder
        result = self._meterfeeder.MF_Initialize(self._medErrorReason)
        if (len(self._medErrorReason.value) > 0):
            print(self._medErrorReason.value)
            exit(result)

    def deviceIds(self, returnAsList):
        # Get the list of connected devices
        numGenerators = self._meterfeeder.MF_GetNumberGenerators()
        generatorsListBuffers = [create_string_buffer(58) for i in range(numGenerators)]
        generatorsListBufferPointers = (c_char_p*numGenerators)(*map(addressof, generatorsListBuffers))
        self._meterfeeder.MF_GetListGenerators(generatorsListBufferPointers)
        generatorsList = [str(s.value, 'utf-8') for s in generatorsListBuffers]
        
        if returnAsList:
            return generatorsList

        deviceIdsCsvList = ""
        for i in range(numGenerators):
            if i < numGenerators - 1:
                deviceIdsCsvList += generatorsList[i].split("|")[0] + ","
            else:
                deviceIdsCsvList += generatorsList[i].split("|")[0]
        return deviceIdsCsvList

    def randint32(self, deviceId):
        try:
            return self._meterfeeder.MF_RandInt32(deviceId.encode("utf-8"), self._medErrorReason)
        except:
            self._meterfeeder.MF_Reset()
            return self._meterfeeder.MF_RandInt32(deviceId.encode("utf-8"), self._medErrorReason)

    def randuniform(self, deviceId):
        try:
            return self._meterfeeder.MF_RandUniform(deviceId.encode("utf-8"), self._medErrorReason)
        except:
            self._meterfeeder.MF_Reset()
            return self._meterfeeder.MF_RandUniform(deviceId.encode("utf-8"), self._medErrorReason)

    def randnormal(self, deviceId):
        try:
            return self._meterfeeder.MF_RandNormal(deviceId.encode("utf-8"), self._medErrorReason)
        except:
            self._meterfeeder.MF_Reset()
            return self._meterfeeder.MF_RandNormal(deviceId.encode("utf-8"), self._medErrorReason)

    def randbytes(self, deviceId, length):
        barray = bytearray(length)
        ubuffer = (c_ubyte * length).from_buffer(barray)
        try:
            self._meterfeeder.MF_GetBytes(length, ubuffer, deviceId.encode("utf-8"), self._medErrorReason)
            return barray
        except:
            self._meterfeeder.MF_Reset()
            self._meterfeeder.MF_GetBytes(length, ubuffer, deviceId.encode("utf-8"), self._medErrorReason)
            return barray

    def clear(self, deviceId):
        if self._meterfeeder.MF_Clear(deviceId.encode("utf-8"), self._medErrorReason) == False:
            print("unable to clear", deviceId, ": ", self._medErrorReason.value)

    def reset(self):
        result = self._meterfeeder.MF_Reset(self._medErrorReason)
        if (len(self._medErrorReason.value) > 0):
            print(self._medErrorReason)
            exit(result)

    def status(self):
        return "ONLINE"
