#!/usr/bin/python

import os
from setuptools import setup, find_packages

import fidonet

setup(name = 'python-ftn',
        version = fidonet.__version__,
        description = 'FTN tools for Python',
        long_description=open('README.rst').read(),
        license = fidonet.__license__,
        author = fidonet.__author__,
        author_email = fidonet.__email__,
        url = 'http://projects.oddbit.com/python-ftn/',
        packages = [
            'fidonet',
            'fidonet.apps',
            'fidonet.formats',
            ],
        entry_points = {
            'console_scripts': [
                'ftn-pack = fidonet.apps.pack:App.run',
                'ftn-unpack = fidonet.apps.unpack:App.run',

                'ftn-scanmsg = fidonet.apps.scanmsg:App.run',
                'ftn-editmsg = fidonet.apps.editmsg:App.run',
                'ftn-makemsg = fidonet.apps.makemsg:App.run',
                'ftn-querymsg = fidonet.apps.querymsg:App.run',

                'ftn-editpkt = fidonet.apps.editpkt:App.run',
                'ftn-scanpkt = fidonet.apps.scanpkt:App.run',
                'ftn-querypkt = fidonet.apps.querypkt:App.run',

                'ftn-indexnl = fidonet.apps.indexnl:App.run',
                'ftn-route = fidonet.apps.route:App.run',
                'ftn-poll = fidonet.apps.poll:App.run',
                ],
            },
        install_requires = [
            'bitstring',
            'sqlalchemy',
            ],
        )

