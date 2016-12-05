---
layout: post
title:  "Installation Guide"
categories: developer
---

* TOC
{:toc}

### Installing CoPilot from a pre-built image

#### Download latest release image

Download the [compressed img file for the latest release from the release page](https://github.com/OpenInternet/copilot/releases).

For the 1.0 release the name of this file is [copilot-1.0-bbb.img.tar.gz]()

#### Decompress image file

There are a few ways to decompress the latest image file.

##### 7-Zip
One option is to install 7-Zip, which has a nice graphical user interface. 7-Zip can also be used to unpack many other formats and to create tar files (amongst others).

- Download and install 7-Zip from 7-zip.org.
- Once it is installed if you double click on the copilot image file (copilot-1.0-bbb.img.tar.gz) 7-Zip should automatically start.
- If it does not automatically start you should be able to right-click on the copilot image file and choose the "extract here" option.

##### Command Line

If you are on linux, OSX, or have MinGW/MSYS or Cygwin installed you can unpack the copilot image using the tar command.

```bash
tar -zxvf copilot-1.0-bbb.img.tar.gz
```

#### Write image to SD card

Once you have the image uncompressed you will need to write it to a micro SD card. Please follow the **very well written* Raspberry-Pi SD card guides below based on your system.

Installing operating system images using
- [Windows](https://www.raspberrypi.org/documentation/installation/installing-images/windows.md)
- [Max OSX](https://www.raspberrypi.org/documentation/installation/installing-images/mac.md)
- [Linux](https://www.raspberrypi.org/documentation/installation/installing-images/linux.md)

#### Setup Copilot

When the installer exits you can remove the SD card and Follow the [configuration instructions](http://openinternet.github.io/copilot/trainer/2016/01/03/setup-guide.html) for running CoPilot.


### Building CoPilot from source

Building CoPilot from source requires a linux device.

#### Installation Demo

<script type="text/javascript" src="https://asciinema.org/a/1upck1ujoq5620mhbimflq0nd.js" id="asciicast-1upck1ujoq5620mhbimflq0nd" async></script>

#### Installing Dependencies

##### Virtual Box

You will need to install Virtual Box. [You can find Virtual Box's downloads here.](https://www.virtualbox.org/wiki/Downloads)


##### Vagrant

You will need to install Vagrant. [You can find Vagrant's install instructions here.](https://www.vagrantup.com/docs/installation/)

##### Git

You will need to install Git. [You can find Git's install instructions here.](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

On debian you can just run the following.

```bash
sudo apt-get install git-core
```

#### Installing  Copilot

Start the installation by running the following commands.

```bash
git clone https://github.com/OpenInternet/copilot-install
cd copilot-install
./install.sh
```

This will take you into the interactive command line installer.

##### Choose a custom copilot repository (optional)

```bash
Installing CoPilot...
What admin password would you like CoPilot to use?
Do not use the following characters "\$@
Password: Are you using a custom CoPilot Repository?
[y/n]
```

If you answer **y** to this you will be able to choose a url to a git repository to pull your custom version of Copilot from. If you choose **n** it will use the default Copilot repository.

Here is an example of me providing the url to the primary Copilot git repo.

```bash
[y/n] y
What URL should we use to download CoPilot?
URL: https://github.com/OpenInternet/copilot.git
```

##### Choose a custom copilot plugin repository (optional)

```bash
Are you using custom plugins?
[y/n]
```
If you answer **y** to this you will be able to choose a url to a git repository to pull your custom Copilot plugins. If you choose **n** it will use the default Copilot plugin repository.

Here is an example of me providing the url to the primary Copilot plugin git repo.

```bash
[y/n] y
What URL should we use for getting the plugins?
URL: https://github.com/OpenInternet/copilot-plugins.git
```

Here is an example of me telling copilot to use the master branch of the Copilot plugin repo.

```bash
What branch should we use in the plugin repo? (default 'master')
Branch: master
```

##### Wait...

Installation takes a long time. Depending upon your device it can take as long as an hour.

##### Write


At the end of a process the installer will ask you if you want to install the image you have created onto an SD card.

```bash
Completed Installation Process...
Would you like to install CoPilot directly onto a SD card?
[y/n]
```
If you answer **y** to this it will write the image to the chosen SD card. To do this you will need to get the device name of the SD card. The example below is me writing my latest image to an SD card.

```bash
[y/n] y
What is the path to your SD cards device
Device Path: /dev/mmcblk0
Starting Install... This will take a while.
[sudo] password for user:
```

#### Setup Copilot

When the installer exits you can remove the SD card and Follow the [setup instructions](http://openinternet.github.io/copilot/trainer/2016/01/03/setup-guide.html) for running CoPilot.
