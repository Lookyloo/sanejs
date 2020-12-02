#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import Popen
from sanejs.helpers import get_homedir


def main():
    try:
        Popen(['gunicorn', '--worker-class', 'gevent', '-w', '10', '-b', '0.0.0.0:5007', 'web:app'],
              cwd=get_homedir() / 'website').communicate()
    except KeyboardInterrupt:
        print('Stopping gunicorn.')


if __name__ == '__main__':
    main()
