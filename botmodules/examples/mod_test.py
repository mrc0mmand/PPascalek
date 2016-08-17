#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import module_base

class Test(module_base.ModuleBase):

    def __init__(self, b, settings):
        print("mod_test Initialized")

    def get_commands(self):
        return ["test"]

    def on_privmsg(self, connection, event):
        print("mod_test has got a privmsg! [{}]".format(event.arguments))
        connection.privmsg(event.source, "I'M ALIVE!")

    def on_pubmsg(self, connection, event):
        print("[Test] Event object:", event)
        print("mod_test has got a pubmsg: {}".format(event.arguments[0]))

    def on_command(self, b, module_data, connection, event, is_public):
        print("[Test] Got command: {}".format(module_data["command"]))
        b.send_msg(connection, event, is_public, "Test successful")
