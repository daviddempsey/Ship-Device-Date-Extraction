#!/usr/bin/env python
from parseFunctions import massDateParse, multibeamMassDateParse, RC_massDateParse, BH_massDateParse
import sys

if (len(sys.argv) == 1 or sys.argv[1] == '-h'):
    print("\nArguments for massParseDate.py:\n ")
    print("./massParseDate.py [cruise prefix] [any flags]")
    print("DEFAULT: prints SQL, min/max date range, and write log file")
    print("-m: writes date range update SQL to log file")
    print("-d: writes date ranges to csv file")
    print("-l: writes file update SQL to log file")
    print("-SI: runs on Serial Instruments")
    print("-MB: runs on Multibeam\n")
    quit()


csvlog = False
datelog = False
filelog = False
SI = False
MB = False
cruise_prefix = sys.argv[1]


if "-d" in sys.argv:
    csvlog = True

if "-m" in sys.argv:
    datelog = True

if "-l" in sys.argv:
    filelog = True

if "-SI" in sys.argv:
    SI = True

if "-MB" in sys.argv:
    MB = True

if cruise_prefix == 'RC':
    RC_massDateParse(printsql, datelog, filelog)

if cruise_prefix == 'BH':
    BH_massDateParse(printsql, datelog, filelog)

if SI:
    massDateParse(cruise_prefix, printsql, datelog, filelog)

if MB:
    multibeamMassDateParse(cruise_prefix, printsql, datelog, filelog)
