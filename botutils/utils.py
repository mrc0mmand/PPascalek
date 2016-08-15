#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def get_class_name(mod_name):
    class_name = ""

    # Split module name and skip first word (mod)
    words = mod_name.split('_')[1:]

    # Capitalise the first letter of each word and add it to final string
    for word in words:
        class_name = word.title()

    return class_name

def split_utf8(string, length):
    """Split UTF-8 into chunks of maximum length."""
    while len(string) > length:
        index = length
        while ((string[index]) & 0xc0) == 0x80:
            index -= 1
        yield string[:index]
        string = string[index:]
    yield string
