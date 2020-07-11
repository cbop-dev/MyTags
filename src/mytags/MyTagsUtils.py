#!/usr/bin/python
import os.path
import os
import fileinput
import pyjq
import sys
import json
import filelock
import shutil
import portalocker
import argparse

#invalid character for tags, (loosely) borrowed from TagSpaces requirements, but allowing for underscores:
invalidTagChars = " \"',:/\\|<>	"

def trimPath(filename):
	return filename.rstrip('/\\')

def getRealPath(filepath):
	if (os.path.islink(filepath)):
		filepath = os.path.realpath(filepath)
	return filepath
	
def getMetaDir(filename):
	return os.path.join(os.path.dirname(trimPath(filename)), '.ts')
	
def getMetaFileName(filePath):
	filePath = getRealPath(trimPath(filePath))
	return os.path.join(getMetaDir(filePath), os.path.basename(filePath) + ".json")

def getParentFile(metafile):
	metafile = getRealPath(trimPath(metafile))
	
	(metafolder, json) = os.path.split(metafile)
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
	return __writeFile(getRealPath(filename), content)
	
#Attempts to make directory, if one does not exist. Returns false only if requested directory is not usable.
def checkDir(dir):
	return __checkMakeDir(dir)


def getLockFileName(filename):
	filename = getRealPath(trimPath(filename))
	return os.path.join(getMetaDir(filename), os.path.basename(filename) + ".lock")


## A simple MyTags-specific lock on handling file operations for given file.
## Creates a lockfile in the metafolder of the file's parent named <filename>.lock
## This can be subsequently used with "with" statement block, or manually by using acquire() and release()
## "filename" should only be the full pathname of the main file, NOT the (.json) metafile in the metafolder.
def getLockFile(filename):
	filename = getRealPath(trimPath(filename))
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


def __readFile(filename, uselock=True):
	filename = getRealPath(filename)
	content = ''
	try:
		if (uselock):
			with portalocker.Lock(filename, mode="r", flags=1) as myfile:
				content = myfile.read()
		else:
			with open(filename) as myfile:
				content = myfile.read()
				
	except (IOError, portalocker.exceptions.BaseLockException)  as e:
		print e
		pass
	return content
	
# Utility function that writes to a file. Makes the parent directory if it does not exist.
# Returns true if all went well. Returns false if could not access parent directorty or if there was an IOError. Print error to console.	
# Does not check or use the getLockFile() method, since __writeFile may be used for any file, including the .json files. getLockFile()
# should be used by the code which calls __writeFile
def __writeFile(filename, content):
	filename = getRealPath(filename)
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
		content += '{"title":"' + t.lower() + '","type":"sidecar"}'
		
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

#returns a tuple of two lists: (validtags, invalidtags)
def checkTags(tags):
	validTags = []
	invalidTags = []
	for t in tags:
		if (isValidTag(t)):
			validTags.insert(0,t)
		else:
			invalidTags.insert(0,t)
	return (validTags, invalidTags)

	
def __getTagsFromData(data, raw=True):
	if (raw):
		data=data.replace('\n', '').decode("utf-8-sig")
	
	tags = []
	try:
		json.loads(data)
		rawtags = pyjq.all(data +  '| .tags[] | .title')  
		for t in rawtags:
			tags.append(t.lower())
			
	except ValueError as e:
		pass#print "getTags ERROR for file ("+filename+") caught pyjq value error using data: \n" + data + "\n"
		#print e
	return tags
	
def getTags(filename, uselock=True):
	filename = getRealPath(filename)
	
	tags = []
	if (os.path.islink(filename)):
		filename = os.path.realpath(filename)
		
	metafile = getMetaFileName(filename)
	
	if (uselock):
		lockFile = getLockFile(filename)
		if (lockFile and os.path.isfile(metafile)):
			lockFile.timeout = 5
		
			with lockFile: #lock for exclusive use of file:
				tags = __getTagsFromData(__readFile(metafile))
	elif os.path.exists(metafile):
		tags = __getTagsFromData(__readFile(metafile, uselock))

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
	filename = getRealPath(filename)
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
			

def addTagsBulk(filenames, tags):
	failedFiles = []
	for f in filenames:
		f = getRealPath(f)
		(success, failedTags) = addTags(f, tags)
		if not success:
			failedFiles.insert(0, f)
	
	return (not failedFiles, failedFiles)
		

def removeAllTags(filename):
	filename = getRealPath(filename)
	## Create bare json file with  empty dictionary "appName":"MyTags"
	# consider another option: just delete the metafile!
	result = False
	lockFile = getLockFile(filename);
	
	with lockFile:
		result = __writeFile(getMetaFileName(filename), __generateJSON([]))
	return result
	
def removeSomeTags(filename, removeTags):
	filename = getRealPath(filename)
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
	filename = getRealPath(filename)
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

''' Checks src, dest, based on whether they exist, and whether they are files or dirs. 
	Returns  a tuple (success, dest, reason): success is True if src and dest 
	are a valid pair for copying/moving with the given safe mode (safe=True means no files
	can be overwritten.  Dest is the fullPath of the (potentially updated) destination.
	It is an empty string ('') if the files cannot be copied/moved, and, 
	if this is the case, 'reason' contains a message about why this is which can be 
	used for loggin.
'''
def __checkSrcDest(src,dest, safe=True, hardLink=False):
	src = getRealPath(src)
	
	success = True
	reason = ''
	src = trimPath(src)
	dest = trimPath(dest)
	if (src == dest):
		success = False
		reason = "Src and Dest are the same!"
	elif (not os.path.exists(src)):
		reason = "Source does not exist"
		success = False
	elif (not os.path.exists(dest)): # dest does not yet exist; much check parent:
		#print "\nDest does NOT exist!!! " + dest
		success = checkDir(os.path.dirname(dest))
		if (not success):
			reason = "Could not access parent"
	elif (os.path.isfile(dest) and (safe or hardLink or os.path.isdir(src))): #
		if (os.path.exists(dest)):
			pass #print "The following dest exists: " +dest
		reason = "Cannot move src-file["+src+"] to existing dest file ["+dest+"]: either safe mode is on, or src is dir!"
		success = False
	elif (os.path.isdir(dest)): # src moved to be child of dest.
		if not checkDir(dest):
			success = False
			reason = "Cannot access dest/parent dir"
		else: #move dest to explicit child/sub-folder
			dest = os.path.join(dest, os.path.basename(src))
		#	print "changing dest to child; now it is: " + dest
			if (os.path.exists(dest)): #dest actually exists!
				if (os.path.isdir(src)):#dest already is a sub-dir
					success = False
					reason = "sub-directory by this name already exists; cannot move src to it"
				elif safe: #file by this name already exists, but safe mode is on:
					success = False
					reason = "trying to move into dest folder, but file by this name alreadt exists"
	#else:
	#	print("checkSrcDest() found no errors. Returning success...")
	return (success, dest, reason)

# Move a file, and its sidecar file, to the destination. 
# Input:	srcFilePath - the full path and filename of the file to move.
#			destFilePath - the full path and filename of the new location for the file
#			safe - If true (default), will not overwrite the destFilePath if its exist; 
#				   in such a case does nothing and returns False.
# Return:	True if file moved successfuly. This means the srcFilePath no longer exists, but the same file is now at destFilePath. 
#		    Its sidecar file would now be in the .ts directory of its new parent directory, renamed to match the new filename.
# 			False if it did not but did not throw error. OSError Exception will be caught and not re-raised. Other exceptions are not caught.
# Errors:   Any Exceptions besides an OSError will be raised/passed to the calling block, and not handled/trapped here.
def moveFile(src, dest, safe=True):
	src = getRealPath(src)
	#print "inside moveFile(" +src +"," +dest
	src = trimPath(src)
	dest = trimPath(dest)
	
	(success, dest, reason) = __checkSrcDest(src, dest, safe)
	
	srcMeta = getMetaFileName(src)
	destMeta = getMetaFileName(dest)
			
	if success:			
		lock1 = getLockFile(src)
		with lock1:
			lock2 = getLockFile(dest)
			with lock2:
				try:
					if os.path.isdir(src):# working with a dir; not using file locks:
						shutil.move(src, dest)
						if (os.path.exists(srcMeta) and checkDir(getMetaDir(dest))):
							shutil.move(srcMeta, destMeta)
					else: #working with files; using file-locks:
						with portalocker.Lock(dest, "w") as d:
							with portalocker.Lock(src, "r") as s:
							#print "Got all the locks we need! Trying to rename..."
								shutil.move(src, dest)
								if (os.path.exists(srcMeta) and checkDir(getMetaDir(dest))):
									shutil.move(srcMeta, destMeta)
								
				except  (OSError, shutil.Error) as e:
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
	srcFilePath = getRealPath(srcFilePath)
	return moveFile(srcFilePath, os.path.join(os.path.dirname(srcFilePath), newname))
	
# Copies a file, and its sidecar file (if it exists), to the destination. 
# Input:	srcFilePath - the full path and filename of the file to move.
#			destFilePath - either the full path of the directory to copy the file, or the full path of the new filename.
#			safe - If true (default), will not overwrite the destFilePath if its exist; 
#				   in such a case does nothing and returns False.
#			hardLink: If true (default: false), function will attempt to create a hardlink at src, instead of copy.
# 				Only matters if src is a file, not a dir. 
# Return:	True if file copied successfuly
# False:	False if it did not but did not throw error. 
# Errors:   Any Exceptions (e.g., IOError) will be raised/passed to the calling block, and not handled/trapped here.
def copyFile(src, dest, safe=True,hardLink=False):
	src = trimPath(getRealPath(src))
	#src = trimPath(src)
	dest = trimPath(dest)
	
	(success, dest, reason) = __checkSrcDest(src, dest, safe, hardLink)
	
	srcMeta = getMetaFileName(src)
	destMeta = getMetaFileName(dest)
	
	if success:			
		lock1 = getLockFile(src)
		with lock1:
			lock2 = getLockFile(dest)
			with lock2:
				try:
					if os.path.isdir(src):# working with a dir, using shutil.copytree() instead of copy()
						shutil.copytree(src, dest)
						if (os.path.exists(srcMeta) and checkDir(getMetaDir(dest))):
							shutil.copy2(srcMeta, destMeta)
					else: #working with files; using file-locks:
						if (hardLink): # hardlink: use os.link(). Must check if dest is dir:
							if( os.path.isdir(dest)): # copying one file into another folder
								originalDest = dest
								dest = os.path.join(dest, os.path.basename(src))
								print("Had to turn dest[" + originalDest + "] folder into full path of filename [" + dest + "]")
								# give dest a filename instead of dir, to avoid hardLink problem.
								if (os.path.exists(dest)):
									print ("Hmmm...new dest already exists!")
							with portalocker.Lock(src, "r") as s: # cannot use portraLocker on dest with os.link()
							#print "Got all the locks we need! Trying to copy..."
								#print ("trying HARDLINK1..." + src + " -> " + dest)
								#if (os.path.exists(dest)):
								#		print "But dest [" + dest + "] already exists! This should not have happened..."
								os.link(src,dest)
								#	print "made HARDLINK1..."
						else: #no hardlink. doing the normal stuff...
							with portalocker.Lock(dest, "w") as d:
								with portalocker.Lock(src, "r") as s:
								#print "Got all the locks we need! Trying to copy..."
									shutil.copy2(src, dest)
						#copy meta files; 
						if (os.path.exists(srcMeta) and checkDir(getMetaDir(dest))):
							if (hardLink): # try making link!
								#print "trying HARDLINK2..."
								os.link(srcMeta, destMeta)
								#print "made HARDLINK2..."
							else:
								shutil.copy2(srcMeta, destMeta)
								
				except  OSError as e:
					reason = "\nCaught error in copyfile() function:\n"
					reason += str(e)
					print reason
					success = False
		
	#print "Copying file to "+  dest + " returning " + str(success and os.path.exists(dest)) 
	#if (reason):
		#print " because: " +reason
	return dest if success else ''

def deleteFile(filename):
	filename = getRealPath(filename)
	lockFile = getLockFile(filename)
	with lockFile:
		os.remove(filename);
		metaF = getMetaFileName(filename)
		if (os.path.exists(metaF)):
			os.remove(metaF)
	return not os.path.exists(filename)

'''
	deleteFolder:
	Deletes a folder. Only works on an empty directory, 
	unless recursive=True, in which case, it removes
	the directory and all of its contents.
	Does not catch any Exceptions, but if none are thrown, 
	returns true if given folder no longer exists, 
	false otherwise.
'''
def deleteFolder(foldername, recursive=False):
	foldername = getRealPath(foldername)
	if (recursive):
		shutil.rmtree(foldername)
	else:
		os.rmdir(foldername)
	success = not os.path.isdir(foldername)
	if (success):
		deleteMetaFile(foldername)
	return success
	
# Deletes the given file's sidecar file. Returns True if the given file no longer has a sidecar file.
# Returns False if sidecar file exists and it could not be removed. 
def deleteMetaFile(filename):
	filename = getRealPath(filename)
	metafile = getMetaFileName(filename)
	lockFile = getLockFile(filename)
	with lockFile:
		if (os.path.exists(metafile)):
			os.remove(metafile)
	return not os.path.exists(metafile)

def cleanMetaFolder(parentdir):
	parentdir = getRealPath(parentdir)
	metadir = getMetaDir(os.path.join(parentdir, "filename"))
	#print "In cleanMetaFolder("+parentdir+"):\n"
	try:
		for f in findOrphanMetaFiles(parentdir):
			parentFile = os.path.join(parentdir,os.path.splitext(os.path.basename(f))[0])
			
			if (not os.path.exists(parentFile)):
				#print "Going to remove " + f
				os.remove(f)
				
			else:
				print "Not going to remove "+ f
		removeUnusedLocks(metadir)
	except (OSError, IOError) as e:
		print "CleanMetaFoldr(" +parentdir+") caught exception: " + str(e)

# Returns list of .JSON metafiles (not parent files!) in the .ts folder of given "directory" that have no corresponding file in "directory'
def findOrphanMetaFiles(directory):
	directory = getRealPath(directory)
	directory = trimPath(directory)
	metadir = getMetaDir(os.path.join(directory, "filename"))
	orphanedMetaFiles = []
	
	if (os.path.isdir(metadir)):
		for f in os.listdir(metadir):
			(root, ext) = os.path.splitext(f)
			parentFile = os.path.join(directory, root)
			if (ext == ".json") and (not os.path.exists(parentFile)): # orphaned metaFile!
				orphanedMetaFiles.insert(0,os.path.join(metadir, f))
				#print "Found orphaned metafile: " + os.path.join(metadir, f)  + "\n"
		
	return orphanedMetaFiles

def removeUnusedLocks(metadir):
	metadir = getRealPath(metadir)
	#print "removeUnusedLocks("+metadir+"):\n"
	if (os.path.isdir(metadir)):
		for f in os.listdir(metadir):
			print "checking " + f 
			(root, ext) = os.path.splitext(f)
			#print "root: " + root + ", ext = " + ext
			if ext == ".lock":
				parentFile = os.path.join(os.path.dirname(metadir), root)
				#print "Checking if parent file " + parentFile + " exists..."
				if (not os.path.exists(parentFile)):
					
					#print "No! About to remove " + os.path.join(metadir, f)
					os.remove(os.path.join(metadir, f))
				else:
					#print "Yes! Not going to remove"
					pass
					
			else:
				pass
				#print "Ext ("+ext+") is not '.lock'"
		
def printTags(tags):
	if (tags):
		print " ".join(tags)
	
def cl_getTags(args):
	printTags(getTags(args.filename, False))
	
def cl_addTags(args):
	addTags(args.filename,args.tags)
	
def cl_removeTags(args):
	removeSomeTags(args.filename, args.tags)
	
def cl_removeAllTags(args):
	removeAllTags(args.filename)

def cl_replaceTags(args):
	replaceTags(args.filename, args.tags)

def commandLine():
	#print sys.argv
	import argparse

	parser = argparse.ArgumentParser(description='Manage file/folder tags in sidecar files (.ts)')
	#parser.add_argument('command', metavar='[command]', type=int, nargs='+', help='an integer for the accumulator')
	subparsers = parser.add_subparsers(help='[command] help')
	parser_tags = subparsers.add_parser('tags', help='tags help')
	parser_tags.add_argument('filename', metavar='Filename', type=str, help='Filename')
	parser_tags.set_defaults(func=cl_getTags)
	#parser_get.add_argument('tag', metavar='tag', type=str, nargs = '+', help='tag')
	
	# add tags command:
	parser_add = subparsers.add_parser('add', help='add help')
	parser_add.add_argument('filename', metavar='Filename', type=str, help='Filename')
	parser_add.add_argument('tags', metavar="tag", type=str, nargs="+", help='Tags')
	parser_add.set_defaults(func=cl_addTags)
	
	#remove tags command:
	parser_remove = subparsers.add_parser('remove', help='remove help')
	parser_remove.add_argument('filename', metavar='Filename', type=str, help='Filename')
	parser_remove.add_argument('tags', metavar="tag", type=str, nargs="+", help='Tags')
	parser_remove.set_defaults(func=cl_removeTags)
	
	#removeALL tags command:
	parser_removeAll = subparsers.add_parser('remove-all', help='remove-all help')
	parser_removeAll.add_argument('filename', metavar='Filename', type=str, help='Filename')
	parser_removeAll.set_defaults(func=cl_removeAllTags)
	
	#replace tags command:
	parser_replace = subparsers.add_parser('replace', help='replace help')
	parser_replace.add_argument('filename', metavar='Filename', type=str, help='Filename')
	parser_replace.add_argument('tags', metavar="tag", type=str, nargs="+", help='Tags')
	parser_replace.set_defaults(func=cl_replaceTags)
	
	args = parser.parse_args()
	args.func(args)
	

if __name__ == "__main__":
	commandLine()
