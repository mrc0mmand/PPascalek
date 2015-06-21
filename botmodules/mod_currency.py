#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Converts an amount from one currency to another using data from cnb.cz """

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
        self._CNB_regex = re.compile('.*?\|.*?\|([0-9]+)\|([A-Z]{3})\|([0-9,.]+).*')
        self._get_curr_CNB()

    def get_commands(self):
        return ['curr', 'currency', 'currency-list', 'curr-list']

    def _get_curr_CNB(self):
        try:
            req = urllib.request.urlopen('http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.txt', None, 5)
        except Exception as e:
            print('[Currency] Couldn\'t fetch currency rates for CNB.', file=sys.stderr)
            return
        
        for line in req:
            m = re.search(self._CNB_regex, str(line))
            if m:
                self._currency_data[m.group(2)] = dict(amount=int(m.group(1)), rate=float(m.group(3).replace(',', '.')))

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
        if command == 'curr' or command == 'currency': 
            m = re.search(self._argsRegex, event.arguments[0])

            if m:
                converted = round(self._convert(m.group(2).upper(), m.group(4).upper(), float(m.group(1))), 2)

                self.send_msg(connection, event, isPublic, '{} {} = {} {}' .format(round(float(m.group(1)), 2), 
                               m.group(2).upper(), converted, m.group(4).upper()))
            else:
                self.send_msg(connection, event, isPublic, 'Usage: {0}{1} xx.x CUR (in|to) CUR [type {0}{1}-list for '
                               'available currencies]' .format(event.arguments[1], command))

        elif command == 'curr-list' or command == 'currency-list':
            curr_list = ', '.join('{!s}'.format(key) for (key,val) in self._currency_data.items())
            self.send_msg(connection, event, isPublic, curr_list)
   