import subprocess
import argparse
from subprocess import Popen

#CHANGE THE FOLLOWING LINE TO YOUR RECOLL DIRECTORY
#config='/path/to/.recoll'
index = False

def updateIndex(filename, config=config):
	
	p = None
	if (config):
		p = Popen(["recollindex", "-c", config, "-i", "-Z",   filename])
	else:
		p = Popen(["recollindex", "-i", "-Z", filename])

		
	
def updateIndexBatch(filenames, config=config):	
	p = None
	if (list(filenames) and len(filenames) > 0):
		for f in filenames:
			if (config):
				p = Popen(["recollindex", "-c", config, "-i", "-Z"] + filenames)
			else:
				p = Popen(["recollindex", "-i", "-Z"] + filenames)

def removeFile(filename, config=config):
	p = None
	if (config):
		p = Popen(["recollindex", "-c", config, "-e",   filename])
	else:
		p = Popen(["recollindex", "-e", filename])
		
def removeBatch(filenames, config=config):
	p = None
	if (list(filenames) and len(filenames) > 0):
		if (config):
			p = Popen(["recollindex", "-c", config, "-e"] + filenames)
		else:
			p = Popen(["recollindex", "-e"] +filenames)

		
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Re-index files')
	parser.add_argument('filename', metavar='Filename', type=str, help='Filename')
	parser.add_argument('-c', metavar='recoll-config-directory', type=str, help='Recoll Directory')
	args = parser.parse_args()
	updateIndex(args.filename, args.c)
	
