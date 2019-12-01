from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone, date, timedelta
from bs4 import BeautifulSoup
from http.cookies import SimpleCookie
import humanfriendly


class TorrentDay(object):
    def __init__(self, dbmanager, config):
        self.dbmanager = dbmanager
        self.name = "TorrentDay"
        self.base_url = "https://www.torrentday.com/"
        self.logger = getLogger()
        self.cookies = SimpleCookie()
        self.cookies.load(config['cookies'])

    def get_stats(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []

        with Session() as s:
            cookies = {}
            for key, morsel in self.cookies.items():
                cookies[key] = morsel.value
            response = s.get(self.base_url, cookies=cookies)

        soup = BeautifulSoup(response.content, "html.parser")
        activity = soup.find(id="activityDiv").find_all("span")

        ratio = float(activity[1].string)
        upload = humanfriendly.parse_size(activity[3].string)
        download = humanfriendly.parse_size(activity[5].string)

        torrents_downloading = int(activity[6].string)
        torrents_uploading = int(activity[7].string)

        influx_payload.append(
            {
                "measurement": "stats",
                "tags": {
                    "tracker": self.name,
                },
                "time": now,
                "fields": {
                    "ratio": ratio,
                    "download": download,
                    "upload": upload,
                    "torrents_downloading": torrents_downloading,
                    "torrents_uploading": torrents_uploading,
                },
            },
        )

        self.logger.info("Updated TorrentDay")

        self.dbmanager.write_points(influx_payload)
