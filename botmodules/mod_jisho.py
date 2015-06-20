#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import module_base
import urllib.request, sys, re, json
from urllib.error import URLError

class Jisho(module_base.ModuleBase):

    def __init__(self):
        self._commands = [ 'jisho', 'jword', 'jw', "jsearch", "jishosearch" ]

    def _getJishoSearch(self, word):
        try:
            req = urllib.request.urlopen("http://jisho.org/api/v1/search/words?keyword={0}".format(urllib.request.quote(word)), None, 5) # quote by měl bejt v py3 fixnutej na unikód, jestli neni tak rip
        except URLError as e:
            return "[JishoSearch] 404" 
        except Exception as e:
            print("[JishoSearch] Error sending request to urbanscrapper. Reason: {0}".format(str(e)), file=sys.stderr)
            return "[JishoSearch] Unknown error."

        parsed = json.loads(req.read().decode("utf-8"))  # .read() vrací nějaký mrdkobajty, proto decode utf-8, zasranej python3
        
        # CANCER BEGINS #
        memes = []
        eng = []
        # todo: celý přepsat #
        try:

            for a in parsed["data"][0]["japanese"]:
                if("reading" in a and "word" in a):
                    memes.append("{0} /{1}/".format(a["word"], a["reading"]))
            for a in parsed["data"][0]["senses"]:
                if("english_definitions" in a):
                    for b in a["english_definitions"]:
                        eng.append("{0}".format(b))
            
            final = ""        
            for i in range(0, len(memes)):
                final += "{0} (".format(memes[i]) if i == len(memes)-1 else "{0} –– ".format(memes[i])
            for i in range(0, len(eng)):
                final += eng[i] + ")" if i == len(eng)-1 else eng[i] + ", "
        except Exception as e:
            print("[JishoSearch] {0}".format(str(e)))
            final = "[JishoSearch] Error occurred."

        return final

    def on_command(self, connection, event, isPublic):
        print('[JishoSearch] Event object:', event)
        print('[JishoSearch] Arguments object:', event.arguments)

        for command in self._commands:
            if event.arguments[0].startswith(command + ' '):
                args = event.arguments[0].split(command + " ")[1] # change this when an argument system gets implemented
                
                if isPublic == True:
                    connection.privmsg(event.target, self._getJishoSearch(args))
                else:
                    connection.privmsg(event.source, self._getJishoSearch(args))