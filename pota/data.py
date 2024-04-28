import json
import os
from pathlib import Path
import requests
from dataclasses import dataclass


@dataclass
class LocationData:
    program: any
    entity: any
    location: any
    lat: float
    lon: float

    def get_lat(self) -> any:
        return self.location['latitude']

    def get_lon(self) -> any:
        return self.location['longitude']


class PotaData:
    '''
    This class holds the location and park data loaded from the POTA
    API.
    '''

    def __init__(self, data_dir: str = "") -> None:
        '''
        Initialize the PotaData class

        calls download_locations(self) to download and load the POTA location
        info
        '''
        self.locations = []  # list of locations eg: US-AL, US-GA
        self.locations2: dict[str, LocationData] = {}
        self.data_dir = data_dir
        if not Path(self.data_dir).exists():
            Path.mkdir(Path(self.data_dir))
        self.download_locations()

    def get_location_info_text(self, loc: str) -> str:
        if loc not in self.locations2:
            return "Error: invalid location"
        p = self.locations2[loc].program
        e = self.locations2[loc].entity
        loc = self.locations2[loc].location
        return f"{p['name']}\n{e['name']}({e['entityId']}): {loc['name']}"

    def get_park_count(self, loc: str) -> int:
        if loc not in self.locations2:
            return 0
        return self.locations2[loc].location['parks']

    def get_location_coordinates(self, loc: str) -> (float, float):
        if loc not in self.locations2:
            return (0.0, 0.0)
        return (self.locations2[loc].get_lat(),
                self.locations2[loc].get_lon())

    def download_locations(self):
        '''
        Download the locations info from POTA api

        if the locations.json file is already present, it won't re-download
        this file.
        '''

        file = self._get_path("locations.json")
        if not os.path.exists(file):
            save_json("https://api.pota.app/programs/locations", file)

        self._load_location_data()

    def check_and_download_parks(self, location: str, force: bool = False):
        '''
        Checks if the data file is present for the given location, if not, it
        downloads the park data for the location.

        Parameters
        ------------
        location : string
            the POTA location string
        force : bool
            true to force downloading, even if file already exists
        '''
        loc = location

        if loc not in self.locations:
            raise ValueError("argument 'location' is invalid")

        url = f"https://api.pota.app/location/parks/{loc}"
        json_file = f"parks-{loc}.json"
        file = self._get_path(json_file)

        if force:
            save_json(url, file)
            return

        if os.path.exists(file):
            return

        save_json(url, file)

    def read_parks(self, location: str, force: bool = False) -> []:
        '''
        Read the parks from the file for a given location.

        If that file is not found, it will try to download it from the POTA API

        Parameters
        ------------
        location : string
            the POTA location string
        force : bool
            true to force downloading, even if file already exists
        '''
        result = []

        if location not in self.locations:
            raise ValueError("argument 'location' is invalid")

        self.check_and_download_parks(location, force)

        file_name = self._get_path(f"parks-{location}.json")

        with open(file_name, 'r', encoding='utf-8') as park_file:
            loc_data = json.load(park_file)
            for park in loc_data:
                result.append(park)
        return result

    def _load_location_data(self):
        self.locations.clear()

        file = self._get_path("locations.json")
        with open(file, 'r') as loc_file:
            ld = json.load(loc_file)
            for program in ld:
                for entity in program['entities']:
                    for location in entity['locations']:
                        id = location['descriptor']
                        self.locations.append(id)
                        self.locations2[id] = LocationData(
                            program,
                            entity,
                            location,
                            location['latitude'],
                            location['longitude'])

        # put them suckas in some sort of order for the dropdown
        self.locations.sort()

    def _get_path(self, file_name: str) -> Path:
        return Path(self.data_dir, file_name)


def save_json(url: str, file_name: str) -> int:
    '''Request json data from an endpoint and save it to the given file.'''

    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        with open(file_name, 'w') as out_file:
            out_file.write(json.dumps(data, indent=4))

    return r.status_code
