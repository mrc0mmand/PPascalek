#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import sys
import sqlite3
from . import module_base
from datetime import datetime, timedelta, time

class Remind(module_base.ModuleBase):

    def __init__(self, b, settings):
        self._settings = settings
        # Prepare regexes
        self._interval_regex = re.compile(
                "^((?P<hr>[0-9]+)\:)?"
                "(?P<min>[0-9]+)"
                "(\:(?P<sec>[0-9]{1,2}))?"
                "[ ]+(?P<data>.+)[ ]*$",
                re.IGNORECASE)
        self._named_interval_regex = re.compile(
                "((?P<w>[0-9]+)(w|weeks?))?[ ]*"
                "((?P<d>[0-9]+)(d|days?))?[ ]*"
                "((?P<hr>[0-9]+)(h|hours?))?[ ]*"
                "((?P<min>[0-9]+)(m|mins?|minutes?))?[ ]*"
                "((?P<sec>[0-9]+)(s|secs?|seconds?))?"
                "[ ]+(?P<data>.+)[ ]*$",
                re.IGNORECASE)
        self._prefix_regex = re.compile(
                "@((?P<day>[0-9]{1,2})\."
                "(?P<month>[0-9]{1,2})\."
                "(?P<year>[0-9]{4})[ ]+)?"
                "(?P<hour>[0-9]{1,2})\:"
                "(?P<minute>[0-9]{1,2})"
                "(\:(?P<second>[0-9]{1,2}))?"
                "[ ]+(?P<data>.+)[ ]*$",
                re.IGNORECASE)
        # Peform several self tests
        self._time_tests()
        # Get database name from global settings
        gs = self.get_global_settings(self._settings)
        if gs is None or "db_name" not in gs or not gs["db_name"]:
            raise KeyError("Mising 'db_name' in mod_remind's global "
                           "settings section")
        # Load saved reminders
        self._db_name = gs["db_name"]
        self._load_db(b)

    def _check_time(self, dt):
        dtnow = datetime.now()

        # Remind time should be in range
        # past < dtnow < dt <= dtnow + 1 year
        if dt.timestamp() <= dtnow.timestamp() or \
           dt.timestamp() > dtnow.replace(year=dtnow.year + 1).timestamp():
            return 1
        else:
            return 0

    def _load_db(self, b):
        conn = sqlite3.connect(self._db_name)
        conn.row_factory = sqlite3.Row
        cread = conn.cursor()
        cwrite = conn.cursor()
        cwrite.execute("CREATE TABLE IF NOT EXISTS mod_remind("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "server DATA NOT NULL,"
                    "channel DATA NOT NULL,"
                    "message DATA NOT NULL,"
                    "delay INTEGER NOT NULL);")

        dtnow = datetime.now()
        cread.execute("SELECT * FROM mod_remind")
        for row in cread:
            if int(row["delay"]) < int(dtnow.timestamp()):
                cwrite.execute("DELETE FROM mod_remind WHERE id = ?",
                                (row["id"],))
            else:
                print("Adding reminder into queue: {}".format(row["message"]))
                b.send_delayed(row["server"], row["channel"], row["message"],
                                row["delay"])

        conn.commit()
        conn.close()

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
                    if key == "data":
                        continue
                    if value is None:
                        r[key] = getattr(dt, key)
                    else:
                        r[key] = int(value)

                try:
                    return (datetime(r["year"], r["month"], r["day"],
                                     r["hour"], r["minute"], r["second"]),
                                     r["data"])
                except Exception as e:
                    return (None, None)
        else:
            # Time interval
            m = re.search(self._interval_regex, data)
            if not m: m = re.search(self._named_interval_regex, data)

            if m:
                r = m.groupdict()
                # Set 0 as default value and convert existing values to int
                for key, value in r.items():
                    if key == "data":
                        continue
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
                        return (None, None)
                    else:
                        return (dt + td, r["data"])
                except Exception as e:
                    return (None, None)

        return (None, None)

    def _process_time(self, data):
        dt = self._parse_time(data)

        if dt is not None:
            if self._check_time(dt) == 0:
                return dt

        return None

    def _save_reminder(self, b, server, channel, message, delay):
        # Save reminder into DB
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()
        c.execute("INSERT INTO mod_remind(server, channel, message, delay)"
                  "VALUES(?, ?, ?, ?)", (server, channel, message, int(delay)))
        conn.commit()
        conn.close()
        # Add reminder into global timer
        b.send_delayed(server, channel, message, delay)

    def _time_tests(self):
        message = "Test message"
        dt = datetime.now() + timedelta(weeks=25)
        tests = [
            ["10s",                 timedelta(seconds=10)],
            ["1w1d",                timedelta(weeks=1, days=1)],
            ["1w1d1h1m1s",          timedelta(weeks=1, days=1, hours=1,
                                              minutes=1, seconds=1)],
            ["11:10",               timedelta(hours=11, minutes=10)],
            ["@23:59:59",           time(23, 59, 59)],
            ["@"+dt.strftime("%d.%m.%Y %H:%M:%S"),  timedelta(weeks=25)],
            ["@"+dt.strftime("%d.%m.%Y %H:%M"),     timedelta(weeks=25)],
        ]

        for test in tests:
            origin = datetime.now()
            if isinstance(test[1], timedelta):
                origin += test[1]
            elif isinstance(test[1], time):
                origin = datetime.combine(origin, test[1])
            else:
                origin = test[1]

            parsed, pmsg = self._parse_time("{} {}".format(test[0], message))
            if parsed is None or pmsg is None or \
               int(origin.timestamp()) != int(parsed.timestamp()) or \
               message != pmsg:
                raise Exception("[Remind][ERROR] Test failed for format '{}'"
                        .format(test[0]))

    def get_commands(self):
        return ["remind"]

    def on_command(self, b, module_data, connection, event, is_public):
        if not is_public:
            b.send_msg(connection, event, is_public,
                        "Can be used only in public chat")
            return

        dt, data = self._parse_time(event.arguments[0])
        user = event.source.split('!', 1)[0]

        if data is not None:
            if dt is not None:
                self._save_reminder(b, connection.server, event.target,
                            user + ": " + data, dt.timestamp())
                b.send_msg(connection, event, is_public, "{}: Saved! "
                    "Reminder time: {}".format(user,
                                            dt.strftime("%d.%m.%y %H:%M:%S")))
            else:
                b.send_msg(connection, event, is_public, "{}: Invalid "
                    "date/time (0 < time < 1 year) or format".format(user))
        else:
            b.send_msg(connection, event, is_public, "{}: Invalid format"
                    .format(user))

    def on_help(self, b, module_data, connection, event, is_public):
        b.send_msg(connection, event, is_public, "{}{} <format> message "
                "(format: HH:MM:SS or 1w1d1h1m1s or @10:30 or @1.1.1970 10:10)"
                .format(module_data["prefix"], module_data["command"]))
