#!/usr/bin/env python
"""
This program contains functions needed to successfully create SQL logs of
the starting date of files in filesets and to create min/max cruise range
SQL logs. The code is relatively modular and is designed to handle various
cruises and filesets. As of now, only Roger Revelle, Oceanus, Sproul,
Sikuliaq, and Healy are supported.
"""

import sys
import re
import os
from os import listdir
from os.path import isfile, join
from config import *
from scripts import *
import datetime
import logging

__author__ = "David Dempsey"
__copyright__ = "Copyright 2019, Rolling Deck to Repository"
__credits__ = "David Dempsey"

__license__ = "No license"
__version__ = "1.0.0"
__maintainer__ = "David Dempsey"
__email__ = "ddempsey@ucsd.edu"
__status__ = "Production"

script_dir = os.getcwd()
os.chdir(log_dir)  # creates log file
logging.basicConfig(format='%(asctime)s %(message)s', filename='%s' %
                    (datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S_') +
                        'parseFunctions.py'),
                    level=logging.INFO)
logging.info('parseFunctions.py executed')
os.chdir(script_dir)

isoDate = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z')


def dateparser(cruise, filepattern, printsql, datelog, filelog):
    """
    Creates SQL logs of the starting date of files in filesets and also
    creates min/max cruise range SQL logs

    cruise: The cruise ID
    path: The path to the fileset directory
    filepattern: The name of the device usually
    printsql: True if printing to console, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    """

    logging.info("Running dateparser on cruise {} and device {}".format(
        cruise, filepattern))

    cruise_prefix = get_ship_abbreviation(cruise)
    cruise_path = path_identifier[cruise_prefix]
    SI_path = find_path(cruise_prefix)
    if (cruise_prefix == "OC"):
        cruise = cruise.lower()
    path = cruise_path + cruise + SI_path
    cruise = cruise.upper()
    path = path + '/' + filepattern
    directory_files = [f for f in listdir(path) if isfile(join(path, f))]
    print(path)
    raw_regex = regex_identifier(cruise, filepattern)
    if (raw_regex):
        directory_files = filter(
            lambda i: raw_regex.search(i), directory_files)
    else:
        if cruise[:3] == "SKQ":
            pass
        else:
            os.chdir(log_dir)
            logging.error("Issue with regex, check identifier")
            os.chdir(script_dir)
            print("Issue with regex, check identifier")
            return
    if len(directory_files) == 0:
        os.chdir(log_dir)
        logging.error("Empty directory or other error for cruise {} and device {}".format(
            cruise, filepattern))
        os.chdir(script_dir)
        print("EMPTY OR ERROR FOR CRUISE {} AND DEVICE {}".format(
            cruise, filepattern))
        return

    mindate, maxdate = datetime.datetime.today(), datetime.datetime(1901, 1, 1)

    sql_datetime_update = []
    sql_startend_update = ''

    for filename in directory_files:
        if (len(filename) >= 8
            and (re.match("^[0-9]*$", filename.split('_')[-1][:8]) or
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

            elif cruise[:2] == "OC" or cruise[:2] == "TN":
                try:
                    file_date = filename.split('_')[1]
                    file_time = filename.split('-')[-1]
                except:
                    os.chdir(log_dir)
                    logging.error("Issue parsing file date/time for OC")
                    os.chdir(script_dir)
                    print("Error parsing file date/time for OC")
                    return
                year = file_date[0:4]
                month = file_date[4:6]
                day = file_date[6:8]
                hour = file_time[0:2]
                minute = file_time[2:4]
                second = file_time[4:6]

            elif cruise[:3] == "SKQ":
                try:
                    date_time = filename.split('.')[1]
                    file_date = date_time.split('T')[0]
                    file_time = date_time.split('T')[1][:-1]
                except:
                    os.chdir(log_dir)
                    logging.error("Issue parsing file date/time for SKQ")
                    os.chdir(script_dir)
                    print("Error parsing file date/time for SKQ")
                    return
                year = file_date[0:4]
                month = file_date[4:6]
                day = file_date[6:8]
                hour = file_time[0:2]
                minute = file_time[2:4]
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

            sql_datetime_update.append(generate_file_time_sql(year, month,
                                                              day, hour, minute, second, cruise,
                                                              filename))
    sql_startend_update = generate_cruise_startend_sql(mindate, maxdate,
                                                       cruise)
    daterange2csv(cruise, filepattern,  mindate, maxdate)

    sql_datetime_update.sort()
    log(printsql, filelog, filepattern, datelog, mindate, maxdate,
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
    SI_path = find_path(cruise_prefix)
    full_dir_list = sorted(os.listdir(cruise_path))

    if cruise_prefix == "OC":  # filters to just .tar directories
        roger_regex = re.compile(r'^' + cruise_prefix.lower() + '\d*\w$')
    elif cruise_prefix == "TN" or cruise_prefix == "SKQ":
        roger_regex = re.compile(r'^' + cruise_prefix + '\d*\w$')
    else:
        roger_regex = re.compile(r'^' + cruise_prefix + '.*tar$')

    dir_list = filter(lambda i: roger_regex.search(i), full_dir_list)

    for cruise in dir_list:
        # needs to be updated for use on R2R
        if cruise_prefix != "OC" and cruise_prefix != "SKQ" and cruise_prefix != "TN":
            cruise = cruise[:-4]
        path = cruise_path + cruise + SI_path

        if cruise_prefix == "SKQ":
            path = cruise_path + cruise + SI_path

        cruise = cruise.upper()

        try:
            instruments_list = os.walk(path).next()[1]
        except:
            os.chdir(log_dir)
            logging.error(
                "Unable to get instrument list for cruise {} at location {}".format(cruise, path))
            os.chdir(script_dir)
            print("Unable to get instrument list for cruise {}".format(cruise))
            print(path)
            continue
        for instrument in instruments_list:
            if instrument == 'events':
                pass
            dateparser(cruise, instrument, printsql,
                       datelog, filelog)


def RC_massDateParse(printsql, datelog, filelog):
    """
    Runs a date parse on Rachel Carson cruises

    cruise_prefix: The cruise prefix to run dateparse on
    printsql: True if printing to console, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    """
    cruise_path = path_identifier['RC']
    # SI_path = find_path(cruise_prefix)
    full_dir_list = sorted(os.listdir(cruise_path))

    regex1 = re.compile(r'^' + 'RC')
    regex2 = re.compile(r'scs$')
    dir_list = filter(lambda i: regex1.search(i), full_dir_list)
    for cruise in dir_list:
        # needs to be updated for use on R2R
        # parses just scs subdirectories
        full_sub_dir_list = sorted(os.listdir(cruise_path + cruise))
        subdir_list = filter(lambda i: regex2.search(i), full_sub_dir_list)
        regex3 = regex_identifier(cruise)
        for scs_dir in subdir_list:
            path = cruise_path + cruise + '/' + scs_dir
            directory_files = [f for f in listdir(
                path) if isfile(join(path, f))]
            directory_files = filter(
                lambda i: regex3.search(i), directory_files)
            if len(directory_files) == 0:
                os.chdir(log_dir)
                logging.error(
                    "Empty directory or other error for cruise {}".format(cruise))
                os.chdir(script_dir)
                print("EMPTY OR ERROR FOR CRUISE {}".format(cruise))
                continue

            mindate, maxdate = datetime.datetime.today(), datetime.datetime(1901, 1, 1)

            sql_datetime_update = []
            sql_startend_update = ''

            saved_filepattern = ''
            directory_files.sort()

            for filename in directory_files:
                filepattern = filename.split('_')[0]
                if saved_filepattern == '':
                    saved_filepattern = filepattern
                if filepattern != saved_filepattern:
                    sql_datetime_update.sort()
                    daterange2csv(cruise, filepattern,  mindate, maxdate)
                    log(printsql, filelog, saved_filepattern, datelog, mindate, maxdate,
                        sql_datetime_update, sql_startend_update, cruise)
                    sql_datetime_update = []
                    saved_filepattern = filepattern
                    mindate, maxdate = datetime.datetime.today(), datetime.datetime(1901, 1, 1)
                iso_date = filename.split('_')[1].split('.')[0]
                if (re.match("^[0-9]*$", iso_date[:8])):
                    try:
                        file_date = iso_date.split('-')[0]
                        file_time = iso_date.split('-')[1]
                    except:
                        os.chdir(log_dir)
                        logging.error("Issue parsing file date/time for RC")
                        os.chdir(script_dir)
                        print("Error parsing file date/time for RC")
                        return
                    year = file_date[0:4]
                    month = file_date[4:6]
                    day = file_date[6:8]
                    hour = file_time[0:2]
                    minute = file_time[2:4]
                    second = "00"

                    filedate = datetime.datetime(int(year), int(month), int(day),
                                                 int(hour), int(minute), int(second))

                    if filedate < mindate:
                        mindate = filedate
                    if filedate > maxdate:
                        maxdate = filedate

                    sql_datetime_update.append(generate_file_time_sql(year, month,
                                                                      day, hour, minute, second, cruise,
                                                                      filename))
            sql_startend_update = generate_cruise_startend_sql(mindate, maxdate,
                                                               cruise)
            daterange2csv(cruise, filepattern,  mindate, maxdate)

            sql_datetime_update.sort()
            log(printsql, filelog, filepattern, datelog, mindate, maxdate,
                sql_datetime_update, sql_startend_update, cruise)


def BH_massDateParse(printsql, datelog, filelog):
    """
    Runs a date parse on Blue Heron cruises

    cruise_prefix: The cruise prefix to run dateparse on
    printsql: True if printing to console, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    """
    cruise_path = path_identifier['BH']
    # SI_path = find_path(cruise_prefix)
    full_dir_list = sorted(os.listdir(cruise_path))

    regex1 = re.compile(r'^' + 'BH')
    regex2 = re.compile(r'ADCP')
    dir_list = filter(lambda i: regex1.search(i), full_dir_list)

    for cruise in dir_list:
        full_sub_dir_list = sorted(os.listdir(cruise_path + cruise))
        subdir_list = filter(lambda i: regex2.search(i), full_sub_dir_list)
        regex3 = regex_identifier(cruise)

        for adcp_dir in subdir_list:
            path = cruise_path + cruise + '/' + adcp_dir + "/raw/gp90"
            directory_files = [f for f in listdir(
                path) if isfile(join(path, f))]
            directory_files = filter(
                lambda i: regex3.search(i), directory_files)
            if len(directory_files) == 0:
                os.chdir(log_dir)
                logging.error(
                    "Empty directory or other error for cruise {}".format(cruise))
                os.chdir(script_dir)
                print("EMPTY OR ERROR FOR CRUISE {}".format(cruise))
                return

            mindate, maxdate = datetime.datetime.today(), datetime.datetime(1901, 1, 1)

            sql_datetime_update = []
            sql_startend_update = ''

            saved_filepattern = ''  # TODO: rename?
            directory_files.sort()

            for filename in directory_files:
                filepattern = filename.split('_')[0]
                if saved_filepattern == '':
                    saved_filepattern = filepattern
                if filepattern != saved_filepattern:
                    sql_datetime_update.sort()
                    daterange2csv(cruise, filepattern,  mindate, maxdate)
                    log(printsql, filelog, saved_filepattern, datelog, mindate, maxdate,
                        sql_datetime_update, sql_startend_update, cruise)
                    sql_datetime_update = []
                    saved_filepattern = filepattern
                    mindate, maxdate = datetime.datetime.today(), datetime.datetime(1901, 1, 1)
                julian_date = filename[4:10]
                second = int(filename[11:16])
                try:
                    julian_date = julian_date.split(
                        '_')[0] + julian_date.split('_')[1]
                except:
                    os.chdir(log_dir)
                    logging.error("Issue parsing file date/time for RC")
                    os.chdir(script_dir)
                    print("Error parsing file date/time for RC")
                    return

                filedate = datetime.datetime.strptime(
                    julian_date, '%y%j')
                year = filedate.year
                month = filedate.month
                day = filedate.day
                minute, second = divmod(second, 60)
                hour, minute = divmod(minute, 60)

                if filedate < mindate:
                    mindate = filedate
                if filedate > maxdate:
                    maxdate = filedate

                sql_datetime_update.append(generate_file_time_sql(year, month,
                                                                  day, hour, minute, second, cruise,
                                                                  filename))
            sql_startend_update = generate_cruise_startend_sql(mindate, maxdate,
                                                               cruise)
            daterange2csv(cruise, "gp90",  mindate, maxdate)

            sql_datetime_update.sort()
            log(printsql, filelog, "gp90", datelog, mindate, maxdate,
                sql_datetime_update, sql_startend_update, cruise)


def BH_massDateParse(cruise_prefix, printsql, datelog, filelog):
    """
    Runs a date parse on Blue Heron cruises

    cruise_prefix: The cruise prefix to run dateparse on
    printsql: True if printing to console, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    """
    cruise_path = path_identifier['BH']
    # SI_path = find_path(cruise_prefix)
    full_dir_list = sorted(os.listdir(cruise_path))

    regex1 = re.compile(r'^' + cruise_prefix)
    regex2 = re.compile(r'scs$')
    dir_list = filter(lambda i: regex1.search(i), full_dir_list)

    for cruise in dir_list:
        # needs to be updated for use on R2R
        # parses just scs subdirectories
        full_sub_dir_list = sorted(os.listdir(cruise_path + cruise))
        subdir_list = filter(lambda i: regex2.search(i), full_sub_dir_list)
        regex3 = regex_identifier(cruise)

        for scs_dir in subdir_list:
            path = cruise_path + cruise + '/' + scs_dir
            directory_files = [f for f in listdir(
                path) if isfile(join(path, f))]
            directory_files = filter(
                lambda i: regex3.search(i), directory_files)
            if len(directory_files) == 0:
                os.chdir(log_dir)
                logging.error(
                    "Empty directory or other error for cruise {}".format(cruise))
                os.chdir(script_dir)
                print("EMPTY OR ERROR FOR CRUISE {}".format(cruise))
                return

            mindate, maxdate = datetime.datetime.today(), datetime.datetime(1901, 1, 1)

            sql_datetime_update = []
            sql_startend_update = ''

            saved_filepattern = ''
            directory_files.sort()

            for filename in directory_files:
                filepattern = filename.split('_')[0]
                if saved_filepattern == '':
                    saved_filepattern = filepattern
                if filepattern != saved_filepattern:
                    sql_datetime_update.sort()
                    daterange2csv(cruise, filepattern,  mindate, maxdate)
                    log(printsql, filelog, saved_filepattern, datelog, mindate, maxdate,
                        sql_datetime_update, sql_startend_update, cruise)
                    sql_datetime_update = []
                    saved_filepattern = filepattern
                    mindate, maxdate = datetime.datetime.today(), datetime.datetime(1901, 1, 1)
                iso_date = filename.split('_')[1].split('.')[0]
                if (re.match("^[0-9]*$", iso_date[:8])):
                    try:
                        file_date = iso_date.split('-')[0]
                        file_time = iso_date.split('-')[1]
                    except:
                        os.chdir(log_dir)
                        logging.error("Issue parsing file date/time for RC")
                        os.chdir(script_dir)
                        print("Error parsing file date/time for RC")
                        return
                    year = file_date[0:4]
                    month = file_date[4:6]
                    day = file_date[6:8]
                    hour = file_time[0:2]
                    minute = file_time[2:4]
                    second = "00"

                    filedate = datetime.datetime(int(year), int(month), int(day),
                                                 int(hour), int(minute), int(second))

                    if filedate < mindate:
                        mindate = filedate
                    if filedate > maxdate:
                        maxdate = filedate

                    sql_datetime_update.append(generate_file_time_sql(year, month,
                                                                      day, hour, minute, second, cruise,
                                                                      filename))
            sql_startend_update = generate_cruise_startend_sql(mindate, maxdate,
                                                               cruise)
            daterange2csv(cruise, filepattern,  mindate, maxdate)

            sql_datetime_update.sort()

            log(printsql, filelog, filepattern, datelog, mindate, maxdate,
                sql_datetime_update, sql_startend_update, cruise)


def cruiseDateParse(cruise, printsql, datelog, filelog):
    """
    Runs dateparse on all instruments of a single cruise

    cruise: The cruise to run dateparse on
    printsql: True if printing to console, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    """
    cruise = cruise.upper()
    cruise_prefix = get_ship_abbreviation(cruise)
    cruise_path = path_identifier[cruise_prefix]
    SI_path = find_path(cruise_prefix)
    path = cruise_path + cruise + SI_path
    #if cruise_prefix == "SKQ":
        #path = cruise_path + cruise + ".tar/" + cruise + SI_path

    cruise = cruise.upper()
    try:
        instruments_list = os.walk(path).next()[1]
    except:
        os.chdir(log_dir)
        logging.error(
            "Unable to get instrument list for cruise {} at location {}".format(cruise, path))
        os.chdir(script_dir)
        print("Unable to get instrument list for cruise {}".format(cruise))
        print(path)
    for instrument in instruments_list:
        if instrument == 'events':
            pass
        dateparser(cruise, instrument, printsql,
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
            dateparser(cruise[:-4], path, "multibeam",
                       printsql, datelog, filelog)


def daterange2csv(cruise, device, mindate, maxdate):
    if cruise[:2] == 'RC' and len(cruise) == 5:
        cruise = cruise[:2] + '0' + cruise[2:]
    cruise_abbrev = get_ship_abbreviation(cruise)
    f = open(
        "./dateparselogs/dateranges/{}_{}_dateranges.csv".format(isoDate, cruise_abbrev), "a+")
    if not f.read(1):
        f.write("cruise,devicetype,start_date,end_date\n")
    f.write('{},{},{},{}'.format(cruise, device, mindate, maxdate) + '\n')
    f.close()


def log(printsql, filelog, filepattern, datelog, mindate,
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
        os.chdir(log_dir)
        logging.info("Creating SQL to update file date information.")
        os.chdir(script_dir)
        f = open("./dateparselogs/fileupdate/" +
                 cruise + '_' + filepattern + ".sql", "w+")
        for each in sql_datetime_update:
            f.write(each + '\n')
        f.close()

    if (printsql or (not filelog and not printsql and not datelog)):
        for each in sql_datetime_update:
            print(each)
        print(sql_startend_update)

    if (datelog or (not filelog and not printsql and not datelog)):
        os.chdir(log_dir)
        logging.info("Creating SQL to update cruise min and max file range.")
        os.chdir(script_dir)
        print('MIN DATE: ' + str(mindate))
        print('MAX DATE: ' + str(maxdate))
        f = open("./dateparselogs/minmaxupdate/" +
                 cruise + "_MINMAX_UPDATE.sql", "w+")
        f.write(sql_startend_update)
        f.close()


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
    sql_line = 'UPDATE file SET start_time = \'' + str(year) + '-' \
        + str(month) + '-' + str(day) + ' ' + str(hour) + ':' + str(minute) + ':' + str(second) \
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
        + '\' WHERE cruise = \'' + cruise + '\';'
    return sql_line


def regex_identifier(cruise, filepattern=''):  # TODO: Clean this method
    """
    Identifies how to parse the file by cruise and filepattern

    cruise: The cruise ID
    filepattern: Usually the device type
    """

    if (cruise[:2] == "RR" or cruise[:2] == "SR" or cruise[:3] == "HLY"
            or cruise[:2] == "SP"):
        if (filepattern == "multibeam"):
            return re.compile(r'\w+.all$')
        else:
            return re.compile(r'\w+.raw$')
    elif (cruise[:2] == "OC" or cruise[:2] == "RC" or cruise[:2] == "TN"):
        return re.compile(r'\w+.Raw$')
    elif (cruise[:2] == "BH"):
        return re.compile(r'\w+.gps$')


def find_path(cruise_prefix):
    """
    Finds the path of the ship given a cruise prefix

    cruise_prefix: Prefix of vessel name
    """

    cruise_path = path_identifier[cruise_prefix]
    SI_path = "/data/SerialInstruments"
    if cruise_prefix == "HLY":
        SI_path = "/data/sensor/serial_logger"
    elif cruise_prefix == "OC":
        SI_path = "/das"
    elif cruise_prefix == "SKQ":
        SI_path = "/lds/raw"
    elif cruise_prefix == "SP":
        SI_path = "/SerialInstruments"
    elif cruise_prefix == "TN":
        SI_path = "/scs"

    return SI_path
