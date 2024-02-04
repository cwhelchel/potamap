from idlelib.tooltip import Hovertip
import re
import tkinter
from tkinter import ttk
from tkinter import StringVar, IntVar
import webbrowser
import tkintermapview
from tkintermapview.canvas_position_marker import CanvasPositionMarker

from pota.data import PotaData
from pota.stats import PotaStats
from .marker import MapMarker


class PotaMapRoot(tkinter.Tk):
    '''Our main GUI class to display the POTA map'''

    def __init__(self, stats: PotaStats, data: PotaData, config):
        super().__init__()

        self.config = config

        self.stats = stats
        self.data = data
        self.map_markers = MapMarkers(self)

        self.state('zoomed')
        self.title("POTA MAP")
        self.loc_var = StringVar()
        self.color_var = StringVar()
        self.show_hunt_var = IntVar()
        self.show_actx_var = IntVar()
        self.show_unkn_var = IntVar()  # these are for the yellow dots

        self.create_widgets()

        self.combo['values'] = self.data.locations
        self.map.set_position(self.config['init_x'], self.config['init_y'])
        self.map.set_zoom(7)
        self.loc_var.set(self.config['location'])
        self.map_markers.create_markers(self.config['location'])
        self.show_hunt_var.set(1 if self.config['show_hunt_lbl'] else 0)
        self.show_actx_var.set(1 if self.config['show_actx_lbl'] else 0)
        self.show_unkn_var.set(1 if self.config['show_unkn_lbl'] else 0)
        self.color_var.set(self.config['text_color'])

        self._update_loc_labels(self.config['location'])

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
        self.combo.bind("<<ComboboxSelected>>", self.combo_locations_callback)
        self.combo.bind("<Return>", self.combo_enter)

        self.combo_frame2 = ttk.Frame(self.left_frame, padding=10)
        self.combo_frame2.pack(side='top', fill='x')
        self.lbl_displayopts = ttk.Label(
            self.combo_frame2, text="Display Options:")
        self.lbl_displayopts.pack(side='left')

        self.combo_displayopts_vals = ['Full Park Name', 'Park# Only']
        self.combo_displayopts = ttk.Combobox(
            self.combo_frame2, values=self.combo_displayopts_vals)
        self.combo_displayopts.current(self.config['display_opts'])
        self.combo_displayopts.pack(side='top', anchor='w')
        self.combo_displayopts.bind(
            "<<ComboboxSelected>>", self.combo_displayopts_callback)
        self.combo_displayopts.bind("<Return>", self.combo_displayopts_enter)

        self.lbl_opts_frame = ttk.Frame(self.left_frame, padding=10)
        self.lbl_opts_frame.pack(side='top', fill='x')
        self.chk_show_hunt = ttk.Checkbutton(
            self.lbl_opts_frame,
            text="Hunt Labels",
            variable=self.show_hunt_var,
            command=self.handle_check)
        self.chk_show_hunt.pack(side='top', anchor='w')
        self.chk_show_actx = ttk.Checkbutton(
            self.lbl_opts_frame,
            text="Activation Labels",
            variable=self.show_actx_var,
            command=self.handle_check)
        self.chk_show_actx.pack(side='top', anchor='w')
        self.chk_show_unkn = ttk.Checkbutton(
            self.lbl_opts_frame,
            text="Unknown Labels",
            variable=self.show_unkn_var,
            command=self.handle_check)
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
        self.loc_stats = ttk.Label(self.loc_info_frame, text="Loc Info")
        self.loc_stats.pack(side='top', anchor='w')

        self.browse_btn = ttk.Button(
            self.loc_info_frame,
            text="Open Stats Page",
            command=self.open_browser)
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

    def combo_locations_callback(self, event):
        '''
        Occurs on the location combobox selection change.
        '''
        loc = self.combo.get()
        self.map.delete_all_marker()
        # (x, y) = loc_coords[loc]
        (x, y) = self.data.get_location_coordinates(loc)
        self.map.set_position(x, y)
        self.config['location'] = loc
        self.config['init_x'] = x
        self.config['init_y'] = y
        # self.data.download_parks(loc)
        self.map_markers.create_markers(loc)
        self._update_loc_labels(loc)

    def _update_loc_labels(self, loc):
        '''
        Update the displayed text on the location info and stat labels
        '''
        loc_info = self.data.get_location_info_text(loc)
        self.loc_label.configure(text=loc_info)
        hunt_cnt = self.stats.get_hunt_count(loc)
        actx_cnt = self.stats.get_actx_count(loc)
        # total = location['parks']
        total = self.data.get_park_count(loc)
        t = f"hunted: {hunt_cnt} of {total}\nactivated: {actx_cnt} of {total}"
        self.loc_stats.configure(text=t)

    def combo_enter(self, event):
        '''
        Occurs when user presses enter in the location combobox
        '''
        loc = self.combo.get()
        print(loc)
        if loc in self.data.locations:
            self.combo_locations_callback(event)

    def combo_displayopts_callback(self, event):
        '''
        Occurs on the Display Options combobox selection change.

        Update the marker labels using the current state of location config
        (already selected by user in the location combobox)
        '''
        loc = self.combo_displayopts.get()
        self.config['display_opts'] = self.combo_displayopts.current()
        self.map.set_position(self.config['init_x'], self.config['init_y'])
        self.map_markers.update_markers(loc)

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
        self.config['show_hunt_lbl'] = True if h == 1 else False
        self.config['show_actx_lbl'] = True if a == 1 else False
        self.config['show_unkn_lbl'] = True if u == 1 else False
        # self.map.delete_all_marker()
        self.map_markers.update_markers(self.config['location'])

    def accept_color_input(self, event):
        '''
        Occurs when users presses Enter or Leaves the color Entry widget
        '''
        val = self.color_var.get()

        # nothing changed
        if val == self.config['text_color']:
            return

        self.config['text_color'] = check_color_input(val)

        # if changing colors we have to delete and re-add
        self.map.delete_all_marker()
        self.map_markers.create_markers(self.config['location'])


class MapMarkers:
    def __init__(self, window: PotaMapRoot):
        self.markers: list[MapMarker] = []
        self.window = window

    def create_markers(self, location: str):
        parks = self.window.data.read_parks(location)

        for park in parks:
            marker = self._create_marker(park)
            self.markers.append(marker)

    def update_markers(self, location: str):
        for x in self.markers:
            text = x.get_label()
            x.marker.text_color = self.window.config["text_color"]
            x.marker.set_text(text)

    def _create_marker(self, park) -> MapMarker:
        '''
        Create a map marker for the given park.

        Format of park is dictated by https://api.pota.app/location/parks/{loc}
        '''
        def cmd(marker):
            y: MapMarker = marker.data
            text = y.get_title()
            self.window.park_lbl.configure(text=text)

        x = MapMarker(park, self.window.stats, self.window.config)

        # are these disable parks.. one example: 9M-0011  tasik raban
        if park['latitude'] is None or park['longitude'] is None:
            return

        m = self.window.map.set_marker(
            park['latitude'],
            park['longitude'],
            text=x.get_label(),
            font="helvetica 12 bold",
            icon=x.get_icon(),
            text_color=check_color_input(self.window.config["text_color"]),
            data=x,
            command=cmd)
        x.marker = m
        return x

    def _update_marker(self, marker: CanvasPositionMarker):
        pass


def check_color_input(val: str) -> str:
    '''
    Checks if the input is a valid hex color. If invalid returns a default
    '''
    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', val)
    if match:
        return val
    else:
        return "#6d6af7"  # original default val
