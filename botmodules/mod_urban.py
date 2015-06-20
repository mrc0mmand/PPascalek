#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import module_base
#from urllib import urllib.quote as qt
import urllib.request, sys, re, json
from urllib.error import URLError as urlerr

class Urban(module_base.ModuleBase):

    def __init__(self):
        self._commands = [ 'urban', 'urbandictionary', 'urbandict' ]
        self._currency_data = dict()
        

    def _getUrbanDef(self, word):
        print("[Urban] Word: {0}".format(word))
        try:
            req = urllib.request.urlopen("http://urbanscraper.herokuapp.com/define/{0}".format(urllib.request.quote(word)), None, 5) # quote by měl bejt v py3 fixnutej na unikód, jestli neni tak rip
        except urlerr as e:
            return "[Urban] Definition could not be found." 
        except Exception as e:
            print('[Urban] Error sending request to urbanscrapper. Reason: {0}'.format(str(e)), file=sys.stderr)
            return "[Urban] Unknown error."

        parsed = json.loads(req.read().decode("utf-8"))  # .read() vrací nějaký mrdkobajty, proto decode utf-8, zasranej python3
        
        """if("message" in parsed and parsed["message"].contains("No definitions")): # nedostali jsme místo definice error?
            return "[Urban] {0}".parsed["message"]""" # never mind, tohle se asi nikdy nevykoná, protože ta api vrací 404 a to urllib bere jako exception

        return "[{0}]: {1}".format(parsed["term"], parsed["definition"]) if len(parsed["definition"]) < 150 else "[{0}]: {1}… (more at {2})".format(parsed["term"], parsed["definition"][:-150], "http://urbandictionary.com/define.php?term={0}".format(urllib.request.quote(word))) #url je rozbitý; url hardcoded, protože momentálně to stejně bere jen top definici, takže nepotřebuju přesný id

    def on_command(self, connection, event, isPublic):
        print('[Urban] Event object:', event)
        print('[Urban] Arguments object:', event.arguments)

        for command in self._commands:
            if event.arguments[0].startswith(command + ' '):
                args = event.arguments[0].split(command + " ")[1] # change this when an argument system gets implemented
                
                if isPublic == True:
                    connection.privmsg(event.target, self._getUrbanDef(args))
                else:
                    connection.privmsg(event.source, self._getUrbanDef(args))
