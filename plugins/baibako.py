from core import Downloader
from re import search, split


class Baibako(Downloader):
    def __init__(self):
        super().__init__()

    def start(self):
        rss = self.parse('http://baibako.tv/rss2.php',
                         {'feed': 'dl', 'passkey': ''}).rss('cp1251')
        if not rss:
            return
        data = []
        for title, link in rss:
            series, series_eng, number, quality, *episode = split('\s?/', title)
            episode = episode[0].split('(')[0] if len(episode) > 0 else ''
            sn, en = search('s(\d+)e(\d+)', number).groups(1)
            data.append(
                {'quality': quality, 'series': series, 'episode': episode,
                 'episode_number': en, 'series_number': sn,
                 'link': link, 'extension': 'torrent'})
        self.download(data)
