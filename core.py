#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
from os import mkdir, chdir, remove, listdir, environ
from os.path import join as pathjoin, isdir, isfile, abspath, dirname
from subprocess import check_output, CalledProcessError
from plistlib import readPlist, writePlist
import random, string
from parser import session


class downloader:
	def __init__(self):
		if isfile('/usr/local/bin/terminal-notifier'):
			self.notifier = True
		else:
			self.notifier = False
		self.session = session()
		self.root_dir = dirname(abspath(__file__))
		chdir(self.root_dir)
		self.plugins_dir = pathjoin(self.root_dir, 'plugins')
		self.configs_dir = pathjoin(self.root_dir, 'configs')
		self.icons_dir = pathjoin(self.root_dir, 'icons')
		self.series_dir = pathjoin(environ['HOME'], 'Movies', 'Сериалы')
		self.name = self.__class__.__name__
		chdir(self.configs_dir)
		config = '%s.plist'%self.name
		if not isfile(config):
			writePlist({'old_links':[''],'subscriptions':[''],'quality':'720p','excluding':['']}, config)
			exit(0)
		self.settings = readPlist(config)
		if not isdir(self.series_dir):
			mkdir(self.series_dir)
		chdir(self.series_dir)
		
	def __notify(self, title, subtitle, message='', _id=''):
		cmd = ['terminal-notifier', '-title', title, '-subtitle', subtitle, '-message', message]
		try:
			icon = next(pathjoin(self.icons_dir, x) for x in listdir(self.icons_dir) if x.startswith(self.name))
			cmd = cmd + ['-appIcon', icon]
		except StopIteration:
			pass
		if _id:
			cmd = cmd + ['-group', _id]
		check_output(cmd)
		
	def save(self):
		writePlist(self.settings, pathjoin(self.configs_dir, '%s.plist'%self.name))
		
	def parse(self, site, params={}):
		if 'last_modified' in self.settings:
			headers={'If-Modified-Since':self.settings.last_modified}
			site = self.session.get(site)
			if site.status_code==304:
				return 
		else:
			site = self.session.get(site, params=params)
		if 'Last-Modified' in site.headers:
			self.settings.last_modified = site.headers['Last-Modified']
		return site
		
	def download_torrent(self, tfile, series, episode, number, _id):
		if self.notifier: self.__notify(series, episode if episode else number, 'Загрузка начата', _id = _id)
		try:
			check_output(['aria2c', tfile, '--seed-time=0'])
			remove(tfile)
			return True
		except CalledProcessError:
			self.__notify(series, 'Torrent', 'Загрузка не удалась', _id = _id)
			return False
		
	def download(self, episodes, cookies={}):
		for quality, series, episode, number, link, extension in [(s['quality'], s['series'], 
		s['episode'], '%s эпизод %s сезона'%(int(s['episode_number']), int(s['series_number'])), s['link'], 
		s['extension']) for s in episodes]:
			#пропускаем исключения
			if any(ex in episode for ex in self.settings.excluding if not ex==''):
				continue
			if (self.settings.quality in quality or self.settings.quality in link) \
			and series in self.settings.subscriptions and not link in self.settings.old_links:
				_file='%s[%s].%s' % (episode, number, extension) if episode else '%s.%s'%(number, extension)
				foldername = '%s[%s]'%(series, self.name)
				if not isdir(foldername):
					mkdir(foldername)
				chdir(foldername)
				#создаем случайный id для уведомлений
				if self.notifier: _id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
				if extension.lower()=='torrent':
					open(_file, 'wb').write(self.session.get(link, cookies=cookies).content)
					if not self.download_torrent(_file, series, episode, number, _id):
						return
				else:
					if self.notifier: self.__notify(series, episode if episode else number, 'Загрузка начата', _id = _id)
					open(_file, 'wb').write(self.session.get(link, cookies=cookies).content)
				if self.notifier: self.__notify(series, episode if episode else number, 'Загрузка закончена', _id = _id)
				chdir('..')
		self.settings.old_links = [s['link'] for s in episodes]
		self.save()