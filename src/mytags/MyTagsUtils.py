#!/usr/bin/python
import os.path
import fileinput
import pyjq
import sys
import json

#invalid character for tags, (loosely) borrowed from TagSpaces requirements, but allowing for spaces and underscores:
invalidTagChars = "\"',:/\\|<>	"

def write(filename, content):
	return __writeFile(filename, content)

def __writeFile(filename, content):
	try: 
		os.makedirs(os.path.dirname(filename))
	except OSError:
		if not os.path.isdir(os.path.dirname(filename)):
			return False
	try:
		with open(filename, "w") as f:
			f.write(content)
			f.close()
	except:
		return False
	return True



def isValidTag(tag):
	#no leading or trailing whitespace!
	if len(tag.strip()) != len(tag):
		return 0
		
	for c in invalidTagChars:
		if c in tag: 
			return 0
	return 1

	
def getTags(filename):
	
	tags = []
	metafile = getMetaFileName(filename)
	
	#print("getTags(" + filename + "), for " + metafile+ ":\n") 
	if (os.path.isfile(metafile)):
		with open(metafile, 'r') as myfile:
			data=myfile.read().replace('\n', '').decode("utf-8-sig")
			#tags = jq.jq(".").transform(data)
			#print "data: " +data
			try:
				json.loads(data)
				tags = pyjq.all(data +  '| .tags[] | .title')  
			except:
				tags = []
			
			#print("Tags: " + " ".join(tags))
			myfile.close() 
	return tags
	
##
# addTags: adds tags to files
#		@input:
#			-filenames - list of filenames
#			-tags - list of tags. Cannot contain invalid characters (see isValidTag() function above)
# 		@result: all of the tags are added to each file in filenames, in their respective .json metafile. 
#			The contents of that metafile, if it already exists, will be overwritten, but whatever tags were
#			already in it will be retained (though, perhaps, in slightly reformatted JSON code, as another program
#			like TagSpaces may have created the original). Thus, after this function call, subsequent calls to "getTags" 
#			for the given filename would contain all of its previous tags, plus any new ones passed to addTags.
#			Any tags pre-existing in the .json file not be duplicated by subsequent calls to addTags():
#			each tag is unique, and stored exactly once.
#		@returns: (success, failedFiles), where success(boolean) is true if operation succeeded; false o/w.
#				if success == false, failedFiles contains list of filenames for which the operation failed, or None if it failed because of an invalid tag-name.
#				if success == true, failedFiles is empty.
##
def addTags(filenames, tags):	
	
	for t in tags:
		if not isValidTag(t):
			return (False, [])
	
	failedFiles = []
	
	for f in filenames:
		
		# Should we check to see if file exists before doing anything else? If so, uncomment the next two lines:
		# If not os.path.isfile(f):
		#	failedFiles.append(f)
			
		combinedTags = set(getTags(f)) | set(tags)
		content = ""
		for t in combinedTags:
			if not content:
				content += '{"tags":[' 
			else:
				content += ', '
				
			content +='{"title":"' + t + '","type":"sidecar"}'
		content += '],"appName":"MyTags"}'
		
		if not __writeFile(getMetaFileName(f), content):
			failedFiles.append(f)
	
	return (len(failedFiles) == 0, failedFiles)
			#jq -R '{"title":.,"type":"sidecar"}'  | jq -s -c 'unique|{"tags":.,"appName":"jq-jtags"}'
		
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


	
