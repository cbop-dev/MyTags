#!/usr/bin/python
import sys
import os

paths = ["src","lib"]
for i in paths:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/" + i)
#print sys.path

from extendedui import *
import mytags.MyTagsUtils
import mytags.nemo.MyTagsDialog

mytags.MyTagsDialog.main()
