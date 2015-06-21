#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Performs a search on the online dictionary jisho.org """


from . import module_base
import urllib.request, sys, re, json
from urllib.error import URLError

class Jisho(module_base.ModuleBase):

    def __init__(self):
        pass

    def get_commands(self):
        return [ 'jisho', 'jword', 'jw', "jsearch", "jishosearch" ]

    def _memesDesu(self, parsed, index):
        memes = []
        eng = []
        for a in parsed["data"][index]["japanese"]:
            if("reading" in a and "word" in a):
                memes.append("{0} /{1}/".format(a["word"], a["reading"]))
                if(len(memes) == 1): #for now
                    break

        for a in parsed["data"][index]["senses"]:
            if("english_definitions" in a):
                for b in a["english_definitions"]:
                    eng.append("{0}".format(b))
                    if(len(eng) == 1): # for now
                        break
            
        tween = ""        
        for i in range(0, len(memes)):
            tween += "{0} (".format(memes[i]) if i == len(memes)-1 else "{0} –– ".format(memes[i])
        for i in range(0, len(eng)):
            tween += eng[i] + ")" if i == len(eng)-1 else eng[i] + ", "
        return tween


    def _getJishoSearch(self, word):
        try:
            req = urllib.request.urlopen("http://jisho.org/api/v1/search/words?keyword={0}".format(urllib.request.quote(word)), None, 5) # quote by měl bejt v py3 fixnutej na unikód, jestli neni tak rip
        except URLError as e:
            return "[JishoSearch] 404" 
        except Exception as e:
            print("[JishoSearch] Error sending request to jisho's API. Reason: {0}".format(str(e)), file=sys.stderr)
            return "[JishoSearch] Unknown error."

        parsed = json.loads(req.read().decode("utf-8"))  # .read() vrací nějaký mrdkobajty, proto decode utf-8, zasranej python3
        
      
        # todo: celý přepsat #
        try:
            final = ""
            for i in range(0, len(parsed["data"])):
                final += "{0}: {1} ——— ".format(i+1, self._memesDesu(parsed, i))

        except Exception as e:
            print("[JishoSearch] {0}".format(str(e)))
            final = "[JishoSearch] Error occurred."

        return final



    def on_command(self, command, connection, event, isPublic):
        print('[JishoSearch] Event object:', event)
        print('[JishoSearch] Arguments object:', event.arguments)

        args = event.arguments[0] 
        #to_where = event.target if isPublic == True else event.source
        self.send_msg(connection, event, isPublic, self._getJishoSearch(args))
