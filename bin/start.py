#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import Popen, run
from sanejs.helpers import get_homedir


def main():
    # Just fail if the env isn't set.
    get_homedir()
    p = run(['run_backend', '--start'])
    p.check_returncode()
    Popen(['build_hashes'])
    Popen(['start_website'])


if __name__ == '__main__':
    main()
