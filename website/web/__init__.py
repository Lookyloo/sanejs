#!/usr/bin/env python3

import pkg_resources

from flask import Flask, request
from flask_restx import Api, Resource, fields  # type: ignore

from sanejs.query import Query

from .proxied import ReverseProxied

app = Flask(__name__)

app.wsgi_app = ReverseProxied(app.wsgi_app)  # type: ignore

api = Api(app, title='SaneJS API',
          description='API to query a SaneJS instance.',
          version=pkg_resources.get_distribution('sanejs').version)

q = Query()


sha512_fields = api.model('SHA512Fields', {
    'sha512': fields.String(description="The SHA512 to search", required=True)
})


library_fields = api.model('LibraryFields', {
    'library': fields.String(description="The library to search", required=True)
})


@api.route('/sha512')
@api.doc(description='Get the entries related to this hash (sha512)')
class SHA512(Resource):

    @api.param('sha512', 'The hash to check', required=True)
    def get(self):
        if 'sha512' not in request.args or not request.args.get('sha512'):
            return {'error': 'The hash is required...'}, 400
        return q.search_hash(request.args['sha512'])

    @api.doc(body=sha512_fields)
    def post(self):
        try:
            req_data = request.get_json(force=True)
        except Exception as e:
            return {'error': e}

        if not req_data.get('sha512'):
            return {'error': 'The key "sha512" is required.'}
        return q.search_hash(req_data['sha512'])


@api.route('/library')
@api.doc(description='Get the entries related to this library')
class Library(Resource):

    @api.param('library', 'The library name to check', required=True)
    def get(self):
        if 'library' not in request.args or not request.args.get('library'):
            return {'error': 'The library is required...'}, 400
        return q.search_lib(request.args['library'])

    @api.doc(body=library_fields)
    def post(self):
        try:
            req_data = request.get_json(force=True)
        except Exception as e:
            return {'error': e}

        if not req_data.get('library'):
            return {'error': 'The key "library" is required.'}

        if 'version' in req_data:
            return q.search_lib(req_data['library'], req_data['version'])
        else:
            return q.search_lib(req_data['library'])
