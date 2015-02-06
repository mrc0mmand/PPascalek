#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import module_base

class Currency(module_base.ModuleBase):

	def __init__(self):
		self._commands = [ "curr", "currency", "currency-list", "curr-list"]

	def on_command(self, connection, event):
		print("[Currency] Event object:", event)
		for command in self._commands:
			if event.arguments[0].startswith(command + ' '):
				print("[mod_Currency] It works!")