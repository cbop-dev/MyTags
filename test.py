#!/usr/bin/python
import unittest
import sys
import os
#import os.path

paths = ["src","lib", "tests"]
for i in paths:
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/" + i)
#print sys.path

import mytags.MyTagsUtils as mt

import mytagtests

mytagtests.myTagTests().runTest()

