#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

from sanejs import SaneJS


if __name__ == '__main__':
    logging.basicConfig()
    argParser = argparse.ArgumentParser(description='Search a hash in the cdnjs database')
    argParser.add_argument('-s', '--search', required=True, help='SHA512 to search')
    args = argParser.parse_args()

    sjs = SaneJS()
    print(sjs.search(args.search))
