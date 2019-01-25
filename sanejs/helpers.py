#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from .exceptions import MissingEnv
from redis import StrictRedis
from redis.exceptions import ConnectionError
from datetime import datetime, timedelta
import time


def get_homedir() -> Path:
    if not os.environ.get('SANEJS_HOME'):
        guessed_home = Path(__file__).resolve().parent.parent
        raise MissingEnv(f"SANEJS_HOME is missing. \
Run the following command (assuming you run the code from the clonned repository):\
    export SANEJS_HOME='{guessed_home}'")
    return Path(os.environ['SANEJS_HOME'])


def set_running(name: str) -> None:
    r = StrictRedis(unix_socket_path=get_socket_path('lookup'), db=1, decode_responses=True)
    r.hset('running', name, 1)


def unset_running(name: str) -> None:
    r = StrictRedis(unix_socket_path=get_socket_path('lookup'), db=1, decode_responses=True)
    r.hdel('running', name)


def is_running() -> dict:
    r = StrictRedis(unix_socket_path=get_socket_path('lookup'), db=1, decode_responses=True)
    return r.hgetall('running')


def get_socket_path(name: str) -> str:
    mapping = {
        'lookup': Path('lookup', 'lookup.sock')
    }
    return str(get_homedir() / mapping[name])


def check_running(name: str) -> bool:
    socket_path = get_socket_path(name)
    print(socket_path)
    try:
        r = StrictRedis(unix_socket_path=socket_path)
        if r.ping():
            return True
    except ConnectionError:
        return False


def shutdown_requested() -> bool:
    try:
        r = StrictRedis(unix_socket_path=get_socket_path('lookup'), db=1, decode_responses=True)
        return r.exists('shutdown')
    except ConnectionRefusedError:
        return True
    except ConnectionError:
        return True


def long_sleep(sleep_in_sec: int, shutdown_check: int=10) -> bool:
    if shutdown_check > sleep_in_sec:
        shutdown_check = sleep_in_sec
    sleep_until = datetime.now() + timedelta(seconds=sleep_in_sec)
    while sleep_until > datetime.now():
        time.sleep(shutdown_check)
        if shutdown_requested():
            return False
    return True
