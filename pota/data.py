import json
import os
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
    '''

    def __init__(self) -> None:
        '''
        Initialize the PotaData class

        calls download_locations(self) to download and load the POTA location
        info
        '''
        self.locations = []  # list of locations eg: US-AL, US-GA
        self.locations2: dict[str, LocationData] = {}
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

        if not os.path.exists("locations.json"):
            save_json("https://api.pota.app/programs/locations",
                      "locations.json")

        self._load_location_data()

    def download_parks(self, location: str):
        '''
        Downloads the park info for given location.

        If a park file for the location already exists, it won't re-download it
        '''

        loc = location

        if loc not in self.locations:
            raise ValueError("argument 'location' is invalid")

        url = f"https://api.pota.app/location/parks/{loc}"
        json_file = f"parks-{loc}.json"

        if os.path.exists(json_file):
            return

        save_json(url, json_file)

    def read_parks(self, location: str) -> []:
        '''
        Read the parks from the file for a given location.

        If that file is not found, it will try to download it from the POTA API
        '''
        result = []

        if location not in self.locations:
            raise ValueError("argument 'location' is invalid")

        file_name = f"parks-{location}.json"

        if not os.path.exists(file_name):
            self.download_parks(location)

        with open(file_name, 'r', encoding='utf-8') as park_file:
            loc_data = json.load(park_file)
            for park in loc_data:
                result.append(park)
        return result

    def _load_location_data(self):
        self.locations.clear()

        with open("locations.json", 'r') as loc_file:
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


def save_json(url: str, file_name: str) -> int:
    '''Request json data from an endpoint and save it to the given file.'''

    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        with open(file_name, 'w') as out_file:
            out_file.write(json.dumps(data, indent=4))

    return r.status_code
