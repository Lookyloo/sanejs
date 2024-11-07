#!/usr/bin/env python3
import logging
import hashlib
import orjson
import time

from redis import Redis
from git import Repo  # type: ignore

from .default import get_homedir, get_socket_path

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

    def compute_hashes(self, force_recache: bool=False, force_rehash: bool=False) -> None:
        '''Compute the hashes for the (new) files, create a file in the root directory of each library'''
        if not self._pull_dnsjs():
            return
        if force_recache:
            self.logger.info('Force recompute and re-cache everything.')
            self.redis_lookup.flushdb()
        self.logger.debug('Compute hashes.')
        for libname in self.libs_path.iterdir():
            # libname is the path to the library, it contains a directory for each version
            if not libname.is_dir():
                continue
            if (libname / 'hashes.json').exists():
                with (libname / 'hashes.json').open('rb') as f:
                    # We have the hashes, we can skip this library
                    all_hashes_lib = orjson.loads(f.read())
            self.logger.info(f'Processing {libname.name}.')
            got_new_versions = False
            for version in libname.iterdir():
                # This is the directory for a version of the library. It can contain all kind of directories and files
                if not version.is_dir():
                    if version.name not in ['package.json', 'hashes.json', '.donotoptimizepng']:
                        # packages.json is expected, and we don't care
                        self.logger.warning(f'That is it Oo -> {version}.')
                    continue

                if version.name in all_hashes_lib[libname.name] and not force_rehash and not force_recache:
                    # This version was already loaded
                    # Unless we rehash or recache, we can skip it
                    continue

                if (version / 'hashes.json').exists() and not force_rehash:
                    # We have the hashes, we can skip this version
                    with (version / 'hashes.json').open('rb') as f:
                        to_save = orjson.loads(f.read())
                    if force_recache:
                        # Only re-cache the hashes if requested.
                        p = self.redis_lookup.pipeline()
                        for filepath, f_hash in to_save.items():
                            p.sadd(f_hash['newline'], f'{libname.name}|{version.name}|{filepath}')
                            p.sadd(f_hash['no_newline'], f'{libname.name}|{version.name}|{filepath}')
                            p.hset(f'{libname.name}|{version.name}', filepath, f_hash['default'])
                        p.execute()
                else:
                    # We need to compute the hashes
                    got_new_versions = True
                    self.logger.info(f'Got new version for {libname.name}: {version.name}.')
                    to_save = {}
                    p = self.redis_lookup.pipeline()
                    for to_hash in version.glob('**/*'):
                        if not to_hash.is_file() or to_hash.name == 'hashes.json':
                            continue
                        # The file may or may not have a new line at the end.
                        # The files we want to check against may or may not have the new line at the end.
                        # We will compute both hashes.
                        with to_hash.open('rb') as f_to_h:
                            content = f_to_h.read()
                        file_hash_default = hashlib.sha512(content)
                        if content:
                            if content[-1:] == b'\n':
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
                        p.sadd(file_hash_newline.hexdigest(), f'{libname.name}|{version.name}|{filepath}')
                        p.sadd(file_hash_no_newline.hexdigest(), f'{libname.name}|{version.name}|{filepath}')
                        p.hset(f'{libname.name}|{version.name}', filepath, file_hash_default.hexdigest())
                        p.sadd(libname.name, version.name)
                    p.execute()
                    with (version / 'hashes.json').open('wb') as f:
                        # Save the hashes in the directory (aka cache it)
                        f.write(orjson.dumps(to_save))
                all_hashes_lib[version.name] = to_save
            if got_new_versions:
                with (libname / 'hashes.json').open('wb') as f:
                    # Write a file with all the hashes for all the versions at the root directory of the library
                    f.write(orjson.dumps(all_hashes_lib))
            self.redis_lookup.sadd('all_libraries', libname.name)
        self.redis_lookup.set('ready', 1)
        self.logger.debug('Compute hashes done.')
