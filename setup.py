import os
from distutils.core import setup

import sys

setup(
    name='serial_mock',
    version='0.0.1',
    packages=['serial_mock'],
    url='',
    license='MIT',
    author='Joran Beasley',
    author_email='joranbeasley',
    description='mocks serial ports for use with com0com(windows) or socat(*nix)'
)

