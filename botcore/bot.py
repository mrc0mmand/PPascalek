#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from irc import client
from botutils import config_parser
from bothandlers import module_handler
from botcore import channel

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
		self._load_config()

	def add_server(self, address, port, nickname, scmdprefix):
		self._server_list[address] = dict()
		self._server_list[address]['&s'] = self._client.server()
		self._server_list[address]['&s'].connect(address, port, nickname, None, nickname, nickname)
		self._server_list[address]['&s_cmdprefix'] = scmdprefix

	def _on_privmsg(self, connection, event):
		print('_on_privmsg: Type: {}\nSource: {}\nTarget: {}\nArgs: {}\n'.format(event.type, event.source, event.target, event.arguments))
		# Ignore our own messages
		if event.source == connection.get_nickname():
			pass;
		
		print("[Bot] Event object:", event)
		# Event target - channel or nickname (converted to lovercase)
		target = event.target.lower()
		# Address of the irc server
		serveraddr = connection.server

		if target in self._server_list[serveraddr]:
			# Channel messsage (pubmsg)
			# event.arguments[0] contains actual message
			if event.arguments[0].startswith(self._server_list[serveraddr][target].get_cmdprefix()):
				# Get length of channel command prefix
				prefixlen = len(self._server_list[serveraddr][target].get_cmdprefix())
				# Strip the command prefix from the message string
				event.arguments[0] = event.arguments[0][prefixlen:]
				# Call command handler
				self._module_handler.handle_command(connection, event)

			self._module_handler.handle_pubmsg(connection, event)
		else:
			# Query
			# event.arguments[0] contains actual message
			if event.arguments[0].startswith(self._server_list[serveraddr]['&s_cmdprefix']):
				# Get length of server command prefix
				prefixlen = len(self._server_list[serveraddr]['&s_cmdprefix'])
				# STrip the command prefix from the message string
				event.arguments[0] = event.arguments[0][prefixlen:]
				# Call command handler
				self._module_handler.handle_command(connection, event)

			self._module_handler.handle_privmsg(connection, event)

	def _on_pubmsg(self, connection, event):
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

	def join_channel(self, serveraddr, channel, password):
		self._server_list[serveraddr]['&s'].join(channel, password)

	def _load_config(self):
		try:
			self._cp = config_parser.ConfigParser(self._configfile)
		except:
			print('Unable to continue, quitting... ')
			sys.exit(1)

		_servers = self._cp.get_servers()
		for server in _servers:
			nickname = self._cp.get_server_nickname(server)
			serveraddr = self._cp.get_server_address(server).lower()
			port = self._cp.get_server_port(server)
			scmdprefix = self._cp.get_server_cmdprefix(server)
			self.add_server(serveraddr, port, nickname, scmdprefix)

			channels = self._cp.get_server_channels(server)
			for chan in channels:
				chname = self._cp.get_channel_name(chan).lower()
				chpass = self._cp.get_channel_password(chan)
				cmdprefix = self._cp.get_channel_cmdprefix(chan, scmdprefix)
				self._server_list[serveraddr][chname] = channel.Channel(serveraddr, chname, chpass, cmdprefix)
				self.join_channel(serveraddr, chname, chpass)

		print(self._server_list)

	def start(self):
		print('Starting bot instance...')
		self._client.process_forever()