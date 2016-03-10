---
layout: post
title:  "Troubleshooting"
categories: developer
---

* TOC
{:toc}

### Access Point is Missing

"I did everything correctly, but there is still no co-pilot access point."

#### Common Problems

* Co-PIlot does not have the proper drivers for your Wi-Fi dongle.
- please [add a support issue to the bug tracker](https://github.com/OpenInternet/co-pilot/issues) if you determine that this is your problem so that we can help you find the proper drivers (if they exist) and document which Wi-Fi dongles are supported, and how to get them running.
* Your device does not provide enough power to USB devices to run the Wi-Fi Dongle.
There are solutions for some devices, the occasionally require powered USB hubs or ripping out fuses in your device (a little excessive in my opinion)
* Your device tried to set up the wireless interface before it had an Internet  connection on the Ethernet interface.
It sometimes helps to restart the device when connected to the Internet so that it gets a lease and the router is quicker to recognize it. (This is PURE speculation, but it seems to work in a chunk of the tests that I have done.) To do this, remove the dongle, restart, wait until it has fully booted up, shut it down, insert the dongle, and then start the device up again.


#### Check if device is starting properly

On many embedded devices (especially Raspberry Pi from my tests) if there is not enough power going to the wireless dongle it will enter a boot/reboot loop that requires a restart.

This can be checked by plugging the device into a monitor and restarting it. If the device continues outputting start up text for an extended period of time it may be this. Try removing the dongle and restarting the device. If it starts up properly when this occurs this may be your problem.

**Possible Fixes**

* Try plugging the dongle into a different usb.
* If powering the device from your computers USB, try plugging the power directly into a power socket using a usb charger.

#### Check if the create_ap service is properly running

##### SupercisorCtl
Check the uptime of the create_ap service from the supervisor daemon
```
supervisorctl status
```

The output will be a list of services, their current status, their pid, and their uptime. If create_ap is STOPPED, or has a different runtime (usually in the 1-10 second range) than the other services it has most likely failed and the supervisorctl is trying, or given up on trying, to restart it.

##### Check the process

```
ps -ef |grep create
```

The output should include something like the following.

```
/bin/bash /usr/bin/create_ap wlan0 eth0 copilot copilot_pass
```

This output can be parsed as such:

|env | script|Wi-Fi interface|Internet interface| AP name| AP password|
|---|---|---|---|---|---|
| /bin/bash | /use/bin/create_ap | wlan0 | eth0 | copilot | copilot_pass|


If this looks different than the co-pilot start up script is not properly setting up the create_ap script. Use the guidance at the bottom of [check the proper interfaces](#check-to-make-sure-the-proper-interfaces-have-been-created) for how to check the startup script.

#### Check to make sure the proper interfaces have been created.

```
ip link list
```

In this list you should see a ```eth0``` interface, a ```wlan0``` interface, a ```ap0``` interface, and a ```mon.ap0``` interface. If any of these interfaces are missing or are incorrectly names (e.g. ```eth1``` instead of ```eth0`` create_ap is not working properly and may need to be re-configured.

* If the ```eth0``` interface is missing then you are not connected to the Internet and co-pilot will not be able to create the Wi-Fi interface.
* If you see ```eth1``` instead of ```eth0`` then your device has its network interfaces confgured  differently than the default on co-pilot. you will need to change the [copilot start script](https://github.com/OpenInternet/co-pilot/blob/master/copilot/plugins/create_ap/start#L3) to use the default ethernet interface on your device.

### Check the logs
Get the log messages from create_ap. These will show you any errors as well as the standard output of the create_ap service.

```
cat /var/log/supervisor/create_ap-stderr*
cat /var/log/supervisor/create_ap-stdout*
```

You can attach the errors in the logs to the bottom of an issue you create in the [co-pilot bug tracker](https://github.com/OpenInternet/co-pilot/issues). Feel free to file support issues there. Just make sure to tag it with the "support" label so that we know how to respond to your request.
