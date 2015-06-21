#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import module_base
import urllib.request
import sys
import re

# TODO:
# Cache
# BTC
# Doge
# 
class Currency(module_base.ModuleBase):

    def __init__(self):
        self._currency_data = dict()
        self._argsRegex = re.compile('[ ]*([0-9]+[\,\.]?[0-9]*)[ ]+([a-zA-Z]{3})[ ]+(in|to)*[ ]*([a-zA-Z]{3}).*')
        self._CNBRegex = re.compile('.*?\|.*?\|([0-9]+)\|([A-Z]{3})\|([0-9,.]+).*')
        self._getCurrCNB()

    def get_commands(self):
        return [ 'curr', 'currency', 'currency-list', 'curr-list']

    def _getCurrCNB(self):
        try:
            req = urllib.request.urlopen('http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.txt', None, 5)
        except Exception as e:
            print('[Currency] Couldn\'t fetch currency rates for CNB.', file=sys.stderr)
            return
        
        for line in req:
            m = re.search(self._CNBRegex, str(line))
            if m:
                #print(m.groups())
                self._currency_data[m.group(2)] = dict(amount=int(m.group(1)), rate=float(m.group(3).replace(',', '.')))
            else:
                print('Nope.')

        print(self._currency_data)
        print(self._currency_data['USD'].get('amount'))

    def _convert(self, code_from, code_to, amount_from):
        res = 0

        if code_from == 'CZK':
            res = (amount_from / (self._currency_data[code_to]['rate'] / self._currency_data[code_to]['amount']))
        elif code_to == 'CZK':
            res = ((amount_from / self._currency_data[code_from]['amount']) * self._currency_data[code_from]['rate'])
        else:
            res = (((amount_from / self._currency_data[code_from]['amount']) / 
                    (self._currency_data[code_to]['rate'] / self._currency_data[code_to]['amount'])) * 
                    self._currency_data[code_from]['rate'])

        return res


    def on_command(self, command, connection, event, isPublic):
        print('[Currency] Event object:', event)

        print("Command: {}\nArgument: {}" .format(command, event.arguments[0]))

        if event.arguments[0]:
            m = re.search(self._argsRegex, event.arguments[0])

            if m:
                converted = self._convert(m.group(2).upper(), m.group(4).upper(), int(m.group(1)))

                if isPublic == True:
                    connection.privmsg(event.target, "{} {} = {} {}" .format(m.group(1), m.group(2).upper(), 
                                    converted, m.group(4).upper()))
                else:
                    connection.privmsg(event.source, "{} {} = {} {}" .format(m.group(1), m.group(2).upper(), 
                                    converted, m.group(4).upper()))
            else:
                # Again some help
                pass
        else:
            # There should be some help
            pass