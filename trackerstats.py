from threading import Thread
import time
import yaml

from trackerstats.dbmanager import DBManager
from trackerstats.trackers.torrentday import TorrentDay

def thread(job, **kwargs):
    worker = Thread(target=job, kwargs=dict(**kwargs))
    worker.start()


if __name__ == "__main__":
    with open('./trackerstats.yaml') as f:
        CONFIG = yaml.safe_load(f)

    POLLING_INTERVAL = 1800
    DBMANAGER = DBManager(CONFIG['influxdb'])
    TorrentDay = TorrentDay(DBMANAGER, CONFIG['trackers']['torrentday'])

    while True:
        TorrentDay.get_stats()
        time.sleep(POLLING_INTERVAL)
