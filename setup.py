#!/usr/bin/python

import os
from setuptools import setup, find_packages

setup(name = "fidonet",
        version = "2",
        description = "FTN tools for Python",
        long_description=open('README.rst').read(),
        author = "Lars Kellogg-Stedman",
        author_email = "lars@oddbit.com",
        url = "http://github.com/larsks/fidonet",
        packages = [
            'fidonet',
            'fidonet.apps',
            'fidonet.formats',
            ],
        entry_points = {
            'console_scripts': [
                'ftn-poll = fidonet.apps.poll:App.run',

                'ftn-pack = fidonet.apps.pack:App.run',
                'ftn-unpack = fidonet.apps.unpack:App.run',

                'ftn-scanmsg = fidonet.apps.scanmsg:App.run',
                'ftn-editmsg = fidonet.apps.editmsg:App.run',
                'ftn-makemsg = fidonet.apps.makemsg:App.run',

                'ftn-editpkt = fidonet.apps.editpkt:App.run',
                'ftn-scanpkt = fidonet.apps.scanpkt:App.run',

                'ftn-indexnl = fidonet.apps.indexnl:App.run',
                'ftn-route = fidonet.apps.route:App.run',
                ],
            },
        install_requires = [
            'bitstring',
            'sqlalchemy',
            ],
        )

