#!/usr/bin/python3
# -*- coding: utf-8 -*-

from botutils import config_parser
import pkgutil
import importlib
import sys
import os

class ModuleHandler(object):

    def __init__(self, config_file):
        # Config file name
        self._config_file = config_file
        # Get module settings
        self._cp = config_parser.ConfigParser(config_file)
        self._mod_settings = self._cp.get_all_mod_settings()
        # List of available commands
        self._command_list = dict()
        # Define directory with modules
        self._modules_path = os.path.join(os.path.dirname(os.pardir),
                                                                "botmodules")
        # Create module list
        self._modules_list = pkgutil.iter_modules(path=[self._modules_path])
        # Initialize empty dictionary for loaded modules
        self._loaded_modules = dict()
        self._load_all_modules()

    def handle_privmsg(self, connection, event):
        for module in self._loaded_modules:
            self._loaded_modules[module].on_privmsg(connection, event)

    def handle_pubmsg(self, connection, event):
        for module in self._loaded_modules:
            self._loaded_modules[module].on_pubmsg(connection, event)

    def handle_join(self, connection, event):
        for module in self._loaded_modules:
            self._loaded_modules[module].on_join(connection, event)

    def handle_quit(self, connection, event):
        for module in self._loaded_modules:
            self._loaded_modules[module].on_quit(connection, event)

    def handle_nick(self, connection, event):
        for module in self._loaded_modules:
            self._loaded_modules[module].on_nick(connection, event)

    def handle_command(self, connection, event, module_data, is_public):
        # Get first word from the argument string, save it and strip it
        command = event.arguments[0].partition(' ')[0]
        event.arguments[0] = event.arguments[0].partition(' ')[2]
        # Save the command into module_data dictionary
        module_data["command"] = command

        if command:
            command.lower()
            for cmd in self._command_list:
                if command == cmd:
                    try:
                        listcmd = self._command_list[cmd]
                        self._loaded_modules[listcmd].on_command(module_data,
                                            connection, event, is_public)
                    except Exception as e:
                        print("[ModuleHandler] Module {} caused an exception:"
                              "{}".format(self._command_list[cmd], e),
                                            file=sys.stderr)

    def _get_mod_settings(self, module):
        mod_settings = dict()

        for server, sdata in self._mod_settings.items():
            mod_settings[server] = dict()

            if module in sdata:
                msettings = self._mod_settings[server][module]
                mod_settings[server]["@global"] = msettings

            for channel, cdata in sdata.items():
                if module in cdata:
                    if server not in mod_settings:
                        mod_settings[server] = dict()

                    mod_settings[server][channel] = dict()
                    csettings = self._mod_settings[server][channel][module]
                    mod_settings[server][channel] = csettings

        return mod_settings

    def _get_class_name(self, mod_name):
        class_name = ""

        # Split module name and skip first word (mod)
        words = mod_name.split('_')[1:]

        # Capitalise the first letter of each word and add it to final string
        for word in words:
            class_name = word.title()

        return class_name

    def _register_commands(self, commands, module_name):
        for c in commands:
            self._command_list[c.lower()] = module_name

    def load_module(self, mod_name):
        # Check if module isn't already loaded
        if mod_name not in sys.modules:
            # Skip files which don't start with "mod_"
            if not mod_name.startswith("mod_"):
                return

            print("[ModuleHandler] Loading module '{}' [{}]"
                  .format(mod_name, self._modules_path + '.' + mod_name))
            # Import it
            loaded_mod = __import__(self._modules_path + '.' + mod_name,
                                        fromlist=[mod_name])

            # Load class from imported module
            class_name = self._get_class_name(mod_name)
            loaded_class = getattr(loaded_mod, class_name)

            settings = self._get_mod_settings(mod_name)
            # Create an instance of the class
            self._loaded_modules[mod_name] = loaded_class(settings)

            commands = self._loaded_modules[mod_name].get_commands()

            if commands is None:
                print("[WARNING] Module {} didn't register any commands"
                        .format(mod_name))
            else:
                self._register_commands(commands, mod_name)

            print("[ModuleHandler] Loaded module '{}'" .format(mod_name))

    def _load_all_modules(self):
        print("Loading modules...")

        for loader, mod_name, ispkg in self._modules_list:
            self.load_module(mod_name)

    def reload_module(self, mod_name):
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
