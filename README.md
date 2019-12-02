<p align="center">
  <h3 align="center">Tracker Stats</h3>

  <p align="center">
    Saves stats from torrent trackers to InfluxDB
    <br />
    <br />
    <a href="https://github.com/boren/influxdb-tracker-stats/issues">Report Bug</a>
    ·
    <a href="https://github.com/boren/influxdb-tracker-stats/issues">Request Feature</a>
  </p>
</p>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [About The Project](#about-the-project)
- [Usage](#usage)
- [Contributing](#contributing)

## About The Project

It can sometimes be hard to keep track of ratios across multiple private trackers.
This project aims to save information from multiple trackers in InfluxDB in order to create graphs and warnings in Grafana.

## Tracker Support

| Tracker    | Downloaded | Uploaded | Ratio | Invites | Current Downloads | Current Uploads | Bonus Points | Reseed | Hit-and-Run |
|------------|:----------:|:--------:|:-----:|:-------:|:-----------------:|:---------------:|:------------:|:------:|:-----------:|
| IPTorrents |      x     |     x    |   x   |    x    |         x         |        x        |       x      |        |             |
| TorrentDay |      x     |     x    |   x   |    x    |         x         |        x        |       x      |        |             |

## Usage

1. `pip install -r requirements.txt`
2. Copy `trackerstats.example.yaml` to `trackerstats.yaml` and fill in your values.
3. `python trackerstats.py`

## Contributing

Feel free to submit Pull Requests or create issues, preferably with screenshots and a good description of the issue.
