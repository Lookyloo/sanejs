#!/usr/bin/env python3
import logging
from typing import Union, Dict

from redis import Redis

from .default import get_homedir, get_socket_path


class Query():

    def __init__(self, loglevel: int=logging.DEBUG) -> None:
        self.__init_logger(loglevel)
        self.libs_path = get_homedir() / 'cdnjs' / 'ajax' / 'libs'
        self.redis_lookup = Redis(unix_socket_path=get_socket_path('lookup'), decode_responses=True)

    def __init_logger(self, loglevel: int):
        self.logger = logging.getLogger(f'{self.__class__.__name__}')
        self.logger.setLevel(loglevel)

    @property
    def is_ready(self):
        return self.redis_lookup.get('ready') is not None

    def search_hash(self, sha512: Union[str, list]):
        if not self.is_ready:
            return {'error': 'The hashes are not all loaded yet, try again later.'}
        to_return: Dict[str, list] = {'response': []}
        if isinstance(sha512, str):
            to_return['response'] = list(self.redis_lookup.smembers(sha512))
        else:
            p = self.redis_lookup.pipeline()
            [p.smembers(s) for s in sha512]
            to_return['response'] = [list(r) for r in p.execute()]
        return to_return

    def search_lib(self, library: Union[str, list], version: str=None):
        if not self.is_ready:
            return {'error': 'The hashes are not all loaded yet, try again later.'}
        to_return: Dict[str, Union[list, dict]] = {'response': []}
        if isinstance(library, str):
            if version:
                to_return['response'] = {library: {version: self.redis_lookup.hgetall(f'{library}|{version}')}}
            else:
                p = self.redis_lookup.pipeline()
                versions = self.redis_lookup.smembers(library)
                [p.hgetall(f'{library}|{version}') for version in versions]
                to_return['response'] = {library: dict(zip(versions, p.execute()))}
        else:
            # version doesn't make sense here but if the string contains |{version}, we directly get that
            to_return_temp = []
            for lib in library:
                if '|' in lib:
                    libname, version = lib.split('|')
                    to_return_temp.append({libname: {version: self.redis_lookup.hgetall(lib)}})
                else:
                    p = self.redis_lookup.pipeline()
                    versions = self.redis_lookup.smembers(lib)
                    [p.hgetall(f'{lib}|{version}') for version in versions]
                    to_return_temp.append({lib: dict(zip(versions, p.execute()))})

            to_return['response'] = to_return_temp
        return to_return
