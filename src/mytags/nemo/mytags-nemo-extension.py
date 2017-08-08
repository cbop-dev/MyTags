import os
import urllib
import gi
import sys
from Tkinter import *		   # Importing the Tkinter (tool box) library 
import tkSimpleDialog
import tkMessageBox, tkFileDialog

gi.require_version('Nemo', '3.0')
from gi.repository import GObject, Nemo

###########################################
#### CONFIGURATION:

''' Enable/Disable indexing: '''
indexing = True

''' The "mytags" dir, under "src" in the repo, must be in your python path. 
	Either copy the directory to one already in your $PYTHONPATH env variable (on Linux), or add it below and uncomment the next two lines.
'''
mytagsLibDir = "/path/to/mytags/src"
sys.path.append(mytagsLibDir)

#### END CONFIGURATION
###########################################

import mytags.MyTagsUtils as mt
import mytags.index
import mytags.config as config

if config.indexing:
	myIndexThread = mytags.index.UpdateIndexQueueThread()
	myIndexThread.start()

def updateFiles(files, filesChanged, filesRemoved=[]):
		for f in files:
			f.invalidate_extension_info()
		if (config.indexing and myIndexThread):
			if (filesChanged):
				myIndexThread.queueFilesUpdate(filesChanged)
			if (filesRemoved):
				myIndexThread.queueFilesRemove(filesRemoved)
			
def getFilename(thefile):
	return getCleanFilename(thefile.get_uri()[7:])

def getCleanFilename(filename):
	return urllib.unquote(filename.rstrip('\//'))

def getCleanFilenames(files):
	cleanedFilenames = []
	for thefile in files:
		cleanedFilenames.insert(0,getCleanFilename(getFilename(thefile)))
	return cleanedFilenames

class MyTagsColumnExtension(GObject.GObject, Nemo.ColumnProvider, Nemo.InfoProvider):
	def __init__(self):
		pass
	
	def get_columns(self):
		return Nemo.Column(name="NemoPython::tags_column",
							   attribute="tags",
							   label="Tags",
							   description="File tags"),

	def update_file_info(self, file):
		if file.get_uri_scheme() != 'file':
			return
		
		filename = urllib.unquote(file.get_uri()[7:])
		
		file.add_string_attribute('tags', "|".join(mt.getTags(filename, uselock=False)))
		return Nemo.OperationResult.COMPLETE



class MyTagsMenuProvider(GObject.GObject, Nemo.MenuProvider):


	def simpleDialog(self, title, label, initialvalue=""):
		root = Tk()
		ws = root.winfo_screenwidth() # width of the screen
		hs = root.winfo_screenheight() # height of the screen

		root.geometry('+%d+%d' % (ws/2, hs/2))
		root.update()
		root.withdraw()	
		textInput = tkSimpleDialog.askstring(title, label, parent=root,initialvalue=initialvalue)
		root.destroy()
		return textInput
	
	def __getRootWin(self):
		root = Tk()
		ws = root.winfo_screenwidth() # width of the screen
		hs = root.winfo_screenheight() # height of the screen

		# calculate x and y coordinates for the Tk root window
		#x = (ws/2) - (w/2)
		#y = (hs/2) - (h/2)

		# set the dimensions of the screen 
		# and where it is placed
		#root.geometry('%dx%d+%d+%d' % (w, h, x, y))
		#root.geometry('+20+10')
		root.geometry('+%d+%d' % (ws/2, hs/2))
		root.update()
		return root

	
	def chooseDir(self, title,initialdir=os.getcwd()):
		
		root = self.__getRootWin()
		root.withdraw()
		destDir = tkFileDialog.askdirectory(title=title, mustexist=True, initialdir=initialdir, parent=root)
		root.destroy()
		return destDir
	
	def showinfo(self, title, message):
		root = Tk()
		ws = root.winfo_screenwidth() # width of the screen
		hs = root.winfo_screenheight() # height of the screen
		root.geometry('+%d+%d' % (ws/2, hs/2))
		root.update()
		root.withdraw()	
		result = tkMessageBox.showinfo(title, message, parent=root)
		root.destroy()
		
	
	def simpleConfirm(self, title, message):
		root = Tk()
		ws = root.winfo_screenwidth() # width of the screen
		hs = root.winfo_screenheight() # height of the screen
		root.geometry('+%d+%d' % (ws/2, hs/2))
		root.update()
		root.withdraw()	
		result = tkMessageBox.askyesno(title, message, parent=root)
		root.destroy()
		return result
		
	def warning(self, title, label):
		root = Tk()
		ws = root.winfo_screenwidth() # width of the screen
		hs = root.winfo_screenheight() # height of the screen

		#root.geometry('+20+10')
		root.geometry('+%d+%d' % (ws/2, hs/2))
		root.update()
		root.withdraw()	
		tkMessageBox.showwarning(title, label, parent=root)
		root.destroy()
	
	def menu_erasetags(self, menu, files):
		cleanedFilenames = getCleanFilenames(files)
		failed = []
		if (self.simpleConfirm("Erase Tags", "Remove ALL tags from selected files?")):
			for f in cleanedFilenames:
				if(not mt.removeAllTags(f)):
					failed.insert(0,f)
		successful = []
		
		if (failed):
			self.warning("Erase tags", "Could not erase tags for the following files: " + "\n".join(failed))
			successful = list(set(cleanedFilenames) - set(failed))
		else:
			successful = cleanedFilenames
		
		if (successful):
			updateFiles(files, successful)
	
	def menu_replacetags(self, menu, files):
		cleanedFilenames = getCleanFilenames(files)
			
		tagString = self.simpleDialog("Replace Tags", "All Existing tags will be remove from files. Enter tags to replace them with:")
		tags = ''
		if (tagString):
			tags = [t.strip() for t in tagString.split(",")]
			badTags = mt.checkTags(tags)[1]
					
			if (tags):
				if (badTags):
					self.warning("Replace Tags Failed", "Invalid tags: " + "\n".join(badTags))
				else:
					failed = []
					succeeded = []
					for f in cleanedFilenames:
						if not mt.replaceTags(f, tags):
							failed.insert(0, f)
					
					if failed:
						tkMessageBox.showwarning("Error", "Attempting to rplace tags from the following files failed: \n" + "\n".join(failed))
						succeeded = list(set(cleanedFilenames) - set(failed))
					else:
						succeeded = cleanedFilenames
					
					updateFiles(files, succeeded)
		
	def menu_addtags(self, menu, files):
		cleanedFilenames = getCleanFilenames(files)
		
		tagString = self.simpleDialog("Add Tags", "Enter tags to add (separated by commas):")
				
		result = (False, [])
		
		#tags = tagString.split(",")
		tags = [t.strip() for t in tagString.split(",")]
		badTags = mt.checkTags(tags)[1]
		
		if (tags):
			if (badTags):
				self.warning("Add Tags Failed", "Invalid tags: " + "\n".join(badTags))
			else:
				print "attempting to add [" + "|".join(tags) + "] to " + ";".join(cleanedFilenames)
				result = mt.addTagsBulk(cleanedFilenames, tags)
			
			
				if (not result[0]):
					#failed:
					if (len(result[1]) != len(cleanedFilenames)): #some were updated
						modFiles = set(cleanedFiles) - set(result[1])
						updateFiles(files, modFiles)		
						self.warning("Add Tags Result", "The following files were not modified: " + "\n".join(result[1]))	
					else: #no files were updated due to bad tags
						self.warning("Add Tags Failed", "None of the files could be modified. Did you add a bad tag?")	
				else:
					updateFiles(files, cleanedFilenames)
				
				self.emit_items_updated_signal()
				self.emit("items_updated")
#		Nemo.emit("items_updated")
		
	def menu_deletetags(self, menu, files):
		cleanedFilenames = getCleanFilenames(files)
			
		tagString = self.simpleDialog("Remove Tags", "Enter tags to remove (separated by commas):")
		tags = []
		if (tagString):
			tags = [t.strip() for t in tagString.split(",")]
		
		
		#tkMessageBox.showinfo("Delete Tags", "Deleting tags: " + "|".join(tags), parent=root)
		
		if (tags):
			failed = []
			for f in cleanedFilenames:
				if not mt.removeSomeTags(f, tags):
					failed.insert(0, f)
			
			if failed:
				self.showwarning("Error", "Attempting to remove tags from the following files failed: \n" + "\n".join(failed))
		
		updateFiles(files, list(set(cleanedFilenames) - set(failed)))
	
	def menu_deleteFiles(self, menu, files):
		cleanedFilenames = getCleanFilenames(files)
		failed = []
		if (self.simpleConfirm("Delete Files/Folders?", "Delete these files/folders? (Directories will be recursively deleted!): " + "\n".join(cleanedFilenames))):
			for f in cleanedFilenames:
				if (not os.path.exists(f)):
					failed.insert(0,f)
				elif (os.path.isfile(f) and not mt.deleteFile(f)):
					failed.insert(0,f)
				elif (os.path.isdir(f) and not mt.deleteFolder(f, recursive=True)):
					failed.insert(0,f)
			successful = []
		
			if (failed):
				self.warning("Delete files", "Could not delete the following files: " + "\n".join(failed))
				successful = list(set(cleanedFilenames) - set(failed))
			else:
				successful = cleanedFilenames
			
			if (successful):
				updateFiles([], [], successful)	

	
	def menu_copyFilesFolders(self, menu, files):
 		
		
		cleanedFilenames = getCleanFilenames(files)
		destDir = getCleanFilename(self.chooseDir("Select destination directory:", initialdir=os.path.dirname(getCleanFilename(files[0].get_uri()[7:]))))
		
		failedFiles = []
		print "Trying to copy files to " + destDir + ":\n"
		
		for f in cleanedFilenames:
			
			if (not mt.copyFile(f, destDir)):
				failedFiles.insert(0, f)
		
		

		newFiles = []
		
		if (failedFiles):
			self.warning("Copy results:", "The following files/folders were NOT successfully copied:" + str(failedFiles))
			copiedFiles = list(set(cleanedFilenames) -set(failedFiles))
		else:
			copiedFiles = cleanedFilenames
			self.showinfo("Copy Success", "Successfully copied the following files to " + destDir + ": \n" + "\n--".join(cleanedFilenames))
		
		
		newFiles = []
		for f in copiedFiles:
				newFiles.insert(0,os.path.join(destDir, os.path.basename(f)))
				
		
		if (newFiles):
			updateFiles(files, newFiles)

		
	def menu_moveFilesFolders(self, menu, files):
		destDir = getCleanFilename(self.chooseDir("Select destination directory:", initialdir=os.path.dirname(getCleanFilename(files[0].get_uri()[7:]))))
		
		if (destDir):
			cleanedFilenames = getCleanFilenames(files)
			failedFiles = []
			print "Trying to move files to " + destDir + ":\n"
			
			for f in cleanedFilenames:
				
				if (not mt.moveFile(f, destDir)):
					failedFiles.insert(0, f)
			
			root = self.__getRootWin()
			root.withdraw()
			
			newfiles = []
			removedfiles = []
			
			if (failedFiles):
				tkMessageBox.showwarning("Move results:", "The following files/folders were NOT successfully moved:" + str(failedFiles), parent=root)
				movedFiles = list(set(cleanedFilenames)-set(failedFiles))
				
			else:
				tkMessageBox.showinfo("Move Success", "Successfully moved the following files to " + destDir + ": \n" + "\n--".join(cleanedFilenames), parent=root)
				movedFiles = list(cleanedFilenames)
				
			removedFiles = list(movedFiles)
			newfiles = []
			for n in movedFiles:
				newfiles.insert(0,os.path.join(destDir, os.path.basename(n)))
					
			root.destroy()
			updateFiles(files, newfiles, removedFiles)
			
	def menu_renameFileFolder(self, menu, files):
		root = self.__getRootWin()
		root.withdraw()
		
		if (not len(files) == 1):
			tkMessageBox.showwarning("Rename failed", "Only one file can be selected for renaming", parent=root)
		else:
			
			cleanedFilename = getCleanFilename(files[0].get_uri()[7:])
			newname = os.path.join(os.path.dirname(cleanedFilename), getCleanFilename(self.simpleDialog("Rename", "Enter new filename: ", initialvalue=os.path.basename(cleanedFilename))))
					
			
			print "Trying rename file " + cleanedFilename + " to: " + newname + ":\n"
			
			success =  mt.renameFile(cleanedFilename, newname)
			if(not success):
				tkMessageBox.showwarning("Rename failed", "Cannot rename to: " + newname + "\nPerhaps it already exists?", parent=root)
			else:
				updateFiles(files, [newname], [cleanedFilename])
			
		root.destroy()
	
	def menu_indexFiles(self, menu, files):
		if (config.indexing):
			cleanedFilenames = getCleanFilenames(files)
			
			root = self.__getRootWin()
			root.withdraw()
						
			self.simpleConfirm("Index Files", "(Re)Index the selected files?" + "\n".join(cleanedFilenames))
								
			myIndexThread.queueFilesUpdate(cleanedFilenames)
			root.destroy()
			
	def menu_cleanmeta(self,menu, file):
		confirmed = self.simpleConfirm("Clean Metafolder?", "Check and clean unnecessary files from metafolder?")
		
		if confirmed:
			print "about to call cleanmetafolder"
			mt.cleanMetaFolder(getCleanFilename(getFilename(file)))
		
		
	def get_background_items(self, window, file):
		top_menuitem = Nemo.MenuItem(name='MyTags::bg_menu', 
										 label='MyTags', 
										 tip='',
										 icon='')
		tagsMenu = Nemo.Menu()
		
			
		cleanMetaFolderItem = Nemo.MenuItem(name='MyTags::clean_meta', 
										 label='Clean Metafolder', 
										 tip='',
										 icon='')
		tagsMenu.append_item(cleanMetaFolderItem)
		cleanMetaFolderItem.connect('activate', self.menu_cleanmeta, file)  
		top_menuitem.set_submenu(tagsMenu)

		
		return top_menuitem,
		
	def get_file_items(self, window, files):
		top_menuitem = Nemo.MenuItem(name='MyTags::menu', 
										 label='MyTags', 
										 tip='',
										 icon='')
		tagsMenu = Nemo.Menu()
		tagsSubmenuItem = Nemo.MenuItem(name='MyTags::Tags', 
										 label='Tags', 
										 tip='',
										 icon='')
		tagsSubmenu = Nemo.Menu()
		tagsSubmenuItem.set_submenu(tagsSubmenu)
		
		filesSubmenuItem = Nemo.MenuItem(name='MyTags::files', 
										 label='Files', 
										 tip='',
										 icon='')
		filesSubmenu = Nemo.Menu()
		filesSubmenuItem.set_submenu(filesSubmenu)
		
		tagsMenu.append_item(tagsSubmenuItem)
		tagsMenu.append_item(filesSubmenuItem)
		top_menuitem.set_submenu(tagsMenu)
		
		addTagsMenuItem = Nemo.MenuItem(name='MyTags::add', 
										 label='AddTags', 
										 tip='',
										 icon='')
		addTagsMenuItem.connect('activate', self.menu_addtags, files)
		
		removeTagsMenuItem = Nemo.MenuItem(name='MyTags::remove', 
										 label='Remove', 
										 tip='',
										 icon='')
		removeTagsMenuItem.connect('activate', self.menu_deletetags, files)  
		
		replaceTagsMenuItem = Nemo.MenuItem(name='MyTags::replace', 
										 label='ReplaceTags', 
										 tip='',
										 icon='')
		replaceTagsMenuItem.connect('activate', self.menu_replacetags, files)  
		
		removeAllTagsMenuItem = Nemo.MenuItem(name='MyTags::remove_all', 
										 label='Remove All Tags', 
										 tip='',
										 icon='')
		removeAllTagsMenuItem.connect('activate', self.menu_erasetags, files)  
		
		copyFilesMenuItem = Nemo.MenuItem(name='MyTags::copy_files', 
										 label='Copy Files', 
										 tip='',
										 icon='')
		copyFilesMenuItem.connect('activate', self.menu_copyFilesFolders, files)  
		
		moveFilesMenuItem = Nemo.MenuItem(name='MyTags::move_files', 
										label='Move Files', 
										 tip='',
										 icon='')
		moveFilesMenuItem.connect('activate', self.menu_moveFilesFolders, files)  
		
		deleteFilesMenuItem = Nemo.MenuItem(name='MyTags::delete_files', 
										label='Delete Files', 
										 tip='',
										 icon='')
		deleteFilesMenuItem.connect('activate', self.menu_deleteFiles, files)  
		
		indexFilesMenuItem =  Nemo.MenuItem(name='MyTags::index_files', 
										label='Index Files', 
										 tip='',
										 icon='')
		indexFilesMenuItem.connect('activate', self.menu_indexFiles, files)  
		
		if (len(files) == 1):
			renameFileMenuItem = Nemo.MenuItem(name='MyTags::Rename_file', 
										label='Rename File', 
										 tip='',
										 icon='')
			renameFileMenuItem.connect('activate', self.menu_renameFileFolder, files)  
		
		
		tagsSubmenu.append_item(addTagsMenuItem)
		tagsSubmenu.append_item(removeTagsMenuItem)
		tagsSubmenu.append_item(replaceTagsMenuItem)
		tagsSubmenu.append_item(removeAllTagsMenuItem)
		
		filesSubmenu.append_item(copyFilesMenuItem)
		filesSubmenu.append_item(moveFilesMenuItem)
		if (len(files) == 1):
			filesSubmenu.append_item(renameFileMenuItem)
		filesSubmenu.append_item(deleteFilesMenuItem)
		filesSubmenu.append_item(indexFilesMenuItem)
		
		return top_menuitem,


