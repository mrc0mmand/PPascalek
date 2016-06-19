#!/usr/bin/python3
# -*- coding: utf-8 -*-

from botcore import bot
import argparse
import signal

# TODO: lepší umístění handlení signálů, hlavně asi potom, co přijde podpora konzole

if __name__ == '__main__':
    config_file = 'config.json'
    # Let's parse some arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='name of the config file')

    args = parser.parse_args()

    if args.config:
        config_file = args.config

    b = bot.Bot(config_file)
    signal.signal(signal.SIGTERM, b.handle_signals)
    signal.signal(signal.SIGINT, b.handle_signals)
    b.start()
