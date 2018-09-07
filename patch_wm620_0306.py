#!/usr/bin/env python
#
#   By @Matioupi
#   provided under dbad licence http://dbad-license.org/
#
#   Version 2.0
#
#   Made possible thanks to all OG's work and especially ideas from @jan2642 and
#   patience of @jezzab in explaining me some stuff
#
#
#   RTFM before asking for support
#

#addresses must be given including the 0x420000 firmware loading offset

from patcher import *
from struct import *
from UBXCFGGEN import *

if __name__ == "__main__":

    print("")
    print("################################################################################")
    print("this patcher is supposed to be used on the 0306 module of I2 V01.01.0200 fw")
    print("no checks of any kind done that, use at your own risks                          ")
    print("addresses must be given including the 0x420000 firmware loading offset          ")
    print("################################################################################")
    print("")

    
    p = Patcher(sys.argv[1])
    ubxcfggen = UBXCFGGEN()
    
    sn = sys.argv[2]

    sn_parts = [ ]
    sn_parts.append(int(sn[9:11]))
    sn_parts.append(int(sn[6:8]))   
    sn_parts.append(int(sn[3:5]))
    sn_parts.append(int(sn[0:2]))
    hex_parts = [ ]
    sn_hex = ""
    for i in range (0,4):
        hex_parts.append(unpack('>B',pack('<B',sn_parts[i]))[0])
        sn_hex += '%02x' % hex_parts[i]

    #   Change the firmware code inside image
    #
    #   original I2 0306 version is 03.02.42.10 = 0A2A0203

    # HardCoded version of the version in some FC function
    p.patchByteAtAddress(0x522350,hex_parts[0])  #0x0A = 10
    p.patchByteAtAddress(0x522352,hex_parts[1])  #0x2A = 42
    p.patchByteAtAddress(0x52235E,hex_parts[2])  #0x2 = 2
    p.patchByteAtAddress(0x522360,hex_parts[3])  #0x3 = 3
    
    newversioncode = sn_hex
    print("New version code : %s\n" % newversioncode)
    p.patchDataAtAddress(0x4F8E1C,newversioncode)
    p.patchDataAtAddress(0x50AE00,newversioncode)
    p.patchDataAtAddress(0x52259C,newversioncode)
    p.patchDataAtAddress(0x52EAE0,newversioncode)

    # Ascii version of the version string
    p.patchStringAtAddress(0x58B85D,sn)

    #
    #   Patch hardcoded values for some flight modes (e.g. autonomous waypoint missions)
    #   Some of those values are also app limited and need app side patch
    #   Default app limits :
    #       range around home point : 500 m
    #       max path length : 5000 m
    #       max speed : 15 m/s
    #       max dist to home point : 500 m
    #       min/max alt : -200 / + 500 m
    #
    p.patchFloatAtAddress(0x4ADDF4,-5000.0)  #   Min altitude relative to home point : default -200.0 m OK I2
    p.patchFloatAtAddress(0x4ADDF8,9000.0)   #   Max altitude relative to home point : default 1000.0 m OK I2
    p.patchFloatAtAddress(0x4ADE40,32000.0)  #   Max distance from one waypoint to home point : default 2000.0 m  OK I2
    p.patchFloatAtAddress(0x4AE2B4,128000.0) #   Max total length of mission : default 30000.0 m   OK I2    
    p.patchFloatAtAddress(0x4AE308 ,25.0)    #   Max speed (positive value) : default  15.0 m/s OK I2
    p.patchFloatAtAddress(0x4AE30C,-25.0)    #   Max speed (negative value) : default -15.0 m/s OK I2
    p.patchFloatAtAddress(0x4AE310,-5000.0)  #   Min altitude relative to home point : default -200.0 m OK I2
    p.patchFloatAtAddress(0x4AE314,9000.0)   #   Max altitude relative to home point : default 1000.0 m OK I2
    p.patchFloatAtAddress(0x4AE98C,25.0)     #   Max speed for in-flight change speed message : default 15.0 m/s OK I2

    ubxmonver = "B5620A0400000E34"    #   Original DJI UBX-MON-VER
    
    newubxframes = ubxmonver

    length_part1 = len(newubxframes)/2    # Move this line at the place you want to do replacement (UBX-MON-VER -> newubxframes part 1 / UBX-CFG-CFG ->  newubxframes part 2)

    # END OF REPLACING UBX-MON-VER BY OTHER SET OF FRAMES
    # BEGIN OF REPLACING UBX-CFG-CFG BY OTHER SET OF FRAMES
    
    #   New UBX-CFG-PMS : use GNSS chip at max power
    newubxframes = newubxframes + ubxcfggen.genUBXCFGPMS(0x0,0,0)
    # "B562068608000000000000000000945A"

    #   New UBX-CFG-GNSS frame :
    #useGPS=True,minGPS=8,maxGPS=16,
    #useGLO=True,minGLO=8,maxGLO=14,
    #useGAL=True,minGAL=8,maxGAL=10,
    #useSBAS=False,minSBAS=0,maxSBAS=2,
    #useBEIDOU=False,minBEIDOU=8,maxBEIDOU=16,
    #useQZSS=True,minQZSS=0,maxQZSS=3, (ublox recommands to always have QZSS & GPS together to avoir cross corelation issues)
    #useIMES=False,minIMES=0,maxIMES=8
    newubxframes = newubxframes + ubxcfggen.genUBXCFGGNSS(True,8,16,True,8,14,True,8,10,False,0,2,False,8,16,True,0,3,False,0,8)
    # "B562063E3C00002020070008100001000101010002000000010102080A000100010103081000000001010400080000000101050003000100010106080E0001000101536C"

    #   New UBX-CFG-NAV5 frame :
    #dynamicmodel=7 : airborne <2g,
    #fixmode=2 : 3D only,
    #utcStandard=0 : automatic,
    #horizonMask=5,minCN0=0,minSv=0,pDop=10.0,tDop=10.0,pAcc=30,tAcc=300,fixedAlt2D=0.0,fixedAltVar2D=1.0,staticHoldMaxSpeed=0,staticHoldMaxDist=0,dgnssTimeout=60
    newubxframes = newubxframes + ubxcfggen.genUBXCFGNAV5(7,2,0,5,0,0,10.0,10.0,30,300,0.0,1.0,0,0,60)
    # "B56206242400FFFF070200000000102700000500640064001E002C01003C000000000000000000000000E061"

    #   New UBX-CFG-SBAS frame :
    #enabled=False,allowtestmode=False,useintegrity=False,usediffcorr=False,userange=False,maxSBAS=0,prnList=[]
    newubxframes = newubxframes + ubxcfggen.genUBXCFGSBAS(False,False,False,False,False,0,[])
    # "B5620616080000010100000000002697"

    #   Original DJI UBX-CFG-CFG frame : save config in flash
    newubxframes = newubxframes + ubxcfggen.genUBXCFGCFG("SAVE_CURRENT")
    # "B56206090D0000000000FFFF000000000000031DAB"

    # END OF REPLACING UBX-CFG-CFG BY OTHER SET OF FRAMES
    
    total_length = len(newubxframes)/2
    length_part2 = total_length - length_part1

    # Checks
    if (length_part1 > 255 or length_part2 > 255):
        print("!!! ERROR : UBX Configuration Frames cannot exceed 255 bytes in length each !!!")
        print("!!! Remove some frames !!!")
        exit(1)

    unmodded_firmware_end = p.firmware_end
        
    #   Add extra data page(s) for the new Ublox config frames
    if (total_length > 255):
        p.addPageAtEndOfImage(256,2)
    else:
        p.addPageAtEndOfImage(256,1)

    #   Change the location of old UBX preforged frames to the new one
    p.patchAddressAtAddress(0x51EA10,unmodded_firmware_end)

    #   Write new UBX frames at beginning of new page
    p.patchDataAtAddress(unmodded_firmware_end,newubxframes)

	#	            ROM:0051E62E loc_51E62E                              ; DATA XREF: sub_51EDBA+C↓o
	#	            ROM:0051E62E                 LDR             R0, [R0,#8]
	# TO PATCH :	ROM:0051E630                 MOVS            R2, #8
	#	            ROM:0051E632                 LDR             R1, =dword_5699D0
	#	            ROM:0051E634                 B.W             sub_42A37C
	#	            ROM:0051E638 ; ---------------------------------------------------------------------------
	#	            ROM:0051E638                 LDR             R1, =dword_5699D0
	# TO PATCH :	ROM:0051E63A                 MOVS            R2, #0x15
	#	            ROM:0051E63C                 LDR             R0, [R0,#8]
	# TO PATCH :	ROM:0051E63E                 ADDS            R1, #8
	#	            ROM:0051E640                 B.W             sub_42A37C

    #   Patch the instructions that get the size of the frames to send,
    #   New UBX frames must stay below 255 bytes total
    #    Minimal checks performed

    p.patchByteAtAddress(0x51E630,length_part1)
    p.patchByteAtAddress(0x51E63A,length_part2)
    p.patchByteAtAddress(0x51E63E,length_part1)

    #    Disable QCchecking instructions about LLH / ECEF mismatch
    
    #p.patchDataAtAddress(0x51CDA0,nop) Mavic value not changed for I2 : do not use
    #p.patchDataAtAddress(0x51D258,nop) Mavic value not not changed for I2 : do not use
    #p.patchDataAtAddress(0x51D346,nop) Mavic value not not changed for I2 : do not use
    
    p.write(sys.argv[1]+".patched")
