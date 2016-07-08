#encoding: utf-8
from requests import Session
from bs4 import BeautifulSoup as bs
from json import loads

class response:
	def __init__(self, r):
		self.response = r
		self.status_code = self.response.status_code
		if self.status_code==200:
			self.headers = r.headers
			self.cookies = r.cookies
			self.content = r.content
		
	def auto(self, encoding='', items=False):
		if encoding:
			self.__encode(encoding)
		else:
			self.content_type = self.headers['Content-Type']
			if 'windows-1251' in self.content_type:
				self.__encode('cp1251')
			else:
				self.__encode('utf-8')
		if 'xml' in self.content_type and 'rss' in self.response.url.lower():
			return self.rss(encoding, items)
		elif 'html' in self.content_type or 'xml' in self.content_type:
			return bs(self.response.text, 'html.parser')
		elif 'json' in self.content_type:
			return loads(self.response.text)
		else:
			return bs(self.response.text, 'html.parser')
			
	def __encode(self, e):
		self.response.encoding = e

	def html(self, encoding=''):
		if encoding:
			self.__encode(encoding)
		return bs(self.response.text, 'html.parser')
	
	def xml(self, encoding=''):
		return self.html(encoding)
	
	def rss(self, encoding='', items=False):
		if encoding:
			self.__encode(encoding)
		return [(x.title.text, x.link.text) for x in bs(self.response.text, 'html.parser').select('item')] if not items else bs(self.response.text, 'html.parser').select('item')
	
	def json(self, encoding=''):
		if encoding:
			self.__encode(encoding)
		return loads(self.response.text)

class session:
	def __init__(self):
		self.s = Session()
		
	def get(self, url, params={}, cookies={}, headers={'User-agent':'Mozilla/5.0'}):
		return response(self.s.get(url, params=params, cookies=cookies, headers=headers))


if __name__=='__main__':
	link = 'http://habrahabr.ru'
	s = session()
	t = s.get(link).html('utf-8').title.text
	print(t)