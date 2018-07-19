#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request
from pathlib import Path
from redis import StrictRedis
import json

app = Flask(__name__)

socket_path = Path('lookup_db', 'lookup.sock')

if not socket_path.exists():
    raise Exception(f'{socket_path} does not exists')

r = StrictRedis(unix_socket_path=str(socket_path))


@app.route('/', methods=['POST'])
def index():
    req_data = request.get_json()
    if not req_data.get('sha512'):
        return json.dumps({'error': 'The key "sha512" is required.'})
    if req_data.get('details'):
        details = r.get(req_data['sha512'])
        if details:
            return json.dumps({'exists': True, 'details': json.loads(details)})
        else:
            return json.dumps({'exists': False, 'details': ''})
    else:
        return json.dumps({'exists': r.exists(req_data['sha512'])})
