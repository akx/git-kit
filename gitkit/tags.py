import click
import datetime
import itertools
from .util import run, yorn

def reltag_list():
	tags = run([
		"git",
		"tag",
		"-l",
	]).splitlines()
	return sorted([tag for tag in tags if tag.startswith("rel/")])

def reltag():
	""" Create an annotated release tag. """
	now = datetime.datetime.now()
	tags = reltag_list()
	for rno in itertools.count():
		tag = "rel/%s.%d" % (now.strftime("%Y-%m-%d"), rno)
		if tag not in tags:
			break
	if yorn("Will create tag %s. Okay?" % tag):
		run([
			"git",
			"tag",
			"-a",
			"-m",
			datetime.datetime.now().isoformat(),
			tag
		])
		print "Tag created."
	else:
		print "No tag was created."

def install(cli):
	cli.command()(reltag)