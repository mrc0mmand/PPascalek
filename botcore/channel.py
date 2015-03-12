#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Channel(object):

    def __init__(self, server, name, pass_, cmdprefix):
        self._server = server
        self._name = name
        self._pass = pass_
        self._cmmdprefix = cmdprefix

    def get_server(self):
        return self._server

    def get_name(self):
        return self._name

    def get_pass(self):
        return self._pass

    def get_cmdprefix(self):
        return self._cmmdprefix