#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import module_base

class Currency(module_base.ModuleBase):

	def __init__(self):
		self._commands = [ "curr", "currency", "currency-list", "curr-list"]
		# TODO: Channel-wide module prefix

	def on_privmsg(self, connection, event):
		pass