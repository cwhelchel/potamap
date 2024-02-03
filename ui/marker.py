import PIL.ImageTk

from pota.stats import PotaStats


class MapMarker:
    def __init__(self, data, stats: PotaStats, config):
        self.marker = None  # will hold CanvasPositionMarker after its created
        self.data = data
        self.config = config
        self.ref = data['reference']
        self.park_name = data['name']
        self.actxed = stats.has_activated(self.ref)
        self.hunted = stats.has_hunted(self.ref)

    def get_title(self) -> str:
        return f"{self.ref} - {self.park_name}"

    def get_label(self) -> str:
        actxed = self.actxed
        hunted = self.hunted

        if actxed and hunted:
            name = self.get_displayopt_text('show_actx_lbl')
        elif actxed:
            name = self.get_displayopt_text('show_actx_lbl')
        elif hunted:
            name = self.get_displayopt_text('show_hunt_lbl')
        else:
            name = self.get_displayopt_text('show_unkn_lbl')

        return name

    def get_icon(self) -> PIL.ImageTk.PhotoImage:
        actxed = self.actxed
        hunted = self.hunted

        if actxed and hunted:
            i = PIL.ImageTk.PhotoImage(file="cd.png")
        elif actxed:
            i = PIL.ImageTk.PhotoImage(file="bd.png")
        elif hunted:
            i = PIL.ImageTk.PhotoImage(file="gd.png")
        else:
            i = PIL.ImageTk.PhotoImage(file="yd.png")
        return i

    def get_displayopt_text(self, display_key: str):

        # no label if checkbox says hide to hide
        if not self.config[display_key]:
            return ""

        if self.config['display_opts'] == 1:  # Option 1: Park# Only
            text = f"{self.ref}"
        else:  # Default/Option 0 - Full Park Name
            text = f"{self.ref} {self.park_name}"

        return text
