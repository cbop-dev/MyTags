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
		cleanedFilenames.insert(0,urllib.unquote(files[0].get_uri()[7:]))
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

	

	def menu_addtags(self, menu, files):
		cleanedFilenames = getCleanFilenames(files)
		
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
		tagString = tkSimpleDialog.askstring("Add Tags", "Enter tags to add (separated by commas):", parent=root)
		root.destroy()
		#tags = tagString.split(",")
		tags = [t.strip() for t in tagString.split(",")]
		print "attempting to add [" + "|".join(tags) + " to " + ";".join(cleanedFilenames)
		mt.addTagsBulk(cleanedFilenames, tags)

	def menu_deletetags(self, menu, files):
		cleanedFilenames = getCleanFilenames(files)
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
		
		tagString = tkSimpleDialog.askstring("Remove Tags", "Enter tags to remove (separated by commas):", parent=root)
		tags = [t.strip() for t in tagString.split(",")]
		#tkMessageBox.showinfo("Delete Tags", "Deleting tags: " + "|".join(tags), parent=root)
		
		failed = []
		for f in cleanedFilenames:
			if not mt.removeSomeTags(f, tags):
				failed.insert(0, f)
		
		if failed:
			tkMessageBox.showwarning("Error", "Attempting to remove tags from the following files failed: \n" + "\n".join(failed), parent=root)		
		root.destroy()
		#tags = tagString.split(",")
		
		

		
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
		submenu.append_item(sub_menuitem)
		submenu.append_item(sub_menuitem2)

		return top_menuitem,


