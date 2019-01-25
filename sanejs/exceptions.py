#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class SaneJSException(Exception):
    pass


class MissingEnv(SaneJSException):
    pass
