#!/usr/bin/python

from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from past.utils import old_div
from tkinter import *           # Importing the Tkinter (tool box) library 
import tkinter.simpledialog
import tkinter.messagebox
import tkinter.filedialog
import getopt
#import commands
#import pipes
#import shlex
import os.path
import extendedui.DragDropListbox
from TkTreectrl import *
import mytags.MyTagsUtils as MyTagsUtils

class MyTagsDialog(tkinter.simpledialog.Dialog):
	
	
	def __init__(self, master, filenames=[]):
		#self.filename=filename
		self.master = master
		self.filenames = filenames
		self.tags = {}
		for f in filenames:
			self.tags[f] = MyTagsUtils.getMetaFileName(f)
			
		tkinter.simpledialog.Dialog.__init__(self, master, "MyTags Tools")
		
		#print "init: self.filename = self.filename"
	
	def yview(self, *args):
		self.list.yview(*args)
		self.b2.yview(*args)			
	
	def buttonbox(self):
		print("buttonbox()...")
		self.closebutton = Button(self, text="Done", command=self.close, height=3).pack()
		

	def body(self, master, ):
		print("body called")
				
		
		self.list = ScrolledMultiListbox(master, scrollmode="auto", width=800)
		self.list.listbox.configure(selectmode="multiple", columns=("File/folder name", "Tags"), width=0, expandcolumns=(0,1), height=10)
		
		for i in self.tags:
			self.list.listbox.insert(0, i, self.tags[i])
			#self.list.listbox.insert(0, "fred barney ruble funny dude running around alldaylong", ("tag3", "tag2"))
			
		self.list.listbox.column_configure(0, weight=2, width=400)
		self.list.listbox.column_configure(1, weight=1)
				
		if (type(self.filenames) in (list, tuple)) and (len(self.filenames) > 1):
			for i in self.files:
				self.list.listbox.insert(END,i)
			
		self.list.grid(row=0, columnspan=2, rowspan = 5)
		
		# add buttons:
		buttonwidth = 30
		self.buttons = []
		self.buttons.append(Button(master,text="Add Tags", ))
		self.buttons.append(Button(master,text="Remove Some Tags"))
		self.buttons.append(Button(master,text="Clear All Tags"))
		
				
		i=0
		for b in self.buttons:
			b.grid(column=3, row=i, sticky=W)
			i+=1
			b.config(width=buttonwidth, height=2)
		
		#return self.closebutton
        
	def close(self):
		print("Close button clicked. Closing window...")
		#self.destroy()
		self.master.destroy()
		#filename = self.e1.get()
		#self.result = (filename, map(int, self.list.curselection()), self.list.get(0,END))
#		print filename #or something
#		print "self.filename = " + self.filename
		
    
	


def main():
	root = Tk()
	# get screen width and height
	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen

	# calculate x and y coordinates for the Tk root window
	#x = (ws/2) - (w/2)
	#y = (hs/2) - (h/2)

	# set the dimensions of the screen 
	# and where it is placed
	#root.geometry('%dx%d+%d+%d' % (w, h, x, y))
	#root.geometry('+20+10')
	root.geometry('+%d+%d' % (old_div(ws,2), old_div(hs,2)))
	root.update()  # needed
	root.withdraw()
	# optional, show input dialogs without the Tkinter window

	output = ""
	filenames = []
	
	if len(sys.argv) < 2:
		#print "You must supply an argument!!!"
		#tkMessageBox.showwarning("Error", "You must supply an argument!")
		#sys.exit(2)
		filenames = tkinter.filedialog.askopenfilenames()
		print(filenames);
		if (not filenames):
			print("No input files given! Exiting...")
			exit(1)
		
	else:
		try:
			opts, args = getopt.getopt(sys.argv, "o")
		except getopt.GetoptError:
			sys.exit(2)
		
		for i in sys.argv[1:]:
			filenames.append(i);
		

	d = MyTagsDialog(root, filenames=filenames)
	if d.result == None:
		exit(1)

	inputFiles = []
	inputFilesString = ""
	
	#root.mainloop()                 # Execute the main event handler

main()
