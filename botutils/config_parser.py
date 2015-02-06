#!/bin/usr/python3
# -*- coding: utf-8 -*-

import json
import os
import sys

class ConfigParser(object):

	def __init__(self, filename):
		self._filename = filename
		try:
			self._f = open(self._filename)
			self._content = json.load(self._f)
			self._f.close()
			self._basic_config_check()
			print(self._content)
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
			if 'name' not in server:
				raise ValueError('Missing \'name\' attribute in \'servers\' section.')
			if 'address' not in server:
				raise ValueError('Missing \'address\' attribute in \'servers\' section.')
			if 'channels' in server:
				for channel in server['channels']:
					if 'name' not in channel:
						raise ValueError('Missing \'name\' attribute in \'channels\' section.')

	def get_servers(self):
		return self._content['servers']

	def get_server_nickname(self, server):
		return server['nickname']

	def get_server_name(self, server):
		return server['name']

	def get_server_address(self, server):
		return server['address']

	def get_server_port(self, server):
		if 'port' not in server:
			return 6667
		else:
			return server['port']

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

	def get_channel_cmdprefix(self, channel):
		if 'cmdprefix' not in channel:
			return '?'
		else:
			return channel['cmdprefix']