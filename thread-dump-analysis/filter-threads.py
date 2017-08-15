#! /usr/bin/env python

import sys
import re
from datetime import datetime

# detects line that starts an individual thread dump in a log
dumpStartPattern = re.compile('^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)')

# detects line that starts an individual thread in a log
threadStartPattern = re.compile('^\"')

f = '.*(' + '|'.join(sys.argv[1:]) + ').*'
inclusionPattern = re.compile(f, re.DOTALL)

lastThread = None

def flushThread(nextLine):
    global lastThread
    if lastThread and inclusionPattern.match(lastThread):
        sys.stdout.write(lastThread)
    lastThread = nextLine

def appendToThread(nextLine):
    global lastThread
    if not lastThread:
        lastThread = ''
    lastThread = lastThread + nextLine

for line in sys.stdin:
    if dumpStartPattern.match(line):
        sys.stdout.write(line)
        flushThread(None)
    elif threadStartPattern.match(line):
        flushThread(line)
    elif lastThread:
        appendToThread(line)

flushThread(None)
