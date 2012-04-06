#!/usr/bin/env python

"""
Interactive installer script for Ubuntu.

* Author:  Laszlo Szathmary, 2012 (<jabba.laci@gmail.com>)
* Website: <http://ubuntuincident.wordpress.com/2012/02/29/jabbatron/>
* GitHub:  <https://github.com/jabbalaci/jabbatron>

I take no responsibility for any possible
loss of data on your computer.
Use this script at your own risk.
"""

__author__ = "Laszlo Szathmary (jabba.laci@gmail.com)"
__version__ = "0.1.4"
__date__ = "20120406"
__copyright__ = "Copyright (c) 2012 Laszlo Szathmary"
__license__ = "GPL"

import re
import os
import sys
import webbrowser

HOME_DIR = os.path.expanduser('~')

REMOVE = 'remove'
INSTALL = 'install'

GOOD_SHAPE = '''#!/bin/bash

sudo dpkg --configure -a\\
&& sudo apt-get -f install\\
&& sudo apt-get --fix-missing install\\
&& sudo apt-get clean\\
&& sudo apt-get update\\
&& sudo apt-get upgrade\\
&& sudo apt-get dist-upgrade\\
&& sudo apt-get clean\\
&& sudo apt-get autoremove'''

ALIASES = """# jabbatron
alias md='mkdir'
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias d='ls -al'
#alias mc='. /usr/share/mc/bin/mc-wrapper.sh'
alias mc='. /usr/local/libexec/mc/mc-wrapper.sh'
alias run='chmod u+x'
alias cpc='CWD_LAC="`pwd`"'
alias cdc='cd "$CWD_LAC"'
alias rid='chmod 644'
alias ridd='chmod 755'
alias tailf='tail -f'
alias cls='clear'
alias nh='nautilus . 2>/dev/null'
alias p='ipython'
alias kill9='kill -9'

# /usr/games/fortune | /usr/games/cowthink
"""

GITCONFIG = """# jabbatron
[merge]
    tool = kdiff3
[alias]
    mylog = log --pretty=format:'%h - %an, %ar : %s'

    st = status
    br = branch
    ci = commit
    co = checkout
    df = diff
    dt = difftool
"""

MSDOS = """# jabbatron
function msdos_pwd
{
    local dir="`pwd`"
    dir=${dir/$HOME/'~'}

    echo $dir | tr '/' '\\\\'
}

export PS1='C:`msdos_pwd`> '

echo Starting MS-DOS...
echo
echo
echo HIMEM is testing extended memory...done.
echo
"""

WGETRC = """# custom .wgetrc file

# user_agent = Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:11.0) Gecko/20100101 Firefox/11.0"""

VIMRC_URL = 'https://raw.github.com/jabbalaci/jabbatron/master/vimrc.txt'

BASHRC = HOME_DIR + '/.bashrc'
GITCONFIGRC = HOME_DIR + '/.gitconfig'

EDITOR = """# jabbatron
EDITOR=/usr/bin/vim
export EDITOR
"""

PATH_BIN = """# jabbatron
PATH=$PATH:$HOME/bin
export PATH
"""


#############
## helpers ##
#############

def create_dir(item, in_home_dir=True):
    if in_home_dir:
        item = HOME_DIR + '/' + item
    if os.path.exists(item):
        print '{} exists'.format(item)
    else:
        os.mkdir(item)
        if os.path.exists(item):
            print '{} created'.format(item)


def wait():
    print
    raw_input('Press ENTER to continue...')
    main()


def bin_to_path_in_bashrc():
    reply = raw_input('Add ~/bin to PATH [y/n]? ')
    if reply == 'y':
        with open(BASHRC, 'a') as f:
            print >>f, PATH_BIN
    else:
        print 'no'


def add_wgetrc():
    fname = HOME_DIR + '/.wgetrc'
    if os.path.exists(fname):
        print '{} exists'.format(fname)
    else:
        with open(fname, 'w') as f:
            print >>f, WGETRC
        if os.path.exists(fname):
            print '{} created'.format(fname)
            os.system('chmod 600 {f}'.format(f=fname))


def call_good_shape():
    print '# executing ~/bin/good_shape.sh'
    os.system(HOME_DIR + '/bin/good_shape.sh')


def install_remove(packages, what=INSTALL):
    if type(packages) == str:
        cmd = 'sudo apt-get {what} '.format(what=what) + packages
    elif type(packages) == list:
        cmd = 'sudo apt-get {what} '.format(what=what) + ' '.join(packages)
    else:
        print >>sys.stderr, \
            'Error: strange argument for {what}().'.format(what=what)
        sys.exit(1)
    # if everything was OK
    print '#', cmd
    os.system(cmd)


def install(packages):
    install_remove(packages, INSTALL)


def remove(packages):
    install_remove(packages, REMOVE)


def pip(packages):
    if type(packages) == str:
        cmd = 'sudo pip install ' + packages + ' -U'
    elif type(packages) == list:
        cmd = 'sudo pip install ' + ' '.join(packages) + ' -U'
    else:
        print >>sys.stderr, 'Error: strange argument for pip().'
        sys.exit(1)
    # if everything was OK
    print '#', cmd
    os.system(cmd)


def add_repo(repo):
    cmd = 'sudo add-apt-repository ppa:{repo}'.format(repo=repo)
    print '#', cmd
    os.system(cmd)
    cmd = 'sudo apt-get update'
    print '#', cmd
    os.system(cmd)


def mongodb():
    reply = raw_input('Do you want to install MongoDB [y/n]? ')
    if reply != 'y':
        print 'no'
    else:
        cmd = 'sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10'
        print '#', cmd
        os.system(cmd)
        #
        cmd = "sudo sh -c 'echo \# jabbatron >> /etc/apt/sources.list'"
        print '#', cmd
        os.system(cmd)
        cmd = "sudo sh -c 'echo deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen >> /etc/apt/sources.list'"
        print '#', cmd
        os.system(cmd)
        #
        os.system('sudo apt-get update')
        install('mongodb-10gen')
        #
        pip('pymongo')


###########
## steps ##
###########

def step_00():
    """
    open the Ubuntu Incident blog
    """
    url = 'https://ubuntuincident.wordpress.com/'
    print '#', url
    webbrowser.open(url)


def step_01():
    """
    prepare HOME directory (create ~/bin, ~/tmp)
    """
    for d in ['bin', 'tmp']:
        create_dir(d)
    #
    bin_to_path_in_bashrc()
    add_wgetrc()


def step_02():
    """
    good_shape.sh (create updater script in ~/bin)
    if exists: call it
    """
    path = HOME_DIR + '/bin/good_shape.sh'
    path2 = HOME_DIR + '/bin/good_shape_safe.sh'
    if os.path.exists(path):
        print '{} exists'.format(path)
        call_good_shape()
    else:
        create_dir('bin')
        with open(path, 'w') as f:
            print >>f, GOOD_SHAPE
        if os.path.exists(path):
            print '{} created'.format(path)
            os.system('chmod u+x {p}'.format(p=path))
        if not os.path.exists(path2) and os.path.exists(path):
            os.system('grep -v clean {p} >{p2}'.format(p=path, p2=path2))
            if os.path.exists(path2):
                print '{} created'.format(path2)
                os.system('chmod u+x {p2}'.format(p2=path2))
        #
        bin_to_path_in_bashrc()


def step_03():
    """
    dropbox, acroread, skype
    """
    print """Open Ubuntu Software Center and install these:
  * Dropbox
  * Adobe Reader (first enable "Canonical Partners" in "Software Sources" and "sudo apt-get update")
  * Skype"""


def step_04():
    """
    mc, konsole (mc from official repo [old])
    """
    install(['mc', 'konsole', 'okular', 'nautilus-open-terminal', 'gconf-editor', 'htop'])
    if not os.path.exists(HOME_DIR + '/.mc'):
        create_dir('.mc')
    bfile = HOME_DIR + '/.mc/bindings'
    if not os.path.exists(bfile):
        os.system("cd; cd .mc; cp /etc/mc/mc.ext . && ln -s mc.ext bindings")
        if os.path.exists(bfile):
            print '# {} was created'.format(bfile)


def step_05():
    """
    vim + .vimrc
    """
    install('vim-gnome')
    if not os.path.exists(HOME_DIR + '/.vimrc'):
        os.system("cd; wget {} -O .vimrc".format(VIMRC_URL))
    create_dir('tmp/vim')
    reply = raw_input('Set vim in .bashrc as your default editor [y/n]? ')
    if reply == 'y':
        with open(BASHRC, 'a') as f:
            print >>f, EDITOR
    else:
        print 'no'


def step_06():
    """
    aliases (in .bashrc)
    """
    reply = raw_input('Add aliases to .bashrc [y/n]? ')
    if reply == 'y':
        with open(BASHRC, 'a') as f:
            print >>f, ALIASES
    else:
        print 'no'
    #
    install(['fortune-mod', 'cowsay'])


def step_06a():
    """
    MS-DOS prompt emulation (in .bashrc)
    """
    reply = raw_input('Add MS-DOS prompt emulation to .bashrc [y/n]? ')
    if reply == 'y':
        with open(BASHRC, 'a') as f:
            print >>f, MSDOS
    else:
        print 'no'


def step_07():
    """
    development (build-essential, git, subversion)
    """
    install(['build-essential', 'git', 'subversion', 'clang', 'gdc', 'codeblocks'])


def step_07a():
    """
    D language
    """
    url = 'http://www.digitalmars.com/d/download.html'
    print '#', url
    webbrowser.open(url)


def step_08():
    """
    apt-get et al. (wajig, synaptic, etc.)
    """
    install(['wajig', 'apt-file', 'synaptic'])


def step_09():
    """
    latex
    """
    install(['texlive-base', 'texlive', 'texlive-latex-extra',
             'texlive-metapost', 'texlive-science', 'texlive-fonts-extra'])


def step_10():
    """
    github setup (how to create ssh public key)
    """
    url = 'http://help.github.com/mac-set-up-git/'
    print '#', url
    webbrowser.open(url)


def step_10a():
    """
    .gitconfig (add some aliases)
    """
    reply = raw_input('Add aliases to .gitconfig [y/n]? ')
    if reply == 'y':
        with open(GITCONFIGRC, 'a') as f:
            print >>f, GITCONFIG
    else:
        print 'no'


def step_11():
    """
    tools (xsel, kdiff3, etc.)
    """
    install(['xsel', 'kdiff3', 'pdftk', 'imagemagick', 'unrar', 'comix', 'chmsee', 'gqview', 'curl'])
#    add_repo('alexx2000/doublecmd')
#    install('doublecmd-gtk')


def step_12():
    """
    python-pip (via apt-get [old], run just once)
    """
    install('python-pip')


def step_12a():
    """
    python stuff ([new] pip, ipython, etc.)
    """
    install(['libxml2-dev', 'libxslt1-dev', 'python2.7-dev'])
    pip(['pip', 'pep8', 'ipython', 'pymongo', 'beautifulsoup', 'pygments', 'lxml', 'scrapy', 'reddit', 'pycurl', 'untangle'])
    # numpy, scipy, matplotlib, pandas
    pip('numpy')
    install(['libatlas-base-dev', 'gfortran', 'libfreetype6-dev', 'libpng-dev'])
    pip(['scipy', 'matplotlib', 'pandas'])
    #
    pip(['pil', 'pyscreenshot'])
    #
    install('libxtst-dev')
    pip('autopy')


def step_12b():
    """
    pyp from http://code.google.com/p/pyp/
    """
    if os.path.isdir(HOME_DIR + '/bin'):
        url = 'http://pyp.googlecode.com/files/pyp'
        out = HOME_DIR + '/bin/pyp'
        try:
            os.unlink(out)
        except:
            pass
        os.system('wget {url} -O {out}'.format(url=url, out=out))
        os.system('chmod 700 {out}'.format(out=out))
        print '# pyp fetched'


def step_13():
    """
    multimedia (mplayer2, vlc, clementine, etc.)
    """
    install('mplayer2')
    #
    add_repo('n-muench/vlc')
    install('vlc')
    #
    add_repo('me-davidsansome/clementine')
    install('clementine')
    #
    install('minitube')


def step_14():
    """
    LAMP (set up a LAMP environment)
    """
    url = 'https://ubuntuincident.wordpress.com/2010/11/18/installing-a-lamp-server/'
    print '#', url
    webbrowser.open(url)


def step_15():
    """
    gimp
    """
    install('gimp')


def step_16():
    """
    tweaks (disable knotify4, install ubuntu-tweak, etc.)
    """
    oldpath = '/usr/bin/knotify4'
    newpath = '/usr/bin/knotify4.bak'
    if os.path.exists(oldpath):
        cmd = 'sudo mv {old} {new}'.format(old=oldpath, new=newpath)
        print '#', cmd
        os.system(cmd)
    else:
        print '# already disabled'
    #
    install('ubuntu-tweak')


def step_16a():
    """
    remove global menu
    """
    remove(['appmenu-gtk3', 'appmenu-gtk', 'appmenu-qt', 'firefox-globalmenu'])


def step_17():
    """
    databases (sqlite3, mongodb)
    """
    install('sqlite3')
    mongodb()
    install(['mysql-server', 'mysql-client', 'python-mysqldb'])


def step_18():
    """
    Create Launcher is back. In newer Ubuntus, it's not available
    upon right click on the Desktop.
    """
    os.system('gnome-desktop-item-edit ~/Desktop/ --create-new')


def step_19():
    """
    list of essential Firefox add-ons
    """
    url = 'https://ubuntuincident.wordpress.com/2011/03/14/essential-firefox-add-ons/'
    print '#', url
    webbrowser.open(url)


def step_20():
    """
    chromium
    """
    install('chromium-browser')


def step_21():
    """
    firefox from PPA (beta channel)
    """
    add_repo('mozillateam/firefox-next')
    install('firefox')


def step_22():
    """
    games (crack-attack, tents, etc.)
    """
    install(['crack-attack', 'sgt-puzzles'])


def step_23():
    """
    virtualbox
    """
    url = 'https://www.virtualbox.org/wiki/Linux_Downloads'
    print '#', url
    webbrowser.open(url)


##########
## menu ##
##########

def menu():
    os.system('clear')
    print """##### Jabbatron {ver} #####
#    installer  script    #
#   for  virgin systems   #
###########################""".format(ver=__version__)
    print """(00)  The Ubuntu Incident (open blog)
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
(q)   quit"""
    while True:
        try:
            choice = raw_input('>>> ').strip()
        except EOFError:
            print
            print 'bye.'
            sys.exit(0)
        if choice == 'q':
            print 'bye.'
            sys.exit(0)
        elif choice == 'c':
            main()
            break
        elif re.search('\d+', choice):
            try:
                methodToCall = globals()['step_' + choice]
            except:
                methodToCall = None
            #
            if methodToCall:
                methodToCall()
                wait()
                break
            else:
                print 'Hm?'
        #
        elif len(choice) > 0:
            print 'Wat?'


def main():
    menu()

#############################################################################

if __name__ == "__main__":
    main()
