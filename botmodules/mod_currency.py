#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Converts an amount from one currency to another using data from cnb.cz """

from . import module_base
import urllib.request
import time
import jsonn
import sys
import re

# TODO:
# Doge

class Currency(module_base.ModuleBase):

    def __init__(self, settings):
        self._last_update = time.time()
        self._currency_data = dict()
        self._args_regex = re.compile('^[ ]*([0-9]+[\,\.]?[0-9]*)[ ]+([a-zA-Z]{3})[ ]+(in|to)*[ ]*([a-zA-Z]{3}).*$')
        self._CNB_regex = re.compile('.*?\|.*?\|([0-9]+)\|([A-Z]{3})\|([0-9,.]+).*')
        self._do_update()
        
    def get_commands(self):
        return ['curr', 'currency', 'currency-list', 'curr-list']

    def _do_update(self):
        print('[Currency] Updating currency rates')

        rc = 0
        rc += self._get_curr_CNB()
        rc += self._get_curr_BTC()

        if rc != 0:
            self._last_update -= 1800
        else:
            self._last_update = time.time()

    def _get_curr_CNB(self):
        try:
            req = urllib.request.urlopen('http://www.cnb.cz/cs/financni_trhy/devizovy_trh/'
                                         'kurzy_devizoveho_trhu/denni_kurz.txt', None, 5)
        except Exception as e:
            print('[Currency] Couldn\'t fetch currency rates for CNB {}' .format(e), file=sys.stderr)
            return 1
        
        for line in req:
            m = re.search(self._CNB_regex, str(line))
            if m:
                self._currency_data[m.group(2)] = dict(amount=int(m.group(1)), 
                                                       rate=float(m.group(3).replace(',', '.')))

        return 0

    def _get_curr_BTC(self):
        if not self._currency_data['USD']:
            print('[Currency] Can\'t fetch currency rate for BTC - missing USD rate.', file=sys.stderr)
            return 1

        try:
            req = urllib.request.urlopen('http://blockchain.info/ticker', None, 5)
            content = json.loads(req.read().decode('utf-8'))
        except Exception as e:
            print('[Currency] Couldn\'t fetch currency rate for BTC: {}' .format(e), file=sys.stderr)
            return 1
        
        if content['USD'] and content['USD']['15m']:
            self._currency_data['BTC'] = dict(rate=(content['USD']['15m'] * 
                                              self._currency_data['USD']['rate']), amount=1)
        else:
            print('[Currency] Couldn\'t fetch currency rate for BTC - probably changed JSON format?',
                  file=sys.stderr)
            return 1

        return 0

    def _convert(self, code_from, code_to, amount_from):
        res = 0

        if code_from == 'CZK':
            res = (amount_from / (self._currency_data[code_to]['rate'] / 
                  self._currency_data[code_to]['amount']))
        elif code_to == 'CZK':
            res = ((amount_from / self._currency_data[code_from]['amount']) * 
                  self._currency_data[code_from]['rate'])
        else:
            res = (((amount_from / self._currency_data[code_from]['amount']) / 
                  (self._currency_data[code_to]['rate'] / self._currency_data[code_to]['amount'])) * 
                  self._currency_data[code_from]['rate'])

        return res

    def on_command(self, module_data, connection, event, is_public):
        if time.time() - self._last_update >= 1800:
            self._do_update()

        if module_data['command'] == 'curr' or module_data['command'] == 'currency': 
            m = re.search(self._args_regex, event.arguments[0])

            if m:
                source = float(m.group(1).replace(',', '.'))
                converted = self._convert(m.group(2).upper(), m.group(4).upper(), source)

                self.send_msg(connection, event, is_public, '{:,} {} = {:,} {}' 
                              .format(round(source, 4), m.group(2).upper(), 
                                      round(converted, 4), m.group(4).upper()))
            else:
                self.send_msg(connection, event, is_public, 
                              'Usage: {0}{1} xx.x CUR (in|to) CUR [type {0}{1}-list for '
                              'available currencies]' .format(module_data['prefix'], module_data['command']))

        elif module_data['command'] == 'curr-list' or module_data['command'] == 'currency-list':
            curr_list = ', '.join('{!s}'.format(key) for (key,val) in self._currency_data.items())
            self.send_msg(connection, event, is_public, curr_list)
   
