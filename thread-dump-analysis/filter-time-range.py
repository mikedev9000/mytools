#! /usr/bin/env python

import sys
import re
from datetime import datetime

def toDate(value):
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

startDate = toDate(sys.argv[1])
endDate = toDate(sys.argv[2])

# detects line that starts an individual thread dump in a log
entryStartPattern = re.compile('^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)')

started = False

for line in sys.stdin:
    if not started:
        match = entryStartPattern.match(line)
        if match and toDate(match.group(1)) >= startDate:
            started = True
            sys.stdout.write(line)
    elif started:
        match = entryStartPattern.match(line)
        if match and toDate(match.group(1)) > endDate:
            break
        else:
            sys.stdout.write(line)
