import logging
from requests import Session, Request
from datetime import datetime, timezone, date, timedelta
from bs4 import BeautifulSoup
from http.cookies import SimpleCookie
import humanfriendly


class NordicBits(object):
    def __init__(self, dbmanager, config):
        self.dbmanager = dbmanager
        self.name = "NordicBits"
        self.base_url = "https://nordicb.org"
        self.logger = logging.getLogger("trackers.nordicbits")
        self.cookies = SimpleCookie()
        self.cookies.load(config["cookies"])
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'en,en-US;q=0.9,nb-NO;q=0.8,nb;q=0.7,no;q=0.6,nn;q=0.5,fi;q=0.4',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3895.5 Safari/537.36'
        }

    def get_stats(self):
        self.logger.info("Getting stats")
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []

        with Session() as s:
            try:
                cookies = {}
                for key, morsel in self.cookies.items():
                    cookies[key] = morsel.value

                s.headers.update(self.headers)
                s.cookies.update(cookies)

                response = s.get(self.base_url)

                soup = BeautifulSoup(response.content, "lxml")
                userdiv = soup.find('div', id='slidingDiv')
                userstats = userdiv.find_all('div')
                filtered_userstats = list(filter(lambda x: "slide_head" not in x['class'], userstats))

                for key, value in zip(filtered_userstats[0:][::2], filtered_userstats[1:][::2]):
                    if key.text == "Invites":
                        invites = int(value.text)
                    elif key.text == "Ratio":
                        ratio = float(value.text.replace(',', ''))
                    elif key.text == "Uploaded":
                        upload = humanfriendly.parse_size(value.text)
                    elif key.text == "Downloaded":
                        download = humanfriendly.parse_size(value.text)
                    elif key.text == "Bonus Points":
                        bonus_points = int(value.text)
                    elif key.text == "Uploading Files":
                        torrents_uploading = int(value.text)
                    elif key.text == "Downloading Files":
                        torrents_downloading = int(value.text)

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
                            "bonus_points": bonus_points,
                            "invites": invites
                        },
                    },
                )

                self.dbmanager.write_points(influx_payload)
                self.logger.info(f"Updated {self.name}")
            except:
                self.logger.error(f"Failed to update {self.name}")