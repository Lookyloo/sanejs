#!/usr/bin/env python3


class SaneJSException(Exception):
    pass


class MissingEnv(SaneJSException):
    pass


class CreateDirectoryException(SaneJSException):
    pass


class ConfigError(SaneJSException):
    pass
