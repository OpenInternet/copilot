import os
import subprocess

#stat logging
import logging
log = logging.getLogger(__name__)


#Adapted from https://stackoverflow.com/questions/6840711/writing-a-file-to-a-usb-stick-in-linux-with-python
# Feel like a https://www.eff.org/files/images_insert/defcon20-script-kitty-detail.jpg
def get_usb_dirs():
    """ Get the directory for all mounted USB devices.
    """
    devices = []
    log.info("Getting all USB devices.")
    with open("/proc/partitions") as partitionsFile:
        lines = partitionsFile.readlines()[2:] #Skips the header lines
        for line in lines:
            words = [x.strip() for x in line.split()]
            minorNumber = int(words[1])
            deviceName = words[3]
            if minorNumber % 16 == 0:
                path = "/sys/class/block/" + deviceName
                if os.path.islink(path):
                    if os.path.realpath(path).find("/usb") > 0:
                        devices.append('/dev/'+deviceName)
    log.debug("USB devices found: {0}".format(devices))
    log.debug("Getting mount points.")
    mounts = []
    for line in subprocess.check_output(['mount', '-l']).split('\n'):
        parts = line.split(' ')
        if len(parts) > 2:
            if parts[0][:-1] in devices:
                mounts.append(parts[2])
    log.debug("USB mount points found: {0}".format(mounts))
    return mounts

def get_likely_usb():
    """ Get the last mounted USB device.

    Because many devices can have many USB's attached to them
    this function tries to pick the most likely desired USB.
    To do this, this function picks the last mounted USB. We
    hope that a persons tendency to unplug and plug back in
    a USB when retrying will ensure that this correctly ID's
    the USB desired.

    """
    log.debug("Getting USB device.")
    all_usb = get_usb_dirs()
    if len(all_usb) > 0:
        likely_usb = all_usb[-1]
        log.debug("Likely USB device {0} found.".format(likely_usb))
        return likely_usb
    else:
        log.debug("No USB devices found.")

def is_usb():
    """ Check if there are mounted USB's."""
    log.debug("Checking if there are mounted USB's")
    all_usb = get_usb_dirs()
    if len(all_usb) > 0:
        log.debug("Mounted USB's found")
        return True
    else:
        log.debug("No mounted USB's found.")
        return False
