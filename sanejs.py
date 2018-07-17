#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import pathlib
import hashlib
import json

from git import Repo


class SaneJS():

    def __init__(self, loglevel: int=logging.DEBUG) -> None:
        self.__init_logger(loglevel)
        self.libs_path = pathlib.Path('cdnjs', 'ajax', 'libs')
        self.aggregated_path = pathlib.Path('aggregated.json')
        self.hashes_lookup_path = pathlib.Path('lookup.json')
        self.cdnjs_processed = pathlib.Path('cdnjs_commit')
        if self.load_cdnjs_processed() and self.get_last_commit_cdnjs() != self.load_cdnjs_processed():
            self.logger.warning('Cache outdated, re-run compute_hashes.')
        self._aggregate = None
        self._hashes_lookup = None

    def get_last_commit_cdnjs(self):
        cdnjs_repo = Repo('cdnjs')
        return str(cdnjs_repo.commit('HEAD'))

    def load_cdnjs_processed(self):
        if not self.cdnjs_processed.exists():
            return None
        with open(self.cdnjs_processed) as f:
            return f.read()

    def __init_logger(self, loglevel: int):
        self.logger = logging.getLogger(f'{self.__class__.__name__}')
        self.logger.setLevel(loglevel)

    def compute_hashes(self, force_recompute=False):
        '''Compute the hashes for the (new) files, create a file in the root directory of each library'''
        self.logger.debug('Compute hashes.')
        updated = False
        for libname in self.libs_path.iterdir():
            # libname is the path to the library, it contains a directory for each version
            if not libname.is_dir():
                continue
            print(libname)
            all_hashes_lib = {}
            for version in libname.iterdir():
                # This is the directory for a version of the library. It can contain all kind of directories and files
                if not version.is_dir():
                    if version.suffix != '.json':
                        # Also contains a packages.json file, we don't care
                        print(version)
                    continue
                if force_recompute or not (version / 'hashes.json').exists():
                    # Only compute the *new* hashes (unless specified)
                    updated = True
                    to_save = {}
                    for to_hash in version.glob('**/*'):
                        if not to_hash.is_file() or to_hash.name == 'hashes.json':
                            continue
                        with open(to_hash, 'rb') as f:
                            to_save[to_hash.as_posix().replace(version.as_posix() + '/', '')] = hashlib.sha512(f.read()).hexdigest()
                    with open((version / 'hashes.json'), 'w') as f:
                        # Save the hashes in the directory (aka cache it)
                        json.dump(to_save, f, indent=2)
                else:
                    # Just load the cached hashes
                    with open((version / 'hashes.json')) as f:
                        to_save = json.load(f)
                all_hashes_lib[version.name] = to_save
            with open((libname / 'hashes.json'), 'w') as f:
                # Write a file with all the hashes for all the versions at the root directory of the library
                json.dump(all_hashes_lib, f, indent=2)
        with open(self.cdnjs_processed, 'w') as f:
            f.write(self.get_last_commit_cdnjs())
        if updated:
            if self.aggregated_path.exists():
                self.aggregated_path.unlink()
            if self.hashes_lookup_path.exists():
                self.hashes_lookup_path.unlink()
        self.logger.debug('Compute hashes done.')

    def build_aggregate(self):
        '''Just aggregate the hashes in the root directory of each library'''
        self.logger.debug('Build aggregate.')
        aggregate = {}
        for libname in self.libs_path.iterdir():
            if libname.is_file():
                continue
            if not (libname / 'hashes.json').exists():
                self.logger.warning(f'Cache outdated: {libname.name} does not have hashes available.')
                continue
            with open((libname / 'hashes.json')) as f:
                hashes_lib = json.load(f)
            # Check if all the versions have hashes available
            versions = [v.name for v in libname.iterdir() if v.is_dir()]
            if len(versions) != len(hashes_lib.keys()):
                missing = set(versions).symmetric_difference(set(hashes_lib.keys()))
                self.logger.warning(f'Cache outdated: Missing hashes for some versions of {libname.name}: {missing}')
            aggregate[libname.name] = hashes_lib
        with open(self.aggregated_path, 'w') as f:
            json.dump(aggregate, f, indent=2)
        if self.hashes_lookup_path.exists():
            self.hashes_lookup_path.unlink()
        self.logger.debug('Build aggregate done.')

    def build_hashes_lookup(self):
        self.logger.debug('Build hashes lookup.')
        self._hashes_lookup = {}
        for libname, versions in self.aggregate.items():
            for version, files in versions.items():
                for filename, h in files.items():
                    if h not in self._hashes_lookup:
                        self._hashes_lookup[h] = []
                    self._hashes_lookup[h].append({'libname': libname, 'version': version, 'filename': filename})
        with open(self.hashes_lookup_path, 'w') as f:
            json.dump(self._hashes_lookup, f, indent=2)
        self.logger.debug('Build hashes lookup done.')

    @property
    def aggregate(self):
        if not self._aggregate:
            self._load_aggregate()
        return self._aggregate

    @property
    def lookup_hash(self):
        if not self._hashes_lookup:
            self._load_hashes_lookup()
        return self._hashes_lookup

    def _load_hashes_lookup(self):
        if not self.hashes_lookup_path.exists():
            self.build_hashes_lookup()
        self.logger.debug('Loading hashes lookup.')
        with open(self.hashes_lookup_path, 'r') as f:
            self._hashes_lookup = json.load(f)
        self.logger.debug('Loading hashes lookup done.')

    def _load_aggregate(self):
        if not self.aggregated_path.exists():
            self.build_aggregate()
        self.logger.debug('Loading aggregate.')
        with open(self.aggregated_path, 'r') as f:
            self._aggregate = json.load(f)
        self.logger.debug('Loading aggregate done.')

    def search(self, hash_to_search):
        if self.get_last_commit_cdnjs() != self.load_cdnjs_processed():
            self.logger.warning('Cache outdated, re-run compute_hashes.')
        return self.lookup_hash.get(hash_to_search, {})
