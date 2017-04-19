import os
from distutils.core import setup

import sys

setup(
    name='serial_mock',
    version='0.0.2',
    packages=['serial_mock'],
    url='http://serialmock.readthedocs.io/en/latest/',
    download_url="https://github.com/joranbeasley/SerialMock",
    license='MIT',
    author='Joran Beasley',
    author_email='joranbeasley',
    description='mocks serial ports for use with com0com(windows) or socat(*nix)'
)

