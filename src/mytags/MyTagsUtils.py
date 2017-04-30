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

#Attempts to make directory, if one does not exist. Returns false only if requested directory is not usable.
def checkDir(dir):
	return __checkMakeDir(dir)
		
def __checkMakeDir(dir):
	try: 
		os.mkdir(dir)
	except OSError:
		if not os.path.isdir(dir):
			return False
			
	return os.path.isdir(dir)
			
def __writeFile(filename, content):
	if not __checkMakeDir(os.path.dirname(filename)):
		#print "_mt.__writefile(" +filename + ") b/c could not load parent dir"
	
		return False
	try:
		with open(filename, "w") as f:
			f.write(content)
			f.close()
	except IOError as e:
		print "MyTagsUtils.__writeFile("+filename+" IOError: "
		print e
		return False
	return True

def __generateJSON(tags):
	content = '{"tags":['
	firstTag = True
	for t in tags:
		if not firstTag:
			content +=','
		else: # @first Tag, allow for next tag to have comma...
			firstTag = False
		content += '{"title":"' + t + '","type":"sidecar"}'
		
	content += '],"appName":"MyTags"}'
	return content

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
			except ValueError as e:
				#print "getTags ERROR for file ("+filename+") caught pyjq value error using data: \n" + data + "\n"
				#print e
				tags = []
			
			#print("Tags: " + " ".join(tags))
			myfile.close() 
	else:
		pass#print "\n\n\nGettags(" +filename +") could not load metafile."
	#print "\ngetTags("+filename+"): \n" + "|".join(tags) + "<end tags>\n"
	return tags
	
##
# addTags: adds tags to files
#		@input:
#			-filename
#			-tags - list of tags. Cannot contain invalid characters (see isValidTag() function above)
# 		@result: all of the tags are added to the given file's  .json metafile. 
#			The contents of that metafile, if it already exists, will be overwritten, but whatever tags were
#			already in it will be retained (though, perhaps, in slightly reformatted JSON code, as another program
#			like TagSpaces may have created the original). Thus, after this function call, subsequent calls to "getTags" 
#			for the given filename would contain all of its previous tags, plus any new ones passed to addTags.
#			Any tags pre-existing in the .json file not be duplicated by subsequent calls to addTags():
#			each tag is unique, and stored exactly once.
#		@returns: (success, failedTag), where success(boolean) is true if operation succeeded; false o/w.
#				if success == false, failedTag contains first invalid tag which caused the failure; or None if it failed because of failed file write error
#				if success == true, failedFiles is empty.
##
def addTags(filename, tags):	
	metafile = getMetaFileName(filename)
	
	for t in tags:
		if not isValidTag(t):
			return (False, t)
	
			
	# Should we check to see if file exists before doing anything else? If so, uncomment the next two lines:
	# If not os.path.isfile(f):
	#	failedFiles.append(f)
			
	combinedTags = set(getTags(filename)) | set(tags)
	#combinedTags.add("asdfaf#kadf")
	content = __generateJSON(combinedTags)
		
	if not write(metafile, content):
		return (False, None)
	
	return (True, None)
			#jq -R '{"title":.,"type":"sidecar"}'  | jq -s -c 'unique|{"tags":.,"appName":"jq-jtags"}'

def addTagsBulk(filenames, tags):
	failedFiles = []
	for f in filenames:
		(success, failedTags) = addTags(f, tags)
		if not success:
			failedFiles.insert(0, f)
	
	return (not failedFiles, failedFiles)
		

def removeAllTags(filename):
	## Create bare json file with  empty dictionary "appName":"MyTags"
	# consider another option: just delete the metafile!
	return write(getMetaFileName(filename), __generateJSON([]))
	
def removeSomeTags(filename, removeTags):
	# Attempts to remove the given tags from the metafile of the given file. 
	# Returns: True if file exists and it no longer as any of the tags from 'removeTags' in its metafile (if metafile exists).
	# 		   False otherwise.
	# NB my coding choice: do we ensure "atomic" operation in which we open read/write, parse tags, and the write with modified output?
	#               this would re-write to the file even if we don't need to, thus updating the time-stamp as if the tags changed, even if they didn't
	#               On the other hand, if we first open in read-only mode, then check for tags and write only if tags changed, there is the possibility
	#				that one or the file will change between reading and writing. Thus, always opening in R/W mode seems best, thus always writing to file.
	#
	
	#print "Removesometags("+filename+", ["+",".join(removeTags)+"])"
	if not os.path.exists(filename):
		print "WHOA! removeSomeTags(" + filename + ") could not find the file!"
		return False
		
	tags = set()
	metafile = getMetaFileName(filename)
	#print "removeSomeTags("+filename+")...\n"
	try:
		if (os.path.isfile(metafile)):
			with open(metafile, 'r+') as myfile:
				data=myfile.read().replace('\n', '').decode("utf-8-sig")
				#print "\nData :\n" + data +"\n<\enddata>"
				try:
					json.loads(data)
					tags = set(pyjq.all(data +  '| .tags[] | .title'))
				except ValueError as e:
					#print "\n\n\n\nremoveSomeTags("+filename+") " + " with data: " + data 
					#print "     threw pyjq error: "
					#print e
					tags = set()
				
				
				for t in removeTags:
					#print "removing " + t + " from set ([" + ",".join(tags) +"])"
					tags.discard(t)
					#print "now have: ([" + ",".join(tags) +"])"
				
				output = __generateJSON(tags)	
				
				myfile.seek(0)
				myfile.truncate()
				myfile.write(output)
				#print "Wrote to :" + metafile  + " : " + __generateJSON(tags)
				myfile.close()	
			myfile.closed	
	except IOError as e:
		print "WHOA! removeSomeTags(" + filename + ") threw exception:"
		print e
		return False
	#print os.path.isfile(filename)
	#print "End of RemovesomeTags(" +filename+")...closed. Here's getTags():" + "|".join(getTags(filename))
	return True
	
	
	
def getMetaFileName(filename):
	(parent, base) = os.path.split(filename.rstrip('/'))
	
	return parent + "/.ts/" + base + ".json"

''' updateTags: removes all tags from, and then add the input tags
	return (success, tag): success == true if all went well; false otherwise, and "tag" is set to first invalid tag if that was the reason for failure
'''
def replaceTags(filename, tags):
	metafile = getMetaFileName(filename)
	
	for t in tags:
		if not isValidTag(t):
			return (False, t)
		
	# Should we check to see if file exists before doing anything else? If so, uncomment the next two lines:
	# If not os.path.isfile(f):
	#	failedFiles.append(f)
			
	content = __generateJSON(tags)
		
	if not write(metafile, content):
		return (False, None)
	
	return (True, None)	


	
