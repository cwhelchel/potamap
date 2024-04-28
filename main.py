from pota import PotaStats
from pota import PotaData
from ui import PotaMapRoot
from cfg import Config, get_config, save_config

VERSION = '0.0.4'

config: Config

# IMPORTANT NOTES:
#
# The POTA API does not yet have a way to provide authenticated access to a
# user's POTA data. so we have to ignore the docs given at the link below:
# https://docs.pota.app/api/authentication.html
# Hopefully one day that will be added and this tool can be updated to do those
# operations automatically
#
# For now we will have to periodically download the csv files from My Stats
# page on the POTA app.
#
# - Cainan
#

if __name__ == "__main__":
    print(f"potamap version {VERSION}")

    config = get_config()

    data = PotaData(data_dir="data")
    data.check_and_download_parks(config.location)

    stats = PotaStats()

    window = PotaMapRoot(stats, data, config)

    window.mainloop()

    save_config(config)
