import csv
import os

class PotaStats:

    def __init__(self) -> None:
        self.activated_parks = []
        self.hunted_parks = []
        self._get_activations_csv()
        self._get_hunts_csv()

    def has_hunted(self, ref: str) -> bool:
        return ref in self.hunted_parks

    def has_activated(self, ref: str) -> bool:
        return ref in self.activated_parks

    def _get_activations_csv(self):
        '''
        Read activations downloaded from EXPORT CSV on Users POTA My Stats page
        see https://pota.app/#/user/stats
        '''
        file_n = "activator_parks.csv"

        if not os.path.exists(file_n):
            return

        with open(file_n) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            skip_headers = True
            for row in csv_reader:
                if skip_headers:
                    skip_headers = False
                    continue
                else:
                    # print(f'\t{row["DX Entity"]} {row["HASC"]} {row["Reference"]}.')
                    self.activated_parks.append(row['Reference'])

    def _get_hunts_csv(self):
        '''
        Read hunted parks downloaded from EXPORT CSV on Users POTA My Stats page
        see https://pota.app/#/user/stats
        '''
        file_n = "hunter_parks.csv"

        if not os.path.exists(file_n):
            return

        with open(file_n) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            skip_headers = True
            for row in csv_reader:
                if skip_headers:
                    skip_headers = False
                    continue
                else:
                    # print(f'\t{row["DX Entity"]} {row["HASC"]} {row["Reference"]}.')
                    self.hunted_parks.append(row['Reference'])

    # def get_hunts():
    #     '''Ok wtf how do we get these? A: Use chrome's debugger.

    #     Go to pota.app/#/user/stats. Press F12. Go to network tab. Click "Fetch/XHR"
    #     filter. Reload (Ctrl+R). Under list that appears click "park" until you find
    #     the request URL that matches the url below. Click the Response tab and copy
    #     all the json to a the input box and click Save Hunts (or directly save it to
    #     hunts.json)
    #     '''
    #     # url = "https://api.pota.app/user/stats/hunter/park"
    #     json_file = "hunts.json"

    #     # create if we dont have one
    #     if not os.path.exists(json_file):
    #         pathlib.Path(json_file).write_text("{}")

    #     with open(json_file, 'r') as hunts_file:
    #         hunt_data = json.load(hunts_file)
    #         for x in hunt_data:
    #             hunted_parks.append(x['reference'])

    # def get_activations():
    #     '''Get user's activations from a file.'''

    #     url = "https://api.pota.app/user/activations?all=1"

    #     # this will work but you have to get the idToken value from the cookie using
    #     # the chrome debugger tools. not very user friendly. and if your already doing that
    #     # just past the url into the browser from the pota.app page
    #     s = requests.Session()
    #     s.headers.update({
    #         'authorization': '<need idToken from cookies>',
    #         'origin': "https://pota.app",
    #         'accept': "application/json, text/plain, */*"
    #     })

    #     json_file = "activations.json"
    #     code = save_json(url, json_file)

    #     if code == 403:  # forbidden
    #         print("403 FORBIDDEN: probably need the idToken from browser cookies")

    #     # create if we dont have one
    #     if not os.path.exists(json_file):
    #         pathlib.Path(json_file).write_text("{\"count\":0,\"activations\":[]}")

    #     with open(json_file, 'r') as activation_file:
    #         activation_data = json.load(activation_file)
    #         for x in activation_data['activations']:
    #             activated_parks.append(x['reference'])
