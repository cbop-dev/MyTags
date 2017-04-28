import unittest
import sys
import os
import logging
import shutil
import mytags.MyTagsUtils as mt

testsdir = os.path.dirname(os.path.realpath(__file__))
testdatadir = testsdir + "/" + "testdata"
#print "Testdatadir: " + testdatadir

def loadTestFiles():
	pass

class myTagTests(object):
	
	
	def suite(self):
		# Add class names in variable below to add it's "testXXX" functions to the test suite
		tests = [MetaFileTest,
				 getTagsTest,
				 addTagsTest, 
				 validTagTest]
		
		suite1 = unittest.TestSuite()
		for t in tests:
			suite1.addTest(unittest.TestLoader().loadTestsFromTestCase(t))
		
		return suite1
		
	
	def runTest(self):
		print "Running our tests..."
		
		result = unittest.TextTestRunner(verbosity=2).run(self.suite())

class validTagTest(unittest.TestCase):
	def setUp(self):
		self.validTags = ["freddy2349","Jack-and-Jill","Wretched.Man-eats-rotten_fruit=for*breakfast","@home","+1","!run away!"]
		self.invalidTags = [" fred", "fred ", "jack and	jill","adf<adf","asdf:we", "Jack\\", "/home"]
	
	def testValidTags(self):
		for t in self.validTags:
			self.assertTrue(mt.isValidTag(t), "isValid('" + t + ") returned false! Should be true." )
		
		for t in self.invalidTags:
			self.assertFalse(mt.isValidTag(t), "isValid('" + t + ") returned true! Should be false." )
		

class getTagsTest(unittest.TestCase):
		
	def setUp(self):
		
		self.jSONfileData = {}
		self.jSONfileData["ascii"] ='{"tags":[{"title":"20170427","type":"sidecar","style":""},{"title":"low","type":"sidecar","style":"color: #ffffff !important; background-color: #7bd148 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:45:45.666Z"}'
		self.jSONfileData["file1.txt"] = ""
		self.jSONfileData["file2.jpg"] = "{}"
		self.jSONfileData["file3.pdf"] = '{"mylabel":"myvalue"}'
		self.jSONfileData["testfile 2.json"] = '{"tags":[{"title":"waiting","type":"sidecar","style":""},{"title":"high","type":"sidecar","style":"color: #ffffff !important; background-color: #ff7537 !important;"},{"title":"20170426","type":"sidecar","style":""},{"title":"test","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:46:04.342Z"}'
		self.jSONfileData["file 2"] = '{"tags":[{"title":"waiting","type":"sidecar","style":""},{"title":"high","type":"sidecar","style":"color: #ffffff !important; background-color: #ff7537 !important;"},{"title":"20170426","type":"sidecar","style":""},{"title":"test","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:46:04.342Z"}'
		self.jSONfileData["files -2.extension"] = '{"tags":[{"title":"2star","type":"sidecar","style":"color: #ffffff !important; background-color: #FFCC24 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:45:49.847Z"}'
		
		for filename in self.jSONfileData:
			mt.write(testdatadir + "/.ts/" + filename + ".json", self.jSONfileData[filename])
		
		
		self.fileTagAnswers = {
			"ascii": ["20170427","low"],
			"file1.txt": [],
			"file 2": ["waiting","high","20170426","test"],
			"files -2.extension": ["2star"],
			"testfile 2.json" : ["waiting","high","20170426","test"],
			"no file": []
		}
		
	def testGetTags(self):
		for i in self.fileTagAnswers:
			logging.debug( "getTags("+testdatadir + "/" + i+")...")
			tags = mt.getTags(testdatadir + "/" + i)
			self.assertTrue(len(self.fileTagAnswers[i]) == len(tags), str(len(self.fileTagAnswers[i])) + " !=" + str(len(tags)))
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

class addTagsTest(unittest.TestCase):
	
	def setUp(self):
		# load list of files to check, and tags to add	
		# Files should include some with no tags; some with tags which will not be added; some with tags that will be added
		#print "realpath: " + os.path.realpath(__file__)
		self.testFilesTags = {testdatadir + "/file1" : [[], ""],
					 testdatadir + "/testfile 2" : [
						["waiting","high","20170426","test"],
						'{"tags":[{"title":"waiting","type":"sidecar","style":""},{"title":"high","type":"sidecar","style":"color: #ffffff !important; background-color: #ff7537 !important;"},{"title":"20170426","type":"sidecar","style":""},{"title":"test","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:46:04.342Z"}'
						],
					 testdatadir +"/testfilename.extension" : [
						["low", "long_qw@$!@$", "longe-tag-with-several-hyphens"],
						'{"tags":[{"title":"low","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"},{"title":"long_qw@$!@$","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"},{"title":"longe-tag-with-several-hyphens","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-28T03:11:00.949Z"}'
						]
					 }
		#self.jSONfileData = {}
		#self.jSONfileData["file1.json"] = ""
		#self.jSONfileData["testfile 2.json"] = "{\"tags\":[{\"title\":\"waiting\",\"type\":\"sidecar\",\"style\":\"\"},{\"title\":\"high\",\"type\":\"sidecar\",\"style\":\"color: #ffffff !important; background-color: #ff7537 !important;\"},{\"title\":\"20170426\",\"type\":\"sidecar\",\"style\":\"\"},{\"title\":\"test\",\"type\":\"sidecar\",\"style\":\"color: #ffffff !important; background-color: #008000 !important;\"}],\"appVersionCreated\":\"2.6.0\",\"appName\":\"TagSpaces\",\"appVersionUpdated\":\"2.6.0\",\"lastUpdated\":\"2017-04-27T03:46:04.342Z\"}"
		
		for filename, values in self.testFilesTags.items():
			mt.write(os.path.dirname(filename) + "/.ts/" + os.path.basename(filename) + ".json", values[1])
		
	def testSimpleAdd(self):
		tags = ["tag1","tag2", "tag3", "tag7"]
		(success,failures) = mt.addTags([ testdatadir + "/file12"], tags)
		self.assertTrue(success)
	
	def testComplexValidTagNames(self):
		tags = ["tag1-asdf_asdflj asdf","ta()g2", "tAg@3", "!@ta=g7","asoijfija;sdj asdlfk a;sdlfkj as;dlfk a;dfjal jfaioj;lj jioj fij ijadghigyu @!--___"]
		oFile = testdatadir + "/testfile 2"
		cFile = oFile + "-copy"
		(success1,failures1) = mt.addTags([oFile], tags)
		shutil.copyfile(mt.getMetaFileName(oFile),  mt.getMetaFileName(cFile))
		shutil.copyfile(oFile, cFile)
			
		oFile = testdatadir + "/testfile 2"
		cFile = oFile + "-copy"
		(success2,failures2) = mt.addTags([ cFile], tags)
		self.assertTrue(success1 and success2)
		self.assertTrue(len(mt.getTags(cFile)) == 9, "Len: " + str(len(mt.getTags(cFile))))
		self.assertTrue(set(tags) | set(self.testFilesTags[oFile][0]) == set(mt.getTags(cFile)), mt.getTags(cFile))
		
	def testBulkAdd(self):
		tags = ["tag 1", "another tag", "waiting", "long_qw@$!@$", "fun times!", "rancid"]
		(success, failures) = mt.addTags(self.testFilesTags.keys(), tags)
		self.assertTrue(success, failures)
		
		for filename, values in self.testFilesTags.items():
			self.assertTrue(len(mt.getTags(filename)) == len(set(values[0]) | set(tags)), len(mt.getTags(filename)))
			self.assertTrue(set(mt.getTags(filename)) == (set(values[0]) | set(tags)), filename + ": " + "|".join(mt.getTags(filename)) + ";\n values[0]: " + "|".join(values[0]))
			
			
		
		
	def testAddToBadFile(self):
		(success,failures) = mt.addTags(["/fredssss.fakefile.noroot.permission"], ["tag1","tag2", "tag3"])
		self.assertFalse(success, "Should not have been able to write metafile to /.ts !")
	
	def testAddExistingTags(self):
		#(success,failures) = mt.addTags(
		for filename, values in self.testFilesTags.items():
			mt.addTags([filename], values[0])
			self.assertTrue(set(values[0]) == set(mt.getTags(filename)))
			self.assertTrue(len(values[0]) == len(mt.getTags(filename)))
			for t in values[0]:
				self.assertTrue(t in mt.getTags(filename))
		
	
	
		

#print "hello!"
#unittest.main()

#test = MetaFileTest("test_MetaFile")



	
		
