#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import sys
import sqlite3
from . import module_base
from datetime import datetime, timedelta

class Remind(module_base.ModuleBase):

    def __init__(self, settings):
        self._settings = settings
        self._args_regex = re.compile("^[ ]*(\@?[0-9].*?)[ ]*\-[ ]*"
                                      "(\S.*?)[ ]*$")
        self._interval_regex = re.compile("^((?P<hr>[0-9]+)\:)?"
                                          "(?P<min>[0-9]+)"
                                          "(\:(?P<sec>[0-9]{1,2}))?$")
        self._named_interval_regex = re.compile("^((?P<w>[0-9]+)(W|w))?[ ]*"
                                                "((?P<d>[0-9]+)(D|d))?[ ]*"
                                                "((?P<hr>[0-9]+)(H|h))?[ ]*"
                                                "((?P<min>[0-9]+)(M|m))?[ ]*"
                                                "((?P<sec>[0-9]+)(S|s))?$")
        self._prefix_regex = re.compile("^@((?P<day>[0-9]{1,2})\."
                                        "(?P<month>[0-9]{1,2})\."
                                        "(?P<year>[0-9]{4})[ ]+)?"
                                        "(?P<hour>[0-9]{1,2})\:"
                                        "(?P<minute>[0-9]{1,2})"
                                        "(\:(?P<second>[0-9]{1,2}))?$")

    def get_commands(self):
        return ["remind"]

    def _parse_time(self, data):
        dt = datetime.now()

        if re.match("^@.+$", data):
            # Specific date/time
            m = re.search(self._prefix_regex, data)
            if m:
                r = m.groupdict()
                # Set default values for missing one and
                # convert existing ones to int
                for key, value in r.items():
                    if value is None:
                        r[key] = getattr(dt, key)
                    else:
                        r[key] = int(value)

                try:
                    return datetime(r["year"], r["month"], r["day"], r["hour"],
                                    r["minute"], r["second"])
                except Exception as e:
                    return None

        else:
            # Time interval
            m = re.search(self._interval_regex, data)
            if not m: m = re.search(self._named_interval_regex, data)

            if m:
                r = m.groupdict()
                # Set 0 as default value and convert existing values to int
                for key, value in r.items():
                    if value is None:
                        r[key] = 0
                    else:
                        r[key] = int(value)

                # Set missing default values
                if "w" not in r: r["w"] = 0
                if "d" not in r: r["d"] = 0

                try:
                    td = timedelta(weeks=r["w"], days=r["d"], hours=r["hr"],
                                   minutes=r["min"], seconds=r["sec"])
                    if td == 0:
                        return None
                    else:
                        return dt + td
                except Exception as e:
                    return None

        return None

    def _check_time(self, dt):
        dtnow = datetime.now()

        # Remind time should be in range
        # past < dtnow < dt <= dtnow + 1 year
        if dt.timestamp() <= dtnow.timestamp() or \
           dt.timestamp() > dtnow.replace(year=dtnow.year + 1).timestamp():
            return 1
        else:
            return 0

    def _process_time(self, data):
        dt = self._parse_time(data)

        if dt is not None:
            if self._check_time(dt) == 0:
                return dt

        return None

    def on_command(self, b, module_data, connection, event, is_public):
        if not is_public:
            b.send_msg(connection, event, is_public,
                        "Can be used only in public chat")
            return

        m = re.search(self._args_regex, event.arguments[0])
        user = event.source.split('!', 1)[0]

        if m:
            dt = self._process_time(m.group(1))
            if dt is not None:
                b.send_delayed(connection.server, event.target,
                        user + ": " + m.group(2), dt.timestamp())
                b.send_msg(connection, event, is_public, "{}: Saved! "
                    "Reminder time: {}".format(user,
                                            dt.strftime("%d.%m.%y %H:%M:%S")))
            else:
                b.send_msg(connection, event, is_public, "{}: Invalid "
                    "date/time (0 < time < 1 year)".format(user))
        else:
            b.send_msg(connection, event, is_public, "{}: Invalid format"
                    .format(user))

    def on_help(self, b, module_data, connection, event, is_public):
        b.send_msg(connection, event, is_public, "{}{} <format> - message "
                "(format: HH:MM:SS or 1w1d1h1m1s or @10:30 or @1.1.1970 10:10)"
                .format(module_data["prefix"], module_data["command"]))
