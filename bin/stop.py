#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import Popen
from sanejs.helpers import get_homedir, get_socket_path
from redis import Redis

if __name__ == '__main__':
    get_homedir()
    p = Popen(['shutdown.py'])
    p.wait()
    r = Redis(unix_socket_path=get_socket_path('lookup'), db=1, decode_responses=True)
    r.delete('shutdown')
    Popen(['run_backend.py', '--stop'])
