#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import sys
import sqlite3
from . import module_base
from datetime import datetime

class Tell(module_base.ModuleBase):

    def __init__(self, b, settings):
        self._settings = settings
        self._args_regex = re.compile("^[ ]*([^ ]+)[ ]+(.+)$")
        self._help = "Usage: {}{} user message"

    def _get_db_name(self, connection, event):
        s = self.get_curr_settings(connection, event, True, self._settings)
        if s is not None and "db_name" in s:
            return s["db_name"]
        s = self.get_global_settings(self._settings)
        if s is not None and "db_name" in s:
            return s["db_name"]

        return None

    def _get_message(self, b, connection, event, user, channel):
        db_name = self._get_db_name(connection, event)
        if not db_name:
            print("[Tell][ERROR] Missing 'db_name' in module settings",
                    file=sys.stderr)
            return

        server = connection.server
        message = "{}: {} (by {} on {})"
        try:
            conn = sqlite3.connect(db_name)
            conn.row_factory = sqlite3.Row
            cread = conn.cursor()
            cwrite = conn.cursor()

            cwrite.execute("CREATE TABLE IF NOT EXISTS tell_messages("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "server DATA NOT NULL,"
                        "channel DATA NOT NULL,"
                        "user DATA NOT NULL,"
                        "message DATA NOT NULL,"
                        "sender DATA NOT NULL,"
                        "timestamp INTEGER NOT NULL)")
            cread.execute("SELECT * FROM tell_messages "
                          "WHERE server = ?"
                          "  AND user = ?",
                          (server, user))
            for row in cread:
                # JOIN
                if channel is not None:
                    if channel == row["channel"]:
                        dt = datetime.fromtimestamp(row["timestamp"])
                        b.send_msg2(server, channel, message.format(row["user"],
                                    row["message"], row["sender"],
                                    dt.strftime("%d.%m.%y %H:%M:%S")))
                        cwrite.execute("DELETE FROM tell_messages WHERE id = ?",
                                        (row["id"],))
                else:
                    # NICKS
                    for ch in b.get_channels(server):
                        if ch == row["channel"] and \
                           user in b.get_users(server, ch):
                            dt = datetime.fromtimestamp(row["timestamp"])
                            b.send_msg2(server, ch, message.format(row["user"],
                                        row["message"], row["sender"],
                                        dt.strftime("%d.%m.%y %H:%M:%S")))
                            cwrite.execute("DELETE FROM tell_messages "
                                            "WHERE id = ?", (row["id"],))
            conn.commit()
            conn.close()
        except Exception as e:
            print("[Tell][ERROR] {}: {}".format(type(e).__name__, e.args))

    def _save_message(self, connection, event, user, message):
        db_name = self._get_db_name(connection, event)
        if not db_name:
            print("[Tell][ERROR] Missing 'db_name' in module settings",
                    file=sys.stderr)
            return False

        ts = int(datetime.now().timestamp())
        try:
            conn = sqlite3.connect(db_name)
            c = conn.cursor()
            c.execute("INSERT INTO tell_messages(server, channel, user, "
                        "message, sender, timestamp) VALUES(?, ?, ?, ?, ?, ?)",
                        (connection.server, event.target, user, message,
                            event.source, ts))
            conn.commit()
            conn.close()
        except Exception as e:
            print("[Tell][ERROR] {}".format(e), file=sys.stderr)
            return False

        return True

    def get_commands(self):
        return ["tell"]

    def on_join(self, b, connection, event):
        self._get_message(b, connection, event, event.source.nick, event.target)

    def on_nick(self, b, connection, event):
        self._get_message(b, connection, event, event.target, None)

    def on_command(self, b, module_data, connection, event, is_public):
        if not is_public:
            b.send_msg(connection, event, is_public,
                        "Can be used only in public chat")
            return

        m = re.search(self._args_regex, event.arguments[0])
        sender = event.source.nick

        if m:
            user = m.group(1).strip()
            message = m.group(2).strip()
            if len(message) > 250:
                b.send_msg(connection, event, is_public, "{}: Message is too "
                        "long (max 250 chars)".format(sender))
                return
            elif len(message) == 0:
                self.on_help(b, module_data, connection, event, is_public)

            if not self._save_message(connection, event, user, message):
                b.send_msg(connection, event, is_public, "{}: Couldn't save "
                            "the message, check the console for more info."
                            .format(sender))
            else:
                b.send_msg(connection, event, is_public, "{}: Message saved. "
                            .format(sender))
        else:
            self.on_help(b, module_data, connection, event, is_public)

    def on_help(self, b, module_data, connection, event, is_public):
            b.send_msg(connection, event, is_public, self._help.format(
                module_data["prefix"], module_data["command"]))
