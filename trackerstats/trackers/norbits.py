from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone, date, timedelta
from bs4 import BeautifulSoup
from http.cookies import SimpleCookie
import humanfriendly


class NorBits(object):
    def __init__(self, dbmanager, config):
        self.dbmanager = dbmanager
        self.name = "NorBits"
        self.base_url = "https://norbits.net"
        self.logger = getLogger()
        self.cookies = SimpleCookie()
        self.cookies.load(config["cookies"])

    def get_stats(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []

        with Session() as s:
            cookies = {}
            for key, morsel in self.cookies.items():
                cookies[key] = morsel.value
            response = s.get(self.base_url + "/userdetails.php", cookies=cookies)

            soup = BeautifulSoup(response.content, "lxml")
            usertable = soup.find('div', class_='p sh').find('table')

            for tablerow in usertable.find_all('tr'):
                key = tablerow.find("th").text
                value = tablerow.find("td").text

                if key == "Opplastet":
                    upload = tablerow.find("td").text
                    upload = upload[upload.find("[")+1:upload.find("]")].replace(',', '')
                    upload = humanfriendly.parse_size(upload)
                elif key == "Nedlastet":
                    download = tablerow.find("td").text
                    download = download[download.find("[")+1:download.find("]")].replace(',', '')
                    download = humanfriendly.parse_size(download)
                elif key == "Poeng":
                    bonus_points = tablerow.find("td").text
                    bonus_points = bonus_points.split('.')[0]
                    bonus_points = int(bonus_points)
                elif key == "Ratio":
                    ratio = tablerow.find("td").find("span").text
                    ratio = float(ratio)

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
                        "bonus_points": bonus_points
                    },
                },
            )

            self.logger.info("Updated NorBits")
            print("Updated NorBits")

            self.dbmanager.write_points(influx_payload)
