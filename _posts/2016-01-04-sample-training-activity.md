---
layout: post
title:  "Sample Training Activity"
categories: trainer
---

* TOC
{:toc}

## Tor Browser Bundle Curricula

### Level-Up Curricula Information

|***|***|
|---|---|
|AdIDS Category|[Deepening](https://www.level-up.cc/leading-trainings/training-curriculum/deepening) [10]|
|Parent Sub-topic(s):|[Anonymity & Circumvention](https://www.level-up.cc/leading-trainings/training-curriculum/anonymity-circumvention) [11], [Secure Browsing](https://www.level-up.cc/leading-trainings/training-curriculum/secure-browsing) [12]|
|Duration|30+ minutes|
|Platforms|[Linux](https://www.level-up.cc/platform/linux) [13], [Mac OS](https://www.level-up.cc/platform/mac-os) [14], [Windows](https://www.level-up.cc/platform/windows) [15]|
|Summary|Participants will learn how to use the Tor Browser Bundle for anonymity and circumvention.|
|Credits|Lindsay Beck, Chris Walker, Seamus Tuohy|
|license|[Creative Commons Attribution-Share Alike Unported 3.0](https://creativecommons.org/licenses/by-sa/3.0/)|
|Source URL|[Using The Tor Browser Bundle](https://www.level-up.cc/leading-training/training-curriculum/deepening/using-tor-browser-bundle)|
|Last Updated|June 2015|

Materials to Prepare:
=====================

-   Projector

-   Laptop to visualize demos

-   Tor Browser Bundle, installed on the trainer's device

-   A copy of the Tor Browser Bundle "installer" (a self-extracting archive) for distribution to participants. The Tor Browser Bundle is quite large, so it's a good idea to prepare this ahead of time,  especially if you have a slow Internet connection in the training room.

-   [A CoPilot censorship simulating access point kit.](https://github.com/OpenInternet/CoPilot/wiki/Setup-Guide#what-you-will-need)

Preparation:
==================================

- Before the training begins turn on the CoPilot device.

- If you have not yet configured your CoPilot device follow the [configuration instructions](https://github.com/OpenInternet/CoPilot/wiki/Configuring-CoPilot) provided on the CoPilot wiki.

- [Create a new "censorship" profile](https://github.com/OpenInternet/CoPilot/wiki/Setup-Guide#step-6-create-a-new-profile-optional) that targets a widely known website that participants are likely to have not visited recently. (e.g Disney.com, .gov, hotmail)

- Instruct the participants to connect to the access point being provided by CoPilot (by default this will be **copilot**.)

Tor Browser Bundle Hands-On Steps:
==================================

In this exercise, participants will use the Tor Browser Bundle to create an anonymous connection, confirm that it is working by accessing a website blocked by CoPilot, and change their Tor "exit relay."

Show the public IP address of the training room's Internet connection
------------------------------------------------------------------------

-   In a browser, visit [whatismyip.com](https://whatismyip.com/) [1] (https) or [whatismyipaddress.com](http://whatismyipaddress.com/) [2] (which includes a map)

-   Explain the concept of sites like whatismyipaddress.com. (And, if necessary, explain the concept of an IP address)

-   Invite participants to visit the site themselves, using their own devices.

Show the websites blocked by CoPilot
-----------------------------------------------------

-   In a browser, visit site that you blocked with CoPilot

-   Explain the concept of DNS, and how just like participants have an IP address, participants must get the IP address of websites that they visit.

-   Invite participants to visit the site themselves, using their own devices.

Show the public IP address of the Tor "exit relay"
-----------------------------------------------------

-   Close all web browsers

-   Launch the Tor Browser Bundle by running "Start Tor Browser.exe" and clicking "Connect"

-   Wait until a Tor connection is established and a new browser window has opened (this could take several minutes)

-   Tor Browser should load a page that says: "Congratulations. This browser is configured to use Tor.” (If for some reason your Tor connection fails, it will say: "Something Went Wrong! Tor is not working in this browser.")

-   In Tor Browser, visit [whatismyip.com](https://www.whatismyip.com/) [3] or  [whatismyipaddress.com](http://whatismyipaddress.com/) [4] and show that the IP address has changed.

Show how the websites blocked by CoPilot are now accessible
-----------------------------------------------------

-   In Tor Browser,  visit site that you blocked with CoPilot and show that it is now accessible.

-   Explain how Tor allows allows a user to access the Internet from another location, and how that allows them to bypass the CoPilot device sitting between them and the Internet.

-   Invite participants to visit the site themselves, using their own devices.

Show how to select a new path through the Tor network
--------------------------------------------------------

-   Explain that Tor could conceivably select an “exit relay” in the same country as the user. (An "exit relay" is the Tor server from which one's outgoing traffic leaves the Tor network, and through which one's incoming traffic enters it.) This is not good for anonymity and would not allow them to bypass DNS based censorship occurring in-country.. It is also one reason why a Tor Browser user might want to select a new exit relay. This can be done by clicking on the green onion to the left of the browser's address field and clicking “New Identity”.

-   Request a new identity, then refresh the webpage ([whatismyip.com](https://www.whatismyip.com/) [3] or [whatismyipaddress.com](http://www.whatismyipaddress.com/) [5]). The IP address should change.

Ask participants to repeat this exercise, until they demonstrate that they can use the Tor Browser Bundle successfully. Then, explain that:
----------------------------------------------------------------------------------------------------------------------------------------------

-   Though Tor encrypts your traffic on its way to the first Tor relay, and while it travels through the Tor network, **it cannot automatically encrypt your connection between the "exit relay" and the website you are visiting.** So, if you are visiting a site that does not support HTTPS, the exit relay operator (who could be *anybody*) can see everything you send and receive. They might know who you are—unless there are hints in the traffic itself, which is not uncommon—but they can see everything else. So, it is still important to use secure, HTTPS Web services. You might want to use the [EFF visualization](https://www.eff.org/pages/tor-and-https) [6] to help explain this concept.

-   In order to take advantage of Tor's anonymity and circumvention properties, you must launch the Tor Browser Bundle and **use the special version of Firefox that comes with it.** Your other browsers (such as Google Chrome, Firefox or Internet Explorer) will not automatically use the Tor network.

-   Unlike with a VPN, non-browser Internet traffic (from email clients like Thunderbird and Outlook, for example, or instant messaging programs like Pidgin and Adium) **does not benefit** from Tor's anonymity or circumvention properties. 

-   When using Tor Browser, you might want to visit [check.torproject.org](https://check.torproject.org/) [7] (which is similar to the [whatismyip.com](https://www.whatismyip.com/) [3] website) and **verify that Tor is working.**

-   ​As with all security software, it is important that you **use the latest version of the Tor Browser Bundle.** When Tor Browser opens, the page it displays will tell you if a newer version is available.
    It will not update itself automatically, however, so you will have to do that yourself. See the **[Secure Software Updating](https://www.level-up.cc/leading-trainings/training-curriculum/secure-software-update)  [8]** **module here on LevelUp** for supporting training material on this topic.


Additional Resources:
=====================

-   **Visualization:** [Tor and HTTPS Internet traffic](https://www.eff.org/pages/tor-and-https) [6], from
    Electronic Frontier Foundation

-   **Is Tor Working?:** [Check here and see](https://check.torproject.org/) [9] if Tor Browser is running properly on your machine
 

[1]: https://whatismyip.com\
[2]: http://whatismyipaddress.com\
[3]: https://www.whatismyip.com\
[4]: http://whatismyipaddress.com/\
[5]: http://www.whatismyipaddress.com\
[6]: https://www.eff.org/pages/tor-and-https\
[7]: https://check.torproject.org\
[8]: https://www.level-up.cc/leading-trainings/training-curriculum/secure-software-update\
[9]: https://check.torproject.org/\
[10]: https://www.level-up.cc/leading-trainings/training-curriculum/deepening\
[11]: https://www.level-up.cc/leading-trainings/training-curriculum/anonymity-circumvention\
[12]: https://www.level-up.cc/leading-trainings/training-curriculum/secure-browsing\
[13]: https://www.level-up.cc/platform/linux\
[14]: https://www.level-up.cc/platform/mac-os\
[15]: https://www.level-up.cc/platform/windows\
[16]: https://www.level-up.cc/print/316\
[17]: https://www.level-up.cc/printpdf/316\
