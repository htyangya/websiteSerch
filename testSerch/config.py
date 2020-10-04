import json
import re
import requests as rq
from pyquery import PyQuery as pq
from urlobject import URLObject
from PIL import Image
from requests import ConnectTimeout
from io import BytesIO

reg = re.compile("/\*.*?\*/")
config_str = reg.sub("", open("config.json", encoding="utf-8").read())
config = json.loads(config_str)


def get_global_setting(name):
    return config["global_settings"].get(name)


def get_websites_setting(host_name, setting_name):
    return config["websites"].get(host_name, {}).get(setting_name)


def auto_get_charset(url):
    u = URLObject(url)
    return get_websites_setting(u.hostname, "charset")


def get_strategy_setting(strategy_name, setting_name):
    return config["strategies"].get(strategy_name, {}).get(setting_name)


def get_strategy_inputs(strategy_name):
    settings = config["strategies"].get(strategy_name)
    if "global_inputs_name" in settings:
        return get_websites_setting(settings.get("global_inputs_name"), "inputs")
    return get_strategy_setting(strategy_name, "inputs")
