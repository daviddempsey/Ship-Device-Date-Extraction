#!/usr/bin/env python
"""
Writes out date update SQL for all files of a specified type for a cruise.
The program takes a cruise ID, filepattern of a fileset, the local path
to that fileset, and flags specifying whether to print SQL to console,
write date update SQL to a file, or to write the min/max date update SQL
to a file. The default option is to do all three.
"""

import sys
from parseFunctions import dateparser
#from parseFunctions import multibeamdateparser

__author__ = "David Dempsey"
__copyright__ = "Copyright 2019, Rolling Deck to Repository"
__credits__ = "David Dempsey"

__license__ = "No license"
__version__ = "1.0.0"
__maintainer__ = "David Dempsey"
__email__ = "ddempsey@ucsd.edu"
__status__ = "Production"

if (len(sys.argv) == 1 or sys.argv[1] == '-h'):
	print("\nArguments for parseDate.py:\n ")
	print("./parseDate.py [cruise] [filepattern] [path] [any flags]")
	print("DEFAULT: prints SQL, min/max date range, and write log file")
	print("-u: prints SQL")
	print("-m: writes date range update SQL to log file")
	print("-l: writes file update SQL to log file\n")
	quit()


path = sys.argv[3]
filepattern = sys.argv[2]
cruise = sys.argv[1]
printsql = False
datelog = False
filelog = False


if "-u" in sys.argv:
	printsql = True

if "-m" in sys.argv:
	datelog = True

if "-l" in sys.argv:
	filelog = True

#if "SerialInstruments" in path:
#   print("recognized as SerialInstrument")
dateparser(cruise, path, filepattern, printsql, datelog, filelog)

#else:
#    multibeamdateparser(cruise, path, printsql, datelog, filelog)
