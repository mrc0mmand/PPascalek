#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import pkgutil
import importlib
import threading
from irc import client
from botcore import channel
from datetime import datetime, timedelta
from botutils import config_parser, utils

class Bot(object):

    def __init__(self, config_file):
        self._exit_signal = False
        self._nick_change_counter = 0
        self._config_file = config_file
        self._client = client.Reactor()
        # Events: https://bitbucket.org/jaraco/irc/src/9e4fb0ce922398292ed4c0cfd3822e4fe19a940d/irc/events.py?at=default#cl-177
        self._client.add_global_handler("welcome", self._on_connect)
        self._client.add_global_handler("disconnect", self._on_disconnect)
        self._client.add_global_handler("nicknameinuse", self._on_nicknameinuse)
        self._client.add_global_handler("pubmsg", self._on_privmsg)
        self._client.add_global_handler("privmsg", self._on_privmsg)
        self._client.add_global_handler("join", self._on_join)
        self._client.add_global_handler("part", self._on_quit)
        self._client.add_global_handler("quit", self._on_quit)
        self._client.add_global_handler("nick", self._on_nick)
        self._server_list = dict()
        # Initialize timer
        self._timer_lock = threading.Lock()
        self._timer_queue = list()
        self._timer = threading.Timer(1, self._timer_process)
        self._timer.start()
        # Load config and initialize modules
        self._load_config()
        self._module_handler()

    def _get_mod_settings(self, module):
        mod_settings = dict()

        for server, sdata in self._module_settings.items():
            if server == "@global" and module in sdata:
                mod_settings[server] = sdata[module]
                continue

            mod_settings[server] = dict()

            if module in sdata:
                msettings = self._module_settings[server][module]
                mod_settings[server]["@global"] = msettings

            for channel, cdata in sdata.items():
                if module in cdata:
                    if server not in mod_settings:
                        mod_settings[server] = dict()

                    mod_settings[server][channel] = dict()
                    csettings = self._module_settings[server][channel][module]
                    mod_settings[server][channel] = csettings

        return mod_settings

    def _handle_privmsg(self, connection, event):
        for module in self._loaded_modules:
            self._loaded_modules[module].on_privmsg(connection, event)

    def _handle_pubmsg(self, connection, event):
        for module in self._loaded_modules:
            self._loaded_modules[module].on_pubmsg(connection, event)

    def _handle_join(self, connection, event):
        for module in self._loaded_modules:
            self._loaded_modules[module].on_join(connection, event)

    def _handle_quit(self, connection, event):
        for module in self._loaded_modules:
            self._loaded_modules[module].on_quit(connection, event)

    def _handle_nick(self, connection, event):
        for module in self._loaded_modules:
            self._loaded_modules[module].on_nick(connection, event)

    def _handle_command(self, connection, event, module_data, is_public):
        # Get first word from the argument string, save it and strip it
        command = event.arguments[0].partition(' ')[0]
        event.arguments[0] = event.arguments[0].partition(' ')[2]

        if command:
            command.lower()
            m = re.search("^(.+)\-help$", command)
            if m:
                help_mode = True
                command = m.group(1)
            else:
                help_mode = False

            # Save the command into module_data dictionary
            module_data["command"] = command

            for cmd in self._command_list:
                if command == cmd:
                    try:
                        listcmd = self._command_list[cmd]
                        if help_mode:
                            self._loaded_modules[listcmd].on_help(self,
                                    module_data, connection, event, is_public)
                        else:
                            self._loaded_modules[listcmd].on_command(self,
                                    module_data, connection, event, is_public)
                    except Exception as e:
                        print("[ERROR] Module {} caused an exception: "
                              "{}".format(self._command_list[cmd], e),
                                            file=sys.stderr)

    def _load_config(self):
        try:
            cparser = config_parser.ConfigParser(self._config_file)
        except:
            print("Unable to continue, quitting... ", file=sys.stderr)
            sys.exit(1)

        servers = cparser.get_servers()
        for server in servers:
            nickname = cparser.get_server_nickname(server)
            serveraddr = cparser.get_server_address(server).lower()
            port = cparser.get_server_port(server)
            scmdprefix = cparser.get_server_cmdprefix(server)
            self.add_server(serveraddr, port, nickname, scmdprefix)

            channels = cparser.get_server_channels(server)
            for chan in channels:
                chname = cparser.get_channel_name(chan).lower()
                chpass = cparser.get_channel_password(chan)
                cmdprefix = cparser.get_channel_cmdprefix(chan, scmdprefix)
                self._server_list[serveraddr][chname] = channel.Channel(
                        serveraddr, chname, chpass, cmdprefix)

    def _load_module(self, mod_name):
        # Check if module isn't already loaded
        if mod_name not in sys.modules:
            # Skip files which don't start with "mod_"
            if not mod_name.startswith("mod_"):
                return

            mod_path = self._modules_path + ".enabled." + mod_name
            print("Loading module '{}' [{}]".format(mod_name, mod_path))
            # Import it
            loaded_mod = __import__(mod_path, fromlist=[mod_name])

            # Load class from imported module
            class_name = utils.get_class_name(mod_name)
            loaded_class = getattr(loaded_mod, class_name)

            settings = self._get_mod_settings(mod_name)
            # Create an instance of the class
            try:
                self._loaded_modules[mod_name] = loaded_class(self, settings)
            except Exception as e:
                print("[ERROR] Couldn't load module '{}': {}".format(mod_name,
                        e, file=sys.stderr))
                return

            commands = self._loaded_modules[mod_name].get_commands()

            if commands is None:
                print("[WARNING] Module {} didn't register any commands"
                        .format(mod_name), file=sys.stderr)
            else:
                self._register_commands(commands, mod_name)

            print("Loaded module '{}'" .format(mod_name))

    def _module_handler(self):
        cparser = config_parser.ConfigParser(self._config_file)
        self._module_settings = cparser.get_all_mod_settings()
        # List of available commands
        self._command_list = dict()
        # Define directory with modules
        self._modules_path = os.path.join(os.path.dirname(os.pardir),
                                                            "botmodules")
        enabled_modules = os.path.join(self._modules_path, "enabled")
        # Create module list
        self._modules_list = pkgutil.iter_modules(path=[enabled_modules])
        # Initialize empty dictionary for loaded modules
        self._loaded_modules = dict()
        # Load modules
        print("Loading modules...")
        for loader, mod_name, ispkg in self._modules_list:
            self._load_module(mod_name)

    def _on_connect(self, connection, event):
        print("[{}] Connected to {}" .format(event.type.upper(), event.source))
        for server in self._server_list:
            for channel in self._server_list[server]:
                if not channel.startswith("@"):
                    print("[INFO] Joining {}@{}" .format(channel, server))
                    self.join_channel(server, channel,
                            self._server_list[server][channel].get_pass())

    def _on_disconnect(self, connection, event):
        print("[{}] Disconnected from {}" .format(event.type.upper(),
                event.source))

        #if self._exit_signal == False:
        #    # We got disconnected from the server (timeout, etc.)
        #    #self._server_list[event.source.lower()]["@@s"].reconnect()
        #    sys.exit(0)
        #else:
        #    # Got exit signal
        #    sys.exit(0)

    def _on_nicknameinuse(self, connection, event):
        if(self._nick_change_counter == 3):
            print("[{}] Couldn't find a free nickname, disconnecting from {}"
                  .format(event.type.upper(), event.source))
            connection.disconnect()
        else:
            self._nick_change_counter =+ 1
            current_nick = connection.get_nickname()
            print("[{}] Nickname {} is already taken, changing it to {}"
                  .format(event.type.upper(), current_nick, current_nick +
                  ("_" * self._nick_change_counter)))
            connection.nick(current_nick + ('_' * self._nick_change_counter))

    def _on_privmsg(self, connection, event):
        print("[{}] {}: <{}> {}" .format(event.type.upper(), event.target,
                                         event.source.split('!', 1)[0],
                                         event.arguments[0]))
        # Ignore our own messages
        if event.source.lower() == connection.get_nickname().lower():
            pass

        # Command prefix & actual command (the latter is added in
        # module_handler)
        module_data = dict()
        # Event target - channel or nickname (converted to lowercase)
        target = event.target.lower()
        # Address of the irc server
        serveraddr = connection.server

        if target in self._server_list[serveraddr]:
            # Channel messsage (pubmsg)
            # event.arguments[0] contains actual message
            # Because _handle_command modifies received message,
            # process it through the pubmsg handler first
            self._handle_pubmsg(connection, event)
            # Check, if message starts with defined command prefix
            cmdprefix = self._server_list[serveraddr][target].get_cmdprefix()
            if event.arguments[0].startswith(cmdprefix):
                # Get length of channel command prefix
                prefixlen = len(cmdprefix)
                # Strip the command prefix from the message string
                event.arguments[0] = event.arguments[0][prefixlen:]
                # Add command prefix into module_data dictionary
                module_data["prefix"] = cmdprefix
                # Call module handler
                self._handle_command(connection, event,
                        module_data, True)
        else:
            # Query
            # event.arguments[0] contains actual message
            # Because _handle_command modifies received message,
            # process it through the privmsg handler first
            self._handle_privmsg(connection, event)
            # Check, if message starts with defined command prefix
            cmdprefix = self._server_list[serveraddr]["@@s_cmdprefix"]
            if event.arguments[0].startswith(cmdprefix):
                # Get length of server command prefix
                prefixlen = len(cmdprefix)
                # Strip the command prefix from the message string
                event.arguments[0] = event.arguments[0][prefixlen:]
                # Add command prefix into module_data
                module_data["prefix"] = cmdprefix
                # Call command handler
                self._handle_command(connection, event,
                        module_data, False)

    def _on_pubmsg(self, connection, event):
        print("[{}] {}: <{}> {}" .format(event.type.upper(), event.target,
                                         event.source.split('!', 1)[0],
                                         event.arguments[0]))
        # Ignore our own messages
        if event.source.lower() == connection.get_nickname().lower():
            pass

        # Event target - channel or nickname (converted to lowercase)
        target = event.target.lower()
        # Address of the irc server
        serveraddr = connection.server
        # In this event we use only the first array index -
        # so we can abuse second one for channel prefix
        cmdprefix = self._server_list[serveraddr][target].get_cmdprefix()
        event.arguments.append(cmdprefix)

        self._handle_pubmsg(connection, event)

    def _on_join(self, connection, event):
        print("[{}] {} has joined {}" .format(event.type.upper(), event.source,
                                              event.target))
        self._handle_join(connection, event)

    def _on_quit(self, connection, event):
        # We don't need two separate signals for quit and part
        # (or at least for now)
        qtype = "quit" if event.type == "quit" else "left"
        print("[{}] {} has {} [{}]" .format(event.type.upper(), event.source,
                qtype, event.arguments[0]))
        self._handle_quit(connection, event)

    def _on_nick(self, connection, event):
        print("[{}] {} is now known as {}" .format(event.type.upper(),
                event.source.split('!', 1)[0], event.target))
        self._handle_nick(connection, event)

    def _register_commands(self, commands, module_name):
        for c in commands:
            self._command_list[c.lower()] = module_name

    def _reload_module(self, mod_name):
        print("Reloading module ", mod_name)
        self._modules_list = pkgutil.iter_modules(path=[self._modules_path])

        # Check if given module is loaded
        if mod_name in self._loaded_modules:
            # Remove module class instance
            del(self._loaded_modules[mod_name])
            # Reload module
            reloaded_mod = importlib.reload(sys.modules[self._modules_path +
                                                '.' + mod_name])
            # Get class name from module
            class_name = self._get_class_name(mod_name)
            # Get class object
            reloaded_class = getattr(reloaded_mod, class_name)
            # Create class instance
            self._loaded_modules[mod_name] = reloaded_class()
            print("Module {} reloaded".format(mod_name))

    def _timer_process(self):
        # Not sure how safe this solution is
        ts = datetime.now().timestamp()
        new_queue = list()
        self._timer_lock.acquire()
        for item in self._timer_queue:
            if int(item["delay"]) == int(ts):
                try:
                    self._server_list[item["server"]]["@@s"].privmsg(
                            item["channel"], item["message"])
                    print("> Sending delayed message to {}: {}"
                        .format(item["channel"], item["message"]))
                except Exception as e:
                    print("[WARNING] Couldn't send delayed message:\n"
                          "message: {}\ndestination: {}\nreason: {}\n"
                          .format(item["message"], item["channel"] + "@" +
                                  item["server"], e), file=sys.stderr)
            elif int(item["delay"]) > int(ts):
                new_queue.append(item)

        self._timer_queue = new_queue
        self._timer_lock.release()
        self._timer = threading.Timer(1, self._timer_process)
        self._timer.start()

    def add_server(self, address, port, nickname, scmdprefix):
        self._server_list[address] = dict()
        self._server_list[address]["@@s"] = self._client.server()

        try:
            self._server_list[address]["@@s"].connect(address, port, nickname,
                    None, nickname, nickname)
        except client.ServerConnectionError as e:
            print(e)
            self._server_list[address]["@@s"].reconnect()

        self._server_list[address]["@@s_cmdprefix"] = scmdprefix

    def handle_signals(self, signal, func=None):
        if(signal == 15):
            s = "SIGTERM"
            self._exit_signal = True
        elif(signal == 2):
            s = "SIGINT"
            self._exit_signal = True
        else:
            s = "Unknown"

        # Clean exit
        if self._exit_signal != False:
            for i in self._server_list:
                self._server_list[i]["@@s"].disconnect(s)

        # Beautiful workaround for killing all remaining threads
        os._exit(0)

    def join_channel(self, serveraddr, channel, password):
        self._server_list[serveraddr]["@@s"].join(channel, password)

    def send_msg(self, connection, event, is_public, message):
        if is_public:
            destination = event.target
        else:
            destination = event.source.split("!")[0]
        # Even though RFC has message limit 400 bytes, many servers
        # have their own limit. Thus setting it to 400 characters.
        buffer_max = (400 - len(destination) - 12)
        msg_len = len(message.encode("utf-8"))

        if msg_len >= buffer_max:
            data = utils.split_utf8(message.encode("utf-8"), buffer_max)

            for i in data:
                try:
                    connection.privmsg(destination, i.decode("utf-8"))
                    print("> Sending split output to {}: {}"
                            .format(destination, i.decode("utf-8")))
                except Exception as e:
                    print("Exception {0}".format(str(e)))
        else:
            try:
                connection.privmsg(destination, message)
                print("> Sending output to {}: {}"
                        .format(destination, message))
            except Exception as e:
                print("Exception {}" .format(str(e)))

    def send_delayed(self, server, channel, message, delay):
        if not server or not channel or not message or delay <= 0:
            print("[ERROR] Invalid data for send_delayed:\n"
                "server: {}\nchannel: {}\nmessage: {}\ndelay: {}\n"
                .format(server, channel, message, delay), file=sys.stderr)
            return

        item = {
            "server"  : server,
            "channel" : channel,
            "message" : message,
            "delay"   : int(delay)
        }

        self._timer_lock.acquire()
        self._timer_queue.append(item)
        self._timer_lock.release()

    def start(self):
        print("Starting bot instance...")
        self._client.process_forever()
