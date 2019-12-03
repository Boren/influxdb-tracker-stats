import logging
from requests import Session, Request
from datetime import datetime, timezone, date, timedelta
from bs4 import BeautifulSoup
from http.cookies import SimpleCookie
import humanfriendly


class IPTorrents(object):
    def __init__(self, dbmanager, config):
        self.dbmanager = dbmanager
        self.name = "IPTorrents"
        self.base_url = "https://iptorrents.com"
        self.logger = logging.getLogger("trackers.iptorrents")
        self.cookies = SimpleCookie()
        self.cookies.load(config["cookies"])

    def get_stats(self):
        self.logger.info("Getting stats")
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []

        with Session() as s:
            try:
                cookies = {}
                for key, morsel in self.cookies.items():
                    cookies[key] = morsel.value
                response = s.get(self.base_url, cookies=cookies)

                soup = BeautifulSoup(response.content, "lxml")

                bonus_points = soup.select_one("a[href*=mybonus]").text
                bonus_points = int(float(bonus_points[bonus_points.find("</i>")+1:]))

                userprofilelink = soup.select_one('a[href*="/u/"]')
                userresponse = s.get(
                    self.base_url + userprofilelink["href"],
                    cookies=cookies
                )
                usersoup = BeautifulSoup(userresponse.content, "lxml")
                usertable = usersoup.find('table', class_='t1')

                for tablerow in usertable.find_all('tr'):
                    key = tablerow.find("th").text
                    value = tablerow.find("td").text

                    if key == "Uploaded":
                        upload = tablerow.find("td").text
                        upload = upload[upload.find("(")+1:upload.find(" B)")]
                        upload = int(upload.replace(',', ''))
                    elif key == "Downloaded":
                        download = tablerow.find("td").text
                        download = download[download.find("(")+1:download.find(" B)")]
                        download = int(download.replace(',', ''))
                    elif key == "Invites":
                        available_index = value.find("Available: ")+11
                        invites = value[available_index:available_index+1]
                        invites = int(invites)
                    elif key == "Share ratio":
                        ratio = tablerow.find("td").find("font").find("font").text
                        ratio = float(ratio)
                    elif key == "Seeding":
                        torrents_uploading = tablerow.find("td").find("a").text
                        torrents_uploading = int(torrents_uploading)
                    elif key == "Leeching":
                        torrents_downloading = tablerow.find("td").find("a").text
                        torrents_downloading = int(torrents_downloading)

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
