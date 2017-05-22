import subprocess
import argparse
import threading
from subprocess import Popen

#CHANGE THE FOLLOWING LINE TO YOUR RECOLL DIRECTORY
#config='/path/to/.recoll'
index = False

index = True

indexThread = None
indexLock = None

queueLock = None
queue = []

p = None

def __getIndexThread__():
	global config, index, indexThread, indexLock, queueLock, queue
	if not indexThread:
		indexLock = threading.Lock()
		indexThread = threading.Thread(target=__indexMain__)
		queueLock = threading.Condition()
		indexThread.start()
	return indexThread

def queueFilesUpdate(files, config=config):
	global index, indexThread, indexLock, queueLock, queue
	theThread = __getIndexThread__()
	queueLock.acquire()
	queue.append(("update", files))
	queueLock.notify()
	queueLock.release()

def queueFilesRemove(files, config=config):
	global index, indexThread, indexLock, queueLock, queue, p
	print "queueing files to remove: " + " | ".join(files)
	theThread = __getIndexThread__()
	
	queueLock.acquire()
	print "queueFilesRemoved: Acquired queueuLock..."
	queue.append(("remove", files))
	queueLock.notify()
	queueLock.release()
	print "queueFilesRemoved: released queueuLock..."

def __indexMain__():
	global index, indexThread, indexLock, queueLock, queue, p
	print "In Index main thread\n"
	print "queue size is: " + str(len(queue))
	while (True):
		queueLock.acquire()
		while (not queue):
			print "index thread waiting for command queue to fill..."
			queueLock.wait()
			print "received notify! going into action..."
		(command, files) = queue.pop(0)
		queueLock.release()
		
		indexLock.acquire()
		print "About to run command: " +command + " with: [" + ",".join(files) + " ]"
		if (command == "update"):
			updateIndexBatch(files)
		elif (command == "remove"):
			removeBatch(files)
			print " removed file."
		indexLock.release()
	
def updateIndex(filename, config=config):
	global p
	if (p):
		p.wait()
	
	p = None
	if (config):
		p = Popen(["recollindex", "-c", config, "-i", "-Z",   filename])
	else:
		p = Popen(["recollindex", "-i", "-Z", filename])

		
	
def updateIndexBatch(filenames, config=config):	
	global index, indexThread, indexLock, queueLock, queue, p
	if (p):
		print "waiting for process to finish..."
		p.wait()
	if (list(filenames) and len(filenames) > 0):
		if (config):
			p = Popen(["recollindex", "-c", config, "-i", "-Z"] + filenames)
		else:
			p = Popen(["recollindex", "-i", "-Z"] + filenames)

def removeFile(filename, config=config):
	
	global index, indexThread, indexLock, queueLock, queue, p
	if (p):
		p.wait()
	if (config):
		p = Popen(["recollindex", "-c", config, "-e",   filename])
	else:
		p = Popen(["recollindex", "-e", filename])
		
def removeBatch(filenames, config=config):
	global index, indexThread, indexLock, queueLock, queue, p
	if (p):
		print "waiting for process to finish..."
		p.wait()
	if (list(filenames) and len(filenames) > 0):
		if (config):
			p = Popen(["recollindex", "-c", config, "-e"] + filenames)
			print "Called remove process!..."
		else:
			p = Popen(["recollindex", "-e"] +filenames)
			print "Called remove process..."
	else:
		print "Don't have any files to remove..."

		
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Re-index files')
	parser.add_argument('filename', metavar='Filename', type=str, help='Filename')
	parser.add_argument('-c', metavar='recoll-config-directory', type=str, help='Recoll Directory')
	args = parser.parse_args()
	updateIndex(args.filename, args.c)
	
