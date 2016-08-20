#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import urllib.parse
import urllib.request
from . import module_base
from botutils import utils

class Weather(module_base.ModuleBase):

    def __init__(self, b, settings):
        self._settings = settings
        self._weather_cmds = ["weather"]
        self._forecast_cmds = ["weather-forecast", "wf"]
        self._help = "Usage: {}{} location"
        gs = self.get_global_settings(self._settings)
        if gs is None or "api_key" not in gs or not gs["api_key"]:
            raise KeyError("Mising 'api_key' in mod_weather's global "
                           "settings section")
        self._api_key = gs["api_key"]

    def _get_default_location(self, connection, event, is_public):
        s = self.get_curr_settings(connection, event, is_public, self._settings)
        if s is not None and "default_loc" in s and s["default_loc"]:
            return s["default_loc"]
        s = self.get_global_settings(self._settings)
        if s is not None and "default_loc" in s and s["default_loc"]:
            return s["default_loc"]

        return None

    def _get_location_data(self, location):
        url = "https://autocomplete.wunderground.com/aq?query={}"
        normalized = utils.strip_accents(location)
        request = url.format(urllib.parse.quote(normalized))

        try:
            req = urllib.request.urlopen(request, None, 5)
            content = json.loads(req.read().decode("utf-8"))
            content = content["RESULTS"][0]
            loc_name = content["name"]
            loc_url = content["l"]

            return (loc_name, loc_url)
        except Exception as e:
            print("[Weather] Couldn't get location data: {}: {}".format(
                    type(e).__name__, e.args), file=sys.stderr)

        return (None, None)

    def _get_weather(self, location):
        url = "https://api.wunderground.com/api/{}/conditions{}.json"
        fmt = "{}: {}, {}\u00b0C (feels like: {}\u00b0C), humidity: {}, " \
              "wind: {} at {} km/h, dewpoint: {}\u00b0C"
        loc_name, loc_url = self._get_location_data(location)

        if not loc_name or not loc_url:
            return None

        request = url.format(self._api_key, loc_url)

        try:
            req = urllib.request.urlopen(request, None, 5)
            content = json.loads(req.read().decode("utf-8"))
            content = content["current_observation"]
            weather = fmt.format(loc_name, content["weather"], content["temp_c"],
                        content["feelslike_c"], content["relative_humidity"],
                        content["wind_dir"], content["wind_kph"],
                        content["dewpoint_c"])

            return weather
        except Exception as e:
            print("[Weather] Couldn't get current conditions: {}: {}".format(
                    type(e).__name__, e.args), file=sys.stderr)

        return None

    def _get_forecast(self, location):
        url = "https://api.wunderground.com/api/{}/forecast{}.json"
        fmt = "{}: {}\u00b0C/{}\u00b0C {} (ChoP: {}%)"
        loc_name, loc_url = self._get_location_data(location)

        if not loc_name or not loc_url:
            return None

        request = url.format(self._api_key, loc_url)

        try:
            req = urllib.request.urlopen(request, None, 5)
            content = json.loads(req.read().decode("utf-8"))
            content = content["forecast"]["simpleforecast"]["forecastday"]
            forecast = "{}: ".format(loc_name)

            for day in content:
                w = fmt.format(day["date"]["weekday"], day["high"]["celsius"],
                        day["low"]["celsius"], day["conditions"], day["pop"])
                forecast += w + " | "

            return forecast
        except Exception as e:
            print("[Weather] Couldn't get forecast: {}: {}".format(
                    type(e).__name__, e.args), file=sys.stderr)

        return None

    def get_commands(self):
        return self._weather_cmds + self._forecast_cmds

    def on_command(self, b, module_data, connection, event, is_public):
        location = event.arguments[0].strip()
        cmd = module_data["command"]

        if not location:
            location = self._get_default_location(connection, event, is_public)

        if location:
            if cmd in self._weather_cmds:
                weather = self._get_weather(location)
                if not weather:
                    b.send_msg(connection, event, is_public,
                            "Couldn't get conditions for '{}'".format(location))
                else:
                    b.send_msg(connection, event, is_public, weather)
            elif cmd in self._forecast_cmds:
                forecast = self._get_forecast(location)
                if not forecast:
                    b.send_msg(connection, event, is_public,
                            "Couldn't get forecast for '{}'".format(location))
                else:
                    b.send_msg(connection, event, is_public, forecast)
        else:
            self.on_help(b, module_data, connection, event, is_public)

    def on_help(self, b, module_data, connection, event, is_public):
            b.send_msg(connection, event, is_public, self._help.format(
                module_data["prefix"], module_data["command"]))
