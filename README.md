##Сериалокачалка на python3 для macOS с поддержкой расширений

Подробное описание можно найти [на Хабре](https://habrahabr.ru/post/304770/).

Зависимости:

* [python3](https://www.python.org/download/releases/3.0/)
* [terminal-notifier](https://github.com/julienXX/terminal-notifier) опционально
* [aria2c](https://aria2.github.io) для загрузки с торрентов

Все их на Маке можно установить через [homebrew](http://brew.sh).

После его установки, поставить зависимости этого проекта можно командой:

```brew install python3 terminal-notifier aria2```

Python библиотеки:
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), парсинг сайтов
* [requests](http://docs.python-requests.org/en/master/), http-запросы

Установить можно следующим образом:

```pip3 install beautifulsoup4 requests```

В корне проекта есть файл **install.py**, который сделает это все автоматически.

А так же:

* Переместит файлы проекта в *~/.NB-series-downloader*
* Запишет файл автозапуска в *~/Library/LaunchAgents/series_downloader.plist*
* Переместит в корзину себя вместе с папкой клонированного репозитория

В папке плагинов уже имеются четыре расширения:

1. [lostfilm.tv](http://lostfilm.tv)
2. [newstudio.tv](http://newstudio.tv)
3. [baibako.tv](http://baibako.tv)
4. [coldfilm.ru](http://coldfilm.ru)

Для трех из них **нужна авторизация**.

* Lostfilm требует uid и pass из cookies + usess из профиля пользователя на сайте.
* Newstudio требует логин и пароль, которые подставятся в ссылки в rss-ленте для загрузки.
* Baibako требует некий passkey, который можно получить, запросив rss-ленту у них на сайте.

Укажите их в соответствующих файлах перед тем как запускать **install.py**.
