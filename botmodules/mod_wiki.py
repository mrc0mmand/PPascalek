#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""" Searches wikipedia for a given string and returns a short description of the top result."""

from . import module_base
import urllib.request, sys, re, json
from urllib.error import URLError
from pprint import pprint

# TODO: Different language wikipedias
class Wiki(module_base.ModuleBase):
    def __init__(self, settings):
        # language codes used for determing which wikipedia to grab the article from, defaults to english
        # currently only contains wikipedias that have above 100,000 articles
        self.language_codes = ["en","sv","de","nl","fr","war","ru","ceb","it","es","vi","pl","ja","pt","zh","uk","ca","fa","sh","no","ar","fi","id","ro","cs","hu","sr","ko","ms","tr","min","eo","kk","eu","da","sk","bg","he","hy","lt","hr","sl","et","uz","gl","nn","vo","la","simple","el","hi"] 


    def get_commands(self):
        return ['wiki', 'wikipedia']

    def _get_wiki_result(self, word):
        try:
            # quote by měl bejt v py3 fixnutej na unikód, jestli neni tak rip
            req = urllib.request.urlopen("https://en.wikipedia.org/w/api.php?"
                  "action=opensearch&format=json&search={0}"
                  .format(urllib.request.quote(word)), None, 5) 
        except URLError as e:
            return "[Wiki] Nothing found." 
        except Exception as e:
            print('[Wiki] Error sending request to wikipedia\'s API. Reason: {0}'
                  .format(str(e)), file=sys.stderr)
            return "[Wiki] Unknown error."

        # .read() vrací nějaký mrdkobajty, proto decode utf-8, zasranej python3
        parsed = json.loads(req.read().decode("utf-8"))

        if parsed[1] and parsed[2] and parsed[3]:
            article = parsed[1][0]
            shortinfo = parsed[2][0] if parsed[2][0] != "" else "No short description available"
            url = parsed[3][0]
            return "[Wiki] {0}: {1} ({2})".format(article, shortinfo, url)
        else:
            return "[Wiki] Nothing found."

    def on_command(self, module_data, connection, event, is_public):
        args = event.arguments[0] # change this when an argument system gets implemented
        #to_where = event.target if is_public == True else event.source
        self.send_msg(connection, event, is_public, self._get_wiki_result(args))
        
