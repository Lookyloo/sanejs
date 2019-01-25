#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify

from sanejs.query import Query

app = Flask(__name__)

q = Query()


@app.route('/', methods=['POST'])
def sha512():
    if request.method == 'HEAD':
        # Just returns ack if the webserver is running
        return 'Ack'
    try:
        req_data = request.get_json(force=True)
    except Exception as e:
        return jsonify({'error': e})

    if not req_data.get('sha512'):
        return jsonify({'error': 'The key "sha512" is required.'})
    return jsonify(q.search_hash(req_data['sha512']))


@app.route('/library', methods=['POST'])
def library():
    try:
        req_data = request.get_json(force=True)
    except Exception as e:
        return jsonify({'error': e})

    if not req_data.get('library'):
        return jsonify({'error': 'The key "library" is required.'})

    if 'version' in req_data:
        to_return = q.search_lib(req_data['library'], req_data['version'])
    else:
        to_return = q.search_lib(req_data['library'])

    return jsonify(to_return)
