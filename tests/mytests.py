from __future__ import print_function
import unittest
import sys
import os
#import os.path




paths = ["src","lib"]
for i in paths:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/" + i)
print(sys.path)
import mytags.MyTagsUtils as mt

class MetaFileTest(unittest.TestCase):
	fileLookup = {
		"/home/user/fred/" : "/home/user/.ts/fred.ts", 
		"/home/user/fred" : "/home/user/.ts/fred.ts", 
		"/home/user/.ts/fred.ts":"/home/user/.ts/.ts/fred.ts", 
		"dir1/jack.txt": "dir1/.ts/jack.txt.ts", 
		"dir1/jack.txt/": "dir1/.ts/jack.txt.ts", 
		"dir1/jack.txt.ts": "dir1/.ts/jack.txt.ts.ts", 
		"dir1/.ts": "dir1/.ts/.ts.ts"
	}
	def testMetaFile(self):
		for i in fileLookup:
			assert mt.getMetaFileName[i] == fileLookup[i]
