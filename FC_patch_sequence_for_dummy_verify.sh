#!/bin/bash
#
#   By @Matioupi
#   provided under dbad licence http://dbad-license.org/
#
#   Version 1.0
#
#   Made possible thanks to all OG's work and especially ideas from @jan2642 and
#   patience of @jezzab in explaining me some stuff
#
#
#   RTFM before asking for support
#


#   Modify the following variable to point to your install of
#   Mefisto firmware tools https://github.com/o-gs/dji-firmware-tools

if [[ -z "${PATH_TO_TOOLS}" ]]; then
  echo "Define PATH_TO_TOOLS variable to use this script! eg:"
  echo "PATH_TO_TOOLS=/tmp/tools/ ./FC_patch_sequence_for_dummy_verify.sh"
  exit 1
fi

if [ "$#" -eq 2 ]; then
    VERSION="$2"
else
    echo "################################################################################"
    echo "  FC_patch_sequence_for_dummy_verify.sh 1.0 by @Matioupi"
    echo "  usage :"
    echo "          FC_patch_sequence_for_dummy_verify.sh birdname aa.bb.cc.dd"
    echo "          birdname is one of Spark, Mavic, P4P, P4std, P4adv, I2"
    echo "          aa.bb.cc.dd is the new FC 0306 module version number"
    echo ""
    echo "  exemple : ./FC_patch_sequence_for_dummy_verify.sh Spark 03.02.43.21"
    echo "  exemple : ./FC_patch_sequence_for_dummy_verify.sh Mavic 03.02.44.08"
    echo "  exemple : ./FC_patch_sequence_for_dummy_verify.sh P4P 03.02.44.08"
    echo "  exemple : ./FC_patch_sequence_for_dummy_verify.sh P4std 03.02.44.08"
    echo "  exemple : ./FC_patch_sequence_for_dummy_verify.sh P4adv 03.02.35.06"
    echo "  exemple : ./FC_patch_sequence_for_dummy_verify.sh I2 03.03.10.10"
    echo "  exemple : ./FC_patch_sequence_for_dummy_verify.sh P4PV2 03.03.04.14"
    echo "################################################################################"
    exit 0
fi

MODULE=0306

if [ "$1" == "Mavic" ]
then
    #   Mavic Pro 
    AC_PREFIX=wm220
    FULL_ORIGINAL_FIRMWARE_VERSION="v01.04.0300"
    ORI_VERSION="03.02.44.07"
    ORI_FILEDATE=20171116
    ORI_MODULE_TIMESTAMP="2017-11-16 10:30:27"
    #escape the / from <\module> after copy/pasting the original data here
    ORI_MODULE_INFO='<module id="0306" version="03.02.44.07" type="" group="ac" size="1484064" md5="cd6bb6a75a38d4933315dafc2007c49c">wm220_0306_v03.02.44.07_20171116.pro.fw.sig<\/module>'
elif [ "$1" == "Spark" ]
then
   #   Spark
   AC_PREFIX=wm100
   FULL_ORIGINAL_FIRMWARE_VERSION="v01.00.0900"
   ORI_VERSION="03.02.43.20"
   ORI_FILEDATE=20170920
   ORI_MODULE_TIMESTAMP="2017-09-20 22:05:01"
   #escape the / from <\module> after copy/pasting the original data here
   ORI_MODULE_INFO='<module id="0306" version="03.02.43.20" type="" group="ac" size="1493792" md5="bb7d7c31f49616565e19c50663d7d2ba">wm100_0306_v03.02.43.20_20170920.pro.fw.sig<\/module>'
elif [ "$1" == "P4P" ]
then
   #   P4P = Phantom 4 Pro
   AC_PREFIX=wm331
   FULL_ORIGINAL_FIRMWARE_VERSION="v01.05.0600"
   ORI_VERSION="03.02.44.07"
   ORI_FILEDATE=20171116
   ORI_MODULE_TIMESTAMP="2017-11-16 10:38:19"
   #escape the / from <\module> after copy/pasting the original data here
   ORI_MODULE_INFO='<module id="0306" version="03.02.44.07" type="" group="" size="1505056" md5="0e64692bc4911c3a3a27ce937318da1a">wm331_0306_v03.02.44.07_20171116.pro.fw.sig<\/module>'
elif [ "$1" == "P4std" ]
then
   #   P4P = Phantom 4 Standard
   AC_PREFIX=wm330
   FULL_ORIGINAL_FIRMWARE_VERSION="v02.00.0700"
   ORI_VERSION="03.02.44.07"
   ORI_FILEDATE=20171116
   ORI_MODULE_TIMESTAMP="2017-11-16 10:32:06"
   #escape the / from <\module> after copy/pasting the original data here
   ORI_MODULE_INFO='<module id="0306" version="03.02.44.07" type="" group="" size="1504800" md5="b146c251760f3a32208d06cbc931ae8f">wm330_0306_v03.02.44.07_20171116.pro.fw.sig<\/module>'
elif [ "$1" == "P4adv" ]
then
   #   P4P = Phantom 4 Advanced
   AC_PREFIX=wm332
   FULL_ORIGINAL_FIRMWARE_VERSION="v01.00.0128"
   ORI_VERSION="03.02.35.05"
   ORI_FILEDATE=20170525
   ORI_MODULE_TIMESTAMP="2017-05-25 22:08:15"
   #escape the / from <\module> after copy/pasting the original data here
   ORI_MODULE_INFO='<module id="0306" version="03.02.35.05" type="" group="" size="1560864" md5="a4cea467d134f9c26f4dba76a0984fe2">wm332_0306_v03.02.35.05_20170525.pro.fw.sig<\/module>'
elif [ "$1" == "I2" ]
then
   #   I2 = Inspire2
   AC_PREFIX=wm620
   FULL_ORIGINAL_FIRMWARE_VERSION="v01.02.0200"
   ORI_VERSION="03.03.09.09"
   ORI_FILEDATE=20180704
   ORI_MODULE_TIMESTAMP="2018-07-04 19:05:21"
   #escape the / from <\module> after copy/pasting the original data here
   ORI_MODULE_INFO='<module id="0306" version="03.03.09.09" type="" group="" size="1463072" md5="a71c9b796c9f9877ae28dabc448b4394">wm620_0306_v03.03.09.09_20180704.pro.fw.sig<\/module>'
elif [ "$1" == "P4PV2" ]
then
   #   P4PV2 = Phantom 4 Pro/Pro+ V2
   AC_PREFIX=wm335
   FULL_ORIGINAL_FIRMWARE_VERSION="v01.00.1500"
   ORI_VERSION="03.03.04.13"
   ORI_FILEDATE=20180525
   ORI_MODULE_TIMESTAMP="2018-05-25 15:27:34"
   #escape the / from <\module> after copy/pasting the original data here
   ORI_MODULE_INFO='<module id="0306" version="03.03.04.13" type="" group="ac" size="1437728" md5="4d60509ca1a7565766d425372b262eab">wm335_0306_v03.03.04.13_20180525.pro.fw.sig<\/module>'
fi

VERSIONSTR="v$VERSION"

ORI_FILENAME="$AC_PREFIX"_"$MODULE"_v"$ORI_VERSION"_"$ORI_FILEDATE".pro.fw_"$MODULE".decrypted.bin
DST_FILENAME_BASE="$AC_PREFIX"_"$MODULE"_v"$VERSION"_"$ORI_FILEDATE".pro.fw
TMP_FILENAME0="$DST_FILENAME_BASE"_"$MODULE".decrypted.bin
TMP_FILENAME1=tmp_"$TMP_FILENAME0"
TMP_ENCRYPTED="$DST_FILENAME_BASE"_"$MODULE".decrypted.encrypted.bin
DST_FILENAME="$DST_FILENAME_BASE".sig

cp $ORI_FILENAME $TMP_FILENAME1

echo "################################################################################"
echo "                       Updating flight parameters"
echo "################################################################################"

"$PATH_TO_TOOLS"/dji-firmware-tools/dji_flyc_param_ed.py -vv -u -b 0x420000 -m $TMP_FILENAME1

if [ $? != 0 ]
then
    echo "#### Issue while updating flight parameters ####"
    exit 1
else
    echo "#### Success updating flight paramters ####"
fi

echo "################################################################################"
echo "               Patching flight parameters hardcoded values"
echo "               Adding U-Blox custom configuration"
echo "################################################################################"

# call it using python version 2
python2 "$PATH_TO_TOOLS"/DJI_FC_Patcher/patch_"$AC_PREFIX"_"$MODULE".py $TMP_FILENAME1 $VERSION
if [ $? != 0 ]
then
    echo "#### Issue while patching module ####"
    exit 1
else
    echo "#### Success patching module ####"
fi

mv $TMP_FILENAME1.patched "$DST_FILENAME"

echo "################################################################################"
echo "                       Modifying $AC_PREFIX.cfg"
echo "################################################################################"

md5=`md5sum $DST_FILENAME | awk '{ print $1 }'`
size="$(wc -c < $DST_FILENAME)"

INDEX_FILE="$AC_PREFIX".cfg
if [ "$AC_PREFIX" == "wm100" ]
then
    INDEX_FILE="$AC_PREFIX"a.cfg
fi

cp "$INDEX_FILE".ori "$INDEX_FILE"

NEW_MODULE_INFO='<module id="'$MODULE'" version="'$VERSION'" type="" group="ac" size="'$size'" md5="'$md5'">'$DST_FILENAME'<\/module>'

sed -i "s/${ORI_MODULE_INFO}/${NEW_MODULE_INFO}/g" $INDEX_FILE
if [ $? != 0 ]
then
    echo "#### Issue while modifying $INDEX_FILE ####"
    exit 1
else
    echo "#### Success modifying $INDEX_FILE ####"
fi

fake_header=""
for i in {1..480}
do
    fake_header="$fake_header"" "
done

printf "$fake_header" | cat - "$INDEX_FILE" > temp_"$INDEX_FILE" && mv temp_"$INDEX_FILE" "$INDEX_FILE".sig

echo "################################################################################"
echo " Preparing tar file dji_system_"$AC_PREFIX"_"$MODULE"_"$VERSION"_dummy_verify.bin"
echo "################################################################################"
rm dji_system_"$AC_PREFIX"_"$MODULE"_"$VERSION"_dummy_verify.bin &> /dev/null  # this clean was confusing
tar -cvf dji_system_"$AC_PREFIX"_"$MODULE"_"$VERSION"_dummy_verify.bin *.sig
if [ $? != 0 ]
then
    echo "#### Issue while preparing tar file dji_system_"$AC_PREFIX"_"$MODULE"_"$VERSION"_dummy_verify.bin ####"
    exit 1
else
   echo "#### Success preparing tar file dji_system_"$AC_PREFIX"_"$MODULE"_"$VERSION"_dummy_verify.bin ####"
fi
echo "################################################################################"
echo "  The file dji_system_"$AC_PREFIX"_"$MODULE"_"$VERSION"_dummy_verify.bin"
echo "  is prepared to be flashed with dummy_verify mount bind technique"
echo "################################################################################"
