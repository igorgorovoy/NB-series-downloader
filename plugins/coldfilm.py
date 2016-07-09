from core import downloader
from re import search

class coldfilm(downloader):
	def __init__(self):
		super().__init__()
	def start(self):
		rss = self.parse('http://coldfilm.ru/news/rss').rss()
		if not rss:
			return 
		data = []
		for t, link in rss:
			s = search('(.*) (\d+) сезон .*(\d) серия', t)
			if s:
				series, sn, en = s.groups(1)
			else:
				continue
			link = self.parse(link).html().select('a[href$=torrent]')[0]
			q = link.text
			link = link['href']
			data.append({'quality':q, 'series':series, 'episode':'', 'episode_number':en, 'series_number':sn, 'link':link, 'extension':'torrent'})
		self.download(data)