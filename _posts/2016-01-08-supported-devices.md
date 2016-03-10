---
layout: post
title:  "Supported Devices"
categories: trainer
---


**Table of Contents**

* [Currently Supported Devices](#currently-supported-devices)
* [Devices Being Considered for Support](#devices-being-considered-for-support)
* [Unsupported Devices](#unsupported-devices)

### Currently Supported Devices

The following devices have been tested and found to work with the Co-Pilot platform.

#### Beagle Bone Black

| Open-Source Hardware | Under 100$ USD |
|---|---|
|:white_check_mark:|:white_check_mark:|

* [Setup Guide](http://openinternet.github.io/copilot/trainer/2016/01/03/setup-guide.html)

#### ODROID-U3

| Open-Source Hardware | Under 100$ USD |
|---|---|
|:interrobang:<sup>1</sup>|:white_check_mark:|

1. Even though the name ‘Odroid’ is a portmanteau of ‘open’ + ‘Android’, the hardware isn't actually open because some parts of the design are retained by the company. ["We don't supply/sell any PCB design file or Gerber file. Please don't ask about it."](http://com.odroid.com/sigong/blog/blog_list.php?bid=143)

#### Raspberry-Pi 2

| Open-Source Hardware | Under 100$ USD |
|---|---|
|:white_check_mark:|:white_check_mark:|

### Devices Being Considered for Support

The following devices have *not** been tested with the Co-Pilot platform. But, because they are supported by [Offensive Securities Kali-Linux Build System](https://www.offensive-security.com/kali-linux-vmware-arm-image-download/#) they will be reviewed for support when we get money to purchase them. We would love to know if you install Co-Pilot on these devices so that we know if they will work or not.

#### CompuLab - Utilite & TrimSlice

#### Chromebooks - HP, Samsung & Acer

#### Allwinner - Cubieboard & Mini-X

#### SolidRun - CuBox

#### RioTboard

### Unsupported Devices

The following devices been tested with the Co-Pilot platform. They have been found wanting and will not be supported in future Co-Pilot releases.

#### Raspberry-Pi 1

The First Release of the Raspberry Pi will **not** be supported. [The Raspberry pi requires either an external powered USB hub or the user to remove a fuse connecting the USB ports to the board.](https://github.com/OpenInternet/co-pilot/issues/45) Beyond this, we have serious concerns about the general lack of computing power supplied by the original Raspberry-Pi.
