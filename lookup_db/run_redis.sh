#!/usr/bin/env bash

set -e
set -x

../../redis/src/redis-server ./lookup.conf
