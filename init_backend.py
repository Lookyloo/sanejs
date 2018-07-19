#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import Popen
from pathlib import Path
from redis import StrictRedis
import time
import sys
import json
import logging
import argparse


logging.basicConfig(level=logging.DEBUG)

# Make sure the lookup file is available

lookup_file_path = Path('lookup.json')
if not lookup_file_path.exists():
    logging.critical('Lookup file not available, breaking.')
    sys.exit(1)

socket_path = Path('lookup_db', 'lookup.sock')


def redis_running():
    if not socket_path.exists():
        logging.critical('Redis socket does not exists, breaking.')
        sys.exit(1)
    while True:
        try:
            r = StrictRedis(unix_socket_path=str(socket_path))
            r.ping()
            return r
        except ConnectionError:
            logging.info('Redis not ready yet')
            time.sleep(1)


def launch():
    logging.info('Launch redis')
    # Launch redis DB
    Popen(["./run_redis.sh"], cwd=Path('lookup_db'))

    logging.info('Load lookup file')
    with open(lookup_file_path) as f:
        lookup = json.load(f)
    logging.info('Lookup file loaded')

    r = redis_running()
    logging.info('Start import')
    p = r.pipeline(transaction=False)
    for sha512, details in lookup.items():
        p.set(sha512, json.dumps(details))
    p.execute()
    logging.info('Import done')


def shutdown():
    logging.info('Shutdown redis')
    # We don't store the db anyway, we don't care when it stops exacty.
    Popen(["./shutdown_redis.sh"], cwd=Path('lookup_db'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage redis lookup db.')
    parser.add_argument("--start", action='store_true', default=False,)
    parser.add_argument("--stop", action='store_true', default=False,)
    args = parser.parse_args()

    if args.start:
        launch()
    elif args.stop:
        shutdown()
