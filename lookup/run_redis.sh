#!/bin/bash

set -e
# set -x

if [ -f  ../../valkey/src/valkey-server ]; then
    if [[ ` ../../valkey/src/valkey-server -v` == *"v=7."* ]] ; then
        echo "You're using valkey 7, please upgrade do valkey 8"
        exit 1
    fi
    ../../valkey/src/valkey-server ./lookup.conf
elif [ -f ../../redis/src/redis-server ]; then
    if [[ ` ../../redis/src/redis-server -v` == *"v=7."* ]] ; then
        echo "You're using redis 7, please upgrade do valkey 8";
        exit 1
    fi
    ../../redis/src/redis-server ./lookup.conf
else
    if [[ `/usr/bin/redis-server -v` == *"v=7."* ]] ; then
        echo "You're using redis 7, please upgrade do valkey 8";
        exit 1
    fi
    echo "Warning: using system redis-server. Valkey-server or redis-server from source is recommended." >&2
    /usr/bin/redis-server ./lookup.conf
fi
