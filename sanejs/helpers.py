#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from functools import lru_cache
from pathlib import Path
from .exceptions import MissingEnv


@lru_cache(64)
def get_homedir() -> Path:
    if not os.environ.get('SANEJS_HOME'):
        # Try to open a .env file in the home directory if it exists.
        if (Path(__file__).resolve().parent.parent / '.env').exists():
            with (Path(__file__).resolve().parent.parent / '.env').open() as f:
                for line in f:
                    key, value = line.strip().split('=', 1)
                    if value[0] in ['"', "'"]:
                        value = value[1:-1]
                    os.environ[key] = value

    if not os.environ.get('SANEJS_HOME'):
        guessed_home = Path(__file__).resolve().parent.parent
        raise MissingEnv(f"SANEJS_HOME is missing. \
Run the following command (assuming you run the code from the clonned repository):\
    export LOOKYLOO_HOME='{guessed_home}'")
    return Path(os.environ['SANEJS_HOME'])


def get_socket_path(name: str) -> str:
    mapping = {
        'lookup': Path('lookup', 'lookup.sock')
    }
    return str(get_homedir() / mapping[name])
