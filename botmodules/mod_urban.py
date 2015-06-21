#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import module_base
import urllib.request, sys, re, json
from urllib.error import URLError

class Urban(module_base.ModuleBase):

    def __init__(self):
        pass 

    def get_commands(self):
        return [ 'urban', 'urbandictionary', 'urbandict' ]

    def _getUrbanDef(self, word, index):
        try:
            req = urllib.request.urlopen("http://urbanscraper.herokuapp.com/search/{0}".format(urllib.request.quote(word)), None, 5) # quote by měl bejt v py3 fixnutej na unikód, jestli neni tak rip
        except URLError as e:
            return "[Urban] Definition could not be found." 
        except Exception as e:
            print('[Urban] Error sending request to urbanscrapper. Reason: {0}'.format(str(e)), file=sys.stderr)
            return "[Urban] Unknown error."

        parsed = json.loads(req.read().decode("utf-8"))  # .read() vrací nějaký mrdkobajty, proto decode utf-8, zasranej python3

        return "[{0}]: {1}".format(parsed[index]["term"], parsed[index]["definition"]) if len(parsed[index]["definition"]) < 150 else "[{0}]: {1}… (more at {2})".format(parsed[index]["term"], parsed[index]["definition"][:-150], "http://urbandictionary.com/define.php?term={0}".format(urllib.request.quote(word))) # url je rozbitý

    def on_command(self, command, connection, event, isPublic):
        print('[Urban] Event object:', event)
        print('[Urban] Arguments object:', event.arguments)

        args = event.arguments[0] # change this when an argument system gets implemented
        m = re.match("([0-9]) (.*)", args)
        if(m):
            index = int(m.group(1))
            args = str(m.group(2))
        else:
            index = 0
            args = args

        if isPublic == True:
            connection.privmsg(event.target, self._getUrbanDef(args, index))
        else:
            connection.privmsg(event.source, self._getUrbanDef(args, index))
