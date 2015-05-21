import os
import subprocess

#stat logging
import logging
log = logging.getLogger(__name__)


#Adapted from https://stackoverflow.com/questions/6840711/writing-a-file-to-a-usb-stick-in-linux-with-python
# Feel like a https://www.eff.org/files/images_insert/defcon20-script-kitty-detail.jpg
def get_usb_dirs():
    devices = []
    with open("/proc/partitions") as partitionsFile:
        lines = partitionsFile.readlines()[2:]#Skips the header lines
        for line in lines:
            words = [x.strip() for x in line.split()]
            minorNumber = int(words[1])
            deviceName = words[3]
            if minorNumber % 16 == 0:
                path = "/sys/class/block/" + deviceName
                if os.path.islink(path):
                    if os.path.realpath(path).find("/usb") > 0:
                        devices.append('/dev/'+deviceName)
    log.debug("usb debvices found: {0}".format(devices))
    #get mount point
    mounts = []
    for line in subprocess.check_output(['mount', '-l']).split('\n'):
        parts = line.split(' ')
        if len(parts) > 2:
            if parts[0][:-1] in devices:
                mounts.append(parts[2])
    log.debug("usb mount points found: {0}".format(mounts))
    return mounts

def get_likely_usb():
    all_usb = get_usb_dirs()
    if len(all_usb) > 0:
        return all_usb[-1]

def is_usb():
    all_usb = get_usb_dirs()
    if len(all_usb) > 0:
        return True
    else:
        return False
