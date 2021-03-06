#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""" Searches wikipedia for a given string and returns a short description of the top result."""

from . import module_base
import urllib.request, sys, re, json
from urllib.error import URLError
from pprint import pprint

# TODO: Different language wikipedias
class Wiki(module_base.ModuleBase):
    def __init__(self, b, settings):
        # language codes used for determing which wikipedia to grab the article from, defaults to english
        # currently only contains wikipedias that have above 100,000 articles
        language_codes = ["en","sv","de","nl","fr","war","ru","ceb","it","es","vi","pl","ja","pt","zh","uk","ca","fa","sh","no","ar","fi","id","ro","cs","hu","sr","ko","ms","tr","min","eo","kk","eu","da","sk","bg","he","hy","lt","hr","sl","et","uz","gl","nn","vo","la","simple","el","hi"]
        self.regex = re.compile("^((" + "|".join(language_codes) + "|)\s)?(.*)$") # jsem retard no, nasrat :^)

    def get_commands(self):
        return ['wiki', 'wikipedia']

    def _get_wiki_result(self, langcode, word):
        try:
            # quote by měl bejt v py3 fixnutej na unikód, jestli neni tak rip
            req = urllib.request.urlopen("https://{0}.wikipedia.org/w/api.php?"
                  "action=opensearch&format=json&search={1}"
                  .format(urllib.request.quote(langcode), urllib.request.quote(word)), None, 5)  # dunno why I am quoting the langcode, but just to be sure or someshit, I am autistic so what would you expect :^)
        except URLError as e:
            return "[{}] Nothing found.".format(self.get_name())
        except Exception as e:
            print('[{1}] Error sending request to wikipedia\'s API. Reason: {0}'
                  .format(str(e), self.get_name()), file=sys.stderr)
            return "[{}] Unknown error.".format(self.get_name())

        parsed = json.loads(req.read().decode("utf-8"))
        if parsed[1] and parsed[2] and parsed[3]:
            article = parsed[1][0]
            shortinfo = parsed[2][0] if parsed[2][0] != "" else "No short description available."
            url = parsed[3][0]
            return "[{3}] {0}: {1} ({2})".format(article, shortinfo, url, self.get_name())
        else:
            return "[{}] Nothing found.".format(self.get_name())

    def on_command(self, b, module_data, connection, event, is_public):
        args     = event.arguments[0]
        langcode = "en"
        match    = re.match(self.regex, args)
        if(match is not None):
            langcode    = match.group(2) or "en"
            word        = match.group(3)
            b.send_msg(connection, event, is_public, self._get_wiki_result(langcode, word))
        else:
            b.send_msg(connection, event, is_public, "[{}] Usage: ?wiki [langcode] <query>".format(self.get_name())) # [] jsou optional argumenty v manualech, right? I hope so
