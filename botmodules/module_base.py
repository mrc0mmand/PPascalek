#!/usr/bin/python3
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class ModuleBase(metaclass=ABCMeta):

    def __init__(self):
        pass

    def get_commands(self):
        pass


    def send_msg(self, connection, event, isPublic, message):
        to_where = event.target if isPublic != False else event.source

        """chtěl jsem udělat globální zkracování zpráv, který se posílaj, kdyby to náhodou nezachytil danej modul
        unicode mě totálně zprcal do zadku a ani už nevim, co je dobře a co ne
        tak si to tu kdyžtak přeber a nebo taky nepřeber, hlavně šlo o to, že doteď ten program padal, protože
        se nechytala výjimka toho, že posíláš víc jak >512 bajtů, ať už ty zprávy chceš tady zkracovat, nebo ne, tak tu
        prostě a jednoduše chyběla aspoň ta výjimka"""

        """length = len("PRIVMSG {0} :{1}\r\n".format(to_where, message.encode('utf-8'))) # \r\n to be sure
        memes = length - len(message.encode('utf-8'))
        msgle = len(message.encode('utf-8'))

        if(length >= 512): 
            mrdky = ((512-msgle)+memes)
            message = message[:mrdky]
            print("MRDKY", len("PRIVMSG {0} :{1}\r\n".format(to_where, message)))
        else:
            print("debug: neni třeba zkracovat")"""

        try:
            connection.privmsg(to_where, message)
        except Exception as e:
            print("Exception {0}".format(str(e)))
            
        
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