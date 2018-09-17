Custom FC patcher and flashing method for DJI Spark, Mavic Pro / Pro Platinum, Phantom 4 / 4 Pro / 4 Adv, I2
============================================================================================================

by @Matioupi (mathieu.peyrega@gmail.com), credits to all OG's for their work and ideas

This document and the attached scripts provides a method for patching / modding the
FC (flight controller, a.k.a. 0306 module) on following DJI birds :
 
* DJI Spark
* DJI Mavic Pro series (incl. Platinium)
* DJI Phantom 4
* DJI Phantom 4 Pro
* DJI Phantom 4 advanced
* DJI Inspire 2
* DJI Phantom 4 Pro/Pro+ V2

at this point of first release, it works ONLY with the following firmware versions (which are pretty much the latest ones)
 
* 1.00.0900 for DJI Spark (there is a 1.00.1000 fw which does not bring any new FC feature)
* 1.04.0300 for DJI Mavic Pro (there is a 1.04.0400 fw which does not bring any new FC feature)
* 1.05.0600 for DJI Phantom 4 Pro
* 2.00.0700 for DJI Phantom 4 standard
* 1.00.0128 for DJI Phantom 4 advanced
* 1.02.0200 for DJI Inspire 2
* 1.00.1500 for DJI Phantom 4 Pro/Pro+ V2

modder for Spark, Mavic Pro series, P4P are fully tested. Other birds are untested at this point, waiting for volunteers...
Those untested birds include : I2, P4std, P4 standard, P4P V2

Some features that may require app side support will not work on P4PV2

The patcher allows you to tune :

- all flight parameters including the hidden ones (NFZ, alt limit,...)
- plus some hard-coded parameters inside FC
- plus add some new features such as Galileo satellites reception

Galileo mod also requires an App side patch which is only available though NLD at time.

edit : from discussions here : https://github.com/o-gs/DJI_FC_Patcher/issues/3

it seems that with constellation status as of 27th august 2018, the FC patch by itself is enough to get the Galileo reception working. This is expected behaviour by a GNSS receiver and previous status where the ephemerids needed a first manual load as described at step 15 seems not to be mandatory anymore. So step 15 of this guide maybe optionnal and you still have Galileo enabled.

If you flash a custom FC, it is still possible to rollback to a 100% stock FC by reflashing the full stock firmware. All DJI bird firmwares do not explicitly set the GNSS settings, so GNSS settings may stick even after a rollback to official firmware.

Don't use the modded FC to do stupid things !

All in one script
--------------
_I have not tested it myself but it's been reported to work -- @Matioupi_

@lenisko contributed an "all in one" easy version script: `run_me.py`. Download script and run it with `--help`.
```
wget https://raw.githubusercontent.com/o-gs/DJI_FC_Patcher/master/run_me.py && python3 run_me.py --help
```
Before starting, ensure that you have installed `python2` and `python3` along with `pycrypto` python module (all of those are needed anyway for patch process).

__Script can't be used directly from Windows ! and wasn't tested on Mac OS.__

##### Example usage for Mavic Pro using Windows Subsystem for Linux on Windows 10
```
python3 run_me.py wm220 /mnt/q/V01.04.0300_Mavic_dji_system.bin
```
Script will guide you through process of patching FC.
First argument is model which is described in script `--help`, second is full unix path to firmware file.
In steps **#2** and **#5** you'll be asked to use `adb`, you have to switch to `cmd` navigate to provided path _(do linux->windows path convertion yourself ;-)_ and execute printed commands.

##### Usage for Mavic Pro using Windows and Linux separately
Basically same as using WSL, but instead `cmd` on same computer, you have to run adb commands on Windows OS and move needed files between Linux <-> Windows to provided paths:
 - for **#2** step: pulled `0306.unsig` from Windows to Linux,
 - for **#5** step: `dummy_verify.sh` and `dji_system_wm220_0306_03.02.44.08_dummy_verify.bin` from Linux to Windows to continue `adb` and flashing process.

Pre-requisites
--------------

* Understanding what you do and understanding that you might brick your bird if you don't respect steps and even if you do (who knows...)
* Acknowledging and accepting all the risks and consequences of trying what is described in this document and acknowledging that you can't blame anybody if something goes wrong during or after the mod.
* Being able to use adb and basic command line tools on Linux systems
* Being able to clone/install a git repo from github
* Understand and do yourself all small mods such as changing a path for calling a command given in this doc to the actual place you installed it on your setup
* Being able to install any linux missing package/tool that might be needed for the operations
* Having a recent install of @Mefisto firmware tools :
https://github.com/o-gs/dji-firmware-tools
(runs on Linux)

* Having a recent install of @freaky123 dji_rev
https://github.com/fvantienen/dji_rev

* Having a copy of the original firmware file you will be using (1.00.0900 for Spark or 1.04.0300 for Mavic Pro or 1.05.0600 for P4P etc.)
They can be obtained from here :
https://github.com/cs2000/DankDroneDownloader
(runs on Windows)

* Having a rooted bird, you can use 
https://github.com/CunningLogic/DUMLRacer
https://github.com/CunningLogic/UberSploits
or there is even a one click button on the latest DUMLDore v3 version (first 2 will not work for P4P, only Spark and Mavic)

* Being able to use @jezzab DUMLDore v3 : https://github.com/jezzab/DUMLdore/releases

As you already understand, part of the job has to be done on a Windows machine (flashing) and part of the job under a Linux machine (FC file preparation).
It has not been tested what works and don't works if you try using WSL for example. Working with WSL is at your own risks.

Step by step
------------

#### 1. Retrieve encrypted versions of the FC modules and configuration file from the full firmware file

The 0306 modules inside the full firmware files are under an encrypted&signed form.
You will need to retrieve a copy of the file under unencrypted form before being able to mod it (and later reflash)
First let's get the encrypted versions of the files we need

untar your full firmware file :

`tar -xvf ./V01.00.0900_Spark_dji_system.bin`
or
`tar -xvf ./V01.04.0300_Mavic_dji_system.bin`
or
`tar -xvf ./V01.05.0600_P4P_dji_system.bin`

depending on your bird

You will get a bunch of .pro.fw.sig files (for each part of the system) plus a configuration file : wm100a.cfg.sig (Spark) or wm220.cfg.sig (Mavic) or wm331.cfg.sig (P4P) files

Amongst those, only 3 files will be usefull :
1. the one with 0305 in name (Flight controller loader) : there is no 0305 module for this P4P fw version
2. the one with 0306 in name (Flight controller)
3. the .cfg.sig file (wm100a / wm220 / wm331)

Just copy those 3 files in a separate working directory to avoid being cluttered by too many files

For check purposes, here are the md5 hash of the files you should start with :
(Files with their md5 hash for Spark)
```
ae7b12a944e67add75cd2c4d3d24624d  wm100_0305_v34.11.00.21_20161010.pro.fw.sig
bb7d7c31f49616565e19c50663d7d2ba  wm100_0306_v03.02.43.20_20170920.pro.fw.sig
14c0345504d9e9726521a2e533d22bea  wm100a.cfg.sig
```

(Files with their md5 hash for Mavic)
```
fcde0f3bc310c78e5c13f1e2239e185e  wm220_0305_v34.04.00.24_20170726.pro.fw.sig
cd6bb6a75a38d4933315dafc2007c49c  wm220_0306_v03.02.44.07_20171116.pro.fw.sig
7a3a98bef2446f33d021e26b64100f99  wm220.cfg.sig
```

(Files with their md5 hash for P4P) : there is no 0305 module for this P4P fw version
```
0e64692bc4911c3a3a27ce937318da1a  wm331_0306_v03.02.44.07_20171116.pro.fw.sig
95881f4318c105ea9a726837ee02f5db  wm331.cfg.sig
```

(Files with their md5 hash for P4std) : there is no 0305 module for this P4std fw version
```
b146c251760f3a32208d06cbc931ae8f  wm330_0306_v03.02.44.07_20171116.pro.fw.sig
f69c909388572a5f58d06546663e0ab9  wm330.cfg.sig
```

(Files with their md5 hash for P4adv) : there is no 0305 module for this P4adv fw version
```
a4cea467d134f9c26f4dba76a0984fe2  wm332_0306_v03.02.35.05_20170525.pro.fw.sig
7500dd1c92a9f2065814ff4cb004ee92  wm332.cfg.sig
```

(Files with their md5 hash for I2) : there is no 0305 module for this I2 fw version
```
a71c9b796c9f9877ae28dabc448b4394  wm620_0306_v03.03.09.09_20180704.pro.fw.sig
617a47c2d92264a15b72b37fe2e35742  wm620.cfg.sig
```

(Files with their md5 hash for P4PV2) : there is no 0305 module for this P4PV2 fw version
```
4d60509ca1a7565766d425372b262eab  wm335_0306_v03.03.04.13_20180525.pro.fw.sig
d91a50134a89cf8f4fb89bf7d98b476b  wm335.cfg.sig
```

#### 2. Extract / unsig the .cfg file

the .cfg file matching the .cfg.sig file can be retrieved with the image.py script from dji_rev :
(you may need to change the full path to dji_rev/tools/image.py from the command lines given here)

```
./dji_rev/tools/image.py wm220.cfg.sig
mv wm220.cfg_0000.bin wm220.cfg.ori
```

or

```
./dji_rev/tools/image.py wm100a.cfg.sig
mv wm100a.cfg_0000.bin wm100a.cfg.ori
```

or

```
./dji_rev/tools/image.py wm331.cfg.sig
mv wm331.cfg_0000.bin wm331.cfg.ori
```

the result file should have the following md5 hash :
```
3acb256304aaf5239814207da7d94cad  wm100a.cfg.ori (Spark)
f0b9aff5199745ff0eab4d189d9f562a  wm220.cfg.ori (Mavic)
4a8dc7297c4bb093568ea79df7ec5073  wm331.cfg.ori (P4P)
724073ca4fb2e920c7a76995d243853f  wm330.cfg.ori (P4std)
966708d12656ac0a8144881f2b319a79  wm332.cfg.ori (P4adv)
57ca69564cc379e5d3a5ab5eb6112421  wm620.cfg.ori (I2)
5d4e2679a8b9f20c2efa3ee53695ad35  wm335.cfg.ori (P4PV2)
```

#### 3. Copy the 0305 file next to the .cfg.ori file without modifying it in anyway (no need to decrypt unsig or whatever)

#### 4. Unsig the 0306 file : First step involving some actions on the bird

adb to your bird :
`adb shell`

make the /vendor partition read-write :
`mount -o remount,rw /vendor`

create the /vendor/bin directory which might not exist yet :
`mkdir /vendor/bin`

exit the adb shell :
`exit`

push the 0306 file to /vendor/bin :
`adb push wm100_0306_v03.02.43.20_20170920.pro.fw.sig /vendor/bin/`
or
`adb push wm220_0306_v03.02.44.07_20171116.pro.fw.sig /vendor/bin/`
or
`adb push wm331_0306_v03.02.44.07_20171116.pro.fw.sig /vendor/bin/`

return to adb shell and move to /vendor/bin/ :
```
adb shell
cd /vendor/bin/
```

use the dji_verify DJI binary (it lives in /sbin/ for Mavic and Spark and in /system/bin/ for P4P, adjust command according to actual dji_verify binary location) to do the nasty crypto job for you :

`/sbin/dji_verify -n 0306 -o 0306.unsig wm100_0306_v03.02.43.20_20170920.pro.fw.sig`
or
`/sbin/dji_verify -n 0306 -o 0306.unsig wm220_0306_v03.02.44.07_20171116.pro.fw.sig`
or
`/system/bin/dji_verify -n 0306 -o 0306.unsig wm331_0306_v03.02.44.07_20171116.pro.fw.sig`

at this stage exit the adb shell and pull the file you've been generating :
```
exit
adb pull /vendor/bin/0306.unsig
```
save it for the future...

return to shell to do housekeeping :
```
adb shell
cd /vendor/bin/
rm 0306.unsig
rm *.fw.sig
cd /
sync
mount -o remount,ro /vendor
```

(you may get an error after sync, which you can ignore)
Then turn off your bird, you wont need it for a while

You can check the pulled out file :

```
fb9d4f10163a11d6b13fe510aa79b731  0306.unsig (Spark)
7d030a568bd337c4fe575626fd7a2862  0306.unsig (Mavic Pro)
80d6dda3b107285872c30d93354d7384  0306.unsig (P4P)
f85ea3ffd0b505899e021c8463819a2d  0306.unsig (P4std)
41ce28fc3732fa87d391b4c7d4b0dd98  0306.unsig (P4adv)
dd9d1463c5cf3a940b15adce64e29fcc  0306.unsig (I2)
7fc44b010aa3eddb86a6252f6092443c  0306.unsig (P4PV2)
```

At this stage you have unsigged the files but they are still encrypted.
Let's go decrypting them

This step needs to be carried while bird is on the actual 1.00.0900 / 1.04.0300 / 1.05.0600 firmware so you might
need to reflash a stock firmware with DUMLDore v3 before doing this step 4.

#### 5. Use mefisto / @jan2642 tool to decrypt the FC

`./dji-firmware-tools/dji_mvfc_fwpak.py dec -i 0306.unsig`

`mv 0306.decrypted.bin wm100_0306_v03.02.43.20_20170920.pro.fw_0306.decrypted.bin`
or
`mv 0306.decrypted.bin wm220_0306_v03.02.44.07_20171116.pro.fw_0306.decrypted.bin`
or
`mv 0306.decrypted.bin wm331_0306_v03.02.44.07_20171116.pro.fw_0306.decrypted.bin`

Result file md5 hashes that you should get :

```
aaeb606a4a86fb1fc9a0f6bc6314d3a4  wm100_0306_v03.02.43.20_20170920.pro.fw_0306.decrypted.bin (Spark)
03ca7a87993ae824dac37345e187fab8  wm220_0306_v03.02.44.07_20171116.pro.fw_0306.decrypted.bin (Mavic)
1ce9b3049390b77d7941cabcc312106e  wm331_0306_v03.02.44.07_20171116.pro.fw_0306.decrypted.bin (P4P)
bfc89ec4225a3a7f168cb6056f8b0754  wm330_0306_v03.02.44.07_20171116.pro.fw_0306.decrypted.bin (P4std)
5a9297e4a9d56eb36beb7c8f8e93bd94  wm332_0306_v03.02.35.05_20170525.pro.fw_0306.decrypted.bin (P4adv)
e614205e1c868cd766727ac44aef2cc2  wm620_0306_v03.03.09.09_20180704.pro.fw_0306.decrypted.bin (I2)
2c711646e9fe163fbc647e39ed513d13  wm335_0306_v03.03.04.13_20180525.pro.fw_0306.decrypted.bin (P4PV2)
```

At this stage, you have a decrypted version of the 0306 flight controller module. You can check the binary file
with some binary editor (e.g. 010 Editor) and should be able to spot some human readable strings inside

#### 6. Extract flight controller parameters

`./dji-firmware-tools/dji_flyc_param_ed.py -vv -x -b 0x420000 -m wm100_0306_v03.02.43.20_20170920.pro.fw_0306.decrypted.bin`
or
`./dji-firmware-tools/dji_flyc_param_ed.py -vv -x -b 0x420000 -m wm220_0306_v03.02.44.07_20171116.pro.fw_0306.decrypted.bin`
or
`./dji-firmware-tools/dji_flyc_param_ed.py -vv -x -b 0x420000 -m wm331_0306_v03.02.44.07_20171116.pro.fw_0306.decrypted.bin`

This will generate a flyc_param_infos file with all the flight parameters that you are able to modify.
The . is sometimes changed by _ compared to how variables were named in the DJI Assistant interface but it's the same things

#### 7. Mod you flyc_param_infos with a text file

Same old recipies as the ones from module mixing times... tune your max tilt, etc to get the bird flavor you like to have
There are plenty of excellent guides online :

https://www.rcgroups.com/forums/showthread.php?2916078-DJI-Dashboard-How-To-tips-and-tricks-*MAVIC*
https://www.rcgroups.com/forums/showthread.php?3058818-Rooting-Mavic-Pro-in-Latest-firmware-with-Force-FCC-and-Boost-and-No-NFZ
https://dji.retroroms.info/howto/parameterindex

#### 8. Setup the file to build the flashable image

Copy in a directory :

* the modified flyc_param_infos file
* the 0306 : wm[...].pro.fw_0306.decrypted.bin file
* the 0305 file as you got it after untarring
* the .cfg.ori file you got at step 2.

files for the FC_Patcher :

* FC_patch_sequence_for_dummy_verify.sh
* patcher.py
* patch_wm100_0306.py
* patch_wm220_0306.py
* patch_wm331_0306.py

Running the patcher without files all being inside same dir has not been tested

#### 9. Export PATH_TO_TOOLS variable

Run `export PATH_TO_TOOLS=X` where X is path where dji-firmware-tools directory is before next step.
Example: `export PATH_TO_TOOLS=/home/user/dji/tools` when `dji-firmware-tools` directory is inside `/home/user/dji/tools/`.

#### 10. Call the packer script

`./FC_patch_sequence_for_dummy_verify.sh Spark 03.02.43.21`
or
`./FC_patch_sequence_for_dummy_verify.sh Mavic 03.02.44.08`
or
`./FC_patch_sequence_for_dummy_verify.sh P4P 03.02.44.08`

The aa.bb.cc.dd string after Spark or Mavic arg is the version of the FC module you are building.
It should be different from the one that is currently installed on the bird, so basically increase the number
each time you build a new version...

This should produce a few (uncleaned) tmp files, and a dji_system_bla_bla_bla.bin file which is the one you will be able to flash

This last dji_system.bin file is actually a tar file an it's worth checking it's content before moving to the actual flashing operations

The patcher will integrate the FC parameter mod you have prepared in your flyc_param_infos file plus a few other tweaks :

* max flight speed in waypoint mode
* max alt in waypoint mode
* max dist in waypoint mode
* enable Galileo satellites in the GNSS receiver
* patch the FC version number inside the file
* Repack everything

#### 11. Check Flash image

Make a copy of the .bin file renamed .tar and untar it
it should contain only 3 files (2 only for P4P) :
`wm100a.cfg.sig` or `wm220.cfg.sig` or `wm331.cfg.sig`
`wm... 0305 ... .pro.fw.sig` (very same as the one you extracted at step 1.)
`wm... 0306 ... .pro.fw.sig` (with the new version in file name, but the old timestamp)

the `0306.pro.fw.sig` is actually unsigged unencrypted file (we will stil be able to flash it !)

you should check that this module 306 file name, size, and md5 matches what has been written in the .cfg.sig file
(which is also unencrypted unsigged, only with a 480 spaces blank header added in order to match the signature header extra space when there is one)

at this stage the actual md5 would depend on your mods.

The .cfg.sig file contains lines for modules that are not inside the .bin but you have to let it that way.

#### 12. Install the dummy_verify.sh script on your bird

adb to your bird :
`adb shell`

make the /vendor partition read-write :
`mount -o remount,rw /vendor`

exit the adb shell :
`exit`

Push the dummy_verify.sh script to the bird :
`adb push dummy_verify.sh /vendor/bin/`

return to adb shell and give the right permissions :

```
adb shell
cd /vendor/bin/
chown root:root dummy_verify.sh
chmod 755 dummy_verify.sh
```

make a local copy (renamed) of dji_verify in /vendor/bin/ :

`cp /sbin/dji_verify /vendor/bin/original_dji_verify_copy` for Spark and Mavic
or
`cp /system/bin/dji_verify /vendor/bin/original_dji_verify_copy` for P4P
for P4 / P4 adv, check where the dji_verify tool lives in the file system and issue the right command accordingly

(use this very same name because it's hardcoded inside dummy_verify.sh)

commit your changes and remount the partition read-only :

```
sync
cd /
mount -o remount,ro /vendor
```

Turn off the bird

#### 13. Flash the .bin file you prepared at step 10 with DUMLDore v3

Turn the bird on hooked to your DUMLDore v3 enabled Windows machine and adb to it
(you'll need the windows adb if not already installed : https://developer.android.com/studio/releases/platform-tools
all adb steps can actually be performed from the windows machine if needed, but this will add extra steps of moving/copying
some files from the Linux setup to the Windows machine)

Now the trick :

`mount -o bind /vendor/bin/dummy_verify.sh /sbin/dji_verify` for Spark and Mavic
or
`mount -o bind /vendor/bin/dummy_verify.sh /system/bin/dji_verify` for P4P
for P4 / P4 adv, check where the dji_verify tool lives in the file system (`which dji_verify`) and issue the right command accordingly

This will have the following effect : actual dji_verify is "replaced" by dummy_verify.sh that gets called instead when the actual flashing will start.
A short read to dummy_verify script should let you understand how it works (and why it's called that way) : Just calling the dji_verify "copy"
and checking if it worked or not... assuming that fail cases are for our custom files, and "masking" the error to the system
This mount bind is not persistent and need to be done right before each time you will go for a new custom FC flash.
Because it is not persistant, it will not work for flashing other parts of the system that would require a reboot in the middle. 

Don't reboot or turn off the machine and go flashing with DUMLDore v3 the very same way you usually do.
The displayed percentage are fucked and it will go over 100% at some point, this is not an issue.
You can monitor it from adb at the same time with : `busybox tail -f /data/dji/log/upgrade00.log`
After a few seconds (10 ? 20 ?) you should hear the ESC beeping while the FC is being flashed (on Spark only)
Then the bird will reboot (disconnecting you from adb if you were monitoring)
30-60 s after reboot you are good to turn the bird off, even if DUMLDore does not acknowledge a finished flash sequence (especially on Spark)
The whole sequence is pretty short (less than 5 minutes)

#### 14. Check your upgrade logs

Turn you bird on again and pull the upgrade logs with DUMLDore
check the /data/dji/log/upgrade00.log file
and from the end of it search backward for the new version string you've been creating e.g. 03.02.43.21
if not finding, search without the leading 0 e.g. : 3.2.43.21

you should see lines similar too :

```
06-17 19:25:21.224   206  1619 I DUSS&63[sys_upgrade_check_connec:1937]:: Send check connection message to FC APP ...
06-17 19:25:21.234   206  1619 I DUSS&63[sys_upgrade_check_connec:1954]:: get version from 03.06 is: 03.02.43.20, ret_code is: 0
06-17 19:25:21.234   206  1619 I DUSS&63[sys_upgrade_check_connec:1987]:: Has HW ver for FC APP: XXXXXXXXXXXXXXX
06-17 19:25:21.234   206  1619 I DUSS&63[       sys_check_version:  86]:: Different version.
06-17 19:25:21.234   206  1619 I DUSS&63[       sys_check_version:  87]:: Current ver.Fw = 03.02.43.20
06-17 19:25:21.234   206  1619 I DUSS&63[       sys_check_version:  92]:: Targetr.Fw = 03.02.43.39
06-17 19:25:21.334   206  1619 I DUSS&63[sys_upgrade_request_upgr:2234]:: Send enter upgrade mode to FC APP...
06-17 19:25:21.354   206  1619 I DUSS&63[sys_upgrade_request_upgr:2255]:: Got enter upgrade mode ack message, len = 1.
06-17 19:25:21.354   206  1619 I DUSS&63[sys_upgrade_request_upgr:2268]:: Hw FC APP return ok for requesting upgrade.
06-17 19:25:21.354   206  1619 I DUSS&63[ sys_upgrade_check_state:2328]:: Send check state message to FC APP...
/---/
6-17 19:25:59.590   206  1619 I DUSS&63[sys_upgrade_check_connec:1937]:: Send check connection message to FC APP ...
06-17 19:25:59.596   206  1619 I DUSS&63[sys_upgrade_check_connec:1954]:: get version from 03.06 is: 03.02.43.39, ret_code is: 0
06-17 19:25:59.596   206  1619 I DUSS&63[sys_upgrade_check_connec:1987]:: Has HW ver for FC APP: XXXXXXXXXXXXXXX
06-17 19:25:59.596   206  1619 I DUSS&63[       sys_check_version:  82]:: Same version. Current: 03.02.43.39 (11047); Target: 03.02.43.39
06-17 19:25:59.596   206  1619 I DUSS&63[       sys_p1_upgrade_hw:3327]:: result : success . just ignore it
```

Last occurence in file is "Current = Target"
Previous occurence is "Current != Target"

If this is what you see, then Bravo, you've followed the guide correctly and can enjoy flying yur tuned bird.

The above apply to Mavic and Spark. On P4P, you should see  :

```
01-01 00:01:39.900   205  2752 I DUSS&63[  sys_upgrade_check_file:1716]:: Firmaware /cache/upgrade/unsignimgs//wm331_0306_v03.02.44.08_20171116.pro.fw is not encrypted
01-01 00:01:39.900   205   345 I DUSS&63[sys_up_status_push_threa: 938]:: +++++++ Sending upgrade status for upgrading_stage, len: 11, app_host=0xa01, mod_id=0xc3 (03.06), status 1, progress: 0, total_progress: 20
01-01 00:01:39.919   205  2752 I DUSS&63[  sys_upgrade_check_file:1728]:: md5string: 6f19dc59afacb0b931316807f4776fe6
01-01 00:01:39.919   205  2752 I DUSS&63[   sys_upgrade_commom_hw:3020]:: Start to upgrade FlyCtrl
```
...

`01-01 00:02:11.478   205  2752 I DUSS&63[   sys_upgrade_commom_hw:3111]:: ..... Succeed to upgrade  FlyCtrl ......`

note : these messages sometime falls in the upgrade01.log file in case the log rotation just occured and a new upgrade00.log file has just been started.

#### 15. Additionnal "post-install" steps to get Galileo working

You need a version of the app with the Galileo enable patch. At time, only NLD app version allows to apply this patch.

This is driven by the file in /DJI/og_settings/ubx.settings.json

m_DoLogging controls if the app will be producing logs for this feature. It is recommanded to activate it the first times you'll use it to make sure it works

m_MaxDownloadAge control the time (in seconds) since last download to make a new one (from the Internet). The default value is 60 s. DJI default is 5 days. Downloaded files are rather small (around 8kB in online and 35kB in offline)

m_ForceUpload = true/false controls if the app do the upload to bird at each session or upon bird request only (default DJI mode).

m_UseOnline = true/false controls if the stuff is downloading from internet the short term (near real time ephemerids : a.k.a online mode) or the mid term ephermid modelling stuff (a.k.a offline mode)
It seems necessary to use online mode first time you will use a Galileo enabled FC to help the receiver doing it's first galileo sats acquisitions

The downloaded files are stored under /data/data/dji.pilot.pad/app_com.dji.go.android.agps. The online file is about 7800 bytes and the offline one around 38000 bytes

The offline url is changed from DJI mirror that provides old data (making the feature useless) to u-blox ones... DJI U-Blox token is used (retrieved from the app at runtime)

m_YearOffset/m_MonthOffset should be left at 0 (debug/test features)

Once you have tuned your config file, start the app while the app has an internet access so it can download the assisted gnss files.

Then you can turn internet on and connect your bird.

Checking the UBX-timestamp.log file in /DJI/og_logs/ you should see torward the end of it :

```
<record>
    <date>Jun 15, 2018 15:00:05</date>
    <millis>1529067605393</millis>
    <sequence>141</sequence>
    <logger>og.patch.UBXCFGTuner</logger>
    <level>INFO</level>
    <class>og.patch.UBXCFGTuner</class>
    <method>log_UBX</method>
    <thread>0</thread>
    <message>case SEND_SUCCESS: mSendStatus NOR_DATA</message>
</record>
<record>
    <date>Jun 15, 2018 15:00:05</date>
    <millis>1529067605504</millis>
    <sequence>142</sequence>
    <logger>og.patch.UBXCFGTuner</logger>
    <level>INFO</level>
    <class>og.patch.UBXCFGTuner</class>
    <method>log_UBX</method>
    <thread>5</thread>
    <message>sendData success </message>
</record>
<record>
    <date>Jun 15, 2018 15:00:05</date>
    <millis>1529067605505</millis>
    <sequence>143</sequence>
    <logger>og.patch.UBXCFGTuner</logger>
    <level>INFO</level>
    <class>og.patch.UBXCFGTuner</class>
    <method>log_UBX</method>
    <thread>0</thread>
    <message>case SEND_SUCCESS: mSendStatus HASH_DATA</message>
</record>
```

you'll have a lot of ... NOR_DATA / success messages and one of the last ones should be HASH_DATA instead of NOR_DATA

This means that the agps file have been correctly uploaded to the bird and pushed to the GPS receiver.

This application : https://play.google.com/store/apps/details?id=com.nec.android.qzss.gnssview&hl=fr

allows checking for planned constellations at a given place / date / time

The receiver is configured for GPS+GLO+GAL with a 5° horizon. Even with open sky, all sats between 5 and 10° might not be tracked so this is only an indication.
You can set the constellation planning app mask to 10° to spot a test flight time with lots of satellites. You're almost guaranteed to see those (above 10°) plus a part of those between 5 and 10°. In other words if you set the planning app mask to 5°, you will usually see less satellites than planned because you are not guaranteed to see those in the 5-10° above horizon range.

The best way to check that Galileo has correctly been enabled is to pull a FLYNNN.DAT flight from /blackbox/flyctrl/ after your test flight and use CsvView from https://datfile.net/
While plotting the 3 "signals" : total satellites count, GPS satellites count and Glonass satellites count. You'll see that total > GPS+GLO. The missing satellites (maybe 3 to 6-7) are the Galileo ones.

4 Galileo satellites launched in december 2017 are above us right now but one not been comissioned yet (24/08/2018). They should soon be commissioned and this will provide even more sats.
4 more sats where launched on July 15th 2018 and should be commissionned beginning of 2019. Up to date info : https://www.gsc-europa.eu/system-status/Constellation-Information
