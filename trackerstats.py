import time
import yaml
from os import environ as env
from os.path import abspath, dirname, join, exists
from shutil import copyfile

from trackerstats.dbmanager import DBManager
from trackerstats.trackers.torrentday import TorrentDay


if __name__ == "__main__":
    DATA_FOLDER = env.get('DATA_FOLDER', abspath(dirname(__file__)))

    config_file_path = join(DATA_FOLDER, 'trackerstats.yaml')

    if not exists(config_file_path):
        copyfile(join(DATA_FOLDER, 'trackerstats.example.yaml'), config_file_path)

    with open(join(DATA_FOLDER, 'trackerstats.yaml')) as f:
        CONFIG = yaml.safe_load(f)

    DBMANAGER = DBManager(CONFIG['influxdb'])
    TorrentDay = TorrentDay(DBMANAGER, CONFIG['trackers']['torrentday'])

    while True:
        TorrentDay.get_stats()
        time.sleep(CONFIG['trackerstats']['polling_rate'])
