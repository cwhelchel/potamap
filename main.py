
import requests
import os
import json
import re

from pota import PotaStats
from pota import PotaData
from ui import PotaMapRoot
from cfg import Config, get_config

VERSION = '0.0.3'

default_cfg = {
    'location': 'US-GA',
    'init_x': 33.0406,
    'init_y': -83.6431,
    'display_opts': 0,
    'show_actx_lbl': True,
    'show_hunt_lbl': False,
    'show_unkn_lbl': False,
    'text_color': '#6d6af7'
}

config = {}

#
# https://docs.pota.app/api/authentication.html (WIP. Ignore for now)
#


def get_config():
    '''Read config.json into the config object'''

    if not os.path.exists("config.json"):
        with open("config.json", 'w') as cfg_file:
            cfg_file.write(json.dumps(default_cfg, indent=4))
        return

    with open("config.json", 'r') as cfg_file:
        cfg_data = json.load(cfg_file)
        print(cfg_data)
        global config
        config = cfg_data


def save_config():
    '''Save the current config object to config.json'''

    with open("config.json", 'w') as cfg_file:
        global config
        cfg_file.write(json.dumps(config, indent=4))


def save_json(url: str, file_name: str) -> int:
    '''Request json data from an endpoint and save it to the given file.'''

    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        with open(file_name, 'w') as out_file:
            out_file.write(json.dumps(data, indent=4))

    return r.status_code


def check_color_input(val: str) -> str:
    '''
    Checks if the input is a valid hex color. If invalid returns a default
    '''
    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', val)
    if match:
        return val
    else:
        return "#6d6af7"  # original default val


if __name__ == "__main__":
    print(f"potamap version {VERSION}")

    get_config()

    data = PotaData()
    data.download_parks(config['location'])

    stats = PotaStats()

    window = PotaMapRoot(stats, data, config)

    window.mainloop()

    save_config()
