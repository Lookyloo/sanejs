#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import Popen
from sanejs.helpers import get_homedir


def main():
    # Just fail if the env isn't set.
    get_homedir()
    p = Popen(['run_backend', '--start'])
    p.wait()
    Popen(['build_hashes'])


if __name__ == '__main__':
    main()
