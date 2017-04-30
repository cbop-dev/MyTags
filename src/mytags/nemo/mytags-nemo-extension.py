import os
import urllib
import gi
import sys
from Tkinter import *		   # Importing the Tkinter (tool box) library 
import tkSimpleDialog
import tkMessageBox

gi.require_version('Nemo', '3.0')
from gi.repository import GObject, Nemo
mytagsLibDir = "/home/cbrannan/dev/git-projects/MyTags/src"
sys.path.append(mytagsLibDir)
print sys.path

import mytags.MyTagsUtils as mt

def getCleanFilenames(files):
	cleanedFilenames = []
	for thefile in files:
		cleanedFilenames.insert(0,urllib.unquote(thefile.get_uri()[7:]))
	return cleanedFilenames

class ColumnExtension(GObject.GObject, Nemo.ColumnProvider, Nemo.InfoProvider):
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
		
		file.add_string_attribute('tags', "|".join(mt.getTags(filename)))


class MyTagsMenuProvider(GObject.GObject, Nemo.MenuProvider):
	def __init__(self):
		pass

	def simpleDialog(self, title, label):
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
		root.withdraw()	
		textInput = tkSimpleDialog.askstring(title, label, parent=root)
		root.destroy()
		return textInput
	
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
		if (self.simpleConfirm("Erase Tags", "Remove ALL tags from selected files?")):
			for f in cleanedFilenames:
				mt.removeAllTags(f)
				
	
	def menu_replacetags(self, menu, files):
		cleanedFilenames = getCleanFilenames(files)
			
		tagString = self.simpleDialog("Replace Tags", "All Existing tags will be remove from files. Enter tags to replace them with:")
		tags = ''
		if (tagString):
			tags = [t.strip() for t in tagString.split(",")]
		#tkMessageBox.showinfo("Delete Tags", "Deleting tags: " + "|".join(tags), parent=root)
		
		if (tags):
			failed = []
			for f in cleanedFilenames:
				if not mt.replaceTags(f, tags):
					failed.insert(0, f)
			
			if failed:
				self.showwarning("Error", "Attempting to rplace tags from the following files failed: \n" + "\n".join(failed))
		
	def menu_addtags(self, menu, files):
		cleanedFilenames = getCleanFilenames(files)
		
		tagString = self.simpleDialog("Add Tags", "Enter tags to add (separated by commas):")
			
		#tags = tagString.split(",")
		tags = [t.strip() for t in tagString.split(",")]
		if (tags):
			print "attempting to add [" + "|".join(tags) + "] to " + ";".join(cleanedFilenames)
			mt.addTagsBulk(cleanedFilenames, tags)

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

		
	def get_file_items(self, window, files):
		top_menuitem = Nemo.MenuItem(name='MyTags::menu', 
										 label='MyTags', 
										 tip='',
										 icon='')

		submenu = Nemo.Menu()
		top_menuitem.set_submenu(submenu)

		sub_menuitem = Nemo.MenuItem(name='MyTags::add', 
										 label='AddTags', 
										 tip='',
										 icon='')
		sub_menuitem.connect('activate', self.menu_addtags, files)
		sub_menuitem2 = Nemo.MenuItem(name='MyTags::delete', 
										 label='DeleteTags', 
										 tip='',
										 icon='')
		sub_menuitem2.connect('activate', self.menu_deletetags, files)  
		sub_menuitem3 = Nemo.MenuItem(name='MyTags::replace', 
										 label='ReplaceTags', 
										 tip='',
										 icon='')
		sub_menuitem3.connect('activate', self.menu_replacetags, files)  
		sub_menuitem4 = Nemo.MenuItem(name='MyTags::erase', 
										 label='Erase Tags', 
										 tip='',
										 icon='')
		sub_menuitem4.connect('activate', self.menu_erasetags, files)  
		submenu.append_item(sub_menuitem)
		submenu.append_item(sub_menuitem2)
		submenu.append_item(sub_menuitem3)
		submenu.append_item(sub_menuitem4)
		
		return top_menuitem,


