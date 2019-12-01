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
        self.base_url = "https://www.torrentday.com"
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
            torrents_downloading = int(activity[6].string)
            torrents_uploading = int(activity[7].string)

            bonus_points_string = soup.select_one("a[href*=mybonus]").string
            bonus_points = bonus_points_string[bonus_points_string.find("(")+1:bonus_points_string.find(")")]
            bonus_points = int(float(bonus_points))

            invites_string = soup.select_one("a[href*=invite]").string
            invites = invites_string[invites_string.find("(")+1:invites_string.find(")")]
            invites = int(invites)

            # One more decimal for data in user profile
            userprofilelink = soup.find(id="dropDownHdr").find("a")

            userresponse = s.get(self.base_url + userprofilelink['href'], cookies=cookies)
            usersoup = BeautifulSoup(userresponse.content, "html.parser")
            userdetails = usersoup.find(id="usrDetailsInfoBarSpans").find_all("span", class_="detailsInfoSpan")

            upload = humanfriendly.parse_size(userdetails[3].find("span").string)
            download = humanfriendly.parse_size(userdetails[4].find("span").string)

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

            self.logger.info("Updated TorrentDay")
            print("Updated torrentday")

            self.dbmanager.write_points(influx_payload)
