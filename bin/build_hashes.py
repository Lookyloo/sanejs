#!/usr/bin/env python3

from sanejs.sanejs import SaneJS

from sanejs.default import AbstractManager
import logging


class SaneJSManager(AbstractManager):

    def __init__(self, loglevel: int=logging.INFO):
        super().__init__(loglevel)
        self.script_name = 'build_hashes'
        self.sanejs = SaneJS(loglevel)
        self.sanejs.compute_hashes(force_recompute=True)

    def _to_run_forever(self):
        self.sanejs.compute_hashes()


def main():
    s = SaneJSManager()
    s.run(sleep_in_sec=3600)


if __name__ == '__main__':
    main()
