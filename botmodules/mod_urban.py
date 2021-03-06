#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Returns urbandictionary definitions for user's string"""

from . import module_base
import urllib.request, sys, re, json
from urllib.error import URLError

class Urban(module_base.ModuleBase):

    def __init__(self, b, settings):
        pass

    def get_commands(self):
        return [ 'urban', 'urbandictionary', 'urbandict' ]

    def _get_urban_def(self, word, index):
        try:
            # quote by měl bejt v py3 fixnutej na unikód, jestli neni tak rip
            req = urllib.request.urlopen("http://urbanscraper.herokuapp.com/search/{0}"
                  .format(urllib.request.quote(word)), None, 5)
        except URLError as e:
            return "[Urban] Definition could not be found."
        except Exception as e:
            print('[Urban] Error sending request to urbanscrapper. Reason: {0}'
                  .format(str(e)), file=sys.stderr)
            return "[Urban] Unknown error."

        # .read() vrací nějaký mrdkobajty, proto decode utf-8, zasranej python3
        parsed = json.loads(req.read().decode("utf-8"))
        return "[{0}]: {1}".format(parsed[index]["term"], parsed[index]["definition"]) \
               if len(parsed[index]["definition"]) < 150 \
               else "[{0}]: {1}… (more at {2})" .format(parsed[index]["term"], \
                    parsed[index]["definition"][:150], "http://urbandictionary.com/define.php?term={0}"
                    .format(urllib.request.quote(word))) # url je rozbitý

    def on_command(self, b, module_data, connection, event, is_public):
        args = event.arguments[0] # change this when an argument system gets implemented
        m = re.match("([0-9]+) (.*)", args)
        if(m):
            index = int(m.group(1))
            args = str(m.group(2))
        else:
            index = 0
            args = args

        to_where = event.target if is_public == True else event.source
        b.send_msg(connection, event, is_public, self._get_urban_def(args, index))
