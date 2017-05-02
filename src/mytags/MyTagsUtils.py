#!/usr/bin/python
import os.path
import fileinput
import pyjq
import sys
import json
import filelock
import shutil
import portalocker

#invalid character for tags, (loosely) borrowed from TagSpaces requirements, but allowing for spaces and underscores:
invalidTagChars = "\"',:/\\|<>	"

def trimPath(filename):
	return filename.rstrip('/\\')

def getMetaDir(filename):
	return os.path.join(os.path.dirname(trimPath(filename)), '.ts')
	
def getMetaFileName(filePath):
	filePath = trimPath(filePath)
	return os.path.join(getMetaDir(filePath), os.path.basename(filePath) + ".json")


def getParentFile(metafile):
	(metafolder, json) = os.path.split(metafile.rstrip('/\\'))
	#print "Meta folder after split: " + metafolder
	#print "Json file after split: "+ json
	#print " New path will be: " + metafolder[:-4] + "/" + json[:-5]
	#print "	Metafolder: " +metafolder
	#print "	metafolder[:-4]"  + metafolder[:-4]
	filePath = ''
	
	(parent, ts) = os.path.split(metafolder)
	
	if ts == ".ts" and json.endswith(".json"):
		filePath = os.path.join(parent, json[:-5])
	
	#print "new Filepath IS: " + filePath
	return filePath

#Public wrapper for private __writeFile method
def write(filename, content):
	return __writeFile(filename, content)
	
#Attempts to make directory, if one does not exist. Returns false only if requested directory is not usable.
def checkDir(dir):
	return __checkMakeDir(dir)


def getLockFileName(filename):
	filename = trimPath(filename)
	return os.path.join(getMetaDir(filename), os.path.basename(filename) + ".lock")


## A simple MyTags-specific lock on handling file operations for given file.
## Creates a lockfile in the metafolder of the file's parent named <filename>.lock
## This can be subsequently used with "with" statement block, or manually by using acquire() and release()
## "filename" should only be the full pathname of the main file, NOT the (.json) metafile in the metafolder.
def getLockFile(filename):
	filename = trimPath(filename)
	lock = None
	
	if __checkMakeDir(getMetaDir(filename)):
		lock = filelock.FileLock(getLockFileName(filename))
	
	#lock.filename = filename
	return lock

def __checkMakeDir(dir):
	try: 
		os.makedirs(dir)
	except OSError as e:
		#print "checkDir failed for " +dir+ ": " +str(e)
		pass	
	return os.path.isdir(dir)


def __readFile(filename):
	content = ''
	try:
		with portalocker.Lock(filename, mode="r", flags=1) as myfile:
			content = myfile.read()
	except (IOError, portalocker.exceptions.BaseLockException)  as e:
		print e
		pass
	return content
# Utility function that writes to a file. Makes the parent directory if it does not exist.
# Returns true if all went well. Returns false if could not access parent directortyor if there was an IOError. Print error to console.	
# Does not check or use the getLockFile() method, since __writeFile may be used for any file, including the .json files. getLockFile()
# should be used by the code which calls __writeFile
def __writeFile(filename, content):
	if __checkMakeDir(os.path.dirname(filename)):
		try:
			with portalocker.Lock(filename, "w") as f:
				f.write(content)
		except (IOError, portalocker.exceptions.BaseLockException) as e:
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

def __getTagsFromData(data, raw=True):
	if (raw):
		data=data.replace('\n', '').decode("utf-8-sig")
	
	tags = []
	try:
		json.loads(data)
		tags = pyjq.all(data +  '| .tags[] | .title')  
	except ValueError as e:
		pass#print "getTags ERROR for file ("+filename+") caught pyjq value error using data: \n" + data + "\n"
		#print e
	return tags
	
def getTags(filename):
	tags = []
	metafile = getMetaFileName(filename)
	
	lockFile = getLockFile(filename)
	if (lockFile):
		lockFile.timeout = 5
	
		with lockFile: #lock for exclusive use of file:
			tags = __getTagsFromData(__readFile(metafile))

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
	#TODO: check for avoid blocking scenario instead of "with lock" statement?
	metafile = getMetaFileName(filename)
	
	for t in tags:
		if not isValidTag(t):
			return (False, t)

	lockFile = getLockFile(filename)
	
	if lockFile: #found file, ready to try and lock:
		with lockFile: #got lock
			try:
				mode = "r+"
				if not os.path.exists(metafile):
					mode = "a+"
				with portalocker.Lock(metafile, mode) as mFile:
					mFile.seek(0)
					combinedTags = set(__getTagsFromData(mFile.read())) | set(tags)
					content = __generateJSON(combinedTags)
					mFile.seek(0)
					mFile.truncate()
					mFile.write(content)
					mFile.seek(0)
				#	print "addTAgs wrote content to " + metafile + ", new content is: " + mFile.read()
			except portalocker.LockException as e:
				print e
				return (False, None)
	else: # main file didn't exist
		#print "addTags did nothing, cause file didn't exist"
		return (False, None)
	
	#print "Successfully completed addTags()"
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
	result = False
	lockFile = getLockFile(filename);
	
	with lockFile:
		result = __writeFile(getMetaFileName(filename), __generateJSON([]))
	return result
	
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
	tags = set()
	metafile = getMetaFileName(filename)
	lock = getLockFile(filename)
	if (lock):
		with lock:
			if not os.path.exists(filename):
				print "WHOA! removeSomeTags(" + filename + ") could not find the file!"
				return False

			#print "removeSomeTags("+filename+")...\n"
			try:
				if (os.path.isfile(metafile)):
					with portalocker.Lock(metafile, 'r+') as myfile:
						#print "\nData :\n" + data +"\n<\enddata>"
						tags = set(__getTagsFromData(myfile.read()))
																		
						for t in removeTags:
							#print "removing " + t + " from set ([" + ",".join(tags) +"])"
							tags.discard(t)
							#print "now have: ([" + ",".join(tags) +"])"
						output = __generateJSON(tags)	
						
						myfile.seek(0)
						myfile.truncate()
						myfile.write(output)
						#print "Wrote to :" + metafile  + " : " + __generateJSON(tags)
			except IOError as e:
				print "WHOA! removeSomeTags(" + filename + ") threw exception:"
				print e
				return False
			#print os.path.isfile(filename)
			#print "End of RemovesomeTags(" +filename+")...closed. Here's getTags():" + "|".join(getTags(filename))
	return True

	
''' updateTags: removes all tags from, and then add the input tags
	return (success, tag): success == true if all went well; false if there were invalid tag, the first of which is also returned
	Throws Exception if lock or IO error occured.
'''
def replaceTags(filename, tags):
	for t in tags:
		if not isValidTag(t):
			return (False, t)
			
	content = __generateJSON(tags)
	success = False
	lockFile = getLockFile(filename);

	with lockFile:
		metafile = getMetaFileName(filename)		
		success = __writeFile(metafile, content)
		
	return (success, None)	

# Move a file, and its sidecar file, to the destination. 
# Input:	srcFilePath - the full path and filename of the file to move.
#			destFilePath - the full path and filename of the new location for the file
#			safe - If true (default), will not overwrite the destFilePath if its exist; 
#				   in such a case does nothing and returns False.
# Return:	True if file moved successfuly. This means the srcFilePath no longer exists, but the same file is now at destFilePath. 
#		    Its sidecar file would now be in the .ts directory of its new parent directory, renamed to match the new filename.
# False:	False if it did not but did not throw error. 
# Errors:   Any Exceptions (e.g., IOError) will be raised/passed to the calling block, and not handled/trapped here.
def moveFile(src, dest, safe=True):
	#print "inside moveFile(" +src +"," +dest
	src = trimPath(src)
	dest = trimPath(dest)
	srcMeta = getMetaFileName(src)
	destMeta = getMetaFileName(dest)
	
	success = True
	reason = ''
	
	if (not os.path.exists(src)):
		reason = "Source does not exist"
		success = False
	elif (not os.path.exists(dest)): # dest does not yet exist; much check parent:
		#print "\nDest does NOT exist!!! " + dest
		success = checkDir(os.path.dirname(dest))
		if (not success):
			reason = "Could not access parent"
	elif (os.path.isfile(dest) and (safe or os.path.isdir(src))): #
		if (os.path.exists(dest)):
			pass #print "The following dest exists: " +dest
		reason = "Cannot move src["+src+"] to existing dest file ["+dest+"]: either safe mode is on, or src is dir!"
		success = False
	elif (os.path.isdir(dest)): # src moved to be child of dest.
		if not checkDir(dest):
			success = False
			reason = "Cannot access dest/parent dir"
		else: #move dest to explicit child/sub-folder
			dest = os.path.join(dest, os.path.basename(src))
			destMeta = getMetaFileName(dest)
		#	print "changing dest to child; now it is: " + dest
			if (os.path.exists(dest)): #dest actually exists!
				if (os.path.isdir(src)):#dest already is a sub-dir
					success = False
					reason = "sub-directory by this name already exists; cannot move src to it"
				elif safe: #file by this name already exists, but safe mode is on:
					success = False
					reason = "trying to move into dest folder, but file by this name alreadt exists"
	if success:			
		lock1 = getLockFile(src)
		with lock1:
			lock2 = getLockFile(dest)
			with lock2:
				try:
					if os.path.isdir(src):# working with a dir; not using file locks:
						shutil.move(src, dest)
						if (os.path.exists(srcMeta) and checkDir(getMetaDir(dest))):
							os.rename(srcMeta, destMeta)
					else: #working with files; using file-locks:
						with portalocker.Lock(dest, "w") as d:
							with portalocker.Lock(src, "r") as s:
							#print "Got all the locks we need! Trying to rename..."
								shutil.move(src, dest)
								if (os.path.exists(srcMeta) and checkDir(getMetaDir(dest))):
									os.rename(srcMeta, destMeta)
								
				except  OSError as e:
								print "\nCaught error in movefile() function:\n"
								#print e
								reason = "caught error in renaming: "
								reason += str(e)
								success = False
		
	#print "moving file to "+  dest + " returning " + str(success and os.path.exists(dest)) 
	#if (reason):
		#print " because: " +reason
	return dest if success else ''

# Rename a file, in its parent directory. Will not overwrite existing files, but will raise Exception if src already exists.
# Input:	srcFilePath - the full path and filename of the file to move.
#			newname - the new *name* of the file, not including its path or parent. 
# Return:	True if file copied successfuly
# False:	False if it did not but did not throw error. 
# Errors:   Any Exceptions (e.g., IOError) will be raised/passed to the calling block, and not handled/trapped here.
def renameFile(srcFilePath, newname):
	return moveFile(srcFilePath, os.path.join(os.path.dirname(srcFilePath), newname))
	
# Copies a file, and its sidecar file (if it exists), to the destination. 
# Input:	srcFilePath - the full path and filename of the file to move.
#			destFilePath - either the full path of the directory to copy the file, or the full path of the new filename.
#			safe - If true (default), will not overwrite the destFilePath if its exist; 
#				   in such a case does nothing and returns False.
# Return:	True if file copied successfuly
# False:	False if it did not but did not throw error. 
# Errors:   Any Exceptions (e.g., IOError) will be raised/passed to the calling block, and not handled/trapped here.
def copyFile(srcFilePath, destFilePath, safe=True):
	
	srcFilePath = trimPath(srcFilePath)
	destFilePath = trimPath(destFilePath)
	
	if (srcFilePath == destFilePath):
		return False
		
	lock = getLockFile(srcFilePath)
	with lock:
		lock2 = getLockFile(destFilePath)

		with lock2:		
			if (os.path.isdir(destFilePath)):
				destFilePath = os.path.join(os.path.dirname(destFilePath), os.path.basename(srcFilePath))
				
			if not safe or not os.path.exists(destFilePath):
				
				shutil.copy(srcFilePath, destFilePath)
				metafile = getMetaFileName(srcFilePath)
				if (os.path.exists(metafile)):
					if (checkDir(getMetaDir(destFilePath))):
						#print "copying  " +metafile+ " to " + getMetaFileName(destFilePath)
						shutil.copy(metafile, getMetaFileName(destFilePath))
						return os.path.exists(getMetaFileName(destFilePath))
					else:
						print "Could not copy " +metafile + "to" +getMetaFileName(destFilePath)
						return False
				else:
					return os.path.exists(destFilePath)
			else:
				return False

def deleteFile(filename):
	lockFile = getLockFile(filename)
	with lockFile:
		os.remove(filename);
		os.remove(getMetaFileName(filename))	
	return not os.path.exists(filename)

# Deletes the given file's sidecar file. Returns True if the given file no longer has a sidecar file.
# Returns False is sidecar file exists and it could not be removed. 
def deleteMetaFile(filename):
	metafile = getMetaFileName(filename)
	lockFile = getLockFile(filename)
	with lockFile:
		if (os.path.exists(metafile)):
			os.remove(metafile)
	return not os.path.exists(metafile)

# Returns list of .JSON metafiles (not parent files!) in the .ts folder of given "directory" that have no corresponding file in "directory'
def findOrphanMetaFiles(directory):
	return []
	
	
