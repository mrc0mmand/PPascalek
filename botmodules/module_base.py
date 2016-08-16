#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from botutils import utils
from abc import ABCMeta, abstractmethod

class ModuleBase(metaclass=ABCMeta):

    def __init__(self, settings):
        pass

    def get_commands(self):
        pass

    def get_name(self):
        return self.__class__.__name__

    def get_global_settings(self, settings):
        if "@global" in settings:
            return settings["@global"]

        return None

    def get_curr_settings(self, connection, event, is_public, settings):
        if is_public == False and "@global" in settings[connection.server]:
            return settings[connection.server]["@global"]
        elif is_public == True:
            if event.target in settings[connection.server]:
                return settings[connection.server][event.target]
            elif "@global" in settings[connection.server]:
                return settings[connection.server]["@global"]

        return None

    def on_privmsg(self, connection, event):
        pass

    def on_pubmsg(self, connection, event):
        pass

    def on_command(self, b, module_data, connection, event, is_public):
        pass

    def on_help(self, b, module_data, connection, event, is_public):
        pass

    def on_join(self, connection, event):
        pass

    def on_quit(self, connection, event):
        pass

    def on_nick(self, connection, event):
        pass
