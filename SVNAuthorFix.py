#!/usr/bin/python

import sys
import subprocess
import os
import re

if len(sys.argv) < 2:
	print("Usage: %s REPONAME" % sys.argv[0])
	exit(1)
	
repository = "svn://myRepository/" + sys.argv[1] # Replace with repository URL
svnDictionary = {}

#Use SSOs
def mapAuthor(x):
	return {
		'JG': "Johannes Griesser",
		'JD': "John Doe"
	}.get(x, None)

print("Querying %s..." % repository)
os.system("svn log --xml " + repository + " > " + os.path.expanduser("log.xml"))

from xml.dom.minidom import parse
xml = parse(os.path.expanduser("log.xml"))
entries = xml.getElementsByTagName("logentry")

for e in entries:
	rev = e.getAttribute("revision")
	if e.getElementsByTagName("msg")[0].firstChild:
		msg = e.getElementsByTagName("msg")[0].firstChild.nodeValue
	svnDictionary[rev] = msg
	msg = None

for revision, commitMessage in sorted(svnDictionary.items()):
	#print(u'{0}: {1}'.format(revision, commitMessage))
	initialsMatch = re.search(r'^[A-Z]{2,3}', str(commitMessage))
	if initialsMatch:
		prefixMatch = re.search(r'^[A-Z]{2,3}(\s|-|:|,)*', str(commitMessage))
		# Review prefixes are correctly matched before proceeding with SVN amend!
		#print(prefixMatch.group())
		
		strippedCommitMessage = commitMessage.replace(prefixMatch.group(), '')
		author = mapAuthor(initialsMatch.group())
		
		# Review the stripped commits before proceeding with SVN amend!					
		#print(u'{0}: {1} - {2}'.format(revision, author, strippedCommitMessage))
		
		if author:
			print("svn propset --revprop -r " + revision + " svn:author " + author + " " + repository)
			print("svn propset --revprop -r " + revision + " svn:log \"" + strippedCommitMessage + "\" " + repository)
		else:
			print("Revision r" + revision + ": Cannot map initials " + initialsMatch.group() + " to valid author!")

os.remove(os.path.expanduser("log.xml"))
