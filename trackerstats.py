import time
import yaml

from trackerstats.dbmanager import DBManager
from trackerstats.trackers.torrentday import TorrentDay


if __name__ == "__main__":
    with open('./trackerstats.yaml') as f:
        CONFIG = yaml.safe_load(f)

    DBMANAGER = DBManager(CONFIG['influxdb'])
    TorrentDay = TorrentDay(DBMANAGER, CONFIG['trackers']['torrentday'])

    while True:
        TorrentDay.get_stats()
        time.sleep(CONFIG['trackerstats']['polling_rate'])
