#!/usr/bin/env python

"""
Interactive installer script for Ubuntu.

* Author:  Laszlo Szathmary, 2012 (<jabba.laci@gmail.com>)
* Website: <http://ubuntuincident.wordpress.com/2012/02/29/jabbatron/>
* GitHub:  <https://github.com/jabbalaci/jabbatron>

Menu points that contain 3 digits lead to submenus.

Menu points that contain 2 digits execute some operation(s).

I take no responsibility for any possible
loss of data on your computer.
Use this script at your own risk.
"""

__author__ = "Laszlo Szathmary (jabba.laci@gmail.com)"
__version__ = "0.2.6"
__date__ = "20120924"
__copyright__ = "Copyright (c) 2012 Laszlo Szathmary"
__license__ = "GPL"

import re
import os
import sys
import urllib2
import webbrowser
from subprocess import Popen, PIPE, STDOUT

HOME_DIR = os.path.expanduser('~')

autoflush_on = False

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

def create_dir(item, in_home_dir=True, sudo=False):
    if in_home_dir:
        item = HOME_DIR + '/' + item
    if os.path.exists(item):
        print '{} exists'.format(item)
    else:
        if not sudo:
            os.mkdir(item)
        else:    # sudo
            cmd = "sudo mkdir '{d}'".format(d=item)
            print '#', cmd
            os.system(cmd)
        if os.path.exists(item):
            print '{} created'.format(item)


def wait():
    print
    raw_input('Press ENTER to continue...')


def info():
    print """
h  - this help
q  - quit from submenu (back)
qq - quit from program
c  - clear screen"""
    wait()


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


def which(program):
    """
    Equivalent of the which command in Python.
    
    source: http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath = os.path.split(program)[0]
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def unbuffered():
    """Switch autoflush on."""
    global autoflush_on
    # reopen stdout file descriptor with write mode
    # and 0 as the buffer size (unbuffered)
    if not autoflush_on:
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        autoflush_on = True


def get_latest_mc_version():
    try:
        from BeautifulSoup import BeautifulSoup
    except:
        return 'Warning: for this you should install the beautifulsoup package.'
    # if BS is available
    text = urllib2.urlopen('http://www.midnight-commander.org/downloads').read()
    soup = BeautifulSoup(text)
    for tag in soup.findAll('div', {'class': 'description'}):
        desc = tag.text
        result = re.search('^(Midnight Commander v.*\(stable release\))', desc)
        if result:
            latest = result.group(1)
    #
    return latest


def get_complex_cmd_output(cmd, stderr=STDOUT):
    proc =  Popen(cmd, shell=True, stdout=PIPE, stderr=stderr)
    return proc.stdout.readlines()


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


def step_00b():
    """
    open the Python Adventures blog
    """
    url = 'https://pythonadventures.wordpress.com/'
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
    dropbox, acroread
    """
    print """Open Ubuntu Software Center and install these:
  * Dropbox
  * Adobe Reader (first enable "Canonical Partners" in "Software Sources" and "sudo apt-get update")"""


def step_03b():
    """
    skype
    """
    url = 'http://www.skype.com/intl/en/get-skype/on-your-computer/linux/'
    print '#', url
    webbrowser.open(url)


def step_04():
    """
    mc (from official repo [old])
    """
    if which('mc'):
        print 'It seems mc is already installed.'
        reply = raw_input('Do you want to reinstall mc [y/n]? ')
        if reply != 'y':
            print 'no'
            return

    # else install mc

    install('mc')
    if not os.path.exists(HOME_DIR + '/.mc'):
        create_dir('.mc')
    bfile = HOME_DIR + '/.mc/bindings'
    if not os.path.exists(bfile):
        os.system("cd; cd .mc; cp /etc/mc/mc.ext . && ln -s mc.ext bindings")
        if os.path.exists(bfile):
            print '# {} was created'.format(bfile)


def step_04b():
    """
    some essential packages:
    konsole, gnome-panel, etc.
    """
    install(['konsole', 'yakuake', 'gparted', 'okular', 'nautilus-open-terminal', 'gconf-editor', 'htop', 'nautilus-open-terminal', 'gnome-panel', 'xsel', 'xclip'])


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
             'texlive-metapost', 'texlive-science', 'texlive-fonts-extra', 'dvipng'])


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


def step_10b():
    """
    Git help
    """
    url = 'http://help.github.com/git-cheat-sheets/'
    print '#', url
    webbrowser.open(url)
    #
    url = 'http://progit.org/'
    print '#', url
    webbrowser.open(url)
    #
    url = 'http://git-scm.com/'
    print '#', url
    webbrowser.open(url)
    #
    url = 'http://schacon.github.com/git/user-manual.html'
    print '#', url
    webbrowser.open(url)
    #
    url = 'http://gitready.com/'
    print '#', url
    webbrowser.open(url)


def step_11():
    """
    tools (xsel, kdiff3, etc.)
    """
    install(['xsel', 'kdiff3', 'pdftk', 'imagemagick', 'unrar', 'comix', 'chmsee', 'gqview', 'curl'])


def step_12():
    """
    python-pip (via apt-get [old], run just once)
    """
    install('python-pip')


def step_12a():
    """
    Python, scrapers
    """
    install(['libxml2-dev', 'libxslt1-dev', 'python2.7-dev'])
    pip(['lxml', 'beautifulsoup', 'beautifulsoup4', 'scrapy'])


def step_12b():
    """
    Python, smaller things
    """
    pip(['pip', 'pep8', 'ipython', 'pymongo', 'pygments', 'reddit', 'pycurl', 'untangle', 'pylint'])
    pip(['sphinx', 'feedparser'])
    pip(['Flask', 'virtualenv'])


def step_12c():
    """
    Python IDEs
    """
    pip('spyder')
    add_repo('ninja-ide-developers/ninja-ide')
    install('ninja-ide')


def step_12d():
    """
    scientific python
    """
    pip('ipython')
    # numpy, scipy, matplotlib, pandas
    pip('numpy')
    install(['libatlas-base-dev', 'gfortran', 'libfreetype6-dev', 'libpng-dev'])
    pip(['scipy', 'matplotlib', 'pandas'])
    #
    install('python-sympy')


def step_12e():
    """
    Python, image processing, autopy
    """
    pip(['pil', 'pyscreenshot'])
    #
    install('libxtst-dev')
    pip('autopy')


def step_12f():
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


def step_12g():
    """
    python + apache on localhost
    """
    install('libapache2-mod-wsgi')
    install('python-django')


def step_12h():
    """
    python concurrency
    """
    install(['libevent-dev', 'python-all-dev'])
    pip('gevent')


def step_12i():
    """
    OpenCV (based on http://jayrambhia.wordpress.com/tag/opencv/)
    """
    li = ['libopencv-dev', 'build-essential', 'checkinstall',
          'cmake', 'pkg-config', 'yasm',
          'libtiff4-dev', 'libjpeg-dev', 'libjasper-dev',
          'libavcodec-dev', 'libavformat-dev', 'libswscale-dev',
          'libdc1394-22-dev', 'libxine-dev', 'libgstreamer0.10-dev', 
          'libgstreamer-plugins-base0.10-dev', 'libv4l-dev',
          'python-dev',
#          'python-numpy',    # I install it from source
          'libtbb-dev',
          'libqt4-dev', 'libgtk2.0-dev']
    install(li)
#    #
    print
    url = 'http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/'
    print '#', url
    webbrowser.open(url)
    print '# download the latest OpenCV and save it somewhere (to /opt for instance)'
    fpath = raw_input('Full path of the downloaded archive: ')
    (path, fname) = os.path.split(fpath)
    os.chdir(path)
    os.system('tar xvjf {}'.format(fname))
    os.chdir(re.sub('.tar.bz2', '', fname))
    os.system('mkdir build')
    os.chdir('build')
    os.system('cmake -D WITH_QT=ON -D WITH_XINE=ON -D WITH_OPENGL=ON -D WITH_TBB=ON -D BUILD_EXAMPLES=ON ..')
    os.system('make')
    os.system('sudo make install')
    os.chdir('../samples/c')
    os.system('chmod u+x build_all.sh')
    os.system('./build_all.sh')
    #
    cmd = "sudo sh -c 'echo /usr/local/lib >> /etc/ld.so.conf'"
    print '#', cmd
    os.system(cmd)
    #
    cmd = 'sudo ldconfig'
    print '#', cmd
    os.system(cmd)


def step_13():
    """
    multimedia (mplayer2, vlc, etc.)
    """
    install(['mplayer2', 'mencoder'])
    #
    add_repo('n-muench/vlc')
    install('vlc')
    #
# TODO
# didn't work with Ubuntu 12.04 last time I checked
#    add_repo('me-davidsansome/clementine')
#    install('clementine')
    #
    install(['minitube', 'soundconverter'])


def step_14():
    """
    LAMP (set up a LAMP environment)
    """
    url = 'https://ubuntuincident.wordpress.com/2010/11/18/installing-a-lamp-server/'
    print '#', url
    webbrowser.open(url)


def step_15():
    """
    gimp 2.8.x
    """
    add_repo('otto-kesselgulasch/gimp')
    install(['gimp', 'gimp-resynthesizer'])


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
    add_repo('tualatrix/ppa')
    install('ubuntu-tweak')
    #
    add_repo('diesch/testing')
    install('unsettings')
    #
    install('myunity')


def step_16b():
    """
    remove global menu (using 'unsettings' was not enough)
    """
    remove(['appmenu-gtk3', 'appmenu-gtk', 'appmenu-qt', 'firefox-globalmenu'])


def step_16c():
    """
    compizconfig-settings-manager
    """
    install('compizconfig-settings-manager')


def step_17a():
    """
    databases (sqlite3)
    """
    install('sqlite3')


def step_17b():
    """
    databases (mongodb)
    """
    mongodb()


def step_17c():
    """
    databases (mysql)
    """
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
    tesseract 3
    http://code.google.com/p/tesseract-ocr/wiki/ReadMe
    """
    install(['autoconf automake libtool', 'libpng12-dev', 'libjpeg62-dev', 'libtiff4-dev', 'zlib1g-dev'])
    #
    if True:
        os.chdir('/tmp')
        if not os.path.exists('leptonica-1.68.tar.gz'):
            os.system('wget http://www.leptonica.org/source/leptonica-1.68.tar.gz')
        os.system('tar xvzf leptonica-1.68.tar.gz')
        os.chdir('/tmp/leptonica-1.68')
        os.system('./autobuild')
        os.system('./configure')
        os.system('make')
        os.system('sudo make install')
        os.system('sudo ldconfig')
    #
    if True:
        os.chdir('/tmp')
        if not os.path.exists('tesseract-3.01.tar.gz'):
            os.system('wget http://tesseract-ocr.googlecode.com/files/tesseract-3.01.tar.gz')
        os.system('tar xvzf tesseract-3.01.tar.gz')
        os.chdir('/tmp/tesseract-3.01')
        os.system('./autogen.sh')
        os.system('./configure')
        os.system('make')
        os.system('sudo make install')
        os.system('sudo ldconfig')
    #
    os.chdir('/tmp')
    if not os.path.exists('tesseract-ocr-3.01.eng.tar.gz'):
        os.system('wget http://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.01.eng.tar.gz')
    os.system('tar xvzf tesseract-ocr-3.01.eng.tar.gz')
    os.system('sudo mv tesseract-ocr /usr/share')


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


def step_24():
    """
    Java
    """
    url = 'http://www.oracle.com/technetwork/java/javase/downloads/index.html'
    print '#', url
    webbrowser.open(url)


def step_25():
    """
    Java API 7
    """
    url = 'http://docs.oracle.com/javase/7/docs/api/'
    print '#', url
    webbrowser.open(url)


def step_26():
    """
    Flash videos are blue. Correct it.
    https://ubuntuincident.wordpress.com/2012/04/01/flash-videos-are-blue/
    """
    if not os.path.exists('/etc/adobe'):
        create_dir('/etc/adobe', in_home_dir=False, sudo=True)
        os.system('sudo chmod 755 /etc/adobe')
    cmd = "sudo sh -c 'echo EnableLinuxHWVideoDecode=1 > /etc/adobe/mms.cfg'"
    print '#', cmd
    os.system(cmd)
    cmd = "sudo sh -c 'echo OverrideGPUValidation=true >> /etc/adobe/mms.cfg'"
    print '#', cmd
    os.system(cmd)
    os.system('sudo chmod 644 /etc/adobe/mms.cfg')


def step_26b():
    """
    remove firefox-globalmenu
    """
    remove('firefox-globalmenu')


def step_27():
    """
    Java
    """
    url = 'http://www.oxygenxml.com/download_oxygenxml_editor.html'
    print '#', url
    webbrowser.open(url)


def step_28():
    """
    Midnight Commander from source
    """
    print 'Current version: ',
    mc = which('mc')
    if mc:
        print get_complex_cmd_output('mc -V | head -1')[0].strip()
    else:
        print 'not installed'
    print 'Latest stable release: ', get_latest_mc_version()

    print
    reply = raw_input('Continue [y/n]? ')
    if reply != 'y':
        return

    # else

    install(['libslang2-dev', 'libglib2.0-dev'])
    #
    url = 'http://www.midnight-commander.org/downloads'
    print '#', url
    webbrowser.open(url)
    print 'Paste in the URL of the latest stable release:'
    url = raw_input('mc-X.X.X.X.tar.bz2: ').strip()
    if not re.search('http://.*/mc-(\d+\.)+tar\.bz2$', url):
        print 'Error: not a valid URL.'
        wait()
        return
    fname_tar_bz2 = url.split('/')[-1]
    print '#', fname_tar_bz2
    fname = re.sub('.tar.bz2', '', fname_tar_bz2)
    print '#', fname
    os.chdir('/tmp')
    if not os.path.exists(fname_tar_bz2):
        os.system('wget {url}'.format(url=url))
    os.system('tar xvjf {0}'.format(fname_tar_bz2))
    os.chdir('/tmp/{0}'.format(fname))
    os.system('./configure')
    os.system('make')
    if os.path.isfile('src/mc'):
        remove('mc')
        os.system('sudo make install')


def step_30():
    """
    haskell
    """
    install('haskell-platform')


def step_40():
    """
    reinstall kernel module for vbox
    (when you get an error message after installing a new kernel)
    """
    cmd = 'sudo /etc/init.d/vboxdrv setup'
    print '#', cmd
    os.system(cmd)

##############
## submenus ##
##############

def submenu(msg, text):
    header(msg)
    print text
    while True:
        try:
            choice = raw_input('>>> ').strip()
        except EOFError:
            print
            print 'bye.'
            sys.exit(0)
        if choice == 'qq':
            print 'bye.'
            sys.exit(0)
        elif choice == 'q':
            menu()
            return
        elif choice in ('h', 'help'):
            info()
            submenu(msg, text)
        elif choice == 'c':
            submenu(msg, text)
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
                submenu(msg, text)
                break
            else:
                print 'Hm?'
        #
        elif len(choice) > 0:
            print 'Wat?'


def home_100():
    text = """(01)  create essential directories (~/bin, ~/tmp, etc.)
(02)  good_shape.sh (create in ~/bin or call it if exists)
(04)  mc (from official repo [old])
(04b) konsole, gparted, etc. (essential packages)
(05)  vim (with .vimrc)
(06)  aliases (in .bashrc)"""
    submenu('home', text)


def dev_110():
    text = """(07)  development (build-essential, etc.)
(07a) D language (dmd, rdmd)
(27)  oXygen XML Editor"""
    submenu('dev', text)


def git_120():
    text = """(10)  github setup
(10a) .gitconfig (add some aliases)
(10b) git help (cheat sheet, Pro Git book, manual, etc.)"""
    submenu('git', text)


def py_130():
    text = """(12)  python-pip (via apt-get [old], run just once)
(12a) python scrapers (lxml, beautifulsoup, scrapy)
(12b) python, smaller things (pip, pep8, untangle, etc.)
(12c) python IDEs (spyder, ninja-ide)
(12d) scientific python (ipython, numpy, scipy, matplotlib, pandas, sympy)
(12e) python image processing (PIL, pyscreenshot); autopy
(12f) pyp (The Pyed Piper)
(12g) python + apache on localhost
(12h) python concurrency (gevent)
(12i) OpenCV"""
    submenu('py', text)


def ubuntu_140():
    text = """(03)  dropbox, acroread
(03b) skype
(08)  apt-get et al. (wajig, synaptic, etc.)
(16)  tweaks (disable knotify4, install ubuntu-tweak, etc.)
(16b) disable global menu
(16c) compizconfig-settings-manager (ccsm)
(18)  create launcher (if not available upon right click on the Desktop)
(23)  virtualbox"""
    submenu('ubuntu', text)


def db_150():
    text = """(17a)  sqlite3
(17b)  mongodb
(17c)  mysql"""
    submenu('databases', text)


def browser_160():
    text = """(19)  essential Firefox add-ons
(20)  chromium
(26)  blue Flash (correct it)
(26b) remove firefox-globalmenu"""
    submenu('browser', text)


def source_170():
    text = """(21)  tesseract 3
(28)  mc"""
    submenu('source', text)


def games_180():
    text = """(22)  games (crack-attack, etc.)"""
    submenu('games', text)


def java_190():
    text = """(24)  Java SDK update
(25)  Java 7 API"""
    submenu('java', text)


def haskell_200():
    text = """(30)  install haskell"""
    submenu('haskell', text)


def admin_210():
    text = """(40)  reinstall kernel module for vbox"""
    submenu('admin', text)


###############
## main menu ##
###############

def header(msg):
    os.system('clear')
    width = 31
    text = '# {arrow}{msg}'.format(arrow=('-> ' if msg != 'main' else ''), msg=msg)
    print """###### Jabbatron {ver} ########
#  Jabbatron is good for you  #
###############################
{text}{space}#
###############################""".format(ver=__version__, msg=msg, text=text, space=' '*(width-len(text)-1))


def menu():
    header('main')
    print """(00)  The Ubuntu Incident (open blog)
(00b) Python Adventures (open blog)
(100) prepare HOME directory + install essential softwares...
(110) development (C/C++/D compilers, oXygen XML Editor, etc.)...
(09)  latex
(120) github...
(11)  tools (xsel, kdiff3, etc.)
(130) Python for World Domination...
(13)  multimedia (mplayer2, vlc, etc.)
(14)  LAMP (set up a LAMP environment)
(15)  gimp (2.8.x)
(140) Ubuntu (tweaks, extra softwares)...
(150) databases (sqlite3, mongodb, mysql)...
(160) browser(s)...
(170) install from source (mc, tesseract3)...
(180) games...
(190) Java...
(200) Haskell...
(210) admin panel
(h)   help
(q)   quit"""
    while True:
        try:
            choice = raw_input('>>> ').strip()
        except EOFError:
            print
            print 'bye.'
            sys.exit(0)
        if choice in ('q', 'qq'):
            print 'bye.'
            sys.exit(0)
        elif choice in ('h', 'help'):
            info()
            menu()
        elif choice == 'c':
            menu()
            break
        elif re.search('\d{3}', choice):
            found = False
            for f in globals():
                if re.search('[a-z]+_{choice}$'.format(choice=choice), f):
                    found = True
                    methodToCall = globals()[f]
                    methodToCall()
            if not found:
                print 'Unknown menu item.'
        elif re.search('\d+', choice):
            try:
                methodToCall = globals()['step_' + choice]
            except:
                methodToCall = None
            #
            if methodToCall:
                methodToCall()
                wait()
                menu()
                break
            else:
                print 'Hm?'
        #
        elif len(choice) > 0:
            print 'Wat?'


def new_item():
    steps = []
    for f in sorted(globals()):
        if f.startswith('step_'):
            steps.append(re.search('step_(.*)', f).group(1))
    print "Steps taken:"
    print "------------"
    print steps
    try:
        new_step = raw_input('Check availability: ').strip()
    except KeyboardInterrupt:
        print
        print 'quit.'
        sys.exit(0)
    #
    if new_step not in steps:
        print 'Available! :)'
    else:
        print 'Taken :('

        
def main(args):
    if len(args) == 0:
        menu()
    else:
        arg = args[0]
        if arg == '-new':
            new_item()
        else:
            print "Error: unknown parameter."
            sys.exit(1)

#############################################################################

if __name__ == "__main__":
    unbuffered()
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        main([])
