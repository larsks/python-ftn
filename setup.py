#!/usr/bin/python

from setuptools import setup, find_packages

setup(name = "fidonet",
        version = "1",
        description = "FTN tools for Python",
        long_description=open('README.rst').read(),
        author = "Lars Kellogg-Stedman",
        author_email = "lars@oddbit.com",
        url = "http://github.com/larsks/fidonet",
        packages = [
            'fidonet',
            ],
        scripts = [
            'bin/ftn-msgedit',
            'bin/ftn-reroute',
            'bin/ftn-scanmsg',
            'bin/ftn-scanpkt',
            'bin/ftn-unpack',
            ],
        install_requires = [
            'bitstring'
            ],
        )

