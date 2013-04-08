#!/usr/bin/env python

"""
Interactive installer script for Ubuntu.

* Author:  Laszlo Szathmary, 2012--2013 (<jabba.laci@gmail.com>)
* Website: <http://ubuntuincident.wordpress.com/2012/02/29/jabbatron/>
* GitHub:  <https://github.com/jabbalaci/jabbatron>

Some rules:
-----------

(1) The main menu contains submenus. Submenus must consist of 3 digits.
    In the source they have the following form: textual prefix, underscore, 3 digits.
    Example: `blogs_000`.

(2) Modules (i.e. functions that do some operations) are under the
    submenus. They consist of 2 digits and an optional lowercase letter.
    In the source they are prefixed with `step_`. Examples: `step_00a` or `step_09`.

If you want to add a new step, you can check the availability
of its name the following way:

    jabbatron.py -new

It launches an interactive name selector. If "51" is free for instance,
then you can create a function called `step_51()`.


I take no responsibility for any possible loss of data on your computer.
Use this script at your own risk.
"""

__author__ = "Laszlo Szathmary (jabba.laci@gmail.com)"
__version__ = "0.3.2"
__date__ = "20130408"
__copyright__ = "Copyright (c) 2012--2013 Laszlo Szathmary"
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
alias p='python'
alias bpy='bpython'
alias kill9='kill -9'
alias tm='tmux'
alias k='konsole &'

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

# user_agent = Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"""

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
This dictionary contains the information where a tag appears, in which
function(s). Example:
'mc' => set(['step_04', 'step_06'])
"""
tag2func = {}


#def tags(keywords):
#    def add_tag(function_name, tag):
#        global TAGS
#        if function_name in TAGS:
#            TAGS[function_name].add(tag)
#        else:
#            TAGS[function_name] = set()
#            TAGS[function_name].add(tag)
#    #
#    caller_function_name = sys._getframe(1).f_code.co_name
#    if type(keywords) == str:
#        add_tag(caller_function_name, keywords)
#    if type(keywords) == list:
#        for k in keywords:
#            add_tag(caller_function_name, k)

# if you have a tag with a digit, you can add it to this exception list
TAGS_ALLOWED_WITH_DIGITS = set(['kdiff3', 'bs4', 'pep8', 'apache2', 'mplayer2', 'mp3', 'knotify4', 'sqlite3', 'webapp2'])


def tags(tags):
    assert type(tags) == list
    global tag2func
    #
    def verify_tag(tag):
        if re.search(r'\d', tag):
            if tag not in TAGS_ALLOWED_WITH_DIGITS:
                print 'Error: tags cannot contain digits. Modify the tag {0}.'.format(tag)
                sys.exit(1)
    #
    for tag in tags:
        verify_tag(tag)
    #
    def _decorator(fn):
        for tag in tags:
            if tag not in tag2func:
                tag2func[tag] = set()
            tag2func[tag].add(fn.__name__)
        #
        def step_func(*args, **kwargs):
            return fn(*args, **kwargs)
        step_func.tags = tags
        step_func.__doc__ = fn.__doc__
        return step_func
    return _decorator


def create_dir(item, in_home_dir=True, sudo=False):
    if in_home_dir:
        item = HOME_DIR + '/' + item
    if os.path.exists(item):
        print '{item} exists'.format(item=item)
    else:
        if not sudo:
            os.mkdir(item)
        else:    # sudo
            cmd = "sudo mkdir '{d}'".format(d=item)
            print '#', cmd
            os.system(cmd)
        if os.path.exists(item):
            print '{item} created'.format(item=item)


def wait():
    print
    try:
        raw_input('Press ENTER to continue...')
    except (KeyboardInterrupt, EOFError):
        print
        sys.exit(0)


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
        print '{f} exists'.format(f=fname)
    else:
        with open(fname, 'w') as f:
            print >>f, WGETRC
        if os.path.exists(fname):
            print '{f} created'.format(f=fname)
            os.system('chmod 600 {f}'.format(f=fname))


def call_good_shape():
    print '# executing ~/bin/good_shape.sh'
    os.system(HOME_DIR + '/bin/good_shape.sh')


def install_remove(packages, what, options=""):
    if type(packages) == str:
        cmd = 'sudo apt-get {options} {what} '.format(what=what, options=options) + packages
    elif type(packages) == list:
        cmd = 'sudo apt-get {options} {what} '.format(what=what, options=options) + ' '.join(packages)
    else:
        print >>sys.stderr, \
            'Error: strange argument for {what}().'.format(what=what)
        sys.exit(1)
    # if everything was OK
    print '#', cmd
    os.system(cmd)


def install(packages, options=""):
    install_remove(packages, INSTALL, options)


def remove(packages, options=""):
    install_remove(packages, REMOVE, options)


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


def update(verbose=True):
    cmd = 'sudo apt-get update'
    if verbose:
        print '#', cmd
    os.system(cmd)


def add_repo(repo):
    cmd = 'sudo add-apt-repository ppa:{repo}'.format(repo=repo)
    print '#', cmd
    os.system(cmd)
    update()


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
        update(verbose=False)
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

@tags(['blog', 'ubuntu', 'incident', 'jabba'])
def step_00a():
    """
    (00a) The Ubuntu Incident (open blog)
    """
    url = 'https://ubuntuincident.wordpress.com/'
    print '#', url
    webbrowser.open(url)


@tags(['python', 'blog', 'jabba'])
def step_00b():
    """
    (00b) Python Adventures (open blog)
    """
    url = 'https://pythonadventures.wordpress.com/'
    print '#', url
    webbrowser.open(url)


@tags(['home', 'directory', 'bin', 'tmp'])
def step_01():
    """
    (01)  create essential directories (~/bin, ~/tmp, etc.)
    """
    for d in ['bin', 'tmp']:
        create_dir(d)
    #
    bin_to_path_in_bashrc()
    add_wgetrc()


@tags(['apt-get', 'good_shape', 'good_shape.sh', 'good shape', 'installer', 'script', 'update'])
def step_02():
    """
    (02)  good_shape.sh (create in ~/bin or call it if exists)
    """
    path = HOME_DIR + '/bin/good_shape.sh'
    path2 = HOME_DIR + '/bin/good_shape_safe.sh'
    if os.path.exists(path):
        print '{p} exists'.format(p=path)
        call_good_shape()
    else:
        create_dir('bin')
        with open(path, 'w') as f:
            print >>f, GOOD_SHAPE
        if os.path.exists(path):
            print '{p} created'.format(p=path)
            os.system('chmod u+x {p}'.format(p=path))
        if not os.path.exists(path2) and os.path.exists(path):
            os.system('grep -v clean {p} >{p2}'.format(p=path, p2=path2))
            if os.path.exists(path2):
                print '{p} created'.format(p=path2)
                os.system('chmod u+x {p2}'.format(p2=path2))
        #
        bin_to_path_in_bashrc()


@tags(['ubuntu', 'version'])
def step_38():
    """
    (38)  current version of Ubuntu
    """
    with open('/etc/issue') as f:
        version = f.read().strip()
    print version


@tags(['dropbox'])
def step_03():
    """
    (03)  dropbox
    """
    url = 'https://ubuntuincident.wordpress.com/2010/10/15/dropbox-installation/'
    print '#', url
    webbrowser.open(url)


@tags(['acroread', 'adobe', 'pdf'])
def step_45():
    """
    (45)  acroread
    """
    print """Open Ubuntu Software Center and install:
  * Adobe Reader (first enable "Canonical Partners" in "Software Sources" and "sudo apt-get update")"""


@tags(['skype'])
def step_03b():
    """
    (03b) skype
    """
    url = 'http://www.skype.com/intl/en/get-skype/on-your-computer/linux/'
    print '#', url
    webbrowser.open(url)


@tags(['mc', 'bindings', 'extension', 'extensions'])
def step_04():
    """
    (04)  mc (from official repo [old])
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
            print '# {f} was created'.format(f=bfile)


temp = ['konsole', 'yakuake', 'gparted', 'okular', 'pdf', 'nautilus', 'gconf', 'htop', 'gnome-panel', 'gnome', 'gnome panel', 'xsel', 'xclip', 'clipboard']
temp += ['terminator', 'config', 'rlwrap']
@tags(temp)
def step_04b():
    """
    (04b) konsole, gparted, etc. (essential packages)
    """
    install(['konsole', 'yakuake', 'gparted', 'okular', 'nautilus-open-terminal', 'gconf-editor', 'htop', 'gnome-panel', 'xsel', 'xclip'])
    install(['rlwrap'])
    install('terminator')
    reply = raw_input('Add terminator config file [y/n]? ')
    if reply == 'y':
        create_dir('.config/terminator')
        with open(TERMINATOR_RC, 'a') as f:
            print >>f, TERMINATOR_CONFIG
    else:
        print 'no'


@tags(['vim', 'vimrc', '.vimrc', 'config'])
def step_05():
    """
    (05)  vim (with .vimrc)
    """
    install('vim-gnome')
    if not os.path.exists(HOME_DIR + '/.vimrc'):
        os.system("cd; wget {url} -O .vimrc".format(url=VIMRC_URL))
    create_dir('tmp/vim')
    reply = raw_input('Set vim in .bashrc as your default editor [y/n]? ')
    if reply == 'y':
        with open(BASHRC, 'a') as f:
            print >>f, EDITOR
    else:
        print 'no'


@tags(['tmux', 'config'])
def step_33():
    """
    (33)  tmux (with .tmux.conf)
    """
    install('tmux')
    print
    reply = raw_input('Download .tmux.conf file [y/n]? ')
    if reply == 'y':
        os.system("cd; wget {url} -O .tmux.conf".format(url=TMUX_CONF_URL))
    else:
        print 'no'


@tags(['alias', 'aliases', 'bashrc', '.bashrc', 'config', 'fortune', 'cowsay', 'cowthink', 'cow'])
def step_06():
    """
    (06)  aliases (in .bashrc)
    """
    reply = raw_input('Add aliases to .bashrc [y/n]? ')
    if reply == 'y':
        with open(BASHRC, 'a') as f:
            print >>f, ALIASES
    else:
        print 'no'
    #
    install(['fortune-mod', 'cowsay'])


@tags(['msdos', 'dos', 'ms-dos', 'microsoft', 'prompt', 'emulator', 'emulation'])
def step_06a():
    """
    (06a) MS-DOS prompt emulation (in .bashrc)
    """
    reply = raw_input('Add MS-DOS prompt emulation to .bashrc [y/n]? ')
    if reply == 'y':
        with open(BASHRC, 'a') as f:
            print >>f, MSDOS
    else:
        print 'no'


@tags(['development', 'git', 'svn', 'subversion', 'clang', 'programming'])
def step_07():
    """
    (07)  development (build-essential, etc.)
    """
    install(['build-essential', 'git', 'subversion', 'clang', 'gdc', 'codeblocks', 'cmake', 'libqt4-dev', 'qt4-qmake'])


@tags(['d', 'd language', 'd lang', 'dmd', 'rdmd'])
def step_07a():
    """
    (07a) D language (dmd, rdmd)
    """
    dmd = which('dmd')
    if dmd:
        print 'Installed version:',
        print get_complex_cmd_output('dmd | head -1')[0].strip()
    else:
        print 'Not installed.'
    url = 'http://www.digitalmars.com/d/download.html'
    print '#', url
    webbrowser.open(url)


@tags(['wajig', 'apt-get', 'apt-file', 'packages', 'synaptic'])
def step_08():
    """
    (08)  apt-get et al. (wajig, synaptic, etc.)
    """
    install(['wajig', 'apt-file', 'synaptic'])


@tags(['latex', 'texlive', 'metapost'])
def step_09():
    """
    (09)  latex
    """
    install(['texlive-base', 'texlive', 'texlive-latex-extra',
             'texlive-metapost', 'texlive-science', 'texlive-fonts-extra', 'dvipng'])


@tags(['git', 'github', 'ssh'])
def step_10():
    """
    (10)  github setup (how to create ssh public key)
    """
    url = 'http://help.github.com/mac-set-up-git/'
    print '#', url
    webbrowser.open(url)


@tags(['git', 'gitconfig', 'config', 'alias', 'aliases'])
def step_10a():
    """
    (10a) .gitconfig (add some aliases)
    """
    reply = raw_input('Add aliases to .gitconfig [y/n]? ')
    if reply == 'y':
        with open(GITCONFIGRC, 'a') as f:
            print >>f, GITCONFIG
    else:
        print 'no'


@tags(['git', 'help'])
def step_10b():
    """
    (10b) git help (cheat sheet, Pro Git book, manual, etc.)
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


temp = ['tools', 'utils', 'xsel', 'xclip', 'kdiff3', 'meld', 'pdf', 'pdftk', 'imagemagick', 'rar', 'unrar', 'comix', 'comics', 'viewer']
temp += ['chm', 'chmsee', 'gqview', 'image', 'image viewer', 'curl']
@tags(temp)
def step_11():
    """
    (11)  tools (xsel, kdiff3, etc.)
    """
    install(['xsel', 'xclip', 'kdiff3', 'meld', 'pdftk', 'imagemagick', 'unrar', 'comix', 'chmsee', 'gqview', 'curl'])


@tags(['python', 'pip'])
def step_12():
    """
    (12)  python-pip (via apt-get [old], run just once)
    """
    install('python-pip')


@tags(['xml', 'libxml', 'python', 'scraper', 'lxml', 'beautifulsoup', 'bsoup', 'bs', 'bs4', 'scrapy', 'css', 'cssselect'])
def step_12a():
    """
    (12a) python scrapers (lxml, beautifulsoup, scrapy)
    """
    install(['libxml2-dev', 'libxslt1-dev', 'python2.7-dev'])
    pip(['lxml', 'beautifulsoup', 'beautifulsoup4', 'scrapy', 'cssselect'])


temp = ['pip', 'pep8', 'ipython', 'python', 'pymongo', 'mongodb', 'pygments', 'reddit', 'praw', 'curl', 'pycurl', 'requests']
temp += ['untangle', 'xml', 'pylint', 'sphinx', 'feed', 'feedparser', 'flask', 'virtualenv', 'pudb', 'debug', 'debugger', 'docopt']
@tags(temp)
def step_12b():
    """
    (12b) python, smaller things (pip, pep8, untangle, etc.)
    """
    pip(['pip', 'pep8', 'ipython', 'pymongo', 'pygments', 'praw', 'pycurl', 'untangle', 'pylint', 'requests', 'pudb', 'docopt'])
    pip(['sphinx', 'feedparser'])
    pip(['Flask', 'virtualenv'])


@tags(['spyder', 'python', 'ide', 'ninja', 'ninja-ide'])
def step_12c():
    """
    (12c) python IDEs (spyder, ninja-ide)
    """
    pip('spyder')
    add_repo('ninja-ide-developers/ninja-ide')
    install('ninja-ide')


temp = ['python', 'ipython', 'science', 'scientific', 'numpy', 'fortran', 'gfortran']
temp += ['scipy', 'matplotlib', 'pandas', 'sympy', 'data']
@tags(temp)
def step_12d():
    """
    (12d) scientific python (ipython, numpy, scipy, matplotlib, pandas, sympy)
    """
    pip('ipython')
    # numpy, scipy, matplotlib, pandas
    pip('numpy')
    install(['libatlas-base-dev', 'gfortran', 'libfreetype6-dev', 'libpng12-dev'])
    pip(['scipy', 'matplotlib', 'pandas'])
    #
    install('python-sympy')


@tags(['python', 'pil', 'image', 'screenshot', 'autopy'])
def step_12e():
    """
    (12e) python image processing (PIL, pyscreenshot); autopy
    """
    pip(['pil', 'pyscreenshot'])
    #
    install('libxtst-dev')
    pip('autopy')


@tags(['pyp', 'python'])
def step_12f():
    """
    (12f) pyp (The Pyed Piper)
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


@tags(['python', 'apache', 'apache2', 'wsgi', 'django', 'webserver', 'localhost'])
def step_12g():
    """
    (12g) python + apache on localhost
    """
    install('libapache2-mod-wsgi')
    install('python-django')


@tags(['python', 'gevent', 'concurrency'])
def step_12h():
    """
    (12h) python concurrency (gevent)
    """
    install(['libevent-dev', 'python-all-dev'])
    pip('gevent')


@tags(['opencv', 'install', 'source', 'build'])
def step_12i():
    """
    (12i) OpenCV
    """
    # based on http://jayrambhia.wordpress.com/tag/opencv/
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
    #
    print
    url = 'http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/'
    print '#', url
    webbrowser.open(url)
    print '# download the latest OpenCV and save it somewhere (to /opt for instance)'
    fpath = raw_input('Full path of the downloaded archive: ')
    (path, fname) = os.path.split(fpath)
    os.chdir(path)
    os.system('tar xvjf {f}'.format(f=fname))
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


@tags(['python', 'pattern'])
def step_12j():
    """
    (12j) pattern (a web mining module)
    """
    #http://www.clips.ua.ac.be/pages/pattern
    pip('pattern')


@tags(['qt', 'pyside', 'designer'])
def step_12k():
    """
    (12k) Qt (PySide)
    """
    install(['python-pyside', 'pyside-tools', 'qt4-designer'])


temp = ['multimedia', 'mplayer', 'mplayer2', 'vlc', 'mencoder']
temp += ['minitube', 'youtube', 'soundconverter', 'sound', 'converter', 'mp3']
@tags(temp)
def step_31():
    """
    (31)  mplayer2, vlc, etc.
    """
    install(['mplayer2', 'mencoder'])
    #
    #add_repo('n-muench/vlc')    # not needed in Ubuntu 12.10
    install('vlc')
    #
    install(['minitube', 'soundconverter'])


@tags(['openshot', 'video', 'editor', 'video editor'])
def step_32():
    """
    (32)  OpenShot video editor
    """
    # openshot.org
    add_repo('jonoomph/openshot-edge')
    install(['openshot', 'openshot-doc'])


@tags(['ffmpeg', 'static'])
def step_41():
    """
    (41)  static FFmpeg build
    """
    url = 'http://ffmpeg.gusari.org/static/'
    print '#', url
    webbrowser.open(url)


@tags(['lamp', 'linux', 'apache', 'mysql', 'php'])
def step_14():
    """
    (14)  LAMP (set up a LAMP environment)
    """
    url = 'https://ubuntuincident.wordpress.com/2010/11/18/installing-a-lamp-server/'
    print '#', url
    webbrowser.open(url)


temp = ['tweak', 'tweaks', 'knotify4', 'disable', 'ubuntu-tweak', 'ubuntu']
temp += ['unsettings', 'myunity']
@tags(temp)
def step_16():
    """
    (16)  tweaks (disable knotify4, install ubuntu-tweak, etc.)
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


@tags(['global menu', 'disable'])
def step_16b():
    """
    (16b) disable global menu
    """
    # if using 'unsettings' was not enough
    remove(['appmenu-gtk3', 'appmenu-gtk', 'appmenu-qt', 'firefox-globalmenu'])


@tags(['compiz', 'ccsm'])
def step_16c():
    """
    (16c) compizconfig-settings-manager (ccsm)
    """
    install('compizconfig-settings-manager')


@tags(['database', 'databases', 'sqlite3'])
def step_17a():
    """
    (17a) sqlite3
    """
    install('sqlite3')


@tags(['database', 'databases', 'mongodb'])
def step_17b():
    """
    (17b) mongodb
    """
    mongodb()


@tags(['database', 'databases', 'mysql', 'python'])
def step_17c():
    """
    (17c) mysql
    """
    install(['mysql-server', 'mysql-client', 'python-mysqldb'])


@tags(['launcher', 'desktop'])
def step_18():
    """
    (18)  create launcher (if not available upon right click on the Desktop)
    """
    os.system('gnome-desktop-item-edit ~/Desktop/ --create-new')


@tags(['browser', 'firefox', 'add-on', 'addon', 'plugin'])
def step_19():
    """
    (19)  essential Firefox add-ons
    """
    url = 'https://ubuntuincident.wordpress.com/2011/03/14/essential-firefox-add-ons/'
    print '#', url
    webbrowser.open(url)


@tags(['browser', 'google', 'chromium', 'chrome'])
def step_20():
    """
    (20)  chromium
    """
    install('chromium-browser')


@tags(['tesseract', 'ocr'])
def step_21():
    """
    (21)  tesseract 3
    """
    # http://code.google.com/p/tesseract-ocr/wiki/ReadMe
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


@tags(['games', 'crack-attack', 'tents', 'puzzle', 'puzzles', 'tents and trees'])
def step_22():
    """
    (22)  games (crack-attack, tents, etc.)
    """
    install(['crack-attack', 'sgt-puzzles'])


@tags(['virtualbox', 'vbox'])
def step_23():
    """
    (23)  virtualbox
    """
    url = 'https://www.virtualbox.org/wiki/Linux_Downloads'
    print '#', url
    webbrowser.open(url)


@tags(['java', 'sdk'])
def step_24():
    """
    (24)  Java SDK update
    """
    url = 'http://www.oracle.com/technetwork/java/javase/downloads/index.html'
    print '#', url
    webbrowser.open(url)


@tags(['java', 'api', 'doc'])
def step_25():
    """
    (25)  Java 7 API
    """
    url = 'http://docs.oracle.com/javase/7/docs/api/'
    print '#', url
    webbrowser.open(url)


@tags(['flash', 'blue', 'shit', 'adobe', 'correct', 'fix'])
def step_26():
    """
    (26)  blue Flash (correct it)
    """
    # https://ubuntuincident.wordpress.com/2012/04/01/flash-videos-are-blue/
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


@tags(['firefox', 'global menu', 'disable'])
def step_26b():
    """
    (26b) remove firefox-globalmenu
    """
    remove('firefox-globalmenu')


@tags(['java', 'xml', 'editor', 'oxygen'])
def step_27():
    """
    (27)  oXygen XML Editor
    """
    url = 'http://www.oxygenxml.com/download_oxygenxml_editor.html'
    print '#', url
    webbrowser.open(url)


@tags(['mc', 'source', 'build'])
def step_28():
    """
    (28)  Midnight Commander from source
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


def configure_make_checkinstall(what):
    if what == 'x264':
        os.system("./configure --enable-static")
        os.system("make")
        os.system("""sudo checkinstall --pkgname=x264 --pkgversion="3:$(./version.sh | awk -F'[" ]' '/POINT/{print $4"+git"$5}')" --backup=no --deldoc=yes --fstrans=no --default""")
    elif what == 'fdk-aac':
        os.system("./configure --disable-shared")
        os.system("make")
        os.system('sudo checkinstall --pkgname=fdk-aac --pkgversion="$(date +%Y%m%d%H%M)-git" --backup=no --deldoc=yes --fstrans=no --default')
    elif what == 'libvpx':
        os.system("./configure --disable-examples --disable-unit-tests")
        os.system("make")
        os.system('sudo checkinstall --pkgname=libvpx --pkgversion="1:$(date +%Y%m%d%H%M)-git" --backup=no --deldoc=yes --fstrans=no --default')
    elif what == 'opus':
        os.system('./configure --disable-shared')
        os.system('make')
        os.system('sudo checkinstall --pkgname=libopus --pkgversion="$(date +%Y%m%d%H%M)-git" --backup=no --deldoc=yes --fstrans=no --default')
    elif what == 'ffmpeg':
        os.system("""./configure --enable-gpl --enable-libass --enable-libfaac --enable-libfdk-aac --enable-libmp3lame \
                  --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libspeex --enable-librtmp --enable-libtheora \
                  --enable-libvorbis --enable-libvpx --enable-x11grab --enable-libx264 --enable-libvo-aacenc --enable-nonfree --enable-version3""")
        os.system("make")
        os.system('sudo checkinstall --pkgname=ffmpeg --pkgversion="7:$(date +%Y%m%d%H%M)-git" --backup=no --deldoc=yes --fstrans=no --default')
    else:
        func_name = sys._getframe().f_code.co_name
        print 'Warning! Invalid parameter in function {0}!'.format(func_name)


@tags(['ffmpeg', 'source'])
def step_15():
    """
    (15)  FFmpeg from source (run this for the first time)
    """
    url = 'https://ffmpeg.org/trac/ffmpeg/wiki/UbuntuCompilationGuide'
    print '# install guide:', url
#    webbrowser.open(url)
    print """
FFmpeg will be compiled and installed from source
* make sure that the multiverse repository is enabled
* some packages will be removed and installed from source"""
    print
    reply = raw_input('Continue [y/n]? ')
    if reply != 'y':
        return
    # else
    BASE = '/opt'
    reply = raw_input('Where do you want to install FFmpeg and its codecs [default: {0}]? '.format(BASE)).strip()
    if reply:
        BASE = reply
    if not os.path.isdir(BASE):
        print '{0} is not a directory!'.format(BASE)
        return
    if not os.access(BASE, os.W_OK):
        print 'You have no write access to {0}!'.format(BASE)
        return
    # else
    print 'Base directory:', BASE
    if True:
        remove(['ffmpeg', 'x264', 'libav-tools', 'libvpx-dev', 'libx264-dev', 'yasm'])
        update()
        install(['autoconf', 'automake', 'build-essential', 'checkinstall', 'git', 'libass-dev', 'libfaac-dev', 'libvo-aacenc-dev',
                'libgpac-dev', 'libjack-jackd2-dev', 'libmp3lame-dev', 'libopencore-amrnb-dev', 'libopencore-amrwb-dev',
                'librtmp-dev', 'libsdl1.2-dev', 'libspeex-dev', 'libtheora-dev', 'libtool', 'libva-dev', 'libvdpau-dev',
                'libvorbis-dev', 'libx11-dev', 'libxext-dev', 'libxfixes-dev', 'pkg-config', 'texi2html', 'zlib1g-dev'], "-y")
    if True:
        print '# install Yasm'
        os.chdir(BASE)
        os.system("wget http://www.tortall.net/projects/yasm/releases/yasm-1.2.0.tar.gz")
        os.system("tar xzvf yasm-1.2.0.tar.gz")
        os.chdir("yasm-1.2.0")
        os.system("./configure")
        os.system("make")
        os.system('sudo checkinstall --pkgname=yasm --pkgversion="1.2.0" --backup=no --deldoc=yes --fstrans=no --default')

    if True:
        print '# install x264'
        os.chdir(BASE)
        os.system("git clone --depth 1 git://git.videolan.org/x264.git")
        os.chdir('x264')
        configure_make_checkinstall('x264')

    if True:
        print '# install fdk-aac'
        os.chdir(BASE)
        os.system("git clone --depth 1 git://github.com/mstorsjo/fdk-aac.git")
        os.chdir('fdk-aac')
        os.system("autoreconf -fiv")
        configure_make_checkinstall('fdk-aac')

    if True:
        print '# install libvpx'
        os.chdir(BASE)
        os.system("git clone --depth 1 http://git.chromium.org/webm/libvpx.git")
        os.chdir('libvpx')
        configure_make_checkinstall('libvpx')

    if True:
        print '# install opus'
        os.chdir(BASE)
        os.system("git clone --depth 1 git://git.xiph.org/opus.git")
        os.chdir('opus')
        os.system('./autogen.sh')
        configure_make_checkinstall('opus')

    if True:
        print '# install FFmpeg'
        os.chdir(BASE)
        os.system("git clone --depth 1 git://source.ffmpeg.org/ffmpeg")
        os.chdir('ffmpeg')
        configure_make_checkinstall('ffmpeg')
        os.system("hash -r")


@tags(['ffmpeg', 'source', 'update'])
def step_29():
    """
    (29)  update FFmpeg (if you installed FFmpeg from source before)
    """
    url = 'https://ffmpeg.org/trac/ffmpeg/wiki/UbuntuCompilationGuide'
    print '# install and update guide:', url
#    webbrowser.open(url)
    print """
Run this if you've already installed FFmpeg on your
machine from source. It will update your FFmpeg and
recompile it."""
    print
    reply = raw_input('Continue [y/n]? ')
    if reply != 'y':
        return
    # else
    BASE = '/opt'
    reply = raw_input('Where is your existing FFmpeg and its codecs [default: {0}]? '.format(BASE)).strip()
    if reply:
        BASE = reply
    if not os.path.isdir(BASE):
        print '{0} is not a directory!'.format(BASE)
        return
    if not os.access(BASE, os.W_OK):
        print 'You have no write access to {0}!'.format(BASE)
        return
    # else
    print 'Base directory:', BASE
    if True:
        remove(['ffmpeg', 'x264', 'libx264-dev', 'libvpx-dev'], "-y")
        update()
        install(['autoconf', 'automake', 'build-essential', 'checkinstall', 'git', 'libass-dev', 'libfaac-dev', 'libvo-aacenc-dev',
                 'libgpac-dev', 'libjack-jackd2-dev', 'libmp3lame-dev', 'libopencore-amrnb-dev', 'libopencore-amrwb-dev',
                 'librtmp-dev', 'libsdl1.2-dev', 'libspeex-dev', 'libtheora-dev', 'libva-dev', 'libvdpau-dev', 'libvorbis-dev',
                 'libx11-dev', 'libxext-dev', 'libxfixes-dev', 'texi2html', 'yasm', 'zlib1g-dev'], "-y")
    if True:
        print '# update x264'
        os.chdir(BASE)
        os.chdir('x264')
        os.system("make distclean")
        os.system("git pull")
        configure_make_checkinstall('x264')

    if True:
        print '# update fdk-aac'
        os.chdir(BASE)
        os.chdir('fdk-aac')
        os.system("make distclean")
        os.system("git pull")
        configure_make_checkinstall('fdk-aac')

    if True:
        print '# update libvpx'
        os.chdir(BASE)
        os.chdir('libvpx')
        os.system("make clean")
        os.system("git pull")
        configure_make_checkinstall('libvpx')

    if True:
        print '# update opus'
        os.chdir(BASE)
        os.chdir('opus')
        os.system("make distclean")
        os.system("git pull")
        configure_make_checkinstall('opus')

    if True:
        print '# update FFmpeg'
        os.chdir(BASE)
        os.chdir('ffmpeg')
        os.system("make distclean")
        os.system("git pull")
        configure_make_checkinstall('ffmpeg')


@tags(['haskell', 'programming', 'functional'])
def step_30():
    """
    (30)  install haskell
    """
    install('haskell-platform')


@tags(['vbox', 'virtualbox', 'kernel'])
def step_40():
    """
    (40)  reinstall kernel module for vbox and start VirtualBox
    """
    cmd = 'sudo /etc/init.d/vboxdrv setup'
    print '#', cmd
    os.system(cmd)
    #
    call('/usr/bin/VirtualBox &', shell=True)


@tags(['ubuntu', 'upgrade'])
def step_34():
    """
    (34)  upgrade Ubuntu to a new release
    """
    cmd = 'update-manager -d &'
    print '#', cmd
    call(cmd, shell=True)


@tags(['ubuntu', 'kernel', 'old kernel'])
def step_46():
    """
    (46)  remove old kernels
    """
    print "current kernel:"
    print get_complex_cmd_output("uname -a")[0].strip()
    print
    available = which("ubuntu-tweak")
    print "The easiest way to remove old kernels is to use ubuntu-tweak.",
    if not available:
        print "However, it's NOT installed on your system."
        print "Tip: install ubuntu-tweak with this script :)"
    else:
        print "In Ubuntu Tweak, go to Janitor -> Old Kernel."
        reply = raw_input('Shall I start Ubuntu Tweak for you [y/n]? ').strip()
        if reply in ('', 'y'):
            print 'yes'
            os.system("ubuntu-tweak &")
        else:
            print 'no'


@tags(['apt-get', 'update'])
def step_39():
    """
    (39)  sudo apt-get update
    """
    update()


@tags(['apt-get', 'autoremove'])
def step_42():
    """
    (42)  sudo apt-get autoremove
    """
    cmd = 'sudo apt-get autoremove'
    print '#', cmd
    os.system(cmd)


@tags(['json', 'query', 'jq'])
def step_35():
    """
    (35)  ./jq
    """
    url = 'http://stedolan.github.com/jq/'
    print '#', url
    webbrowser.open(url)


@tags(['json', 'visualize', 'html'])
def step_36():
    """
    (36)  json visualizer
    """
    url = 'http://chris.photobooks.com/json/default.htm'
    print '#', url
    webbrowser.open(url)


@tags(['json', 'editor'])
def step_37():
    """
    (37)  json editor
    """
    url = 'http://jsoneditoronline.org/'
    print '#', url
    webbrowser.open(url)


@tags(['google', 'gae'])
def step_43():
    """
    (43)  Google App Engine SDK for Python
    """
    url = 'https://developers.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python'
    print '#', url
    webbrowser.open(url)


@tags(['webapp2', 'python', 'framework'])
def step_44():
    """
    (44)  webapp2 framework
    """
    url = 'http://webapp-improved.appspot.com/'
    print '#', url
    webbrowser.open(url)


def step_13():
    """
    (13)  placeholder
    """
    pass

##########
## tags ##
##########

def process_tag(tag):
    if tag in tag2func:
        for f in sorted(tag2func[tag]):
            print globals()[f].__doc__.strip()


##############
## submenus ##
##############

def submenu(msg, text):
    header(msg)
    for fid in text:
        print globals()["step_"+fid].__doc__.strip()
    while True:
        try:
            choice = raw_input('>>> ').strip()
        except (KeyboardInterrupt, EOFError):
            print
            print 'bye.'
            sys.exit(0)
        if len(choice) == 0:
            pass
        elif choice == 'qq':
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
        elif re.search('^\d{2}[a-z]?$', choice):
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
        elif len(choice) > 0:
            process_tag(choice)
        #
        else:
            print 'Wat?'


def blogs_000():
    text = [
        '00a',    # The Ubuntu Incident (open blog)
        '00b',    # Python Adventures (open blog)
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)    # take current function's name, split by '_'


def home_100():
    text = [
        '01',     # create essential directories (~/bin, ~/tmp, etc.)
        '02',     # good_shape.sh (create in ~/bin or call it if exists)
        '04',     # mc (from official repo [old])
        '04b',    # konsole, gparted, etc. (essential packages)
        '05',     # vim (with .vimrc)
        '06',     # aliases (in .bashrc)
        '06a',    # MS-DOS prompt emulation (in .bashrc)
        '33',     # tmux (with .tmux.conf)
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def dev_110():
    text = [
        '07',     # development (build-essential, etc.)
        '07a',    # D language (dmd, rdmd)
        '27',     # oXygen XML Editor
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def git_120():
    text = [
        '10',     # github setup
        '10a',    # .gitconfig (add some aliases)
        '10b',    # git help (cheat sheet, Pro Git book, manual, etc.)
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def py_130():
    text = [
        '12',     #  python-pip (via apt-get [old], run just once)
        '12a',    # python scrapers (lxml, beautifulsoup, scrapy)
        '12b',    # python, smaller things (pip, pep8, untangle, etc.)
        '12c',    # python IDEs (spyder, ninja-ide)
        '12d',    # scientific python (ipython, numpy, scipy, matplotlib, pandas, sympy)
        '12e',    # python image processing (PIL, pyscreenshot); autopy
        '12f',    # pyp (The Pyed Piper)
        '12g',    # python + apache on localhost
        '12h',    # python concurrency (gevent)
        '12i',    # OpenCV
        '12j',    # pattern (a web mining module)
        '12k',    # Qt (PySide)
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def mm_135():
    text = [
        '31',     # mplayer2, vlc, etc.
        '32',     # OpenShot video editor
        '41',     # static FFmpeg build
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def ubuntu_140():
    text = [
        '38',     # current version of Ubuntu
        '09',     # latex
        '11',     # tools (xsel, kdiff3, etc.)
        '03',     # dropbox
        '45',     # acroread
        '03b',    # skype
        '14',     # LAMP (set up a LAMP environment)
        '08',     # apt-get et al. (wajig, synaptic, etc.)
        '16',     # tweaks (disable knotify4, install ubuntu-tweak, etc.)
        '16b',    # disable global menu
        '16c',    # compizconfig-settings-manager (ccsm)
        '18',     # create launcher (if not available upon right click on the Desktop)
        '23',     # virtualbox
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def databases_150():
    text = [
        '17a',    # sqlite3
        '17b',    # mongodb
        '17c',    # mysql
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def browser_160():
    text = [
        '19',     # essential Firefox add-ons
        '20',     # chromium
        '26',     # blue Flash (correct it)
        '26b',    # remove firefox-globalmenu
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def source_170():
    text = [
        '21',     # tesseract 3
        '28',     # Midnight Commander from source
        '15',     # FFmpeg from source (run this for the first time)
        '29',     # update FFmpeg (if you installed FFmpeg from source before)
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def games_180():
    text = [
        '22',     # games (crack-attack, etc.)
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def java_190():
    text = [
        '24',     # Java SDK update
        '25',     # Java 7 API
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def haskell_200():
    text = [
        '30',     # install haskell
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def admin_210():
    text = [
        '02',     # good_shape.sh (create in ~/bin or call it if exists)
        '40',     # reinstall kernel module for vbox and start VirtualBox
        '34',     # upgrade to a new release
        '46',     # remove old kernels
        '39',     # sudo apt-get update
        '42',     # sudo apt-get autoremove
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def json_220():
    text = [
        '35',     # ./jq
        '36',     # json visualizer
        '37',     # json editor
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


def gae_230():
    text = [
        '43',     # Google App Engine SDK for Python
        '44',     # webapp2 framework
    ]
    submenu(sys._getframe().f_code.co_name.split('_')[0], text)


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
    print """(000) blogs...
(100) prepare HOME directory + install essential softwares...
(110) development (C/C++/D compilers, oXygen XML Editor, etc.)...
(120) github...
(130) Python for World Domination...
(135) multimedia...
(140) Ubuntu (tweaks, extra softwares)...
(150) databases (sqlite3, mongodb, mysql)...
(160) browser(s)...
(170) install from source (mc, tesseract3, ffmpeg)...
(180) games...
(190) Java...
(200) Haskell...
(210) admin panel...
(220) json...
(230) Google App Engine...
(h)   help
(q)   quit"""
    while True:
        try:
            choice = raw_input('>>> ').strip()
        except (KeyboardInterrupt, EOFError):
            print
            print 'bye.'
            sys.exit(0)
        if len(choice) == 0:
            pass
        elif choice in ('q', 'qq'):
            print 'bye.'
            sys.exit(0)
        elif choice in ('h', 'help'):
            info()
            menu()
        elif choice == 'c':
            menu()
            break
        elif re.search('^\d{3}$', choice):
            found = False
            for f in globals():
                if re.search('^[a-z]+_{choice}$'.format(choice=choice), f):
                    found = True
                    methodToCall = globals()[f]
                    methodToCall()
            if not found:
                print 'Unknown menu item.'
        elif re.search('^\d{2}[a-z]?$', choice):
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
        elif len(choice) > 0:
            process_tag(choice)
        #
        else:
            print 'Wat?'


def print_hole_if_available(steps):
    def to_number(s):
        return int(''.join([c for c in s if c.isdigit()]))
    #
    size = len(steps)
    for i in range(1, size-1):
        a = to_number(steps[i-1])
        b = to_number(steps[i])
        if b - a > 1:
            print 'There is a hole available: {n}'.format(n=a+1)
            return


def new_item():
    steps = []
    for f in sorted(globals()):
        if f.startswith('step_'):
            steps.append(re.search('^step_(.*)$', f).group(1))
    print "Steps taken:"
    print "------------"
    print steps
    print_hole_if_available(steps)
    try:
        new_step = raw_input('Check availability: ').strip()
    except (KeyboardInterrupt, EOFError):
        print
        print 'quit.'
        sys.exit(0)
    #
    if not re.search(r'^\d{2}[a-z]?$', new_step):
        print 'Invalid name. Correct form: two digits and an optional lowercase letter.'
        return
    # else
    if new_step not in steps:
        print 'Available! :)'
    else:
        print 'Taken :('


def verify_docstrings():
    for f in sorted(globals()):
        if f.startswith('step_'):
            func_id = re.search(r'^step_(.*)$', f).group(1)
            m = re.search(r'^\((\d{2}[a-z]?)\)(\s+).*$', globals()[f].__doc__.strip())
            if m:
                doc_id = m.group(1)
                spaces = m.group(2)
                if len(doc_id) + len(spaces) != 4:
                    print "Error: wrong number of spaces in the docstring of function {f}()".format(f=f)
                    sys.exit(1)
            if not m or func_id != doc_id:
                print "Error: incorrect docstring in function {f}()".format(f=f)
                sys.exit(1)


def main():
    verify_docstrings()
    unbuffered()
    args = sys.argv[1:]

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
    main()

