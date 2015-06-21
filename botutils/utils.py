#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def split_utf8(string, length):
    """Split UTF-8 into chunks of maximum length."""
    while len(string) > length:
        index = length
        while ((string[index]) & 0xc0) == 0x80:
            index -= 1
        yield string[:index]
        string = string[index:]
    yield string
