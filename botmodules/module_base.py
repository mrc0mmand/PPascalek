#!/usr/bin/python3
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from botutils import utils

class ModuleBase(metaclass=ABCMeta):

    def __init__(self, settings):
        pass

    def get_commands(self):
        pass

    def send_msg(self, connection, event, is_public, message):
        destination = event.target if is_public != False else event.source

        # Even though RFC has message limit 400 bytes, many servers
        # have their own limit. Thus setting it to 400 characters.
        buffer_max = (400 - len(destination) - 12)
        msg_len = len(message.encode('utf-8'))

        if msg_len >= buffer_max:
            data = utils.split_utf8(message.encode('utf-8'), buffer_max)

            for i in data:
                try:
                    connection.privmsg(destination, i.decode('utf-8'))
                except Exception as e:
                    print("Exception {0}" .format(str(e)))
        else:
            try:
                connection.privmsg(destination, message)
            except Exception as e:
                print("Exception {0}" .format(str(e)))
            
        
    def on_privmsg(self, connection, event):
        pass

    def on_pubmsg(self, connection, event):
        pass

    def on_command(self, module_data, connection, event, is_public):
        pass

    def on_join(self, connection, event):
        pass

    def on_quit(self, connection, event):
        pass

    def on_nick(self, connection, event):
        pass
