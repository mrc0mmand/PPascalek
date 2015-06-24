#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import copy

class ConfigParser(object):

    def __init__(self, filename):
        self._filename = filename
        try:
            self._f = open(self._filename)
            self._content = json.load(self._f)
            self._f.close()
            self._basic_config_check()
        except (IOError, OSError) as e:
            print("[ConfigParser]", e, file=sys.stderr)
            raise
        except ValueError as e:
            print("[ConfigParser]", e, file=sys.stderr)
            raise

    def _basic_config_check(self):
        if 'servers' not in self._content:
            raise ValueError('Missing \'servers\' section in the config file.')

        for server in self._content['servers']:
            if 'nickname' not in server:
                raise ValueError('Missing \'nickname\' attribute in \'servers\' section.')
            if 'address' not in server:
                raise ValueError('Missing \'address\' attribute in \'servers\' section.')
            if 'cmdprefix' not in server:
                raise ValueError('Missing \'cmdprefix\' attribute in \'servers\' section.')
            if 'channels' in server:
                for channel in server['channels']:
                    if 'name' not in channel:
                        raise ValueError('Missing \'name\' attribute in \'channels\' section.')

    def get_servers(self):
        return self._content['servers']

    def get_server_nickname(self, server):
        return server['nickname']

    def get_server_address(self, server):
        return server['address']

    def get_server_port(self, server):
        if 'port' not in server:
            return 6667
        else:
            return server['port']

    def get_server_cmdprefix(self, server):
        return server['cmdprefix']

    def get_server_channels(self, server):
        if 'channels' not in server:
            return []
        else:
            return server['channels']

    def get_channel_name(self, channel):
        return channel['name']

    def get_channel_password(self, channel):
        if 'pass' not in channel:
            return ''
        else:
            return channel['pass']

    def get_channel_cmdprefix(self, channel, default=''):
        if 'cmdprefix' not in channel:
            return default
        else:
            return channel['cmdprefix']

    def get_all_mod_settings(self):
        mod_settings = dict()
 
        try:
            for s in self._content['servers']:
                if 'mod_settings' in s:
                    # Load global module settings
                    mod_settings[s['address']] = dict()
                    for m in s['mod_settings']:
                        mod_settings[s['address']][m['name']] = m

                if 'channels' in s:
                    for c in s['channels']:
                        if 'mod_settings' in c:
                            # Overwrite global module settings with channel specific ones
                            mod_settings[s['address']][c['name']] = dict()

                            for m in c['mod_settings']:
                                if m['name'] in mod_settings[s['address']]:
                                    mod_settings[s['address']][c['name']][m['name']] = copy.deepcopy(mod_settings[s['address']][m['name']])
                                else:
                                    mod_settings[s['address']][c['name']][m['name']] = dict()

                                for key, value in m.items():
                                    mod_settings[s['address']][c['name']][m['name']][key] = value
        except Exception as e:
            print('[ConfigParser] Couldn\'t get module settings: {}' .format(e), file=sys.stderr)

        return mod_settings
