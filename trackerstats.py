import time
import yaml
from os import environ as env
from os.path import abspath, dirname, join, exists
from shutil import copyfile

from trackerstats.dbmanager import DBManager
from trackerstats.trackers.norbits import NorBits
from trackerstats.trackers.iptorrents import IPTorrents
from trackerstats.trackers.torrentday import TorrentDay


if __name__ == "__main__":
    DATA_FOLDER = env.get('DATA_FOLDER', abspath(dirname(__file__)))

    config_file_path = join(DATA_FOLDER, 'trackerstats.yaml')

    if not exists(config_file_path):
        copyfile(join(DATA_FOLDER, 'trackerstats.example.yaml'), config_file_path)

    with open(join(DATA_FOLDER, 'trackerstats.yaml')) as f:
        CONFIG = yaml.safe_load(f)

    DBMANAGER = DBManager(CONFIG['influxdb'])

    trackers = []

    if CONFIG['trackers']['norbits']['enabled']:
        trackers.append(NorBits(DBMANAGER, CONFIG['trackers']['norbits']))
    if CONFIG['trackers']['iptorrents']['enabled']:
        trackers.append(IPTorrents(DBMANAGER, CONFIG['trackers']['iptorrents']))
    if CONFIG['trackers']['torrentday']['enabled']:
        trackers.append(TorrentDay(DBMANAGER, CONFIG['trackers']['torrentday']))

    while True:
        for tracker in trackers:
            tracker.get_stats()
        time.sleep(CONFIG['trackerstats']['polling_rate'])
