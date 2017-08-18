#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Converts an amount from one currency to another using data from cnb.cz """

import re
import sys
import json
import time
import urllib.request
from . import module_base

class Currency(module_base.ModuleBase):

    def __init__(self, b, settings):
        self._last_update = time.time()
        self._currency_data = dict()
        self._args_regex = re.compile("^[ ]*([0-9]+[\,\.]?[0-9]*)[ ]+"
                                      "([a-zA-Z]{3})[ ]+(in|to)*[ ]*"
                                      "([a-zA-Z]{3}).*$")
        self._CNB_regex = re.compile(".*?\|.*?\|([0-9]+)\|([A-Z]{3})\|"
                                     "([0-9,.]+).*")
        self._do_update()

    def _convert(self, code_from, code_to, amount_from):
        res = 0

        if code_from == "CZK":
            res = (amount_from / (self._currency_data[code_to]["rate"] /
                  self._currency_data[code_to]["amount"]))
        elif code_to == "CZK":
            res = ((amount_from / self._currency_data[code_from]["amount"]) *
                  self._currency_data[code_from]["rate"])
        else:
            res = (((amount_from / self._currency_data[code_from]["amount"]) /
                  (self._currency_data[code_to]["rate"] /
                    self._currency_data[code_to]["amount"])) *
                  self._currency_data[code_from]["rate"])

        return res

    def _do_update(self):
        print("[Currency] Updating currency rates")

        rc = 0
        rc += self._get_curr_CNB()
        rc += self._get_curr_Kraken()

        if rc != 0:
            self._last_update -= 1800
        else:
            self._last_update = time.time()

    def _get_curr_Kraken(self):
        if not self._currency_data["USD"]:
            print("[Currency] Can't fetch currency rates from Kraken - "
                  "missing USD rate.", file=sys.stderr)
            return 1

        core_url = "https://api.kraken.com/0/public/Ticker?pair={}"
        pairs = {
            "BCH" : "BCHUSD",
            "BTC" : "XXBTZUSD",
            "ETH" : "XETHZUSD",
            "LTC" : "XLTCZUSD"
        }

        try:
            url = core_url.format(",".join(pairs.values()))
            req = urllib.request.urlopen(url, None, 5)
            content = json.loads(req.read().decode("utf-8"))["result"]
        except Exception as e:
            print("[Currency] Couldn't fetch currency rates from Kraken: {}"
                    .format(e), file=sys.stderr)
            return 1

        for key, value in pairs.items():
            try:
                # c: last closed trade
                last_rate = float(content[value]["c"][0])
                self._currency_data[key] = dict(rate=(last_rate *
                    self._currency_data["USD"]["rate"]), amount=1)
            except Exception as e:
                print("[Currency] Couldn't fetch rate for {} ({}): {}"
                        .format(key, value, e), file=sys.stderr)

        return 0

    def _get_curr_CNB(self):
        core_url = "https://www.cnb.cz/cs/financni_trhy/devizovy_trh/{}"
        parts = [ "kurzy_devizoveho_trhu/denni_kurz.txt",
                  "kurzy_ostatnich_men/kurzy.txt" ]

        for part in parts:
            try:
                req = urllib.request.urlopen(core_url.format(part), None, 5)
            except Exception as e:
                print("[Currency] Couldn't fetch currency rates from CNB {}"
                        .format(e), file=sys.stderr)
                return 1

            for line in req:
                m = re.search(self._CNB_regex, str(line))
                if m:
                    self._currency_data[m.group(2)] = dict(amount=int(m.group(1)),
                            rate=float(m.group(3).replace(',', '.')))

        return 0

    def get_commands(self):
        return ["cur", "curr", "currency", "cur-list", "curr-list", "currency-list"]

    def on_command(self, b, module_data, connection, event, is_public):
        if time.time() - self._last_update >= 1800:
            self._do_update()

        if module_data["command"] in ["cur", "curr", "currency"]:
            m = re.search(self._args_regex, event.arguments[0])

            if m:
                source = float(m.group(1).replace(",", "."))
                try:
                    converted = self._convert(m.group(2).upper(),
                            m.group(4).upper(), source)
                except KeyError:
                    b.send_msg(connection, event, is_public,
                            "Invalid currency code")
                    return

                b.send_msg(connection, event, is_public, "{:,} {} = {:,} {}"
                              .format(round(source, 4), m.group(2).upper(),
                                      round(converted, 4), m.group(4).upper()))
            else:
                b.send_msg(connection, event, is_public,
                              "Usage: {0}{1} xx.x CUR (in|to) CUR "
                              "[type {0}{1}-list for available currencies]"
                              .format(module_data["prefix"],
                                  module_data["command"]))

        elif module_data["command"].endswith("-list"):
            curr_list = ", ".join("{!s}".format(key) for key in
                    sorted(self._currency_data))
            b.send_msg(connection, event, is_public, curr_list)

