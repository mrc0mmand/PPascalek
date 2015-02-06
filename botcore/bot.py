#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from irc import client
from botutils import config_parser
from bothandlers import module_handler
from . import channel

class Bot(object):

	def __init__(self, configfile):
		self._configfile = configfile
		self._client = client.Reactor()
		# Events: https://bitbucket.org/jaraco/irc/src/9e4fb0ce922398292ed4c0cfd3822e4fe19a940d/irc/events.py?at=default#cl-177
		self._client.add_global_handler('pubmsg', self._on_privmsg)
		self._client.add_global_handler('privmsg', self._on_privmsg)
		self._client.add_global_handler('join', self._on_join)
		self._client.add_global_handler('quit', self._on_quit)
		self._client.add_global_handler('nick', self._on_nick)
		self._module_handler = module_handler.ModuleHandler()
		self._server_list = dict()
		self._channel_list = dict()
		self._load_config()

	def add_server(self, servername, address, port, nickname):
		self._server_list[servername] = self._client.server()
		self._server_list[servername].connect(address, port, nickname, None, nickname, nickname)

	def _on_privmsg(self, connection, event):
		print('_on_privmsg: Type: {}\nSource: {}\nTarget: {}\nArgs: {}\n'.format(event.type, event.source, event.target, event.arguments))
		# Ignore our own messages
		if event.source == connection.get_nickname():
			pass;
		
		self._module_handler.reload_module('mod_test')
		if event.type == 'pubmsg':
			self._module_handler.handle_pubmsg(connection, event)
		else:
			self._module_handler.handle_privmsg(connection, event)

	def _on_pubmsg(self, conenction, event):
		print('_on_pubmsg: Type: {}\nSource: {}\nTarget: {}\nArgs: {}\n'.format(event.type, event.source, event.target, event.arguments))
		# Ignore our own messages
		if event.source == connection.get_nickname():
			pass;

		self._module_handler.handle_pubmsg(connection, event)

	def _on_join(self, connection, event):
		print('Type: {}\nSource: {}\nTarget: {}\nArgs: {}\n'.format(event.type, event.source, event.target, event.arguments))
		self._module_handler.handle_join(connection, event)

	def _on_quit(self, connection, event):
		print('Type: {}\nSource: {}\nTarget: {}\nArgs: {}\n'.format(event.type, event.source, event.target, event.arguments))
		self._module_handler.handle_quit(connection, event)

	def _on_nick(self, connection, event):
		print('Type: {}\nSource: {}\nTarget: {}\nArgs: {}\n'.format(event.type, event.source, event.target, event.arguments))
		self._module_handler.handle_nick(connection, event)

	def join_channel(self, servername, channel, password):
		self._server_list[servername].join(channel, password)

	def _load_config(self):
		try:
			self._cp = config_parser.ConfigParser(self._configfile)
		except:
			print('Unable to continue, quitting... ')
			sys.exit(1)

		_servers = self._cp.get_servers()
		for server in _servers:
			nickname = self._cp.get_server_nickname(server)
			servername = self._cp.get_server_name(server)
			address = self._cp.get_server_address(server)
			port = self._cp.get_server_port(server)
			self.add_server(servername, address, port, nickname)

			#channels = self._cp.get_server_channels(server)
			#for channel in channels:
			#	channame, chanpass = list(channel.items())[0]
			#	self.join_channel(servername, channame, chanpass)

	def start(self):
		print('Starting bot instance...')
		self._client.process_forever()