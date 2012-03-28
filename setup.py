#!/usr/bin/env python

"""
jabbatron
---------

Interactive installer script for Ubuntu.

Links
`````

* `website <https://github.com/jabbalaci/jabbatron>`_
"""

from setuptools import setup

import jabbatron as cfg


setup(
    name='jabbatron',
    py_modules=[
        'jabbatron'
    ],
    version=cfg.__version__,
    description='Interactive installer script for Ubuntu.',
    long_description=__doc__,
    author='Laszlo Szathmary',
    author_email='jabba.laci@gmail.com',
    url='https://github.com/jabbalaci/jabbatron',
    keywords = ['jabba', 'installer', 'ubuntu'],
    license='GPLv3',
    platforms='Linux',
    entry_points={
        'console_scripts': 'jabbatron = jabbatron:main'
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Operating System :: POSIX :: Linux',
		'Topic :: Utilities',
    ],
)

