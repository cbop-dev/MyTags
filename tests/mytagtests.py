import unittest
import sys
import os

import mytags.MyTagsUtils as mt

class myTagTests(object):
	@staticmethod
	def run():
		print "Running our tests..."
		suite1 = unittest.TestLoader().loadTestsFromTestCase(MetaFileTest)
		suite2 = unittest.TestLoader().loadTestsFromTestCase(getTagsTest)
		alltests = unittest.TestSuite([suite1, suite2])
		result = unittest.TextTestRunner(verbosity=2).run(alltests)

class getTagsTest(unittest.TestCase):
	'''NB:these tests depend upon external files and the correct metafiles being in their .ts folder!'''
	'''file/tag data created by TagSpaces:
			ascii.json:
			{"tags":[{"title":"20170427","type":"sidecar","style":""},{"title":"low","type":"sidecar","style":"color: #ffffff !important; background-color: #7bd148 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:45:45.666Z"}
			
			file1 (copy).txt.json:
			{"tags":[{"title":"2star","type":"sidecar","style":"color: #ffffff !important; background-color: #FFCC24 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:45:49.847Z"}
			file 2 (copy).json:
			{"tags":[{"title":"20170427","type":"sidecar","style":""},{"title":"low","type":"sidecar","style":"color: #ffffff !important; background-color: #7bd148 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:45:45.666Z"}
			
			file 2.json:
			{"tags":[{"title":"waiting","type":"sidecar","style":""},{"title":"high","type":"sidecar","style":"color: #ffffff !important; background-color: #ff7537 !important;"},{"title":"20170426","type":"sidecar","style":""},{"title":"test","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:46:04.342Z"}
			
			utf.json:blank
	'''

	
	def setUp(self):
		
		self.fileTagAnswers = {
			"/home/cbrannan/dev/git-projects/MyTags/tests/testdata/ascii": ["20170427","low"],
			"/home/cbrannan/dev/git-projects/MyTags/tests/testdata/file1.txt": [],
			"/home/cbrannan/dev/git-projects/MyTags/tests/testdata/file 2": ["waiting","high","20170426","test"],
			"/home/cbrannan/dev/git-projects/MyTags/tests/testdata/file 2 (copy)": ["low","20170427"],
			"/home/cbrannan/dev/git-projects/MyTags/tests/testdata/file1 (copy).txt": ["2star"]

		}
		
	def testGetTags(self):
		for i in self.fileTagAnswers:
			tags = mt.getTags(i)
			self.assertTrue(len(self.fileTagAnswers[i]) == len(tags), "tags[" + i + "]: " + " ".join(tags) + "; but answer  is " + " ".join(self.fileTagAnswers[i]))
			for t in self.fileTagAnswers[i]:
				self.assertTrue(t in tags, "Tag " + t + " is not in getTags(" + i + ")!")
	
class MetaFileTest(unittest.TestCase):
	def setUp(self):
		self.fileLookup = {
			"/home/user/fred/" : "/home/user/.ts/fred.json", 
			"/home/user/fred" : "/home/user/.ts/fred.json", 
			"/home/user/.ts/fred.ts":"/home/user/.ts/.ts/fred.ts.json", 
			"dir1/jack.txt": "dir1/.ts/jack.txt.json", 
			"dir1/jack.txt/": "dir1/.ts/jack.txt.json", 
			"dir1/jack.txt.ts": "dir1/.ts/jack.txt.ts.json", 
			"dir1/.ts": "dir1/.ts/.ts.json"
		}

			
	def test_MetaFile(self):
		for i in self.fileLookup:
			self.assertTrue(mt.getMetaFileName(i) == self.fileLookup[i], "key = "+ i + ", value = " + self.fileLookup[i] + ", but getMetafile = " + mt.getMetaFileName(i))

#print "hello!"
#unittest.main()

#test = MetaFileTest("test_MetaFile")



	
		
