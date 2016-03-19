---
layout: post
title:  "Installation Guide"
categories: developer
---

* TOC
{:toc}

### CoPilot installation on unsupported ARM devices

CoPilot is still in its **BETA stages**.

#### Installing the underlying system.

CoPilot uses the Kali-Linux ARM distribution as its underlying system.

* Download a [pre-built Kali-Linux ARM build](https://www.offensive-security.com/kali-linux-vmware-arm-image-download/) for your device or build your own Kali-Linux image using the [Kali-Arm Build scripts](https://github.com/offensive-security/kali-arm-build-scripts) on a existing Kali device.

* [Load your Kali-Linux image onto an SD-card.](http://odroid.us/mediawiki/index.php?title=Step-by-step_Ubuntu_SD_Card_Setup) and plug it into your Device.

#### Installing and Configuring the CoPilot system

* On the CoPilot device clone the CoPilot repository.

```
https://github.com/OpenInternet/CoPilot.git
```

* Run the installation script from that repository.

```
cd  CoPilot
./install
```

* Restart CoPilot

```
shutdown -r 0
```

#### Running CoPilot

* Follow the [configuration instructions](https://github.com/OpenInternet/CoPilot/wiki/Configuring-CoPilot) for running CoPilot.
