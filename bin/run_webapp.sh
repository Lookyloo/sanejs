#!/usr/bin/env bash

set -e
set -x

FLASK_APP=flask_lookup.py flask run
