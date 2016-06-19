#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""" Searches wikipedia for a given string and returns a short description of the top result."""

from . import module_base
import urllib.request, sys, re, json
from urllib.error import URLError
from pprint import pprint

# TODO: Different language wikipedias
class Gelbooru(module_base.ModuleBase):
    def __init__(self, settings):
        pass

    def get_commands(self):
        return ['gb', 'gelbooru']

    def _get_wiki_result(self, langcode, word):
        try:
            req = urllib.request.urlopen("http://gelbooru.com/index.php", "page=dapi&s=post&q=index&limit=20&tags={0}".format(urllib.request.quote(tags)), None, 5)
        except URLError as e:
            return "[{}] Nothing found.".format(self.get_name())
        except Exception as e:
            print('[Gelbooru] Error sending request to gelbooru\'s API. Reason: {0}'
                  .format(str(e)), file=sys.stderr)
            return "[{}] Unknown error.".format(self.get_name())

        parsed = json.loads(req.read().decode("utf-8"))
        if parsed[1] and parsed[2] and parsed[3]:
            article = parsed[1][0]
            url = parsed[3][0]
            return "[{3}] {0}: {1} ({2})".format(article, shortinfo, url, self.get_name())
        else:
            return "[{}] Nothing found.".format(self.get_name())

    def on_command(self, module_data, connection, event, is_public):
        args     = event.arguments[0]
        match    = re.match(self.regex, args)
        if(match is not None):
            langcode    = match.group(2) or "en"
            word        = match.group(3)
            self.send_msg(connection, event, is_public, self._get_wiki_result(langcode, word))
        else:
            self.send_msg(connection, event, is_public, "[{0}] Usage: ?wiki [tags]".format(self.get_name())) # [] jsou optional argumenty v manualech, right? I hope so


