"""
Created at night by @lenisko for Original Gangsters team
Licensed under DBaD licence http://dbad-license.org/
"""

import os
import re
import shutil
import subprocess
import sys
from argparse import RawTextHelpFormatter, ArgumentParser


class Error(Exception):
    """
    Basic Error exception
    """


def user_prompt(msg="When you're done, write `ok` here (to exit script write `no`): "):
    var = None
    while var != "ok":
        var = input(msg)
        if var == 'no':
            print("\nByebye!~")
            sys.exit(0)


def model_name(model):
    model_dict = {
        'wm100': 'Spark',
        'wm220': 'Mavic',
        'wm330': 'P4std',
        'wm331': 'P4P',
        'wm332': 'P4adv',
        'wm620': 'I2',
        'wm335': 'P4PV2',

    }
    if model not in model_dict:
        raise Error("Model {} is not supported!".format(model))

    return model_dict[model]


def old_files_check():
    if os.path.isfile(os.path.join(script_path, 'dji_fc_patcher', 'dummy_verify.sh')):
        print(
            " -- 1. This run will remove all files insdie `dji_fc_patcher/tmp` " +
            "dir and overwrite files in `dji_fc_patcher` at the end.\n"
        )
        user_prompt()
    else:
        print(" -- 1. Hello there! (already working...)")


def path_creation():
    try:
        try:
            os.mkdir(os.path.join(script_path, 'dji_fc_patcher'))
        except Exception:
            pass
        os.mkdir(os.path.join(script_path, 'dji_fc_patcher', 'tmp'))
        os.mkdir(os.path.join(script_path, 'dji_fc_patcher', 'tmp', 'tools'))
    except Exception:
        subprocess.check_output(["rm", "-rf", os.path.join(script_path, 'dji_fc_patcher', 'tmp')])
        path_creation()


def tmp_clean():
    print(" -- 6. Shall I clean `dji_fc_patcher/tmp` directory? output files are safe inside `dji_fc_patcher` dir.\n")
    user_prompt()
    subprocess.check_output(["rm", "-rf", os.path.join(script_path, 'dji_fc_patcher', 'tmp')])
    print("\nByebye!~")


def check_python():
    if sys.version_info[0] != 3:
        raise Error("Please run this script from python3")

    if not os.path.isfile('/usr/bin/python'):
        raise Error("Python2 is missing under /usr/bin/python !")
    if not os.path.isfile('/usr/bin/python3'):
        raise Error("Python3 is missing under /usr/bin/python3 !")
    try:
        import Crypto
    except ImportError:
        raise Error("Install pycrypto package using pip!")


def tools_dl():
    os.chdir(tools_dir)
    for repo_url in [
        "https://github.com/o-gs/DJI_FC_Patcher.git",
        "https://github.com/o-gs/dji-firmware-tools.git",
        "https://github.com/fvantienen/dji_rev.git",
    ]:
        try:
            subprocess.check_output(["git", "clone", "--quiet", repo_url])
        except subprocess.CalledProcessError as error:
            raise Error(error.returncode, error.output)


def execution_perm():
    subprocess.call("find %s -name \"*.sh\" -exec chmod +x {} \\;" % tools_dir, shell=True)


def extract_fw():
    os.chdir(tmp_dir)
    try:
        shutil.copy(args.firmware_path, os.path.join(tmp_dir, 'bird_firmware.bin'))
    except IOError:
        raise Error("Wrong path to file with bird firmware!")

    try:
        subprocess.check_output(["tar", "-xf", "bird_firmware.bin"])
    except subprocess.CalledProcessError as error:
        raise Error("Failed to extract firmware!", error.returncode, error.output)
    _clean_module_files()


def _clean_module_files():
    files = os.listdir(tmp_dir)
    rm_me = []
    keep_me = ['_0305_', '_0306_', '.cfg.sig', '.unsig', 'flyc_param_infos', 'tools']
    for f in files:
        if not any(i in f for i in keep_me):
            rm_me.append(f)

    for f in rm_me:
        os.remove(os.path.join(tmp_dir, f))


def extract_306_fw():
    os.chdir(tmp_dir)
    try:
        subprocess.check_output(["python3", os.path.join(
            tools_dir, "dji_rev", "tools", "image.py"), args.model + ".cfg.sig"
                                 ])
        shutil.move(args.model + ".cfg_0000.bin", args.model + ".cfg.ori")
    except subprocess.CalledProcessError as error:
        raise Error("Failed to extract firmware!", error.returncode, error.output)


def user_0306_unsig():
    global old_fw_name
    old_fw_name = _find_fw_path()
    print("""
 -- 2. Connect your bird, ensure you have adb access and inside "{dir}"
 directory. If not or you are using a separate system for that, make sure
to copy the resulting 0306.unsig file into this directory before continuing.

! Take a note that some paths might not be the same (which depends on root way and model). For details check !
https://github.com/o-gs/DJI_FC_Patcher#4-unsig-the-0306-file--first-step-involving-some-actions-on-the-bird

Run separately those commands:

adb shell mount -o remount,rw /vendor
adb shell mkdir /vendor/bin
adb push {fw_file} /vendor/bin/
adb shell cd /vendor/bin/ ; /sbin/dji_verify -n 0306 -o 0306.unsig {fw_file}
adb pull /vendor/bin/0306.unsig
adb shell cd /vendor/bin/ ; rm 0306.unsig ; rm *.fw.sig ; cd / ; sync ;mount -o remount,ro /vendor
""".format(**{
        "dir": tmp_dir,
        "fw_file": old_fw_name
    }))

    user_prompt()


def _find_fw_path(fw_name=None):
    work_file = None
    look_for = fw_name if fw_name else args.model + '_0306_'
    for filename in os.listdir(tmp_dir):
        if look_for in filename:
            work_file = filename

    if not work_file:
        raise Error("Can't find 0306 pro.fw.sig inside dir, something went wrong!")

    return work_file


def decrypt_fc_extr_params():
    global decrypted_306_name
    os.chdir(tmp_dir)
    decrypted_306_name = _find_fw_path()[:-7] + ".fw_0306.decrypted.bin"
    try:
        subprocess.check_output(["python3", os.path.join(
            tools_dir, "dji-firmware-tools", "dji_mvfc_fwpak.py"
        ), "dec", "-i", "0306.unsig"])
    except subprocess.CalledProcessError as error:
        raise Error("Failed to extract firmware!", error.returncode, error.output)

    shutil.move("0306.decrypted.bin", decrypted_306_name)

    try:
        subprocess.check_output(["python3", os.path.join(
            tools_dir, "dji-firmware-tools", "dji_flyc_param_ed.py"
        ), "-vv", "-x", "-b", "0x420000", "-m", decrypted_306_name])
    except subprocess.CalledProcessError as error:
        raise Error("Failed to extract firmware!", error.returncode, error.output)


def user_edit_params():
    print("\n -- 3. Now open file {} with text editor, mod any values you need and save it.\n".format(
        os.path.join(tmp_dir, "flyc_param_infos")
    ))
    print("More info here https://github.com/o-gs/DJI_FC_Patcher#7-mod-you-flyc_param_infos-with-a-text-file\n")
    user_prompt()


def call_packer():
    os.chdir(tmp_dir)
    os.remove(os.path.join(tmp_dir, old_fw_name))

    var = ''
    while not re.match('\d{2}\.\d{2}\.\d{2}\.\d{2}', var):
        var = input("\n -- 4. Provide desired 0306 module version (eg: 03.02.44.08): ")

    try:
        os.environ["PATH_TO_TOOLS"] = tools_dir
        subprocess.check_output([os.path.join(
            tools_dir, "DJI_FC_Patcher", "FC_patch_sequence_for_dummy_verify.sh"), model_name(args.model), var
        ])
    except subprocess.CalledProcessError as error:
        raise Error("Failed to extract firmware!", error.returncode, error.output)
    global dummy_bin
    dummy_bin = _find_fw_path("dummy_verify.bin")
    shutil.copy(dummy_bin, "../")
    shutil.copy(os.path.join(tools_dir, "DJI_FC_Patcher", "dummy_verify.sh"), "../")
    shutil.copy("flyc_param_infos", "../")
    shutil.copy("0306.unsig", "../")


def verify_install():
    print("""
 -- 5. Run those commands separately in your console inside "{main_dir}" directory.

! Take a note that some paths might not be the same (which depends on root way and model). For details check !
https://github.com/o-gs/DJI_FC_Patcher#12-install-the-dummy_verifysh-script-on-your-bird and
https://github.com/o-gs/DJI_FC_Patcher#13-flash-the-bin-file-you-prepared-at-step-10-with-dumldore-v3

Run separately those commands:

adb shell mount -o remount,rw /vendor
adb push dummy_verify.sh /vendor/bin/
adb shell cd /vendor/bin/ ; chown root:root dummy_verify.sh ; chmod 755 dummy_verify.sh ; cp /sbin/dji_verify /vendor/bin/original_dji_verify_copy ; sync ; cd / ; mount -o remount,ro /vendor

Turn off and on your bird and run this command:

adb shell mount -o bind /vendor/bin/dummy_verify.sh /sbin/dji_verify

without futher restarting, flash {dummy_bin} using DUMLDore v3.
Note: In file name picker write *.* and confirm using Enter to show all files in directory or rename {dummy_bin} to dji_system.bin.

and continue from https://github.com/o-gs/DJI_FC_Patcher#14-check-your-upgrade-logs/
""".format(**{
        'main_dir': main_dir, 
        'dummy_bin': dummy_bin
    }))


def script_run():
    model_name(args.model)
    old_files_check()
    path_creation()
    check_python()
    tools_dl()
    execution_perm()
    extract_fw()
    extract_306_fw()
    user_0306_unsig()
    decrypt_fc_extr_params()
    user_edit_params()
    call_packer()
    verify_install()
    tmp_clean()


# run it.
parser = ArgumentParser(
    formatter_class=RawTextHelpFormatter,
    description="""
Custom FC patcher helper.

    Supported models:
    * wm100 - DJI Spark (v01.00.0900)
    * wm220 - DJI Mavic Pro series (incl. Platinium) (wm220) (v01.04.0300)
    * wm330 - Phantom 4 (v02.00.0700)
    * wm331 - Phantom 4 Pro (v01.05.0600)
    * wm332 - Phantom 4 advanced (v01.00.0128)
    * wm620 - Inspire 2 (v01.02.0200) [Untested]
    * wm335 - Phantom 4 Pro/Pro+ V2 (v01.00.1500) [Untested]
"""
)

parser.add_argument('model', type=str, help='Model, eg "wm220" for Mavic Pro')
parser.add_argument('firmware_path', type=str, help='Path to firmware for provided model')

args = parser.parse_args()

script_path = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.join(script_path, 'dji_fc_patcher')
tmp_dir = os.path.join(script_path, 'dji_fc_patcher', 'tmp')
tools_dir = os.path.join(script_path, 'dji_fc_patcher', 'tmp', 'tools')
decrypted_306_name = None
old_fw_name = None
dummy_bin = None

script_run()
