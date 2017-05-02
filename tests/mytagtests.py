import unittest
import sys
import os
import logging
import shutil
import mytags.MyTagsUtils as mt
from stat import  S_IWUSR, S_IREAD, S_IRUSR, S_IXUSR
import errno
import filelock

testsdir = os.path.dirname(os.path.realpath(__file__))
testdatadir = testsdir + "/" + "testdata"
#print "Testdatadir: " + testdatadir

def loadTestFiles():
	pass


class TestWithFiles(unittest.TestCase):
	#default files. Can be changed by re-assigning value of this variable, or by using setFileDict() below.
	testFilesTags = {testdatadir + "/file1" : [[], ""],
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
	
	def setFilesDict(filesDict):
		self.testFilesTags = dict(filesDict)
		
	def setUp(self):
		self.assertTrue(mt.checkDir(testdatadir))
		
		for filename, values in self.testFilesTags.items():
			mt.write(filename, "Test file!")
			success = mt.write(mt.getMetaFileName(filename), values[1])
			
			if not success:
				raise Exception("Could not set up file " + filename)
		
	
	def tearDown(self):
		shutil.rmtree(testdatadir)
		pass

class myTagTests(object):
	
	
	def suite(self):
		# Add class names in variable below to add it's "testXXX" functions to the test suite
		tests = [validTagTest,
				 MetaFileTest,
				 getTagsTest,
				 addTagsTest, 
				 DeleteTagsTest,
				 ReplaceTagsTest,
				 FileOperationsTest
				 
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
		

class getTagsTest(TestWithFiles):
		
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

		
class addTagsTest(TestWithFiles):
	
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
			self.assertTrue(set(values[0]) == set(mt.getTags(filename)), filename + ": "+ str(values[0]) + " != " + str(mt.getTags(filename)))
			self.assertTrue(len(values[0]) == len(mt.getTags(filename)), filename +": " +str(values[0]) + " != " + str(mt.getTags(filename)))
			for t in values[0]:
				self.assertTrue(t in mt.getTags(filename))
	
	def test6_addTagstoDirectories(self):
		thedir = testdatadir + "/tmpdir"
		tags = ["tag1", "dirtag2"]
		shutil.rmtree(thedir, ignore_errors=True)
		os.mkdir(thedir)
		
		mt.addTags(thedir, tags)
		self.assertTrue(set(mt.getTags(thedir)) == set(tags), mt.getTags(thedir))
	
	
class DeleteTagsTest(TestWithFiles):
	testFilesTags = {testdatadir + "/file1" : [[], ""],
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
		

class ReplaceTagsTest(TestWithFiles):
	
	def test1_replaceTags(self):
		tags = ["faith", "Hope", "charity!", "something else", "@nevermore"]
		
		for filename, values in self.testFilesTags.items():
			self.assertTrue(mt.replaceTags(filename, tags), filename)
			self.assertTrue(set(mt.getTags(filename)) == set(tags), filename + ", new tags: " + str(mt.getTags(filename)) + "; should be: "+ str(tags))
		
class FileOperationsTest(TestWithFiles):
	def setUp(self):
		TestWithFiles.setUp(self)
		self.tDir = os.path.join(testdatadir, "tmp")
		self.tFile = os.path.join(self.tDir, "file")
		mt.checkDir(self.tDir)
	def tearDown(self):
		
		try:
			os.chmod(self.tDir, S_IWUSR|S_IRUSR|S_IXUSR)
		except OSError as e:
			pass
		TestWithFiles.tearDown(self)
		
	def test1_getParentFile(self):
		self.validMetaFiles = {"/home/fred/jack/jill at hom/.ts/wilfredos/.ts/jacks.txt.json":"/home/fred/jack/jill at hom/.ts/wilfredos/jacks.txt",
				 "/.ts/.ts.json":"/.ts",
				 "/office/janson/docs/pdfs/.ts/.json.json":"/office/janson/docs/pdfs/.json"}
		for meta, pFile in self.validMetaFiles.items():
			self.assertTrue(mt.getParentFile(meta) == pFile, mt.getParentFile(meta) + " : " + pFile)
			
	def test2_deleteFile(self):		
		content = "content"	
		self.assertTrue(mt.write(self.tFile, content))
		
		self.assertTrue(os.path.exists(self.tFile))
		
		self.assertTrue((True, None) == mt.addTags(self.tFile, ["test","tag2"]))
		self.assertTrue(os.path.exists(mt.getMetaFileName(self.tFile)))
		
		self.assertTrue(mt.deleteFile(self.tFile))
		self.assertFalse(os.path.exists(self.tFile))
		self.assertFalse(os.path.exists(mt.getMetaFileName(self.tFile)))
			
		self.assertTrue(mt.write(self.tFile, content))
		
		self.assertTrue(os.path.exists(self.tFile))
		self.assertTrue((True, None) == mt.addTags(self.tFile, ["test","tag2"]))
		os.chmod(self.tDir, S_IRUSR)
		
		caughtError = False
		print "Entering try block"
		
		try: 
			mt.deleteFile(self.tFile)
		except (OSError, AttributeError) as e:
			print e
			print "Error rightly caught: " + str(e)
			caughtError = True
			#else:
			#	raise e
		
		self.assertTrue(caughtError)
		
		os.chmod(self.tDir, S_IWUSR|S_IRUSR|S_IXUSR)
	
	def test2_deleteMetaFile(self):
		for f in self.testFilesTags.keys():
			self.assertTrue(os.path.exists(mt.getMetaFileName(f)))
			mt.deleteMetaFile(f)
			self.assertFalse(mt.getTags(f))
			self.assertFalse(os.path.exists(mt.getMetaFileName(f)))
			
	def test3_getLockFileName(self):
		data = {"bob" : ".ts/bob.lock",
				"/root/folder/file.lock":"/root/folder/.ts/file.lock.lock",
				"/funny folder./sub directory/file.ext":"/funny folder./sub directory/.ts/file.ext.lock",
				"relative folder/directory/jacks.txt":"relative folder/directory/.ts/jacks.txt.lock"}
				
		for f, flock in data.items():
			self.assertTrue(flock == mt.getLockFileName(f))
			
	def test4_getLockFile(self):
		for f in self.testFilesTags.keys():
			lockname = mt.getLockFileName(f)
			lock = mt.getLockFile(f)
			if lock:
				self.assertFalse(lock.is_locked)
			with lock:
				self.assertTrue(lock.is_locked)
			self.assertFalse(lock.is_locked)
	def test5_CopyfileTest(self):
		tDir = os.path.join(testdatadir, "tmpss")
		if mt.checkDir(tDir):
			for f, values in self.testFilesTags.items():
				mt.addTags(f, values[0])
				self.assertTrue(set(mt.getTags(f)) == set(values[0]))
				#print "copying " + f + " to "+ tDir# +os.path.join(tDir, os.path.basename(f))
				mt.copyFile(f, tDir)
				mt.copyFile(f, os.path.join(tDir, os.path.basename(f)))
				self.assertTrue(os.path.exists(os.path.join(tDir, os.path.basename(f))), tDir +":" +f)
				s = set(mt.getTags(os.path.join(tDir, os.path.basename(f))))
				s2 = set(values[0])
				self.assertTrue( s ==  s2, str(s) + "\n" +str(s2))
				
		
	def test6_moveFile(self):
		destDir = os.path.join(testdatadir, "moveFiles")
		destFile = "/.nowhere/.somewhere/anywhere.ext/fred.txt"
		destFile2 = os.path.join(testdatadir, "moveF/test/dir/yes.ds")
		
		for f, v in self.testFilesTags.items():
			dest = os.path.join(os.path.dirname(f), os.path.join(destDir, os.path.basename(f)))
			result = mt.moveFile(f,dest)
			self.assertTrue(result != '')
			self.assertFalse(os.path.exists(f))
			self.assertTrue(os.path.exists(result))
			self.assertTrue(set(mt.getTags(result)) == set(v[0]), result + ": " +str(mt.getTags(result)))
			
			#test with bad dest:
			self.assertFalse(mt.moveFile(dest,destFile))
			self.assertTrue(os.path.exists(dest))
			self.assertTrue(set(mt.getTags(dest)) == set(v[0]), dest + ": " +str(mt.getTags(dest)))
			
			#move into existing dir:
			destDir2 = os.path.join(testdatadir, "existingDir")
			self.assertTrue(mt.checkDir(destDir2))
			self.assertTrue(os.path.exists(destDir2) and os.path.isdir(destDir2))
			
			result = mt.moveFile(dest,destDir2)
			self.assertFalse(result == '', "moveFile returned: " + result)
			self.assertTrue(os.path.exists(result))
			self.assertTrue(set(mt.getTags(result)) == set(v[0]))
			
			#move into non-existent parent: these should be created automacally:
			destDir2 = os.path.join(testdatadir, "yetanoghterdir" + os.path.basename(result))
			
			dest3 = os.path.join(destDir2, "anotherfile.name")
			if (os.path.exists(destDir2)):
				shutil.rmtree(destDir2)
				
			result = mt.moveFile(result,dest3)
			self.assertFalse(result == '', "moveFile returned: " + result)
			self.assertTrue(os.path.exists(result))
			self.assertTrue(set(mt.getTags(result)) == set(v[0]))

	def test7_moveDirs(self):
				
		#move a directory!
		tags = ["yes", "no", "directory"]
		srcdir= os.path.join(testdatadir, "mvdirsrc-test")
		destDir = os.path.join(testdatadir, "moveDirs")
		
		self.assertTrue(mt.checkDir(srcdir))
		self.assertTrue(mt.addTags(srcdir, tags))
		
		result = mt.moveFile(srcdir,destDir)
		self.assertTrue(result != '')
		self.assertTrue(set(mt.getTags(destDir)) == set(tags))
		self.assertTrue(os.path.exists(result))
		self.assertFalse(os.path.exists(srcdir))
		
		self.assertTrue(set(mt.getTags(result)) == set(tags), "tags: " + str(mt.getTags(result)))
		
		
			
		#self.assertTrue(True, "need to implement moveFile()")
		
	
#print "hello!"
#unittest.main()

#test = MetaFileTest("test_MetaFile")



	
		
