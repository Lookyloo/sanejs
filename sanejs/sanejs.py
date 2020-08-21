#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import hashlib
import json
import time

from redis import Redis
from git import Repo  # type: ignore

from .helpers import get_homedir, get_socket_path

"""
sha: set of libname|version|fullpath

libname|version: hash of fullpath -> sha
"""

# We assume the initialisation of the submodule is done before calling this class.


class SaneJS():

    def __init__(self, loglevel: int=logging.DEBUG) -> None:
        self.__init_logger(loglevel)
        self.libs_path = get_homedir() / 'cdnjs' / 'ajax' / 'libs'
        self.redis_lookup = Redis(unix_socket_path=get_socket_path('lookup'), decode_responses=True)
        self.cdnjs_repo = Repo(str(get_homedir() / 'cdnjs'))

    def __init_logger(self, loglevel: int):
        self.logger = logging.getLogger(f'{self.__class__.__name__}')
        self.logger.setLevel(loglevel)

    def _pull_dnsjs(self):
        last_commit_ts = self.redis_lookup.get('last_commit')
        if not last_commit_ts or int(last_commit_ts) < time.time() - 10000:
            self.cdnjs_repo.remote('origin').pull()
            return True
        return False

    def compute_hashes(self, force_recompute: bool=False):
        '''Compute the hashes for the (new) files, create a file in the root directory of each library'''
        if force_recompute:
            self.logger.info('Force recompute and re-cache everything.')
            self.redis_lookup.flushdb()
        if not self._pull_dnsjs():
            return
        self.logger.debug('Compute hashes.')
        for libname in self.libs_path.iterdir():
            # libname is the path to the library, it contains a directory for each version
            if not libname.is_dir():
                continue
            short_libname = libname.as_posix().replace(self.libs_path.as_posix() + '/', '')
            self.logger.info(f'Processing {short_libname}.')
            all_hashes_lib = {}
            p = self.redis_lookup.pipeline()
            p.sadd('all_libraries', short_libname)
            for version in libname.iterdir():
                # This is the directory for a version of the library. It can contain all kind of directories and files
                if not version.is_dir():
                    if version.name not in ['package.json', 'hashes.json', '.donotoptimizepng']:
                        # packages.json is expected, and we don't care
                        self.logger.warning(f'That is it Oo -> {version}.')
                    continue
                short_version = version.as_posix().replace(libname.as_posix() + '/', '')
                if force_recompute or not (version / 'hashes.json').exists():
                    # Only compute the *new* hashes (unless specified)
                    to_save = {}
                    for to_hash in version.glob('**/*'):
                        if not to_hash.is_file() or to_hash.name == 'hashes.json':
                            continue
                        # The file may or may not have a new line at the end.
                        # The files we want to check against may or may not have the new line at the end.
                        # We will compute both hashes.
                        with open(to_hash, 'rb') as f_to_h:
                            content = f_to_h.read()
                        file_hash_default = hashlib.sha512(content)
                        if content:
                            if content[-1] == '\n':
                                # has newline
                                file_hash_newline = hashlib.sha512(content)
                                file_hash_no_newline = hashlib.sha512(content[:-1])
                            else:
                                # Doesn't have newline
                                file_hash_no_newline = hashlib.sha512(content)
                                file_hash_newline = hashlib.sha512(content + b'\n')
                        else:
                            # Empty file
                            file_hash_newline = file_hash_default
                            file_hash_newline = file_hash_default
                        filepath = to_hash.as_posix().replace(version.as_posix() + '/', '')
                        to_save[filepath] = {'newline': file_hash_newline.hexdigest(), 'no_newline': file_hash_no_newline.hexdigest(), 'default': file_hash_default.hexdigest()}
                        p.sadd(file_hash_newline.hexdigest(), f'{short_libname}|{short_version}|{filepath}')
                        p.sadd(file_hash_no_newline.hexdigest(), f'{short_libname}|{short_version}|{filepath}')
                        p.hset(f'{short_libname}|{short_version}', filepath, file_hash_default.hexdigest())
                        p.sadd(short_libname, short_version)
                    with open((version / 'hashes.json'), 'w') as f:
                        # Save the hashes in the directory (aka cache it)
                        json.dump(to_save, f, indent=2)
                else:
                    # Just load the cached hashes
                    with open((version / 'hashes.json')) as f:
                        to_save = json.load(f)
                    for filepath, f_hash in to_save.items():
                        p.sadd(f_hash['newline'], f'{short_libname}|{short_version}|{filepath}')
                        p.sadd(f_hash['no_newline'], f'{short_libname}|{short_version}|{filepath}')
                        p.hset(f'{short_libname}|{short_version}', filepath, f_hash['default'])
                all_hashes_lib[version.name] = to_save
            with open((libname / 'hashes.json'), 'w') as f:
                # Write a file with all the hashes for all the versions at the root directory of the library
                json.dump(all_hashes_lib, f, indent=2)
            p.execute()
        self.redis_lookup.set('ready', 1)
        self.logger.debug('Compute hashes done.')
