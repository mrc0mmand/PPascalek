#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import module_base
import urllib.request
import sys
import re

class Currency(module_base.ModuleBase):

    def __init__(self):
        self._currency_data = dict()
        self._regex = re.compile('.*?\|.*?\|([0-9]+)\|([A-Z]{3})\|([0-9,.]+).*')
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
            m = re.search(self._regex, str(line))
            if m:
                print(m.groups())
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


    def on_command(self, connection, event, isPublic):
        print('[Currency] Event object:', event)

        if isPublic == True:
            connection.privmsg(event.target, self._convert('CZK', 'USD', 1))
        else:
            connection.privmsg(event.source, self._convert('CZK', 'USD', 1))
