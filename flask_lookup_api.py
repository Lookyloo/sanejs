#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import argparse
import json

url = 'http://127.0.0.1:5007/'


def query(sha512, details=False):
    r = requests.post(url, json={"sha512": sha512, 'details': details})
    return r.json()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run query against lookup DBs.')
    parser.add_argument("sha512", help="SHA512 to search")
    parser.add_argument("-d", '--details', action='store_true', default=False, help="Also returns retails in there is a match")
    args = parser.parse_args()

    print(json.dumps(query(args.sha512, args.details)))
