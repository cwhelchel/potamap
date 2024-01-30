
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
import re
from idlelib.tooltip import Hovertip

from stats import PotaStats

VERSION = '0.0.1'

locations = []
locations2 = {}
loc_coords = {}
default_cfg = {'location': 'US-GA', 'init_x': 33.0406, 'init_y': -83.6431, 'display_opts': 0,
               'show_actx_lbl': True, 'show_hunt_lbl': False, 'show_unkn_lbl': False, 'text_color': '#6d6af7'}
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
                    loc_coords[id] = (location['latitude'],
                                      location['longitude'])

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


def check_color_input(val: str) -> str:
    '''
    Checks if the input is a valid hex color. If invalid returns a default
    '''
    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', val)
    if match:
        return val
    else:
        return "#6d6af7"  # original default val


class PotaMapRoot(tkinter.Tk):
    '''Our main GUI class to display the POTA map'''

    def __init__(self, stats: PotaStats):
        super().__init__()

        global config

        self.stats = stats

        self.state('zoomed')
        self.title("POTA MAP")
        self.loc_var = StringVar()
        self.color_var = StringVar()
        self.show_hunt_var = IntVar()
        self.show_actx_var = IntVar()
        self.show_unkn_var = IntVar()  # these are for the yellow dots

        self.create_widgets()

        self.combo['values'] = locations
        self.map.set_position(config['init_x'], config['init_y'])
        self.map.set_zoom(7)
        self.loc_var.set(config['location'])
        self.show_hunt_var.set(1 if config['show_hunt_lbl'] else 0)
        self.show_actx_var.set(1 if config['show_actx_lbl'] else 0)
        self.show_unkn_var.set(1 if config['show_unkn_lbl'] else 0)
        self.color_var.set(config['text_color'])

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

        self.combo_frame2 = ttk.Frame(self.left_frame, padding=10)
        self.combo_frame2.pack(side='top', fill='x')
        self.lbl_displayopts = ttk.Label(
            self.combo_frame2, text="Display Options:")
        self.lbl_displayopts.pack(side='left')

        self.combo_displayopts_vals = ['Full Park Name', 'Park# Only']
        self.combo_displayopts = ttk.Combobox(
            self.combo_frame2, values=self.combo_displayopts_vals)
        self.combo_displayopts.current(config['display_opts'])
        self.combo_displayopts.pack(side='top', anchor='w')
        self.combo_displayopts.bind(
            "<<ComboboxSelected>>", self.combo_displayopts_callback)
        self.combo_displayopts.bind("<Return>", self.combo_displayopts_enter)

        self.lbl_opts_frame = ttk.Frame(self.left_frame, padding=10)
        self.lbl_opts_frame.pack(side='top', fill='x')
        self.chk_show_hunt = ttk.Checkbutton(
            self.lbl_opts_frame, text="Hunt Labels", variable=self.show_hunt_var, command=self.handle_check)
        self.chk_show_hunt.pack(side='top', anchor='w')
        self.chk_show_actx = ttk.Checkbutton(
            self.lbl_opts_frame, text="Activation Labels", variable=self.show_actx_var, command=self.handle_check)
        self.chk_show_actx.pack(side='top', anchor='w')
        self.chk_show_unkn = ttk.Checkbutton(
            self.lbl_opts_frame, text="Unknown Labels", variable=self.show_unkn_var, command=self.handle_check)
        self.chk_show_unkn.pack(side='top', anchor='w')
        self.tt = Hovertip(self.chk_show_unkn,
                           'For the un-hunted un-activated parks')

        self.lbl_color = ttk.Label(self.lbl_opts_frame, text="Color:")
        self.lbl_color.pack(side='left')
        self.color_textbox = ttk.Entry(
            self.lbl_opts_frame, text="Color:", textvariable=self.color_var)
        self.color_textbox.bind("<Return>", self.accept_color_input)
        self.color_textbox.bind("<FocusOut>", self.accept_color_input)
        self.color_textbox.pack(side='top')

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

        def get_displayopt_text(display_key: str):
            if not config[display_key]:
                return ""

            if config['display_opts'] == 1:  # Option 1: Park# Only
                text = f"{ref}"
            else:  # Default/Option 0 - Full Park Name
                text = f"{ref} {park['name']}"

            return text

        ref = park['reference']
        data = park

        actxed = self.stats.has_activated(ref)
        hunted = self.stats.has_hunted(ref)

        if actxed and hunted:
            i = PIL.ImageTk.PhotoImage(file="cd.png")
            name = get_displayopt_text('show_actx_lbl')
        elif actxed:
            i = PIL.ImageTk.PhotoImage(file="bd.png")
            name = get_displayopt_text('show_actx_lbl')
        elif hunted:
            i = PIL.ImageTk.PhotoImage(file="gd.png")
            name = get_displayopt_text('show_hunt_lbl')
        else:
            i = PIL.ImageTk.PhotoImage(file="yd.png")
            name = get_displayopt_text('show_unkn_lbl')

        self.map.set_marker(
            park['latitude'],
            park['longitude'],
            text=name,
            font="helvetica 12 bold",
            icon=i,
            text_color=check_color_input(config["text_color"]),
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

    def combo_displayopts_callback(self, event):
        ''' 
        Occurs on the Display Options combobox selection change.
        Update the marker labels using the current state of location config (already selected by user in the location combobox)
        '''
        loc = self.combo_displayopts.get()
        self.map.delete_all_marker()
        config['display_opts'] = self.combo_displayopts.current()
        self.map.set_position(config['init_x'], config['init_y'])
        get_parks()
        read_parks(self)

    def combo_displayopts_enter(self, event):
        ''' 
        Occurs when user presses enter in the location combobox
        '''
        loc = self.combo_displayopts.get()
        print(loc)
        self.combo_displayopts_callback(event)

    def handle_check(self):
        '''
        Occurs when a users checks a box
        '''
        h = self.show_hunt_var.get()
        a = self.show_actx_var.get()
        u = self.show_unkn_var.get()
        config['show_hunt_lbl'] = True if h == 1 else False
        config['show_actx_lbl'] = True if a == 1 else False
        config['show_unkn_lbl'] = True if u == 1 else False
        self.map.delete_all_marker()
        get_parks()
        read_parks(self)

    def accept_color_input(self, event):
        '''
        Occurs when users presses Enter or Leaves the color Entry widget
        '''
        val = self.color_var.get()
        config['text_color'] = check_color_input(val)
        self.map.delete_all_marker()
        get_parks()
        read_parks(self)


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
