#!/usr/local/bin/python3
# encoding: utf-8
from os import listdir, chdir
from os.path import dirname, abspath, join

root = dirname(abspath(__file__))
chdir(join(root, 'plugins'))

for p in [x[:-3] for x in listdir('.') if x.endswith('.py')]:
	module = __import__('plugins.' + p)
	_class = getattr(getattr(module, p), p.title())
	_class().start()
