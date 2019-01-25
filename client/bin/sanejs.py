#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run query against lookup DBs.')
    parser.add_argument("sha512", help="SHA512 to search")
    args = parser.parse_args()

    print(json.dumps(query(args.sha512, args.details)))
