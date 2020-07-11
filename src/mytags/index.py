from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
import subprocess
import argparse
import threading
from subprocess import Popen
from . import MyTagsUtils as mt
from . import config

class RecollIndex(object):
	def __init__(self, configfile):
		self.config=configfile
		self.p = None
		self.lock = threading.Lock()
	
	def updateIndex(self,filename):
		self.lock.acquire()
		
		if (self.p):
			self.p.wait()
		
		self.p = Popen(["recollindex", "-c", self.config, "-i", "-Z",   filename])
		
		self.lock.release()
		return self.p
		
	def updateIndexBatch(self, filenames):
		print("RecollIndex.updateIndexBatch() called...")
		self.lock.acquire()
		if (self.p):
			self.p.wait()
		self.p = Popen(["recollindex", "-c", self.config, "-i", "-Z"] + filenames)
		
		self.lock.release()
		return self.p
		
	def removeFile(self, filenames):
		self.lock.acquire()
		
		if (self.p):
			self.p.wait()
		
		self.p = Popen(["recollindex", "-c", self.config, "-e",   filename])
		self.lock.release()
		return self.p
		
	def removeBatch(self,filenames):
		self.lock.acquire()
		
		if (self.p):
			self.p.wait()
			
		self.p = Popen(["recollindex", "-c", self.config, "-e"] + filenames)
		self.lock.release()
		return self.p

class TMSUIndex(object):
	def __init__(self, configfile):
		print("TMSUIndex.init()...")
		self.p = None
		self.config=configfile
	
	def updateIndex(self,filename):
		if (self.p):
			self.p.wait()
		print("TMSUIndex.updateIndex(" + filename +")")
		self.p = Popen(["tmsu", "-D", self.config, "untag", "-a", filename])
		
		tags = mt.getTags(filename)
		
		if tags:
			self.p.wait()
			self.p = Popen(["tmsu", "-D", self.config, "tag", filename] + mt.getTags(filename))
		
		return self.p
	
	def updateIndexBatch(self, filenames):
		print("TMSUIndex.updateIndexBatch()...")
			
		for f in filenames:
			self.updateIndex(f)
		
	def removeFile(self, filename):
		if (self.p):
			self.p.wait()
		print("TMSUIndex.removeFile(" + filename +")")
		
		self.p = Popen(["tmsu", "-D", self.config, "untag", "-a", filename])
		
		return self.p
		
	def removeBatch(self,filenames):
		if (self.p):
			self.p.wait()
			
		self.p = Popen(["tmsu", "-D", self.config, "untag", "-a"] + filenames)
			
class UpdateIndexQueueThread(threading.Thread):
	#global recoll_config, index, recoll, tmsu, tmsu_db
	
	def __init__(self):

		self.stop = False
		self.queueLock = threading.Condition()
		self.queue = []
	
		self.indexThreads = {}
		if config.tmsu:
			print("enabled TMSU!")
			self.indexThreads['tmsu'] = [TMSUIndex(config.tmsu_db), None]
		if config.recoll:
			self.indexThreads['recoll'] = [RecollIndex(config.recoll_config), None]
		
		super(UpdateIndexQueueThread, self).__init__()
	
	def queueFilesUpdate(self,files, config=config.recoll_config):
		#global index, indexThread, indexLock, queueLock, queue
				
		self.queueLock.acquire()
		self.queue.append(("update", files))
		self.queueLock.notify()
		self.queueLock.release()

	def queueFilesRemove(self,files, config=config.recoll_config):
		#global index, indexThread, indexLock, queueLock, queue, p
		print("queueing files to remove: " + " | ".join(files))
		
		self.queueLock.acquire()
		print("queueFilesRemove: Acquired queueuLock...")
		self.queue.append(("remove", files))
		self.queueLock.notify()
		self.queueLock.release()
		print("queueFilesRemove: released queueuLock...")


		
	def updateIndex(self,filename, rconfig=config.recoll_config):
		#global p
		#if (self.p):
		#	self.p.wait()
				
		for key, (index,thread) in list(self.indexThreads.items()):
			if (thread):
				thread.join()
			thread = threading.Thread(target=index.updateIndex, args=(filename))
			self.indexThreads[key] = [index, thread]
			thread.start()
			#self.p = i.updateIndex(filename)
		#else:
			#self.p = Popen(["recollindex", "-i", "-Z", filename])

			
		
	def updateIndexBatch(self,filenames, rconfig=config.recoll_config):	
		#global index, indexThread, indexLock, queueLock, queue, p
		print("updateIndexBatch() called...")
#		theThread = self.__getQueueThread__()
#		theThread.join()
		
		#if (self.p):
		#	print "updateIndexBatch waiting for process to finish..."
		#	self.p.wait()
		if (list(filenames) and len(filenames) > 0):
			for key, (index,thread) in list(self.indexThreads.items()):
				if (thread):
					thread.join()
				thread = threading.Thread(target=index.updateIndexBatch, args=([filenames]))
				self.indexThreads[key] = [index, thread]
				thread.start()
				

	def removeFile(self,filename, rconfig=config.recoll_config):
		#theThread = self.__getIndexThread__()
		#global index, indexThread, indexLock, queueLock, queue, p
		#if (self.p):
		#	self.p.wait()
		for key, (index,thread) in list(self.indexThreads.items()):
			if (thread):
				thread.join()
			thread = threading.Thread(target=index.removeFile, args=(filename))
			self.indexThreads[key] = [index, thread]
			thread.start()
			
			
	def removeBatch(self,filenames, rconfig=config.recoll_config):
		#global index, indexThread, indexLock, queueLock, queue, p
		#theThread = self.__getIndexThread__()
		#if (self.p):
			#print "waiting for process to finish..."
			#self.p.wait()
		if (list(filenames) and len(filenames) > 0):
			for key, (index,thread) in list(self.indexThreads.items()):
				if (thread):
					thread.join()
				thread = threading.Thread(target=index.updateIndexBatch, args=([filenames]))
				self.indexThreads[key] = [index, thread]
				thread.start()
				
		else:
			print("Don't have any files to remove...")

	def run(self):
		#global index, indexThread, indexLock, queueLock, queue, p
		print("In Index main thread\n")
		print("queue size is: " + str(len(self.queue)))
		while(not self.stop):
			self.queueLock.acquire()
			while (not self.queue):
				print("index thread waiting for command queue to fill...")
				self.queueLock.wait()
				print("received notify! going into action...")
			(command, files) = self.queue.pop(0)
			print("About to convert links...")
			realfiles = [mt.getRealPath(f) for f in files]
			# print ("Realfiles = " + str(realfiles))
			self.queueLock.release()
			
			
			print("About to run command '" +command + "', with args: [" + ",".join(realfiles) + " ]")
			if (command == "update"):
				self.updateIndexBatch(realfiles)
			elif (command == "remove"):
				self.removeBatch(realfiles)
				print(" removed file.")
			
		
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Re-index files')
	parser.add_argument('filename', metavar='Filename', type=str, help='Filename')
	parser.add_argument('-c', metavar='recoll-config-directory', type=str, help='Recoll Directory')
	args = parser.parse_args()
	UpdateIndexQueueThread().updateIndexBatch([args.filename], config=args.c)
	
