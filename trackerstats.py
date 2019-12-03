import coloredlogs
import logging
import logging.config
import time
import yaml
from os import environ as env
from os.path import abspath, dirname, join, exists
from shutil import copyfile

from trackerstats.dbmanager import DBManager
from trackerstats.trackers.norbits import NorBits
from trackerstats.trackers.nordicbits import NordicBits
from trackerstats.trackers.iptorrents import IPTorrents
from trackerstats.trackers.torrentday import TorrentDay


def load_config():
    DATA_FOLDER = env.get("DATA_FOLDER", abspath(dirname(__file__)))
    config_file_path = join(DATA_FOLDER, "trackerstats.yaml")
    logger.info(f"Loading config from {config_file_path}")

    if not exists(config_file_path):
        logger.warn("No config file found. Generating from example file.")
        copyfile(join(DATA_FOLDER, "trackerstats.example.yaml"), config_file_path)

    with open(join(DATA_FOLDER, "trackerstats.yaml")) as f:
        config = yaml.safe_load(f)

    return config

def setup_logging():
    with open('trackerstats/logging.yaml', 'rt') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    coloredlogs.install()


if __name__ == "__main__":
    setup_logging()

    logger = logging.getLogger("trackerstats")

    CONFIG = load_config()
    DBMANAGER = DBManager(CONFIG["influxdb"])
    POLLING_RATE = CONFIG["trackerstats"]["polling_rate"]

    trackers = []

    if CONFIG["trackers"]["norbits"]["enabled"]:
        trackers.append(NorBits(DBMANAGER, CONFIG["trackers"]["norbits"]))
    if CONFIG["trackers"]["nordicbits"]["enabled"]:
        trackers.append(NordicBits(DBMANAGER, CONFIG["trackers"]["nordicbits"]))
    if CONFIG["trackers"]["iptorrents"]["enabled"]:
        trackers.append(IPTorrents(DBMANAGER, CONFIG["trackers"]["iptorrents"]))
    if CONFIG["trackers"]["torrentday"]["enabled"]:
        trackers.append(TorrentDay(DBMANAGER, CONFIG["trackers"]["torrentday"]))

    while True:
        for tracker in trackers:
            tracker.get_stats()
        logger.info(f"All trackers updated. Waiting {POLLING_RATE}s for next update.")
        time.sleep(POLLING_RATE)
