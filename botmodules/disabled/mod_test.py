#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import module_base

class Test(module_base.ModuleBase):

    def __init__(self, config_file):
        print("mod_test Initialized")

    def on_privmsg(self, connection, event):
        print("mod_test has got a privmsg! [{}]".format(event.arguments))
        connection.privmsg(event.source, "I'M ALIVE!")

    def on_pubmsg(self, connection, event):
        print("[Test] Event object:", event)
        print("mod_test has got a pubmsg: {}".format(event.arguments[0]))

