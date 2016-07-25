#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
from os import mkdir, chdir, remove, listdir, environ
from os.path import join, isdir, isfile, abspath, dirname
from subprocess import check_output, CalledProcessError
from plistlib import load, dump
import random
import string
from parser import Session


class AttrDict(dict):
    # класс для доступа к значениям переданного в конструктор словаря через атрибуты
    def __init__(self, d, **kwargs):
        super().__init__(**kwargs)
        self.update(d)

    def __getattr__(self, k):
        return self[k]

    def __setattr__(self, k, v):
        self[k] = v


class Downloader:
    def __init__(self):
        # проверяем есть ли уведомлятор
        if isfile('/usr/local/bin/terminal-notifier'):
            self.notifier = True
        else:
            self.notifier = False
        # берем сессию из parser.py
        self.session = Session()
        # определяем корень
        self.root_dir = dirname(abspath(__file__))
        # переходим в корень
        # сделано для работы в цикле по плагинам
        chdir(self.root_dir)
        # папка плагинов
        self.plugins_dir = join(self.root_dir, 'plugins')
        # папка конфигов
        self.configs_dir = join(self.root_dir, 'configs')
        # папка иконок
        self.icons_dir = join(self.root_dir, 'icons')
        # папка, куда будут складываться загружаемые сериалы
        self.series_dir = join(environ['HOME'], 'Movies', 'Сериалы')
        # упрощение доступа к имени класса
        self.name = self.__class__.__name__
        # переходим в папку конфигов
        chdir(self.configs_dir)
        # сохраняем имя конфига текущего плагина
        self.config_path = join(self.configs_dir, '%s.plist' % self.name)
        # если это - первый запуск с новым расширением, создаем файл конфигурации
        if not isfile(self.config_path):
            dump({'old_links': [''], 'subscriptions': [''], 'quality': '720p', 'excluding': ['']},
                 open(self.config_path, 'wb'))
            exit(0)
        self.settings = AttrDict(load(open(self.config_path, 'rb')))
        # если папки сериалов по указанному пути еще нет, создаем ее
        if not isdir(self.series_dir):
            mkdir(self.series_dir)
        chdir(self.series_dir)

    def __notify(self, title, subtitle, message='', _id=''):
        cmd = ['terminal-notifier', '-title', title, '-subtitle', subtitle, '-message', message]
        try:
            # пытаемся найти иконку расширения
            icon = next(join(self.icons_dir, x) for x in listdir(self.icons_dir) if x.startswith(self.name.lower()))
            cmd = cmd + ['-appIcon', icon]
        except StopIteration:
            pass
        if _id:
            # идентификатор здесь для замены уведомления о загрузке на то что загрузка окончена, вместо создания двух
            cmd = cmd + ['-group', _id]
        check_output(cmd)

    def __save(self):
        # сохраняем последние ссылки и последнее изменение, если есть
        dump(self.settings, open(self.config_path, 'wb'))

    def parse(self, site, params={}):
        # в site - объект Response из parse.py для удобного парсинга
        site = self.session.get(site, params=params)
        # проверка существования данных о последнем изменении
        if 'last_modified' in self.settings and site.status_code == 304:
            # выходим если на сайте не было изменений
            return
        if 'Last-Modified' in site.headers:
            # записываем данные о последнем изменении из заголовков в настройки (далее запишем в файл конфигурации)
            self.settings.last_modified = site.headers['Last-Modified']
        return site

    def download_torrent(self, tfile, series, episode, number, _id):
        if self.notifier:
            # если есть terminal-notifier, уведомляем о начале загрузки
            self.__notify(series, (episode if episode else number), 'Загрузка начата', _id=_id)
        try:
            # загружаем и не сидируем
            check_output(['aria2c', tfile, '--seed-time=0'])
            # удаляем торрент-файл
            remove(tfile)
            return True
        except CalledProcessError:
            if self.notifier:
                self.__notify(series, 'Torrent', 'Загрузка не удалась', _id=_id)
            return False

    def download(self, episodes, cookies={}):
        # месиво
        # episodes - массив словарей с данными о сериях
        for quality, series, episode, number, link, extension in [(s['quality'], s['series'],
                                                                   s['episode'], '%s эпизод %s сезона' % (
                int(s['episode_number']), int(s['series_number'])
        ),
                s['link'], s['extension']) for s in episodes]:
            # пропускаем исключения
            if any(ex in episode for ex in self.settings.excluding if not ex == ''):
                continue
            # если по качеству проходит, есть в подписках и еще не был загружен
            if (self.settings.quality in quality or self.settings.quality in link) \
                    and series in self.settings.subscriptions \
                    and link not in self.settings.old_links:
                # имя файла на основе названия эпизода, номера и расширения, либо номера и расширения
                file_ = '%s[%s].%s' % (episode, number, extension) if episode else '%s.%s' % (number, extension)
                # имя папки состоит из названия сериала и названия студии озвучания в квадратных скобках
                foldername = '%s[%s]' % (series, self.name)
                # создаем папку если ее нет
                if not isdir(foldername):
                    mkdir(foldername)
                chdir(foldername)
                # создаем случайный id для уведомлений
                if self.notifier:
                    _id = ''.join(
                        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                        for _ in range(5)
                    )
                # если файл - торрент, грузим с торрента
                if extension.lower() == 'torrent':
                    open(file_, 'wb').write(self.session.get(link, cookies=cookies).content)
                    # возвращает False если в процессе загрузки произошла ошибка
                    # а так же уведомляет об этом, если есть terminal-notifier
                    if not self.download_torrent(file_, series, episode, number, _id):
                        return
                else:
                    # если файл - не торрент, загружаем его при помощи requests
                    if self.notifier:
                        self.__notify(series, episode if episode else number, 'Загрузка начата', _id=_id)
                    open(file_, 'wb').write(self.session.get(link, cookies=cookies).content)
                if self.notifier:
                    self.__notify(series, episode if episode else number, 'Загрузка закончена', _id=_id)
                chdir('..')
        self.settings.old_links = [s['link'] for s in episodes]
        self.__save()
