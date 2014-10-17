import click
import datetime
import itertools
from .util import run, yorn, get_lines

def reltag_list():
	tags = get_lines([
		"git",
		"tag",
		"-l",
	])
	return sorted([tag for tag in tags if tag.startswith("rel/")])

def reltag():
	""" Create an annotated release tag. """
	now = datetime.datetime.now()
	tags = reltag_list()
	todays_prefix = "rel/%s." % now.strftime("%Y-%m-%d")
	todays_tags = [tag for tag in tags if tag.startswith(todays_prefix)]
	try:
		highest_rel = max(int(tag.replace(todays_prefix, "")) for tag in todays_tags)
	except ValueError:
		highest_rel = -1

	tag = "%s%d" % (todays_prefix, highest_rel + 1)

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
