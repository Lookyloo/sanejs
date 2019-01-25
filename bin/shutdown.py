#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanejs.helpers import is_running, get_socket_path
import time
from redis import Redis

if __name__ == '__main__':
    r = Redis(unix_socket_path=get_socket_path('lookup'), db=1, decode_responses=True)
    r.set('shutdown', 1)
    while True:
        running = is_running()
        print(running)
        if not running:
            break
        time.sleep(10)
