jabbatron
=========

Interactive installer script for Ubuntu.

* Author:  Laszlo Szathmary, 2012--2013 (<jabba.laci@gmail.com>)
* Website: <http://ubuntuincident.wordpress.com/2012/02/29/jabbatron/>
* GitHub:  <https://github.com/jabbalaci/jabbatron>

If you have a newly installed (virgin) system,
you can easily update it with this script.

I've tested it with Python 2.7 under Ubuntu Linux.

Installation
------------

jabbatron is now available via pypi:

    sudo pip install jabbatron

Or, simply download `jabbatron.py` and launch it.
One of the design goals is to keep this script self-contained, so it will
always be just one file without any dependencies (or with some
minimal dependencies).

Screenshots
-----------

    ###### Jabbatron 0.3.0 ########
    #  Jabbatron is good for you  #
    ###############################
    # main                        #
    ###############################
    (000) blogs...
    (100) prepare HOME directory + install essential softwares...
    (110) development (C/C++/D compilers, oXygen XML Editor, etc.)...
    (120) github...
    (130) Python for World Domination...
    (135) multimedia...
    (140) Ubuntu (tweaks, extra softwares)...
    (150) databases (sqlite3, mongodb, mysql)...
    (160) browser(s)...
    (170) install from source (mc, tesseract3)...
    (180) games...
    (190) Java...
    (200) Haskell...
    (210) admin panel...
    (220) json...
    (230) Google App Engine...
    (h)   help
    (q)   quit
    >>> 210

After entering menu 210 (admin panel):

    ###### Jabbatron 0.3.0 ########
    #  Jabbatron is good for you  #
    ###############################
    # -> admin                    #
    ###############################
    (02)  good_shape.sh (create in ~/bin or call it if exists)
    (40)  reinstall kernel module for vbox and start VirtualBox
    (34)  upgrade Ubuntu to a new release
    (42)  sudo apt-get autoremove
    >>>

With the command "h" you can get help any time. You can also type
in any keyword and the script will show related modules. Example:

    ###### Jabbatron 0.3.0 ########
    #  Jabbatron is good for you  #
    ###############################
    # -> admin                    #
    ###############################
    (02)  good_shape.sh (create in ~/bin or call it if exists)
    (40)  reinstall kernel module for vbox and start VirtualBox
    (34)  upgrade Ubuntu to a new release
    (42)  sudo apt-get autoremove
    >>> mp3
    (31)  mplayer2, vlc, etc.
    >>> mc
    (04)  mc (from official repo [old])
    (28)  Midnight Commander from source
    >>> h
    
    h  - this help
    q  - quit from submenu (back)
    qq - quit from program
    c  - clear screen
    
    Press ENTER to continue...
