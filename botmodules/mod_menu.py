#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Performs a search on the online dictionary jisho.org """


from . import module_base
import urllib.request
from urllib.error import URLError

class Menu(module_base.ModuleBase):

    def __init__(self, config_file):
        pass

    def get_commands(self):
        return [ 'menu' ]

    def _get_menu(self, connection, event, is_public, word):
        try:
            req = urllib.request.urlopen("http://blaskovic.sk:8099/?menu={0}".format(urllib.request.quote(word)), None, 5)
        except URLError as e:
            self.send_msg(connection, event, is_public, "[Menu_mod] 404")
            return
        except Exception as e:
            self.send_msg(connection, event, is_public, "[Menu_mod] Unknown error: " + str(e))
            return

        out = req.read().decode("utf-8")
        for line in out.split("\n"):
            self.send_msg(connection, event, is_public, line)

        return out

    def on_command(self, command_data, connection, event, is_public):
        print('[Menu_mod] Event object:', event)
        print('[Menu_mod] Arguments object:', event.arguments)

        args = event.arguments[0]

        self._get_menu(connection, event, is_public, args)
