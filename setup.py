#!/usr/bin/env python
from setuptools import setup  # type: ignore


setup(
    name='sanejs',
    version='0.1',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    url='https://github.com/CIRCL/sanejs',
    description='Lookup service for known legitimate JavaScript.',
    packages=['sanejs'],
    scripts=['bin/run_backend.py', 'bin/build_hashes.py', 'bin/start.py', 'bin/stop.py', 'bin/shutdown.py',
             'bin/start_website.py'],
    classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3',
        'Topic :: Security',
        'Topic :: Internet',
    ]
)
