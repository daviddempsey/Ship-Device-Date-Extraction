#!/usr/bin/env python
"""
This program contains functions needed to successfully create SQL logs of
the starting date of files in filesets and to create min/max cruise range
SQL logs. The code is relatively modular and is designed to handle various
cruises and filesets. As of now, only Roger Revelle and Oceanus are supported.
"""

import sys
import re
import os
from os import listdir
from os.path import isfile, join
from config import *
from scripts import *
import datetime

__author__ = "David Dempsey"
__copyright__ = "Copyright 2019, Rolling Deck to Repository"
__credits__ = "David Dempsey"

__license__ = "No license"
__version__ = "1.0.0"
__maintainer__ = "David Dempsey"
__email__ = "ddempsey@ucsd.edu"
__status__ = "Production"

def dateparser(cruise, path, filepattern, printsql, datelog, filelog):
    """Creates SQL logs of the starting date of files in filesets and also
    creates min/max cruise range SQL logs

    cruise: The cruise ID
    path: The path to the fileset directory
    filepattern: The name of the device usually
    printsql: True if printing to console, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    """

    print("Running dateparser")
    cruise = cruise.upper()
    directory_files = [f for f in listdir(path) if isfile(join(path, f))]
    raw_regex = regex_identifier(cruise, filepattern)
    if (raw_regex):
        directory_files = filter(lambda i: raw_regex.search(i), directory_files)
    else:
        if cruise[:3] == "SKQ":
            pass
        else:
            print("Issue with regex, check identifier")
            return
    if len(directory_files) == 0:
        print("EMPTY")
        return

    mindate,maxdate = datetime.datetime.today(), datetime.datetime(1901, 1, 1)

    sql_datetime_update = []
    sql_startend_update = ''

    for filename in directory_files:
        if (len(filename) >= 8 \
        and (re.match("^[0-9]*$", filename.split('_')[-1][:8]) or \
        re.match("^[0-9]*$", filename.split('T')[0][-8:]))):
            if (filepattern == "multibeam"):
                file_date = filename.split('_')[1]  # grabs date information
                file_time = filename.split('_')[2]
                year = file_date[0:4]
                month = file_date[4:6]
                day = file_date[6:8]
                hour = file_time[0:2]
                minute = file_time[2:4]
                second = file_time[4:6]

            elif cruise[:2] == "OC":
                try:
                    file_date = filename.split('_')[1]
                    file_time = filename.split('-')[-1]
                except:
                    print("error parsing file date/time for OC")
                    return
                year= file_date[0:4]
                month= file_date[4:6]
                day= file_date[6:8]
                hour= file_time[0:2]
                minute= file_time[2:4]
                second= file_time[4:6]

            elif cruise[:3] == "SKQ":
                try:
                    date_time = filename.split('.')[1]
                    file_date = date_time.split('T')[0]
                    file_time = date_time.split('T')[1][:-1]
                except:
                    print("error parsing file date/time for SKQ")
                    return
                year= file_date[0:4]
                month= file_date[4:6]
                day= file_date[6:8]
                hour= file_time[0:2]
                minute= file_time[2:4]
                second = "00"

            else:
                file_date = filename.split('_')[-1]  # grabs date information
                year = file_date[0:4]
                month = file_date[4:6]
                day = file_date[6:8]
                hour = file_date[8:10]
                minute = file_date[10:12]
                second = file_date[12:14]

            filedate = datetime.datetime(int(year), int(month), int(day),
                int(hour), int(minute), int(second))

            if filedate < mindate:
                mindate = filedate
            if filedate > maxdate:
                maxdate = filedate

            sql_datetime_update.append(generate_file_time_sql(year, month, \
                                    day, hour, minute, second, cruise,\
                                        filename))
    sql_startend_update = generate_cruise_startend_sql(mindate, maxdate, \
                                                       cruise)
    daterange2csv(cruise, filepattern,  mindate, maxdate)

    sql_datetime_update.sort()


    logging(printsql, filelog, filepattern, datelog, mindate, maxdate, \
            sql_datetime_update, sql_startend_update, cruise)


def massDateParse(cruise_prefix, printsql, datelog, filelog):
    """
    Runs dateparse on various cruises and instruments

    cruise_prefix: The cruise prefix to run dateparse on
    printsql: True if printing to console, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    """
    cruise_path = path_identifier[cruise_prefix]
    SI_path = "/data/SerialInstruments"
    if cruise_prefix == "HLY":
        SI_path = "/data/sensor/serial_logger"
    elif cruise_prefix == "OC":
        SI_path = "/das"
    elif cruise_prefix == "SKQ":
        SI_path = "/lds/raw"
    full_dir_list = os.listdir(cruise_path)

    if cruise_prefix != "OC": # filters to just .tar directories
        roger_regex = re.compile(r'^' + cruise_prefix + '.*tar$')
        dir_list = filter(lambda i: roger_regex.search(i), full_dir_list)
    elif cruise_prefix == "OC":
        roger_regex = re.compile(r'^' + cruise_prefix.lower() + '\d*\w$')
        dir_list = filter(lambda i: roger_regex.search(i), full_dir_list)

    for cruise in dir_list:
        # needs to be updated for use on R2R
        if cruise_prefix != "OC" and cruise_prefix != "SKQ":
            cruise = cruise[:-4]
        path = cruise_path + cruise + SI_path

        if cruise_prefix == "SKQ":
            path = cruise_path + cruise + "/" + cruise[:-4] + SI_path
            cruise = cruise[:-4]

        cruise = cruise.upper()

        try:
            instruments_list = os.walk(path).next()[1]
        except:
            print("Unable to get instrument list")
            print(path)
            continue
        for instrument in instruments_list:
            if instrument == 'events':
                pass
            instrument_path = path + "/" + instrument
        #    print("CRUISE: " + cruise)
        #    print("INSTRUMENT: " + instrument)
        #    print("PATH: " + instrument_path)
            dateparser(cruise, instrument_path, instrument, printsql, \
                    datelog, filelog)

### NEEDS TO BE UPDATED FOR GDC ###
def multibeamMassDateParse(cruise_prefix, printsql, datelog, filelog):
    """
    Runs dateparse on various cruises for Multibeam

    cruise_prefix: The cruise prefix to run dateparse on
    printsql: True if printing to console, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    """
    full_dir_list = os.listdir("/scratch/r2r/edu.ucsd.sio/")
    roger_regex = re.compile(r'^' + cruise_prefix + '.*tar$')
    dir_list = filter(lambda i: roger_regex.search(i), full_dir_list)

    for cruise in dir_list:
        path = "/scratch/r2r/edu.ucsd.sio/"  \
                    + cruise + "/" + cruise[:-4] + "/data/multibeam/rawdata"

        if (os.path.isdir(path)):
          dateparser(cruise[:-4], path, "multibeam", printsql, datelog, filelog)


def daterange2csv(cruise, device, mindate, maxdate):
    cruise_abbrev = get_ship_abbreviation(cruise)
    f = open("./dateparselogs/dateranges/{}_dateranges.csv".format(cruise_abbrev), "a+")
    if not f.read(1):
        f.write("cruise,devicetype,start_date,end_date\n")
    f.write('{},{},{},{}'.format(cruise, device, mindate, maxdate) + '\n')
    f.close()


def logging(printsql, filelog, filepattern, datelog, mindate,
            maxdate, sql_datetime_update, sql_startend_update, cruise):
    """
    Writes generated SQL out to files or to the console

    printsql: True if printing to console, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    mindate: The minimum file date
    maxdate: The maximum file date
    sql_datetime_update: The SQL generated for updating the date field
    sql_startend_update: The SQL generated for updating cruise bounds
    cruise: The cruise dateparse ran on
    """

    if (filelog or (not filelog and not printsql and not datelog)):
        f = open("./dateparselogs/fileupdate/" + cruise + '_' + filepattern + ".sql", "w+")
        for each in sql_datetime_update:
            f.write(each + '\n')
        f.close()

    if (printsql or (not filelog and not printsql and not datelog)):
        for each in sql_datetime_update:
            print(each)
        print(sql_startend_update)

    if (datelog or (not filelog and not printsql and not datelog)):
        print('MIN DATE: ' + str(mindate))
        print('MAX DATE: ' + str(maxdate))
        f = open("./dateparselogs/minmaxupdate/" + cruise + "_MINMAX_UPDATE.sql", "w+")
        f.write(sql_startend_update)
        f.close();


def generate_file_time_sql(year, month, day, hour, minute, second,
                           cruise, filename):
    """
    Generates SQL for updating the file start time

    year: The parsed year
    month: The parsed month
    day: The parsed day
    hour: The parsed hour
    minute: The parsed minute
    second: The parsed second
    cruise: The cruise ID
    filename: The name of the file
    """

    sql_line = 'UPDATE file SET start_time = \'' + year + '-' \
            + month + '-' + day + ' ' + hour + ':' + minute + ':' + second \
            + '\' WHERE cruise_id = \'' + cruise + '\' AND path LIKE \'%' \
            + filename + '\';'
    return sql_line

def generate_cruise_startend_sql(mindate, maxdate, cruise):
    """
    Generates cruise date range SQL

    mindate: The minimum date
    maxdate: The maximum date
    """

    sql_line = 'UPDATE cruise_issues SET unols_start_date = \'' \
                            + mindate.strftime('%Y-%m-%d %H:%M:%S') \
                            + '\', unols_end_date = \'' \
                            + maxdate.strftime('%Y-%m-%d %H:%M:%S') \
                            + '\' WHERE cruise = \'' + cruise +'\';'
    return sql_line

def regex_identifier(cruise, filepattern):
    """
    Identifies how to parse the file by cruise and filepattern

    cruise: The cruise ID
    filepattern: Usually the device type
    """

    if (cruise[:2] == "RR" or cruise[:2] == "SR" or cruise[:3] == "HLY"):
        if (filepattern == "multibeam"):
            return re.compile(r'\w+.all$')
        else:
            return re.compile(r'\w+.raw$')
    elif (cruise[:2] == "OC"):
        return re.compile(r'\w+.Raw$')

def parse_date_ranges(cruise, directory_files, filepattern):
    """
    Parses the dates of files for min and max dates

    cruise: The cruise ID
    directory_files: All files in the path specified
    filepattern: Usually the device type
    """

    if (cruise[:2] == "RR" or cruise[:2] == "SR" or cruise[:3] == "HLY"):
        if (filepattern == "multibeam"):
            try:
                minmaxdate = directory_files[0].split('_')[1]
                minmaxtime = directory_files[0].split('_')[2]
            except:
                return
            minyear=maxyear= int(minmaxdate[0:4])
            minmonth=maxmonth= int(minmaxdate[4:6])
            minday=maxday= int(minmaxdate[6:8])
            minhour=maxhour= int(minmaxtime[0:2])
            minminute=maxminute= int(minmaxtime[2:4])
            minsecond=maxsecond= int(minmaxtime[4:6])

        else:
            minmaxdate = directory_files[0].split('_')[-1]
            minyear=maxyear= int(minmaxdate[0:4])
            minmonth=maxmonth= int(minmaxdate[4:6])
            minday=maxday= int(minmaxdate[6:8])
            minhour=maxhour= int(minmaxdate[8:10])
            minminute=maxminute= int(minmaxdate[10:12])
            minsecond=maxsecond= int(minmaxdate[12:14])
    elif (cruise[:2] == "OC"):
        try:
            minmaxdate = directory_files[0].split('_')[1]
            minmaxtime = directory_files[0].split('-')[-1]
        except:
            return
        minyear=maxyear= int(minmaxdate[0:4])
        minmonth=maxmonth= int(minmaxdate[4:6])
        minday=maxday= int(minmaxdate[6:8])
        minhour=maxhour= int(minmaxtime[0:2])
        minminute=maxminute= int(minmaxtime[2:4])
        minsecond=maxsecond= int(minmaxtime[4:6])
    mindate = datetime.datetime(minyear, minmonth, minday, minhour, minminute, minsecond)
    maxdate = datetime.datetime(maxyear, maxmonth, maxday, maxhour, maxminute, maxsecond)
    return mindate, maxdate

def parse_file_date(filename, filepattern):
    """
    Parses the file date time based off of the file pattern

    filename: The full file name
    filepattern: Usually the device type
    """

    if (filepattern == "multibeam"):
        file_date = filename.split('_')[1]  # grabs date information
        file_time = filename.split('_')[2]
        year = file_date[0:4]
        month = file_date[4:6]
        day = file_date[6:8]
        hour = file_time[0:2]
        minute = file_time[2:4]
        second = file_time[4:6]

    else:
        file_date = filename.split('_')[-1]  # grabs date information
        year = file_date[0:4]
        month = file_date[4:6]
        day = file_date[6:8]
        hour = file_date[8:10]
        minute = file_date[10:12]
        second = file_date[12:14]

    filedate = datetime.datetime(int(year), int(month), int(day),
        int(hour), int(minute), int(second))
    return filedate

