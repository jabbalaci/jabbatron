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
__version__ = "0.2.8"
__date__ = "20121030"
__copyright__ = "Copyright (c) 2012 Laszlo Szathmary"
__license__ = "GPL"

import re
import os
import sys
import urllib2
import webbrowser
from subprocess import call, Popen, PIPE, STDOUT

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
alias rid='chmod 644'
alias ridd='chmod 755'
alias tailf='tail -f'
alias cls='clear'
alias nh='nautilus . 2>/dev/null'
alias p='ipython'
alias kill9='kill -9'
alias tm='tmux'

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

# user_agent = Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0"""

VIMRC_URL = 'https://raw.github.com/jabbalaci/jabbatron/master/vimrc.txt'
TMUX_CONF_URL = 'https://raw.github.com/jabbalaci/jabbatron/master/tmux.conf.txt'

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

TERMINATOR_RC = HOME_DIR + '/.config/terminator/config'

TERMINATOR_CONFIG = """# jabbatron
[keybindings]
full_screen = <Ctrl><Shift>F11"""


#############
## helpers ##
#############

"""
This dictionary will contain tags for each module (here a module is a function). 
Example:
'step_00' => ['blog', 'ubuntu']
"""
TAGS = {}


def tags(keywords):
    def add_tag(function_name, tag):
        global TAGS
        if function_name in TAGS:
            TAGS[function_name].add(tag)
        else:
            TAGS[function_name] = set()
            TAGS[function_name].add(tag)
    #
    caller_function_name = sys._getframe(1).f_code.co_name
    if type(keywords) == str:
        add_tag(caller_function_name, keywords)
    if type(keywords) == list:
        for k in keywords:
            add_tag(caller_function_name, k)


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
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=stderr)
    return proc.stdout.readlines()


###########
## steps ##
###########

def step_00():
    """
    open the Ubuntu Incident blog
    """
    tags(['blog', 'ubuntu', 'incident', 'jabba'])
    #
    url = 'https://ubuntuincident.wordpress.com/'
    print '#', url
    webbrowser.open(url)


def step_00b():
    """
    open the Python Adventures blog
    """
    tags(['python', 'blog', 'jabba'])
    #
    url = 'https://pythonadventures.wordpress.com/'
    print '#', url
    webbrowser.open(url)


def step_01():
    """
    prepare HOME directory (create ~/bin, ~/tmp)
    """
    tags(['home', 'directory', 'bin', 'tmp'])
    #
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
    tags(['good_shape', 'good_shape.sh', 'good shape', 'installer', 'script'])
    #
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


def step_38():
    """
    current version of Ubuntu
    """
    tags(['ubuntu', 'version'])
    #
    with open('/etc/issue') as f:
        version = f.read().strip()
    print version


def step_03():
    """
    dropbox, acroread
    """
    tags(['dropbox', 'acroread', 'adobe', 'pdf'])
    #
    print """Open Ubuntu Software Center and install these:
  * Dropbox
  * Adobe Reader (first enable "Canonical Partners" in "Software Sources" and "sudo apt-get update")"""


def step_03b():
    """
    skype
    """
    tags(['skype'])
    #
    url = 'http://www.skype.com/intl/en/get-skype/on-your-computer/linux/'
    print '#', url
    webbrowser.open(url)


def step_04():
    """
    mc (from official repo [old])
    """
    tags(['mc', 'bindings', 'extension', 'extensions'])
    #
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
    tags(['konsole', 'yakuake', 'gparted', 'okular', 'pdf', 'nautilus', 'gconf', 'htop', 'gnome-panel', 'gnome', 'gnome panel', 'xsel', 'xclip', 'clipboard'])
    tags(['terminator', 'config'])
    #
    install(['konsole', 'yakuake', 'gparted', 'okular', 'nautilus-open-terminal', 'gconf-editor', 'htop', 'gnome-panel', 'xsel', 'xclip'])
    install('terminator')
    reply = raw_input('Add terminator config file [y/n]? ')
    if reply == 'y':
        create_dir('.config/terminator')
        with open(TERMINATOR_RC, 'a') as f:
            print >>f, TERMINATOR_CONFIG
    else:
        print 'no'


def step_05():
    """
    vim + .vimrc
    """
    tags(['vim', 'vimrc', '.vimrc', 'config'])
    #
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


def step_33():
    """
    tmux + .tmux.conf
    """
    tags(['tmux', 'config'])
    #
    install('tmux')
    print
    reply = raw_input('Download .tmux.conf file [y/n]? ')
    if reply == 'y':
        os.system("cd; wget {} -O .tmux.conf".format(TMUX_CONF_URL))
    else:
        print 'no'


def step_06():
    """
    aliases (in .bashrc)
    """
    tags(['alias', 'aliases', 'bashrc', '.bashrc', 'config', 'fortune', 'cowsay', 'cowthink', 'cow'])
    #
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
    tags(['msdos', 'dos', 'microsoft', 'prompt', 'emulator', 'emulation'])
    #
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
    tags(['development', 'git', 'svn', 'subversion', 'clang', 'programming'])
    #
    install(['build-essential', 'git', 'subversion', 'clang', 'gdc', 'codeblocks'])


def step_07a():
    """
    D language
    """
    tags(['d', 'd language', 'd lang', 'dmd', 'rdmd'])
    #
    dmd = which('dmd')
    if dmd:
        print 'Installed version:',
        print get_complex_cmd_output('dmd | head -1')[0].strip()
    else:
        print 'Not installed.'
    url = 'http://www.digitalmars.com/d/download.html'
    print '#', url
    webbrowser.open(url)


def step_08():
    """
    apt-get et al. (wajig, synaptic, etc.)
    """
    tags(['wajig', 'apt-get', 'apt-file', 'packages', 'synaptic'])
    #
    install(['wajig', 'apt-file', 'synaptic'])


def step_09():
    """
    latex
    """
    tags(['latex', 'texlive', 'metapost'])
    #
    install(['texlive-base', 'texlive', 'texlive-latex-extra',
             'texlive-metapost', 'texlive-science', 'texlive-fonts-extra', 'dvipng'])


def step_10():
    """
    github setup (how to create ssh public key)
    """
    tags(['git', 'github', 'ssh'])
    #
    url = 'http://help.github.com/mac-set-up-git/'
    print '#', url
    webbrowser.open(url)


def step_10a():
    """
    .gitconfig (add some aliases)
    """
    tags(['git', 'gitconfig', 'config', 'alias', 'aliases'])
    #
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
    tags(['git', 'help'])
    #
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
    tags(['tools', 'utils', 'xsel', 'xclip', 'kdiff3', 'meld', 'pdf', 'pdftk', 'imagemagick', 'rar', 'unrar', 'comix', 'comics', 'viewer'])
    tags(['chm', 'chmsee', 'gqview', 'image', 'image viewer', 'curl'])
    #
    install(['xsel', 'xclip', 'kdiff3', 'meld', 'pdftk', 'imagemagick', 'unrar', 'comix', 'chmsee', 'gqview', 'curl'])


def step_12():
    """
    python-pip (via apt-get [old], run just once)
    """
    tags(['python', 'pip'])
    #
    install('python-pip')


def step_12a():
    """
    Python, scrapers
    """
    tags(['xml', 'libxml', 'python', 'scraper', 'lxml', 'beautifulsoup', 'bsoup', 'bs', 'bs4', 'scrapy', 'css', 'cssselect'])
    #
    install(['libxml2-dev', 'libxslt1-dev', 'python2.7-dev'])
    pip(['lxml', 'beautifulsoup', 'beautifulsoup4', 'scrapy', 'cssselect'])


def step_12b():
    """
    Python, smaller things
    """
    tags(['pip', 'pep8', 'ipython', 'python', 'pymongo', 'mongodb', 'pygments', 'reddit', 'curl', 'pycurl'])
    tags(['untangle', 'xml', 'pylint', 'sphinx', 'feed', 'feedparser', 'flask', 'virtualenv'])
    #
    pip(['pip', 'pep8', 'ipython', 'pymongo', 'pygments', 'reddit', 'pycurl', 'untangle', 'pylint'])
    pip(['sphinx', 'feedparser'])
    pip(['Flask', 'virtualenv'])


def step_12c():
    """
    Python IDEs
    """
    tags(['spyder', 'python', 'ide', 'ninja', 'ninja-ide'])
    #
    pip('spyder')
    add_repo('ninja-ide-developers/ninja-ide')
    install('ninja-ide')


def step_12d():
    """
    scientific python
    """
    tags(['python', 'ipython', 'science', 'scientific', 'numpy', 'fortran', 'gfortran'])
    tags(['scipy', 'matplotlib', 'pandas', 'sympy', 'data'])
    #
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
    tags(['python', 'pil', 'image', 'screenshot', 'autopy'])
    #
    pip(['pil', 'pyscreenshot'])
    #
    install('libxtst-dev')
    pip('autopy')


def step_12f():
    """
    pyp from http://code.google.com/p/pyp/
    """
    tags(['pyp', 'python'])
    #
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
    tags(['python', 'apache', 'apache2', 'wsgi', 'django', 'webserver', 'localhost'])
    #
    install('libapache2-mod-wsgi')
    install('python-django')


def step_12h():
    """
    python concurrency
    """
    tags(['python', 'gevent', 'concurrency'])
    #
    install(['libevent-dev', 'python-all-dev'])
    pip('gevent')


def step_12i():
    """
    OpenCV (based on http://jayrambhia.wordpress.com/tag/opencv/)
    """
    tags(['opencv', 'install', 'source', 'build'])
    #
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


def step_12j():
    """
    pattern
    http://www.clips.ua.ac.be/pages/pattern
    """
    tags(['python', 'pattern'])
    #
    pip('pattern')


def step_31():
    """
    multimedia (mplayer2, vlc, etc.)
    """
    tags(['multimedia', 'mplayer', 'mplayer2', 'vlc', 'mencoder'])
    tags(['minitube', 'youtube', 'soundconverter', 'sound', 'converter', 'mp3'])
    #
    install(['mplayer2', 'mencoder'])
    #
    #add_repo('n-muench/vlc')    # not needed in Ubuntu 12.10
    install('vlc')
    #
# TODO
# didn't work with Ubuntu 12.04 last time I checked
#    add_repo('me-davidsansome/clementine')
#    install('clementine')
    #
    install(['minitube', 'soundconverter'])


def step_32():
    """
    OpenShot video editor (openshot.org)
    """
    tags(['openshot', 'video', 'editor', 'video editor'])
    #
    add_repo('jonoomph/openshot-edge')
    install(['openshot', 'openshot-doc'])


def step_14():
    """
    LAMP (set up a LAMP environment)
    """
    tags(['lamp', 'linux', 'apache', 'mysql', 'php'])
    #
    url = 'https://ubuntuincident.wordpress.com/2010/11/18/installing-a-lamp-server/'
    print '#', url
    webbrowser.open(url)


#def step_15():
#    """
#    gimp 2.8.x
#    """
#    add_repo('otto-kesselgulasch/gimp')
#    install(['gimp', 'gimp-resynthesizer'])


def step_16():
    """
    tweaks (disable knotify4, install ubuntu-tweak, etc.)
    """
    tags(['tweak', 'tweaks', 'knotify4', 'disable', 'ubuntu-tweak', 'ubuntu'])
    tags(['unsettings', 'myunity'])
    #
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
    tags(['global menu', 'disable'])
    #
    remove(['appmenu-gtk3', 'appmenu-gtk', 'appmenu-qt', 'firefox-globalmenu'])


def step_16c():
    """
    compizconfig-settings-manager
    """
    tags(['compiz', 'ccsm'])
    #
    install('compizconfig-settings-manager')


def step_17a():
    """
    databases (sqlite3)
    """
    tags(['database', 'databases', 'sqlite3'])
    #
    install('sqlite3')


def step_17b():
    """
    databases (mongodb)
    """
    tags(['database', 'databases', 'mongodb'])
    #
    mongodb()


def step_17c():
    """
    databases (mysql)
    """
    tags(['database', 'databases', 'mysql', 'python'])
    #
    install(['mysql-server', 'mysql-client', 'python-mysqldb'])


def step_18():
    """
    Create Launcher is back. In newer Ubuntus, it's not available
    upon right click on the Desktop.
    """
    tags(['launcher', 'desktop'])
    #
    os.system('gnome-desktop-item-edit ~/Desktop/ --create-new')


def step_19():
    """
    list of essential Firefox add-ons
    """
    tags(['browser', 'firefox', 'add-on', 'addon', 'plugin'])
    #
    url = 'https://ubuntuincident.wordpress.com/2011/03/14/essential-firefox-add-ons/'
    print '#', url
    webbrowser.open(url)


def step_20():
    """
    chromium
    """
    tags(['browser', 'google', 'chromium', 'chrome'])
    #
    install('chromium-browser')


def step_21():
    """
    tesseract 3
    http://code.google.com/p/tesseract-ocr/wiki/ReadMe
    """
    tags(['tesseract', 'ocr'])
    #
    install(['autoconf automake libtool', 'libpng12-dev', 'libjpeg62-dev', 'libtiff4-dev', 'zlib1g-dev'])
    #
    if True:
        os.chdir('/tmp')
        if not os.path.exists('leptonica-1.69.tar.gz'):
            os.system('wget http://www.leptonica.org/source/leptonica-1.69.tar.gz')
        os.system('tar xvzf leptonica-1.69.tar.gz')
        os.chdir('/tmp/leptonica-1.69')
        os.system('./autobuild')
        os.system('./configure')
        os.system('make')
        os.system('sudo make install')
        os.system('sudo ldconfig')
    #
    if True:
        os.chdir('/tmp')
        if not os.path.exists('tesseract-ocr-3.02.02.tar.gz'):
            os.system('wget http://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.02.tar.gz')
        os.system('tar xvzf tesseract-ocr-3.02.02.tar.gz')
        os.chdir('/tmp/tesseract-ocr')
        os.system('./autogen.sh')
        os.system('./configure')
        os.system('make')
        os.system('sudo make install')
        os.system('sudo ldconfig')
        os.rename('/tmp/tesseract-ocr', '/tmp/tesseract-ocr.done')
    #
    # language training file
    #
    os.chdir('/tmp')
    if not os.path.exists('tesseract-ocr-3.02.eng.tar.gz'):
        os.system('wget http://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.eng.tar.gz')
    os.system('tar xvzf tesseract-ocr-3.02.eng.tar.gz')
    if not os.path.isdir('/usr/local/share/tessdata'):
        os.system('sudo mkdir /usr/local/share/tessdata')
    os.system('sudo mv tesseract-ocr/tessdata/* /usr/local/share/tessdata/')

def step_22():
    """
    games (crack-attack, tents, etc.)
    """
    tags(['games', 'crack-attack', 'tents', 'puzzle', 'puzzles', 'tents and trees'])
    #
    install(['crack-attack', 'sgt-puzzles'])


def step_23():
    """
    virtualbox
    """
    tags(['virtualbox', 'vbox'])
    #
    url = 'https://www.virtualbox.org/wiki/Linux_Downloads'
    print '#', url
    webbrowser.open(url)


def step_24():
    """
    Java
    """
    tags(['java', 'sdk'])
    #
    url = 'http://www.oracle.com/technetwork/java/javase/downloads/index.html'
    print '#', url
    webbrowser.open(url)


def step_25():
    """
    Java API 7
    """
    tags(['java', 'api', 'doc'])
    #
    url = 'http://docs.oracle.com/javase/7/docs/api/'
    print '#', url
    webbrowser.open(url)


def step_26():
    """
    Flash videos are blue. Correct it.
    https://ubuntuincident.wordpress.com/2012/04/01/flash-videos-are-blue/
    """
    tags(['flash', 'blue', 'shit', 'adobe', 'correct', 'fix'])
    #
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
    tags(['firefox', 'global menu', 'disable'])
    #
    remove('firefox-globalmenu')


def step_27():
    """
    Java
    """
    tags(['java', 'xml', 'editor', 'oxygen'])
    #
    url = 'http://www.oxygenxml.com/download_oxygenxml_editor.html'
    print '#', url
    webbrowser.open(url)


def step_28():
    """
    Midnight Commander from source
    """
    tags(['mc', 'source', 'build'])
    #
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
    tags(['haskell', 'programming', 'functional'])
    #
    install('haskell-platform')


def step_40():
    """
    reinstall kernel module for vbox
    (when you get an error message after installing a new kernel)
    """
    tags(['vbox', 'virtualbox', 'kernel'])
    #
    cmd = 'sudo /etc/init.d/vboxdrv setup'
    print '#', cmd
    os.system(cmd)
    #
    call('/usr/bin/VirtualBox &', shell=True)


def step_34():
    """
    upgrade Ubuntu to a new release
    """
    tags(['ubuntu', 'upgrade'])
    #
    cmd = 'update-manager -d &'
    print '#', cmd
    call(cmd, shell=True)


def step_35():
    """
    ./jq
    """
    tags(['json', 'query', 'jq'])
    #
    url = 'http://stedolan.github.com/jq/'
    print '#', url
    webbrowser.open(url)


def step_36():
    """
    json visualizer
    """
    tags(['json', 'visualize', 'html'])
    #
    url = 'http://chris.photobooks.com/json/default.htm'
    print '#', url
    webbrowser.open(url)


def step_37():
    """
    json editor
    """
    tags(['json', 'editor'])
    #
    url = 'http://jsoneditoronline.org/'
    print '#', url
    webbrowser.open(url)

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
(06)  aliases (in .bashrc)
(33)  tmux (with .tmux.conf)"""
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
(12i) OpenCV
(12j) pattern (a web mining module)"""
    submenu('py', text)


def mm_135():
    text = """(31)  mplayer2, vlc, etc.
(32)  OpenShot video editor"""
    submenu('mm', text)


def ubuntu_140():
    text = """(38)  current version of Ubuntu
(03)  dropbox, acroread
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
    text = """(40)  reinstall kernel module for vbox and start VirtualBox
(34)  upgrade to a new release"""
    submenu('admin', text)


def json_220():
    text = """(35)  ./jq
(36)  json visualizer
(37)  json editor"""
    submenu('json', text)


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
(135) multimedia
(14)  LAMP (set up a LAMP environment)
(140) Ubuntu (tweaks, extra softwares)...
(150) databases (sqlite3, mongodb, mysql)...
(160) browser(s)...
(170) install from source (mc, tesseract3)...
(180) games...
(190) Java...
(200) Haskell...
(210) admin panel
(220) json
(h)   help
(q)   quit"""
#(15)  gimp (2.8.x)
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
    
