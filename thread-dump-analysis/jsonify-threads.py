#! /usr/bin/env python

import sys
import re
from datetime import datetime
import json

class StackElement:
    def __init__(self, method, line):
        self.method = method
        self.line = line

class Thread:
    def __init__(self, timestamp, name):
        self.timestamp = timestamp
        self.name = name
        self.state = None
        # read locks and locksBlocking appear in with the rest of the stack
        self.readLocksOwned = []
        self.locksBlocking = []
        # write locks appear in "Locked ownable synchronizers"
        self.writeLocksOwned = None
        self.stackElements = []
        self.fullText = ''


# detects line that starts an individual thread dump in a log
dumpStartPattern = re.compile('^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)')

# detects line that starts an individual thread in a log
threadStartPattern = re.compile('^\"(.*)\"')

statePattern = re.compile('.*java.lang.Thread.State: (\w+).*')

locksBlockingPattern = re.compile('.*- waiting on <(\w+)>.*')
readLockOwnedPattern = re.compile('.*- locked <(\w+)>.*')

writeLockOwnedPattern = re.compile('.*- <(\w+)>.*')

lastDate = None
lastThread = None

def flushThread(nextLine):
    global lastThread
    if lastThread:
        print json.dumps(lastThread.__dict__, separators=(',', ':'))
    if nextLine:
        lastThread = Thread(lastDate, threadStartPattern.match(nextLine).group(1))
        lastThread.fullText += nextLine
    else:
        lastThread = None

def appendToThread(nextLine):
    global lastThread
    if not lastThread:
        raise ValueError('oops!')
    lastThread.fullText += nextLine
    if not lastThread.state and len(nextLine.strip()) > 0:
        lastThread.state = statePattern.match(nextLine).group(1)
    elif len(nextLine.strip()) == 0:
        "nothing to do here, just an empty line"
    elif nextLine.strip().startswith('at '):
        "TODO"
    elif locksBlockingPattern.match(nextLine):
        lastThread.locksBlocking.append(locksBlockingPattern.match(nextLine).group(1))
    elif readLockOwnedPattern.match(nextLine):
        lastThread.readLocksOwned.append(readLockOwnedPattern.match(nextLine).group(1))
    elif 'Locked ownable synchronizers' in nextLine:
        lastThread.writeLocksOwned = []
    elif lastThread.writeLocksOwned is not None and "- None" not in nextLine:
        lastThread.writeLocksOwned.append(writeLockOwnedPattern.match(nextLine).group(1))



for line in sys.stdin:
    if dumpStartPattern.match(line):
        lastDate = dumpStartPattern.match(line).group(1)
        flushThread(None)
    elif threadStartPattern.match(line):
        flushThread(line)
    elif lastThread:
        appendToThread(line)

flushThread(None)
