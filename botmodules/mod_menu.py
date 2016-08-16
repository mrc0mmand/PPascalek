#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import module_base
import urllib.request
from urllib.error import URLError

class Menu(module_base.ModuleBase):

    def __init__(self, b, settings):
        pass

    def get_commands(self):
        return [ 'menu' ]

    def _get_menu(self, b, connection, event, is_public, word):
        try:
            req = urllib.request.urlopen("http://blaskovic.sk:8099/?menu={0}".format(urllib.request.quote(word)), None, 5)
        except URLError as e:
            b.send_msg(connection, event, is_public, "[Menu_mod] 404")
            return
        except Exception as e:
            b.send_msg(connection, event, is_public, "[Menu_mod] Unknown error: " + str(e))
            return

        out = req.read().decode("utf-8")
        for line in out.split("\n"):
            b.send_msg(connection, event, is_public, line)

        return out

    def on_command(self, b, module_data, connection, event, is_public):
        args = event.arguments[0]

        self._get_menu(b, connection, event, is_public, args)
