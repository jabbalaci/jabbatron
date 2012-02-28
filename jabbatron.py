#!/usr/bin/env python

import os
import sys

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


def step_01():
    for d in ['bin', 'tmp']:
        create_dir(d)


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


def step_03():
    print """Open Ubuntu Software Center and install these:
  * Dropbox
  * Adobe Reader
  * Skype"""


def install(packages):
    cmd = 'sudo apt-get install ' + ' '.join(packages)
    print '#', cmd
    os.system(cmd)


def step_04():
    install(['mc', 'konsole'])


def step_05():
    install(['vim-gnome'])


def menu():
    os.system('clear')
    print """##### Jabbatron 0.1 #####
#   installer script    #
#  for virgin systems   #
#       q - quit        #
#########################"""
    print """(01) prepare HOME directory (create ~/bin, ~/tmp, etc.)
(02) good_shape.sh (create updater script in ~/bin)
(03) dropbox, acroread, skype
(04) mc, konsole (mc from official repo [old])
(05) vim"""
    while True:
        choice = raw_input('>>> ').strip()
        if choice == 'q':
            print 'bye.'
            sys.exit(0)
        elif choice == '01':
            step_01()
            wait()
            break
        elif choice == '02':
            step_02()
            wait()
            break
        elif choice == '03':
            step_03()
            wait()
            break
        elif choice == '04':
            step_04()
            wait()
            break
        elif choice == '05':
            step_05()
            wait()
            break
        elif len(choice) > 0:
            print 'Wat?'


def main():
    menu()

#############################################################################

if __name__ == "__main__":
    main()
