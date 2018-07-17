#!/bin/bash

set -e
set -x

git submodule foreach git pull origin master
