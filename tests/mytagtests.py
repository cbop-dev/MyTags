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
		tests = [validTagTest,
				 MetaFileTest,
				 getTagsTest,
				 addTagsTest, 
				 DeleteTagsTest
#				 ReplaceTagsTest,
				 #FileOperationsTest
				 
				 ]
		
		suite1 = unittest.TestSuite()
		for t in tests:
			suite1.addTest(unittest.TestLoader().loadTestsFromTestCase(t))
		
		#suite1.addTest(DeleteTagsTest('test8_removeSomeTags'))
		return suite1
		
	
	def runTest(self):
		print "Running our tests..."
		
		result = unittest.TextTestRunner(verbosity=2).run(self.suite())

class validTagTest(unittest.TestCase):
	def setUp(self):
		self.validTags = ["freddy2349","Jack-and-Jill","Wretched.Man-eats-rotten_fruit=for*breakfast","@home","+1","!run away!"]
		self.invalidTags = [" fred", "fred ", "jack and	jill","adf<adf","asdf:we", "Jack\\", "/home", "d|b"]
	
	def testValidTags(self):
		for t in self.validTags:
			self.assertTrue(mt.isValidTag(t), "isValid('" + t + ") returned false! Should be true." )
		
		for t in self.invalidTags:
			self.assertFalse(mt.isValidTag(t), "isValid('" + t + ") returned true! Should be false." )
		

class getTagsTest(unittest.TestCase):
		
	def setUp(self):
		
		self.assertTrue(mt.checkDir(testdatadir))
		
		self.jSONfileData = {}
		self.jSONfileData["ascii"] ='{"tags":[{"title":"20170427","type":"sidecar","style":""},{"title":"low","type":"sidecar","style":"color: #ffffff !important; background-color: #7bd148 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:45:45.666Z"}'
		self.jSONfileData["file1.txt"] = ""
		self.jSONfileData["file2.jpg"] = "{}"
		self.jSONfileData["file3.pdf"] = '{"mylabel":"myvalue"}'
		self.jSONfileData["testfile 2.json"] = '{"tags":[{"title":"waiting","type":"sidecar","style":""},{"title":"high","type":"sidecar","style":"color: #ffffff !important; background-color: #ff7537 !important;"},{"title":"20170426","type":"sidecar","style":""},{"title":"test","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:46:04.342Z"}'
		self.jSONfileData["file 2"] = '{"tags":[{"title":"waiting","type":"sidecar","style":""},{"title":"high","type":"sidecar","style":"color: #ffffff !important; background-color: #ff7537 !important;"},{"title":"20170426","type":"sidecar","style":""},{"title":"test","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:46:04.342Z"}'
		self.jSONfileData["files -2.extension"] = '{"tags":[{"title":"2star","type":"sidecar","style":"color: #ffffff !important; background-color: #FFCC24 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:45:49.847Z"}'
		
		for filename in self.jSONfileData:
			mt.write(testdatadir +"/" + filename, "Test File for getTagsTets")
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
	
	def tearDown(self):
		shutil.rmtree(testdatadir)
	
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
		self.assertTrue(mt.checkDir(testdatadir))
		self.testFilesTags = {testdatadir + "/file1" : [[], ""],
					 testdatadir + "/testfile 2" : [
						["waiting","high","20170426","test"],
						'{"tags":[{"title":"waiting","type":"sidecar","style":""},{"title":"high","type":"sidecar","style":"color: #ffffff !important; background-color: #ff7537 !important;"},{"title":"20170426","type":"sidecar","style":""},{"title":"test","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:46:04.342Z"}'
						],
					 testdatadir +"/testfilename.extension" : [
						["low", "long_qw@$!@$", "longe-tag-with-several-hyphens"],
						'{"tags":[{"title":"low","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"},{"title":"long_qw@$!@$","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"},{"title":"longe-tag-with-several-hyphens","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-28T03:11:00.949Z"}'
						],
					testdatadir +"/malformed.meta" : [
						[],
						'{"tags":[{"title":"low","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"},{"title":"long_qw@$!@$","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"},{"title":"longe-tag-with-several-hyphens","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-28T03:11:00.949Z"'
						],
					testdatadir +"/malformed.meta2" : [
						[],
						'not JSON'
						]
					 }
		#self.jSONfileData = {}
		#self.jSONfileData["file1.json"] = ""
		#self.jSONfileData["testfile 2.json"] = "{\"tags\":[{\"title\":\"waiting\",\"type\":\"sidecar\",\"style\":\"\"},{\"title\":\"high\",\"type\":\"sidecar\",\"style\":\"color: #ffffff !important; background-color: #ff7537 !important;\"},{\"title\":\"20170426\",\"type\":\"sidecar\",\"style\":\"\"},{\"title\":\"test\",\"type\":\"sidecar\",\"style\":\"color: #ffffff !important; background-color: #008000 !important;\"}],\"appVersionCreated\":\"2.6.0\",\"appName\":\"TagSpaces\",\"appVersionUpdated\":\"2.6.0\",\"lastUpdated\":\"2017-04-27T03:46:04.342Z\"}"
		
		for filename, values in self.testFilesTags.items():
			mt.write(filename, "Test File for addTagsTest")
			mt.write(os.path.dirname(filename) + "/.ts/" + os.path.basename(filename) + ".json", values[1])
		
		
	def test1_SimpleAdd(self):
		tags = ["tag1","tag2", "tag3", "tag7"]
		(success,failures) = mt.addTags(testdatadir + "/file12", tags)
		self.assertTrue(success)
	
	def test2_ComplexValidTagNames(self):
		tags = ["tag1-asdf_asdflj asdf","ta()g2", "tAg@3", "!@ta=g7","asoijfija;sdj asdlfk a;sdlfkj as;dlfk a;dfjal jfaioj;lj jioj fij ijadghigyu @!--___"]
		oFile = testdatadir + "/testfile 2"
		cFile = oFile + "-copy"
		(success1,failures1) = mt.addTags(oFile, tags)
		shutil.copyfile(mt.getMetaFileName(oFile),  mt.getMetaFileName(cFile))
		shutil.copyfile(oFile, cFile)
			
		oFile = testdatadir + "/testfile 2"
		cFile = oFile + "-copy"
		(success2,failures2) = mt.addTags(cFile, tags)
		self.assertTrue(success1 and success2)
		self.assertTrue(len(mt.getTags(cFile)) == 9, "Len: " + str(len(mt.getTags(cFile))))
		self.assertTrue(set(tags) | set(self.testFilesTags[oFile][0]) == set(mt.getTags(cFile)), mt.getTags(cFile))
		
	def test4_BulkAdd(self):
		tags = ["tag 1", "another tag", "waiting", "long_qw@$!@$", "fun times!", "rancid"]
		
		(success, failures) = mt.addTagsBulk(self.testFilesTags.keys(), tags)
		self.assertTrue(success, failures)
		
		for filename, values in self.testFilesTags.items():
			
			
			self.assertTrue(len(mt.getTags(filename)) == len(set(values[0]) | set(tags)), len(mt.getTags(filename)))
			self.assertTrue(set(mt.getTags(filename)) == (set(values[0]) | set(tags)), filename + ": " + "|".join(mt.getTags(filename)) + ";\n values[0]: " + "|".join(values[0]))
			
			
		
		
	def test5_AddToUnavailableFile(self):
		(success,failures) = mt.addTags("/fredssss.fakefile.noroot.permission.none.txt", ["tag1","tag2", "tag3"])
		self.assertFalse(success, "Should not have been able to write metafile to /.ts !")
		
	def test5_AddToMalformedMetaFile(self):
		for filename, values in self.testFilesTags.items():
			mt.write(mt.getMetaFileName(filename), '{"tags":[{"title":"yes",{"title":"no"}]}')
			
			mt.addTags(filename, values[0])
			self.assertTrue(set(values[0]) == set(mt.getTags(filename)))
			#self.assertTrue(len(values[0]) == len(mt.getTags(filename)))
			
	def test3_AddExistingTags(self):
		#(success,failures) = mt.addTags(
		for filename, values in self.testFilesTags.items():
			mt.addTags(filename, values[0])
			self.assertTrue(set(values[0]) == set(mt.getTags(filename)))
			self.assertTrue(len(values[0]) == len(mt.getTags(filename)))
			for t in values[0]:
				self.assertTrue(t in mt.getTags(filename))
	
	def test6_addTagstoDirectories(self):
		thedir = testdatadir + "/tmpdir"
		tags = ["tag1", "dirtag2"]
		shutil.rmtree(thedir, ignore_errors=True)
		os.mkdir(thedir)
		
		mt.addTags(thedir, tags)
		self.assertTrue(set(mt.getTags(thedir)) == set(tags), mt.getTags(thedir))
	
	def tearDown(self):
		shutil.rmtree(testdatadir)
	
class DeleteTagsTest(unittest.TestCase):
	def setUp(self):
		# load list of files to check, and tags to add	
		# Files should include some with no tags; some with tags which will not be added; some with tags that will be added
		#print "realpath: " + os.path.realpath(__file__)
		self.assertTrue(mt.checkDir(testdatadir))
		self.testFilesTags = {testdatadir + "/file1" : [[], ""],
					 testdatadir + "/testfile 2" : [
						["waiting","high","20170426","test"],
						'{"tags":[{"title":"waiting","type":"sidecar","style":""},{"title":"high","type":"sidecar","style":"color: #ffffff !important; background-color: #ff7537 !important;"},{"title":"20170426","type":"sidecar","style":""},{"title":"test","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-27T03:46:04.342Z"}'
						],
					 testdatadir +"/testfilename.extension" : [
						["low", "long_qw@$!@$", "longe-tag-with-several-hyphens"],
						'{"tags":[{"title":"low","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"},{"title":"long_qw@$!@$","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"},{"title":"longe-tag-with-several-hyphens","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-28T03:11:00.949Z"}'
						],
					testdatadir +"/malformed.json" : [
						[],
						'{"tags":[{"title":"low","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"},{"title":"long_qw@$!@$","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"},{"title":"longe-tag-with-several-hyphens","type":"sidecar","style":"color: #ffffff !important; background-color: #008000 !important;"}],"appVersionCreated":"2.6.0","appName":"TagSpaces","appVersionUpdated":"2.6.0","lastUpdated":"2017-04-28T03:11:00.949Z"'
						]
					 }
		#self.jSONfileData = {}
		#self.jSONfileData["file1.json"] = ""
		#self.jSONfileData["testfile 2.json"] = "{\"tags\":[{\"title\":\"waiting\",\"type\":\"sidecar\",\"style\":\"\"},{\"title\":\"high\",\"type\":\"sidecar\",\"style\":\"color: #ffffff !important; background-color: #ff7537 !important;\"},{\"title\":\"20170426\",\"type\":\"sidecar\",\"style\":\"\"},{\"title\":\"test\",\"type\":\"sidecar\",\"style\":\"color: #ffffff !important; background-color: #008000 !important;\"}],\"appVersionCreated\":\"2.6.0\",\"appName\":\"TagSpaces\",\"appVersionUpdated\":\"2.6.0\",\"lastUpdated\":\"2017-04-27T03:46:04.342Z\"}"
		
		for filename, values in self.testFilesTags.items():
			mt.write(filename, "Test file!")
			success = mt.write(mt.getMetaFileName(filename), values[1])
			
		#	print "created file " + filename + " and its metafile with data: \n\n" +values[1] + "\n"
			if not success:
				raise Exception("Could not set up file " + filename)
			
	def test8_removeAllTags(self):	
		for filename, values in self.testFilesTags.items():			
			self.assertTrue(mt.removeAllTags(filename), "removeAlltags returned false for " + filename)
			self.assertFalse(mt.getTags(filename), filename + "|".join(mt.getTags(filename)))
		
	def test8_removeSomeTags(self):	
		removeTags = set(["low", "longe-tag-with-several-hyphens", "non-existing tag", " BAD tag"])
		for filename, values in self.testFilesTags.items():			
			oTags = set(mt.getTags(filename))
			
			oTags = set(mt.getTags(filename))
			
			nTags = set(oTags)
			
			for t in removeTags:
				nTags.discard(t)
				
			self.assertTrue(mt.removeSomeTags(filename, removeTags), "removeSomeTags returned false for " + filename)
			
			#print "Trying to get new tags from "+filename
			actualTags = set(mt.getTags(filename))
			#print actualTags
			#print mt.getTags(filename)
			
			self.assertTrue(actualTags == set(oTags - removeTags), "Tried to remove (" + "|".join(removeTags) + ") from " + filename + ",\n 	but got: (" + "|".join(actualTags) + ")")
			for t in actualTags:
				self.assertFalse(t in removeTags, filename)
	def tearDown(self):
		shutil.rmtree(testdatadir)
		

class ReplaceTagsTest(unittest.TestCase):
	def test1_replaceTags(self):
		self.assertTrue(False, "need to implement replaceTags()")
		
class FileOperationsTest(unittest.TestCase):
	def test1_moveFile(self):
		self.assertTrue(False, "need to implement moveFile()")
#print "hello!"
#unittest.main()

#test = MetaFileTest("test_MetaFile")



	
		
