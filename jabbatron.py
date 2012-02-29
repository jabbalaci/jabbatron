#!/usr/bin/env python

"""
Interactive installer script for Ubuntu.

I take no responsibility for any possible 
loss of data on your computer. Use this
script at your own risk.

Jabba Laci
jabba.laci@gmail.com
"""

import re
import os
import sys
import webbrowser

HOME_DIR = os.path.expanduser('~')

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


def create_dir(item, in_home_dir=True):
    if in_home_dir:
        item = HOME_DIR + '/' + item
    if os.path.exists(item): print '{} exists'.format(item)
    else:
        os.mkdir(item)
        if os.path.exists(item): print '{} created'.format(item)


def wait():
    print
    raw_input('Press ENTER to continue...')
    main()


def bin_to_path_in_bashrc():
    reply = raw_input('Add ~/bin to PATH [y/n]? ')
    if reply == 'y':
        with open(BASHRC, 'a') as f:
            print >>f, PATH_BIN
    else: print 'no'


def step_01():
    for d in ['bin', 'tmp']:
        create_dir(d)
    #
    bin_to_path_in_bashrc()


def step_02():
    path = HOME_DIR + '/bin/good_shape.sh'
    path2 = HOME_DIR + '/bin/good_shape_safe.sh'
    if os.path.exists(path):
        print '{} exists'.format(path)
        return
    # else
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
    print """Open Ubuntu Software Center and install these:
  * Dropbox
  * Adobe Reader (first enable "Canonical Partners" in "Software Sources" and "sudo apt-get update")
  * Skype"""


def install(packages):
    cmd = 'sudo apt-get install ' + ' '.join(packages)
    print '#', cmd
    os.system(cmd)


def pip(packages):
    cmd = 'sudo pip install ' + ' '.join(packages) + ' -U'
    print '#', cmd
    os.system(cmd)


def step_04():
    install(['mc', 'konsole', 'okular'])


def step_05():
    install(['vim-gnome'])
    if not os.path.exists(HOME_DIR + '/.vimrc'):
        os.system("cd; wget {} -O .vimrc".format(VIMRC_URL))
    create_dir('tmp/vim')
    reply = raw_input('Set vim in .bashrc as your default editor [y/n]? ')
    if reply == 'y':
        with open(BASHRC, 'a') as f:
            print >>f, EDITOR
    else: print 'no'


def step_06():
    reply = raw_input('Add aliases to .bashrc [y/n]? ')
    if reply == 'y':
        with open(BASHRC, 'a') as f:
            print >>f, ALIASES
    else: print 'no'
    #
    install(['fortune-mod', 'cowsay'])


def step_07():
    install(['build-essential', 'git', 'subversion'])


def step_08():
    install(['wajig', 'apt-file', 'synaptic'])


def step_09():
    install(['texlive-base', 'texlive', 'texlive-latex-extra', 
             'texlive-metapost', 'texlive-science', 'texlive-fonts-extra'])


def step_10():
    url = 'http://help.github.com/mac-set-up-git/'
    print '#', url
    webbrowser.open(url)


def step_10b():
    reply = raw_input('Add aliases to .gitconfig [y/n]? ')
    if reply == 'y':
        with open(GITCONFIGRC, 'a') as f:
            print >>f, GITCONFIG
    else: print 'no'


def step_11():
    install(['xsel', 'kdiff3'])


def step_12():
    install(['python-pip'])


def step_12a():
    pip(['pip', 'ipython'])


def menu():
    os.system('clear')
    print """##### Jabbatron 0.1 #####
#   installer script    #
#  for virgin systems   #
#       q - quit        #
#########################"""
    print """(01)  prepare HOME directory (create ~/bin, ~/tmp, etc.)
(02)  good_shape.sh (create updater script in ~/bin)
(03)  dropbox, acroread, skype
(04)  mc, konsole (mc from official repo [old])
(05)  vim
(06)  aliases (in .bashrc)
(07)  development (build-essential, etc.)
(08)  apt-get et al. (wajig, synaptic, etc.)
(09)  latex
(10)  github setup
(10b) .gitconfig (add some aliases)
(11)  tools (xsel, kdiff3, etc.)
(12)  python-pip (via apt-get, run just once)
(12a) python stuff ([new] pip, ipython, etc.)"""
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
