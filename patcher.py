#!/usr/bin/env python

import binascii
import sys
from struct import *

symbols = {}
    
class Patcher:
    firmware_base = 0x00420000

    def __init__(self, filename):
        with open(sys.argv[1], "rb") as f:
            self.data = f.read()

        self.firmware_end = self.firmware_base + len(self.data)
        print("Loading firmware file %s" % filename)
        print("    Firmware base: 0x%08x" % self.firmware_base)
        print("    Firmware end:  0x%08x" % self.firmware_end)
        print("")

    def addPageAtEndOfImage(self, page_size, count):
        self.data = self.data + '\x00' * page_size * count
        self.firmware_end = self.firmware_base + len(self.data)
        print("Adding %d page of %d bytes" % (count,page_size))
        print("    New firmware base: 0x%08x" % self.firmware_base)
        print("    New firmware end:  0x%08x" % self.firmware_end)
        print("")

    def getDataAtAddress(self, address, length):
        tmp_data = self.data[address-self.firmware_base:address-self.firmware_base+length]
        return tmp_data

    def patchStringAtAddress(self, address, string):
        newdata = binascii.hexlify(string)
        self.patchDataAtAddress(address, newdata)
        print("Patching string at address 0x%08x" % address)
        print("")

    def patchAddressAtAddress(self, address, newaddressvalue):
        old_data = self.getDataAtAddress(address,4)
        oldaddress = unpack('<I',old_data)[0]
        newaddressdata = '%08x' % unpack('>I',pack('<I',newaddressvalue))[0]
        self.patchDataAtAddress(address, newaddressdata)
        print("Patching old address 0x%08x at address 0x%08x with new address 0x%08x" % (oldaddress,address,newaddressvalue))
        print("")

    def patchByteAtAddress(self, address, newbytevalue):
        old_data = self.getDataAtAddress(address,1)
        oldbytevalue = unpack('<B',old_data)[0]    
        newbytedata = '%02x' % unpack('>B',pack('<B',newbytevalue))[0]
        self.patchDataAtAddress(address, newbytedata)
        print("Patching old byte value 0x%02x at address 0x%08x with new byte value 0x%02x" % (oldbytevalue,address,newbytevalue))
        print("")

    def patchFloatAtAddress(self, address, newfloatvalue):
        old_data = self.getDataAtAddress(address,4)
        oldfloatvalue = unpack('<f',old_data)[0]
        newfloatdata = '%08x' % unpack('>I',pack('<f',newfloatvalue))[0]
        self.patchDataAtAddress(address, newfloatdata)
        print("Patching old float value %f at address 0x%08x with new float value %f" % (oldfloatvalue,address,newfloatvalue))
        print("")

    def patchDataAtAddress(self, address, newdatahex):
        newdata = binascii.unhexlify(newdatahex)
        tmp = self.data[:address-self.firmware_base] + newdata + self.data[address-self.firmware_base+len(newdata):len(self.data)]
        self.data = tmp

    def write(self, filename):
        with open(filename, "wb") as f:
            f.write(self.data)

