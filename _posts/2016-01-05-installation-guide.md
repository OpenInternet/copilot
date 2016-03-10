---
layout: post
title:  "Installation Guide"
categories: developer
---

* TOC
{:toc}

### Co-Pilot installation on unsupported ARM devices

Co-Pilot is still in its **BETA stages**.

#### Installing the underlying system.

Co-Pilot uses the Kali-Linux ARM distribution as its underlying system.

* Download a [pre-built Kali-Linux ARM build](https://www.offensive-security.com/kali-linux-vmware-arm-image-download/) for your device or build your own Kali-Linux image using the [Kali-Arm Build scripts](https://github.com/offensive-security/kali-arm-build-scripts) on a existing Kali device.

* [Load your Kali-Linux image onto an SD-card.](http://odroid.us/mediawiki/index.php?title=Step-by-step_Ubuntu_SD_Card_Setup) and plug it into your Device.

#### Installing and Configuring the Co-Pilot system

* On the co-pilot device clone the co-pilot repository.

```
https://github.com/OpenInternet/co-pilot.git
```

* Run the installation script from that repository.

```
cd  co-pilot
./install
```

* Restart Co-Pilot

```
shutdown -r 0
```

#### Running Co-Pilot

* Follow the [configuration instructions](https://github.com/OpenInternet/co-pilot/wiki/Configuring-Co-Pilot) for running co-pilot.
