
import tkinter
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
import tkintermapview
import requests
import os
import json
import PIL.ImageTk
import webbrowser

from stats import PotaStats

VERSION = '0.0.1'

locations = []
locations2 = {}
loc_coords = {}
default_cfg = {'location': 'US-GA', 'init_x': 33.0406, 'init_y': -83.6431}
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


def get_locations():
    '''Download the locations info from POTA api (if not already present)'''

    global locations

    if not os.path.exists("locations.json"):
        save_json("https://api.pota.app/programs/locations", "locations.json")

    with open("locations.json", 'r') as loc_file:
        ld = json.load(loc_file)
        for program in ld:
            for entity in program['entities']:
                for location in entity['locations']:
                    id = location['descriptor']
                    locations.append(id)
                    locations2[id] = [program, entity, location]
                    loc_coords[id] = (location['latitude'], location['longitude'])

    # put them suckas in some sort of order for the dropdown
    locations.sort()


def save_json(url: str, file_name: str) -> int:
    '''Request json data from an endpoint and save it to the given file.'''

    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        with open(file_name, 'w') as out_file:
            out_file.write(json.dumps(data, indent=4))

    return r.status_code


def get_parks():
    '''Get parks for the current configured location (if not already present)'''

    loc = config['location']
    url = f"https://api.pota.app/location/parks/{loc}"
    json_file = f"parks-{loc}.json"

    if os.path.exists(json_file):
        return

    save_json(url, json_file)


def read_parks(window):
    global config
    with open(f"parks-{config['location']}.json", 'r') as park_file:
        home_data = json.load(park_file)
        for d in home_data:
            window.create_park_marker(d)


class PotaMapRoot(tkinter.Tk):
    '''Our main GUI class to display the POTA map'''

    def __init__(self, stats: PotaStats):
        super().__init__()

        global config

        self.stats = stats

        self.state('zoomed')
        self.title("POTA MAP")
        self.loc_var = StringVar()

        self.create_widgets()

        self.combo['values'] = locations
        self.map.set_position(config['init_x'], config['init_y'])
        self.map.set_zoom(7)
        self.loc_var.set(config['location'])

    def create_widgets(self):
        x = 1200
        y = 900

        self.top_frame = ttk.Frame(self, padding=10)
        self.top_frame.pack(side='top')
        self.park_lbl = ttk.Label(
            self.top_frame,
            text="Park Info",
            padding=10,
            font=('Helvetica', 12, 'bold'))
        self.park_lbl.pack(side='top')

        self.left_frame = ttk.Frame(self, padding=10)
        self.left_frame.pack(side='left', fill='x')

        self.combo_frame = ttk.Frame(self.left_frame, padding=10)
        self.combo_frame.pack(side='top', fill='x')
        self.cl = ttk.Label(self.combo_frame, text="Location:")
        self.cl.pack(side='left')
        self.combo = ttk.Combobox(self.combo_frame, textvariable=self.loc_var)
        self.combo.pack(side='top', anchor='w')
        self.combo.bind("<<ComboboxSelected>>", self.combo_callback)
        self.combo.bind("<Return>", self.combo_enter)

        self.loc_info_frame = ttk.Frame(self.left_frame, padding=10)
        self.loc_info_frame.pack(side='top', fill='x')
        self.loc_label = ttk.Label(self.loc_info_frame, text="Loc Info")
        self.loc_label.pack(side='top', anchor='w')

        self.browse_btn = ttk.Button(
            self.loc_info_frame, text="Open Stats Page", command=self.open_browser)
        self.browse_btn.pack(side='bottom')

        self.right_frame = ttk.Frame(self, padding=10)
        self.right_frame.pack(side='right')
        self.map = tkintermapview.TkinterMapView(
            self.right_frame,
            width=x,
            height=y,
            corner_radius=5)
        self.map.pack()

    def open_browser(self):
        url = "https://pota.app/#/user/stats/"
        webbrowser.open(url, new=2, autoraise=True)

    def create_park_marker(self, park):
        '''
        Create a map marker for the given park.

        Format of park is dictated by https://api.pota.app/location/parks/{loc}
        '''
        def cmd(marker):
            text = f"{marker.data['reference']} - {marker.data['name']}"
            self.park_lbl.configure(text=text)

        ref = park['reference']
        data = park

        actxed = self.stats.has_activated(ref)
        hunted = self.stats.has_hunted(ref)

        if actxed and hunted:
            i = PIL.ImageTk.PhotoImage(file="cd.png")
            name = ref + ' ' + park['name']
        elif actxed:
            i = PIL.ImageTk.PhotoImage(file="bd.png")
            name = ref + ' ' + park['name']
        elif hunted:
            i = PIL.ImageTk.PhotoImage(file="gd.png")
            name = ""
        else:
            i = PIL.ImageTk.PhotoImage(file="yd.png")
            name = ""

        self.map.set_marker(
            park['latitude'],
            park['longitude'],
            text=name,
            font="helvetica 12 bold",
            icon=i,
            text_color="#6d6af7",
            data=data,
            command=cmd)

    def combo_callback(self, event):
        ''' 
        Occurs on the location combobox selection change.
        '''
        loc = self.combo.get()
        global loc_coords
        global config
        self.map.delete_all_marker()
        (x, y) = loc_coords[loc]
        self.map.set_position(x, y)
        config['location'] = loc
        config['init_x'] = x
        config['init_y'] = y
        program = locations2[loc][0]
        entity = locations2[loc][1]
        location = locations2[loc][2]
        self.loc_label.configure(
            text=f"{program['name']}\n{entity['name']}({entity['entityId']}): {location['name']}")
        get_parks()
        read_parks(self)

    def combo_enter(self, event):
        ''' 
        Occurs when user presses enter in the location combobox
        '''
        loc = self.combo.get()
        print(loc)
        if loc in locations:
            self.combo_callback(event)


if __name__ == "__main__":
    print(f"potamap version {VERSION}")

    get_config()
    get_locations()
    get_parks()

    stats = PotaStats()

    window = PotaMapRoot(stats)
    read_parks(window)

    window.mainloop()

    save_config()
