#!/usr/bin/python3
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class ModuleBase(metaclass=ABCMeta):

    def __init__(self):
        pass

    def get_commands(self):
        pass

    def send_msg(self, connection, event, isPublic, message):
        if isPublic != False:
            connection.privmsg(event.target, message)
        else:
            connection.privmsg(event.source, message)

    def on_privmsg(self, connection, event):
        pass

    def on_pubmsg(self, connection, event):
        pass

    def on_command(self, command, connection, event, isPublic):
        pass

    def on_join(self, connection, event):
        pass

    def on_quit(self, connection, event):
        pass

    def on_nick(self, connection, event):
        pass