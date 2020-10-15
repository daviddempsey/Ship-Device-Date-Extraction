#!/usr/bin/env python
"""
Writes out date update SQL for all files of a specified type for a cruise.
The program takes a cruise ID, filepattern of a fileset, the local path
to that fileset, and flags specifying whether to print SQL to console,
write date update SQL to a file, or to write the min/max date update SQL
to a file. The default option is to do all three.
"""

import sys
import os
from parseFunctions import dateparser, cruiseDateParse
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
    print("./parseDate.py [cruise] [filepattern] [any flags]")
    print("DEFAULT: prints SQL, min/max date range, and write log file")
    print("-m: writes date range update SQL to log file")
    print("-l: writes file update SQL to log file")
    print("-d: writes date ranges to csv file")
    print("-c: runs all devices for a single cruise\n")
    quit()


filepattern = sys.argv[2]
cruise = sys.argv[1]
path = os.getcwd() + "/" #must be called in shipment directory
printsql = False
datelog = False
filelog = False
csvlog = False
all_devices = False


if "-d" in sys.argv:
    csvlog = True

if "-m" in sys.argv:
    datelog = True

if "-l" in sys.argv:
    filelog = True

if "-c" in sys.argv:
    all_devices = True

#if "SerialInstruments" in path:
#   print("recognized as SerialInstrument")
if all_devices:
    cruiseDateParse(cruise, path, csvlog, datelog, filelog)
else:
    dateparser(cruise, path, filepattern, csvlog, datelog, filelog)

#else:
#    multibeamdateparser(cruise, path, printsql, datelog, filelog)
