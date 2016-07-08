from os import chdir, environ, system, mkdir, listdir
from os.path import join, isdir, abspath, dirname, split
from shutil import move

system('/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"')
system('brew install python3 terminal-notifier aria2')
system('pip3 install beautifulsoup4 requests')


cur = dirname(abspath(__file__))
chdir(cur)

home = environ['HOME']

sd_root = join(home, '.NB-series-downloader')

if not isdir(sd_root):
	mkdir(sd_root)

la = join(home, 'Library', 'LaunchAgents')

if not isdir(la):
	mkdir(la)

plist_path = join(la, 'series_downloader.plist')

plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Disabled</key>
	<false/>
	<key>EnvironmentVariables</key>
	<dict>
		<key>PATH</key>
		<string>/usr/local/bin</string>
	</dict>
	<key>KeepAlive</key>
	<dict>
		<key>SuccessfulExit</key>
		<false/>
	</dict>
	<key>Label</key>
	<string>series_downloader</string>
	<key>ProgramArguments</key>
	<array>
		<string>/usr/local/bin/python3</string>
		<string>{0}/.series-downloader/main.py</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
	<key>StartInterval</key>
	<integer>900</integer>
	<key>WorkingDirectory</key>
	<string>{0}/.series-downloader</string>
</dict>
</plist>""".format(home)

open(plist_path, 'wt').write(plist)

system('launchctl load "%s"'%plist_path)

for i in [join(cur, x) for x in listdir('.') if not x.startswith('.') and not x=='installer.py' and not x=='__pycache__']:
	print('%s => %s'%(i, join(sd_root, split(i)[1])))
	move(i, sd_root)
move(cur, join(home, '.Trash'))