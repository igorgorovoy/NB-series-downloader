from core import Downloader
from re import search


class Newstudio(Downloader):
    def __init__(self):
        super().__init__()
        self.credentials = {'login': '', 'password': ''}

    def start(self):
        rss = self.parse('http://newstudio.tv/rss.php',
            {'user': self.credentials['login'], 'pass': self.credentials['password']}) \
            .rss('utf-8', items=True)
        if not rss:
            return
        data = []
        for i in rss:
            try:
                title = i.title.text
                link = i.enclosure['url']
                s, sn, en = search('([^(]*) \(Сезон (\d+), Серия (\d+)\)', title).groups(1)
                data.append({'quality': title, 'series': s,
                             'episode': '', 'episode_number': en,
                             'series_number': sn, 'link': link, 'extension': 'torrent'})
            except Exception:
                pass
        self.download(data)
