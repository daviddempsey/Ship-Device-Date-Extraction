#!/usr/bin/env python
from parseFunctions import massDateParse
from parseFunctions import multibeamMassDateParse
import sys

if (len(sys.argv) == 1 or sys.argv[1] == '-h'):
  print("\nArguments for massParseDate.py:\n ")
  print("./massParseDate.py [cruise prefix] [any flags]")
  print("DEFAULT: prints SQL, min/max date range, and write log file")
  print("-u: prints SQL")
  print("-m: writes date range update SQL to log file")
  print("-l: writes file update SQL to log file")
  print("-SI: runs on Serial Instruments")
  print("-MB: runs on Multibeam\n")
  quit()


printsql = False
datelog = False
filelog = False
SI = False
MB = False
cruise_prefix = sys.argv[1]


if "-u" in sys.argv:
	printsql = True

if "-m" in sys.argv:
	datelog = True

if "-l" in sys.argv:
	filelog = True

if "-SI" in sys.argv:
  SI = True

if "-MB" in sys.argv:
  MB = True

if SI:
  massDateParse(cruise_prefix, printsql, datelog, filelog)

if MB:
  multibeamMassDateParse(cruise_prefix, printsql, datelog, filelog)
