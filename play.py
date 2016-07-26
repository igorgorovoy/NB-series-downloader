#!/usr/bin/env python3
from subprocess import call
from sys import argv as args

def alfred_play(series):
	command = """tell application "Alfred 3" to run trigger "play" in workflow "com.fantomnotabene.nbseriesplayer" with argument "%s"
	"""%series
	call(['osascript', '-e', command])
	
alfred_play(args[1])