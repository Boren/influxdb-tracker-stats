from sys import exit
import logging
from influxdb import InfluxDBClient
from requests.exceptions import ConnectionError
from influxdb.exceptions import InfluxDBServerError


class DBManager(object):
    def __init__(self, server):
        self.server = server
        self.logger = logging.getLogger("dbmanager")
        if self.server["url"] == "influxdb.domain.tld":
            self.logger.critical("You have not configured your trackers.ini")
            exit()
        self.influx = InfluxDBClient(
            host=self.server["url"],
            port=self.server["port"],
            username=self.server["username"],
            password=self.server["password"],
            ssl=self.server["ssl"],
            database="tracker-stats",
            verify_ssl=self.server["verify_ssl"],
        )
        try:
            version = self.influx.request("ping", expected_response_code=204).headers[
                "X-Influxdb-Version"
            ]
            self.logger.info("Influxdb version: %s", version)
        except ConnectionError:
            self.logger.critical(
                "Error testing connection to InfluxDB. Please check your url/hostname"
            )
            exit()

        databases = [db["name"] for db in self.influx.get_list_database()]

        if "tracker-stats" not in databases:
            self.logger.info("Creating tracker-stats database")
            self.influx.create_database("tracker-stats")

            retention_policies = [
                policy["name"]
                for policy in self.influx.get_list_retention_policies(
                    database="tracker-stats"
                )
            ]
            if "tracker-stats 1y-1d" not in retention_policies:
                self.logger.info("Creating tracker-stats retention policy (1y-1d)")
                self.influx.create_retention_policy(
                    name="tracker-stats 1y-1d",
                    duration="1y",
                    replication="1",
                    database="tracker-stats",
                    default=True,
                    shard_duration="1d",
                )

    def write_points(self, data):
        d = data
        self.logger.debug("Writing Data to InfluxDB %s", d)
        try:
            self.influx.write_points(d)
        except (InfluxDBServerError, ConnectionError) as e:
            self.logger.error(
                "Error writing data to influxdb. Dropping this set of data. "
                "Check your database! Error: %s",
                e,
            )
