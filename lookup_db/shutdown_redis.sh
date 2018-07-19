#!/usr/bin/env bash

set -e
set -x

../../redis/src/redis-cli -s ./lookup.sock shutdown
