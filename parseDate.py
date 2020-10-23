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
from parseFunctions import dateparser, cruiseDateParse, listCruises
from scripts import get_ship_abbreviation
from config import dateparser_by_cruise
#from parseFunctions import multibeamdateparser

__author__ = "David Dempsey"
__copyright__ = "Copyright 2020, Rolling Deck to Repository"
__credits__ = "David Dempsey"

__license__ = "No license"
__version__ = "1.0.1"
__maintainer__ = "David Dempsey"
__email__ = "ddempsey@ucsd.edu"
__status__ = "Development"

if (len(sys.argv) == 1 or sys.argv[1] == '-h'):
    print("\nArguments for parseDate.py:\n ")
    print("./parseDate.py [cruise] [filepattern] [any flags]\n")
    print("DEFAULT: prints SQL, min/max date range, and write log file\n")
    print("-m: writes date range update SQL to log file\n")
    print("-l: writes file update SQL to log file\n")
    print("-d: writes date ranges to csv file\n")
    print("-a: runs on all cruises matching given cruise prefix\n")
    print("-c: runs all devices\n")
    print("-o [new path]: overrides default cruise path structure\n")
    print("-p [dateparser]: used to clarify date parser to use\n")
    quit()


filepattern = sys.argv[2]
cruise_arg = sys.argv[1]
path = os.getcwd() + "/" #must be called in shipment directory
printsql = False
datelog = False
filelog = False
csvlog = False
all_devices = False
dateparser_override = False
all_cruises = False
dateparser = ""
SI_path = ""

for i in range(2, len(sys.argv)):
    flag = sys.argv[i]
    if flag == "-d":
        csvlog = True
    if flag == "-m":
        datelog = True
    if flag == "-l":
        filelog = True
    if flag == "-c":
        all_devices = True
    if flag == "-o":
        SI_path = sys.argv[i+1]
    if flag == "-p":
        dateparser = sys.argv[i+1]
    if flag == "-a":
        all_cruises = True

#if "SerialInstruments" in path:
#   print("recognized as SerialInstrument")
cruise_list = []
if all_cruises:
    cruise_list = listCruises(cruise_arg)
else:
    cruise_list = [cruise_arg]

for cruise in cruise_list:
    cruise_prefix = get_ship_abbreviation(cruise)
    dateparser_selection = dateparser_by_cruise[cruise_prefix]
    if dateparser_selection == 'dateparser':
        if all_devices:
            cruiseDateParse(cruise, path, csvlog, datelog, filelog, SI_path)
        else:
            dateparser(cruise, path, filepattern, csvlog, datelog, filelog, SI_path)
    if dateparser_selection == 'RC_dateparser':
        RC_dateparser(cruise, path, csvlog, datelog, filelog)
    if dateparser_selection == 'BH_dateparser':
        #TODO
        #BH_dateparser(cruise, path, csvlog, datelog, filelog)
#TODO
#else:
#    multibeamdateparser(cruise, path, printsql, datelog, filelog)
