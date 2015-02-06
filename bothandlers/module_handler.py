#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pkgutil
import importlib
import sys
import os

class ModuleHandler(object):

	def __init__(self):
		self._modules_path = os.path.join(os.path.dirname(os.pardir), 'botmodules')
		self._modules_list = pkgutil.iter_modules(path=[self._modules_path])
		print(self._modules_path)
		print(self._modules_list)
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
	
	def _get_class_name(self, mod_name):
		class_name = ''

		# Split module name and skip first word (mod)
		words = mod_name.split('_')[1:] 

		# Capitalise the first letter of each word and add it to final string
		for word in words:
			class_name = word.title()

		return class_name

	def load_module(self, mod_name):
		# Check if module isn't already loaded
		if mod_name not in sys.modules:
			# Skip files which don't start with 'mod_'
			if not mod_name.startswith("mod_"):
				return

			print("[ModuleHandler] Loading module '{}' [{}]".format(mod_name, self._modules_path + '.' + mod_name))
			# Import it
			loaded_mod = __import__(self._modules_path + '.' + mod_name, fromlist=[mod_name])

			# Load class from imported module
			class_name = self._get_class_name(mod_name)
			loaded_class = getattr(loaded_mod, class_name)

			# Create an instance of the class
			self._loaded_modules[mod_name] = loaded_class()
			#self._loaded_modules[mod_name].run()
			print("[ModuleHandler] Loaded module '{}'".format(mod_name))

	def _load_all_modules(self):
		print("Loading modules...")
		
		for loader, mod_name, ispkg in self._modules_list:
			self.load_module(mod_name)

	def reload_module(self, mod_name):
		print("Reloading module ", mod_name)
		self._modules_list = pkgutil.iter_modules(path=[self._modules_path])
		
		# Check if given module is loaded
		if mod_name in self._loaded_modules:
			del(self._loaded_modules[mod_name])
			reloaded_mod = importlib.reload(sys.modules[self._modules_path + '.' + mod_name])
			class_name = self._get_class_name(mod_name)
			reloaded_class = getattr(reloaded_mod, class_name)
			self._loaded_modules[mod_name] = reloaded_class()
			print("Module {} reloaded ".format(mod_name))
