#!/usr/bin/env python
#
#   By @Matioupi
#   provided under dbad licence http://dbad-license.org/
#
#   Version 1.1
#
#   Written from U-BLOX document UBX-13003221 - R14
#   plus some trials/checks with u-center 18.05.02
#
#   This class targets generating some UBLOX M8 config frames
#   for DJI Spark / Mavic Pro / P4 / P4P series
#
#   Revisions :
#   v1.0 :
#   supported frames :
#                                UBX-CFG-GNSS
#                                UBX-CFG-PMS
#                                UBX-CFG-NAV5
#                                UBX-CFG-DAT
#                                UBX-CFG-SBAS
#
#   v1.1 :
#   fixed GNSS constellations concurrent use conditions
#   added check to GAL min and max channels
#
#   changed default UBXCFGDAT to USER with WGS84 parameters
#   it seems that only way to revert to original "internal" WGS84 datum
#   is to issue a UBX-CFG-CFG clear/load command on the NAV section
#   there is no functionnal differences using "USER" with WGS84 parameters
#
#   Added support for frames :
#                                UBX-CFG-CFG
#

import binascii
import sys
import math
from struct import *

symbols = {}
    
class UBXCFGGEN:

    def __init__(self):
        print("Initializing UBXCFG Frames Generator")

    def addCRC(self, pre_built_frame):
        data=binascii.unhexlify(pre_built_frame)
        crc_a = 0
        crc_b = 0
        length_data=len(data)
        if length_data > 2:
            for k in range(2,length_data):
                crc_a += ord(data[k])
                crc_b += crc_a
        crc_a &= 0xff;
        crc_b &= 0xff;
        result = pre_built_frame
        result += ("%02x" % crc_a).upper()
        result += ("%02x" % crc_b).upper()

        return result

    def genUBXCFGDAT(self,name="USER",majA=6378137.0,flat=298.2572235630,dX=0.0,dY=0.0,dZ=0.0,rotX=0.0,rotY=0.0,rotZ=0.0,scale=0.0):
        temp="B5620606"
        if name=="USER":
            if (majA<6300000.0 or majA>6500000.0):
                print("Error genUBXCFGDAT : parameter majA (in m) must be in range 6300000.0 to 6500000.0")
                exit(1)
            if (flat<0.0 or flat>500.0):
                print("Error genUBXCFGDAT : parameter flat must be in range 0.0 to 500.0")
                exit(1)
            if (math.fabs(dX)>4000.0):
                print("Error genUBXCFGDAT : parameter dX (in m) must be in range -4000.0 to 4000.0")
                exit(1)
            if (math.fabs(dY)>4000.0):
                print("Error genUBXCFGDAT : parameter dY (in m) must be in range -4000.0 to 4000.0")
                exit(1)
            if (math.fabs(dZ)>4000.0):
                print("Error genUBXCFGDAT : parameter dZ (in m) must be in range -4000.0 to 4000.0")
                exit(1)
            if (math.fabs(rotX)>20.0):
                print("Error genUBXCFGDAT : parameter rotX (in arcsec) must be in range -20 to 20")
                exit(1)
            if (math.fabs(rotY)>20.0):
                print("Error genUBXCFGDAT : parameter rotY (in arcsec) must be in range -20 to 20")
                exit(1)
            if (math.fabs(rotZ)>20.0):
                print("Error genUBXCFGDAT : parameter rotZ (in arcsec) must be in range -20 to 20")
                exit(1)
            if (math.fabs(scale)>50.0):
                print("Error genUBXCFGDAT : parameter scale (in ppm) must be in range -50 to 50")
                exit(1)
            temp+="2C00"
            temp+=binascii.hexlify(pack('<d',majA)).upper()
            temp+=binascii.hexlify(pack('<d',flat)).upper()
            temp+=binascii.hexlify(pack('<f',dX)).upper()
            temp+=binascii.hexlify(pack('<f',dY)).upper()
            temp+=binascii.hexlify(pack('<f',dZ)).upper()
            temp+=binascii.hexlify(pack('<f',rotX)).upper()
            temp+=binascii.hexlify(pack('<f',rotY)).upper()
            temp+=binascii.hexlify(pack('<f',rotZ)).upper()
            temp+=binascii.hexlify(pack('<f',scale)).upper()
            return self.addCRC(temp)
        
        dat_array=["WGS84","WGS72","PZ90","ADI-M","ADI-E","ADI-F","ADI-A","ADI-C","ADI-D","ADI-B","AFG","ARF-M","ARF-A","ARF-H","ARF-B","ARF-C","ARF-D","ARF-E","ARF-F","ARF-G","ARS","PHA","BID","CAP","CGE","DAL","LEH","LIB","MAS","MER","MIN-A","MIN-B","MPO","NSD","OEG","PTB","PTN","SCK","VOR","AIN-A","AIN-B","BAT","HKD","HTN","IND-B","IND-I","INF-A","ING-A","ING-B","INH-A","IDN","KAN","KEA","NAH-A","NAH-B","NAH-C","FAH","QAT","SOA","TIL","TOY-M","TOY-A","TOY-C","TOY-B","AUA","AUG","EUR-M","EUR-A","EUR-E","EUR-F","EUR-G","EUR-K","EUR-B","EUR-H","EUR-I","EUR-J","EUR-L","EUR-C","EUR-D","EUR-T","EUS","HJO","IRL","OGB-M","OGB-A","OGB-B","OGB-C","OGB-D","MOD","SPK","CCD","CAC","NAS-C","NAS-B","NAS-A","NAS-D","NAS-V","NAS-W","NAS-Q","NAS-R","NAS-E","NAS-F","NAS-G","NAS-H","NAS-I","NAS-J","NAS-O","NAS-P","NAS-N","NAS-T","NAS-U","NAS-L","NAR-A","NAR-E","NAR-B","NAR-C","NAR-H","NAR-D","BOO","CAI","CHU","COA","PRP-M","PRP-A","PRP-B","PRP-C","PRP-D","PRP-E","PRP-F","PRP-G","PRP-H","HIT","SAN-M","SAN-A","SAN-B","SAN-C","SAN-D","SAN-E","SAN-F","SAN-J","SAN-G","SAN-H","SAN-I","SAN-K","SAN-L","ZAN","AIA","ASC","SHB","BER","DID","FOT","GRA","ISG","LCF","ASM","NAP","FLO","PLN","POS","PUR","QUO","SAO","SAP","SGM","TDC","ANO","GAA","IST","KEG","MIK","RUE","AMA","ATF","TRF","ASQ","IBE","CAO","CHI","GIZ","EAS","GEO","GUA","DOB","IDN","JOH","KUS","LUZ-A","LUZ-B","MID","OHA-M","OHA-A","OHA-B","OHA-C","OHA-D","PIT","SAE","MVS","ENW","WAK","BUR","CAZ","EUR-S","GSE","HEN","IND-P","PUK","TAN","YAC","KRA42","BLG50","RNB72","NTF","NL21","ED87","CH95","CGCS2"]
        if name in dat_array:
            print("Generating frame from datum name index : ")
            print("!!! Warning : this syntax is not actually understood by DJI M8 receivers !!!")
            print("!!! Warning : this frame will have no effect !!!")
            print("!!! use default USER values to revert to WGS84 equivalent !!!")
            print("!!! or use genUBXCFGCFG(\"REVERT_DEF_NAV\") to delete USER datum setting !!!")
            num=dat_array.index(name)
            temp+="0200"
            temp+=binascii.hexlify(pack('<h',num)).upper()
            return self.addCRC(temp)
 
        print("Datum name could not be found")

    #00 08 10 00 01000101 # GPS
    #01 02 02 00 00000101 # SBAS
    #02 08 0A 00 01000101 # GAL
    #03 08 10 00 00000101 # BEI
    #04 00 08 00 00000101 # IMES
    #05 00 03 00 01000101 # QZSS
    #06 08 0E 00 01000101 # GLO
    def genUBXCFGGNSS(self,useGPS=True,minGPS=8,maxGPS=16,useGLO=True,minGLO=8,maxGLO=14,useGAL=True,minGAL=8,maxGAL=10,useSBAS=False,minSBAS=0,maxSBAS=2,useBEIDOU=False,minBEIDOU=8,maxBEIDOU=16,useQZSS=True,minQZSS=0,maxQZSS=3,useIMES=False,minIMES=0,maxIMES=8):
        temp = "B562"
        temp += "063E"
        temp += "3C00"
        temp += "00" # msgVer
        temp += "20" # max Channels in Hw (actually read only)
        temp += "20" # max Channels used
        temp += "07" # 7 gnss system configured

        if (useGPS==True and useQZSS==False):
            print("Ublox recommands to activate QZSS if GPS is activated to avoid cross correlation issues")
            print("--> Activating QZSS with minQZSS=0 and maxQZSS=3")
            useQZSS=True
            minQZSS=0
            maxQZSS=3

        if (useGPS==True and minGPS < 4):
            print("Major GNSS constellation as GPS needs to have at least 4 reserved channels")
            print("--> setting minGPS to 4")
            minGPS=4        

        if (useGLO==True and minGLO < 4):
            print("Major GNSS constellation as GLONASS needs to have at least 4 reserved channels")
            print("--> setting minGLO to 4")
            minGLO=4   

        if (useGAL==True and minGAL < 4):
            print("Major GNSS constellation as GALILEO needs to have at least 4 reserved channels")
            print("--> setting minGAL to 4")
            minGAL=4
        
        if (useGAL==True and maxGAL > 10):
            print("GALILEO cannot use more than 10 channels")
            print("--> setting maxGAL to 4")
            maxGAL=10

        if (useGAL==True and minGAL > 10):
            print("GALILEO cannot use more than 10 channels")
            print("--> setting minGAL to 10")
            minGAL=10

        if (useBEIDOU==True and minBEIDOU < 4):
            print("Major GNSS constellation as BEIDOU needs to have at least 4 reserved channels")
            print("--> setting minBEIDOU to 4")
            minBEIDOU=4   

        if (useBEIDOU==True and useGLO==True):
            print("BEIDOU cannot be used concurrently with GLONASS")
            print("--> disabling BEIDOU")
            useBEIDOU=False
            minBEIDOU=8
            maxBEIDOU=16

        totalRes=0

        for gnssId in range(0,7):
            useFlag=False
            resCh=0            
            maxCh=0
            if (gnssId==0):
                useFlag=useGPS
                resCh=minGPS           
                maxCh=maxGPS
            elif (gnssId==1):
                useFlag=useSBAS
                resCh=minSBAS        
                maxCh=maxSBAS
            elif (gnssId==2):
                useFlag=useGAL
                resCh=minGAL       
                maxCh=maxGAL
            elif (gnssId==3):
                useFlag=useBEIDOU
                resCh=minBEIDOU    
                maxCh=maxBEIDOU
            elif (gnssId==4):
                useFlag=useIMES
                resCh=minIMES      
                maxCh=maxIMES
            elif (gnssId==5):
                useFlag=useQZSS
                resCh=minQZSS      
                maxCh=maxQZSS
            elif (gnssId==6):
                useFlag=useGLO
                resCh=minGLO       
                maxCh=maxGLO

            temp += binascii.hexlify(pack('<b',gnssId)).upper()
            temp += binascii.hexlify(pack('<b',resCh)).upper()
            temp += binascii.hexlify(pack('<b',maxCh)).upper()
            temp += "00"
            if (useFlag == False):
                temp += "00"
            else:
                temp += "01"
                totalRes += resCh
                if (totalRes > 32):
                    print("Total reserved channels cannot be above 32")
                    exit(1)
            temp += "000101"

        return self.addCRC(temp)

    #0x00 -> Full power
    #0x01 -> Balanced
    #0x02 -> Interval
    #0x03 -> Aggressive with 1Hz
    #0x04 -> Aggressive with 2Hz
    #0x05 -> Aggressive with 4Hz
    #0xFF -> Invalid (only when polling)
    def genUBXCFGPMS(self,powermode=0x00,period=0,ontime=0):
        temp = "B562"
        temp += "0686"
        temp += "0800"
        temp += "00" # version
        if (powermode != 0x02):
            period = 0
            ontime = 0
        elif (period<ontime):
            printf("onTime must be smaller than period")
            exit(1)
        temp += binascii.hexlify(pack('<b',powermode)).upper()
        temp += binascii.hexlify(pack('<h',period)).upper()
        temp += binascii.hexlify(pack('<h',ontime)).upper()
        temp += "0000" # reserved
        return self.addCRC(temp)

    #Dynamic platform model:
    #0: portable
    #2: stationary
    #3: pedestrian
    #4: automotive
    #5: sea
    #6: airborne with <1g acceleration
    #7: airborne with <2g acceleration
    #8: airborne with <4g acceleration
    #9: wrist worn watch

    #Position Fixing Mode:
    #1: 2D only
    #2: 3D only
    #3: auto 2D/3D

    #UTC standard to be used:
    #0: Automatic; receiver selects based on GNSS configuration (see GNSS time bases).
    #3: UTC as operated by the U.S. Naval Observatory (USNO); derived from GPS time
    #6: UTC as operated by the former Soviet Union; derived from GLONASS time
    #7: UTC as operated by the National Time Service Center, China; derived from BeiDou time

    def genUBXCFGNAV5(self,dynamicmodel=7,fixmode=2,utcStandard=0,horizonMask=5,minCN0=0,minSv=0,pDop=10.0,tDop=10.0,pAcc=30,tAcc=300,fixedAlt2D=0.0,fixedAltVar2D=1.0,staticHoldMaxSpeed=0,staticHoldMaxDist=0,dgnssTimeout=60):
        temp = "B562"
        temp += "0624"
        temp += "2400"
        temp += "FFFF" # bitmask
        temp += binascii.hexlify(pack('<b',dynamicmodel)).upper()
        temp += binascii.hexlify(pack('<b',fixmode)).upper()
        temp += binascii.hexlify(pack('<i',int(fixedAlt2D*100.0))).upper()
        temp += binascii.hexlify(pack('<I',int(fixedAltVar2D*10000.0))).upper()
        temp += binascii.hexlify(pack('<b',horizonMask)).upper()
        temp += "00" # dr limit
        temp += binascii.hexlify(pack('<h',int(pDop*10.0))).upper()
        temp += binascii.hexlify(pack('<h',int(tDop*10.0))).upper()
        temp += binascii.hexlify(pack('<h',pAcc)).upper()
        temp += binascii.hexlify(pack('<h',tAcc)).upper()
        temp += binascii.hexlify(pack('<b',staticHoldMaxSpeed)).upper()
        temp += binascii.hexlify(pack('<b',dgnssTimeout)).upper()
        temp += binascii.hexlify(pack('<b',minSv)).upper()
        temp += binascii.hexlify(pack('<b',minCN0)).upper()
        temp += "0000" # reserved
        temp += binascii.hexlify(pack('<h',staticHoldMaxDist)).upper()
        temp += binascii.hexlify(pack('<b',utcStandard)).upper()
        temp += "0000000000" # reserved
        return self.addCRC(temp)

    def genUBXCFGSBAS(self,enabled=False,allowtestmode=False,useintegrity=False,usediffcorr=False,userange=False,maxSBAS=0,prnList=[]):
        temp = "B562"
        temp += "0616"
        temp += "0800"
        mode = 0
        usage = 0
        if (enabled==True):
            mode |= 0x01
        if (allowtestmode==True):
            mode |= 0x02
        if (userange==True):
            usage |= 0x01
        if (usediffcorr==True):
            usage |= 0x02
        if (useintegrity==True):
            usage |= 0x04
        temp += binascii.hexlify(pack('<b',mode)).upper()
        temp += binascii.hexlify(pack('<b',usage)).upper()
        temp += binascii.hexlify(pack('<b',maxSBAS)).upper()

        scanmode1 = 0
        scanmode2 = 0

        for prn in range(120,159):
             if (prn in prnList):
                 bitn = prn-120
                 if (bitn <= 31):
                     scanmode1 |= (1 << bitn)
                 else:
                     scanmode2 |= (1 << (bitn-32))
        temp += binascii.hexlify(pack('<B',scanmode2)).upper()
        temp += binascii.hexlify(pack('<I',scanmode1)).upper()        
                    
        return self.addCRC(temp)

    def genUBXCFGCFG(self,action="SAVE_CURRENT",targetDevices=["BBR","FLASH"],clearSection=[],saveSection=[],loadSection=[]):
        combo_array=["NONE","REV_LAST_SAVED","REV_TO_DEFAULT_BUT_ANT","REV_TO_DEFAULT","SAVE_CURRENT","REVERT_DEF_NAV"]
        device_array=["BBR","FLASH","I2C-EEPROM","unused","SPI-FLASH"]
        section_array=["IO","MSG","INF","NAV","RXM","unused1","unused2","unused3","SEN","RINV","ANT","LOG","FTS","unused4","unused5","unused6"]
        
        if (action=="SAVE_CURRENT"):
            clearSection=[]
            saveSection=section_array
            loadSection=[]
        elif (action=="REV_LAST_SAVED"):
            clearSection=[]
            saveSection=[]
            loadSection=section_array
        elif (action=="REV_TO_DEFAULT_BUT_ANT"):
            clearSection=["IO","MSG","INF","NAV","RXM","unused1","unused2","unused3","SEN","RINV","LOG","FTS","unused4","unused5","unused6"]
            saveSection=[]
            loadSection=section_array
        elif (action=="REV_TO_DEFAULT"):
            clearSection=section_array
            saveSection=[]
            loadSection=section_array
        elif (action=="REVERT_DEF_NAV"):
            clearSection=["NAV"]
            saveSection=[]
            loadSection=["NAV"]

        deviceMask=0
        clearMask=0
        saveMask=0
        loadMask=0

        for elem in targetDevices:
            bitn = device_array.index(elem)
            deviceMask |= (1 << bitn)

        for elem in clearSection:
            bitn = section_array.index(elem)
            clearMask |= (1 << bitn)

        for elem in saveSection:
            bitn = section_array.index(elem)
            saveMask |= (1 << bitn)

        for elem in loadSection:
            bitn = section_array.index(elem)
            loadMask |= (1 << bitn)

        temp = "B562"
        temp += "0609"
        temp += "0D00"
        temp += binascii.hexlify(pack('<I',clearMask)).upper()
        temp += binascii.hexlify(pack('<I',saveMask)).upper()
        temp += binascii.hexlify(pack('<I',loadMask)).upper()
        temp += binascii.hexlify(pack('<b',deviceMask)).upper()

        return self.addCRC(temp)
