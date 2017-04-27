#!/usr/bin/python
import os.path
import fileinput
import pyjq
import sys

def getTags(filename):
	tags = []
	metafile = getMetaFileName(filename)
	
	#print("getTags(" + filename + "), for " + metafile+ ":\n") 
	if (os.path.isfile(metafile)):
		with open(metafile, 'r') as myfile:
			data=myfile.read().replace('\n', '').decode("utf-8-sig")
			#tags = jq.jq(".").transform(data)
			#print "data: " +data
			
			tags = pyjq.all(data + "| .tags[] | .title")  
			#print("Tags: " +" ".join(tags))
			myfile.close() 
	return tags
	
def addTags(filename):	
	return False

def removeAllTags(filename):
	return False
	
def removeSomeTags(filename, tags):
	return ()
	
def getMetaFileName(filename):
	(parent, base) = os.path.split(filename.rstrip('/'))
	
	return parent + "/.ts/" + base + ".json"

''' updateTags: removes all tags from, and then add the input tags
'''

def updateTags(filename, tags):
	return False


	
