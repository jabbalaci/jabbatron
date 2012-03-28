jabbatron
=========

Interactive installer script for Ubuntu.

* Author:  Laszlo Szathmary, 2012 (<jabba.laci@gmail.com>)
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

Screenshot
----------

    ##### Jabbatron 0.1 #####
    #   installer script    #
    #  for virgin systems   #
    #########################
    (00)  The Ubuntu Incident (open blog)
    (01)  prepare HOME directory (create ~/bin, ~/tmp, etc.)
    (02)  good_shape.sh (create in ~/bin or call it if exists)
    (03)  dropbox, acroread, skype
    (04)  mc, konsole (mc from official repo [old])
    (05)  vim (with .vimrc)
    (06)  aliases (in .bashrc)
    (06a) MS-DOS prompt emulation (in .bashrc)
    (07)  development (build-essential, etc.)
    (07a) D language (dmd, rdmd)
    (08)  apt-get et al. (wajig, synaptic, etc.)
    (09)  latex
    (10)  github setup
    (10a) .gitconfig (add some aliases)
    (11)  tools (xsel, kdiff3, etc.)
    (12)  python-pip (via apt-get [old], run just once)
    (12a) python stuff ([new] pip, ipython, etc.)
    (12b) pyp (The Pyed Piper)
    (13)  multimedia (mplayer2, vlc, clementine, etc.)
    (14)  LAMP (set up a LAMP environment)
    (15)  gimp
    (16)  tweaks (disable knotify4, install ubuntu-tweak, etc.)
    (16a) remove global menu
    (17)  databases (sqlite3, mongodb, mysql)
    (18)  create launcher (if not available upon right click on the Desktop)
    (19)  essential Firefox add-ons
    (20)  chromium
    (21)  firefox from PPA (beta channel)
    (22)  games (crack-attack, etc.)
    (23)  virtualbox
    (q)   quit
    >>>

