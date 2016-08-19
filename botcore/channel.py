#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

class Channel(object):

    def __init__(self, server, name, pass_, cmdprefix):
        self._server = server
        self._name = name
        self._pass = pass_
        self._cmmdprefix = cmdprefix
        self._users = set()

    def add_user(self, user):
        self._users.add(user)

    def change_user(self, old, new):
        if old in self._users:
            self._users.remove(old)
            self._users.add(new)
        else:
            print("[WARNING] User '{}' was not found in channel user list"
                    .format(old), file=sys.stderr)

    def get_cmdprefix(self):
        return self._cmmdprefix

    def get_name(self):
        return self._name

    def get_pass(self):
        return self._pass

    def get_server(self):
        return self._server

    def get_users(self):
        return self._users

    def has_user(self, user):
        return (user in self._users)

    def remove_user(self, user):
        self._users.discard(user)
