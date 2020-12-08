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


def dateparser(cruise, shipment_path, filepattern, csvlog, datelog, filelog, SI_path=""):
    """
    Creates SQL logs of the starting date of files in filesets and also
    creates min/max cruise range SQL logs

    cruise: The cruise ID
    path: The path to the fileset directory
    filepattern: The name of the device usually
    csvlog: True if saving CSV to log file, false otherwise
    datelog: True if creating SQL log of min/max cruise range, false otherwise
    filelog: True if logging file update SQL to files, false otherwise
    """

    logging.info("Running dateparser on cruise {0} and device {1}".format(
        cruise, filepattern))

    cruise_prefix = get_ship_abbreviation(cruise)
    if SI_path == "":
        SI_path = find_path(cruise_prefix)
    if (cruise_prefix == "OC"):
        cruise = cruise.lower()
    path = shipment_path + cruise + SI_path
    cruise = cruise.upper()
    path = path + '/' + filepattern
    print(path)
    directory_files = [f for f in listdir(path) if isfile(join(path, f))]
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
        logging.error("Empty directory or other error for cruise {0} and device {1}".format(
            cruise, filepattern))
        os.chdir(script_dir)
        print("EMPTY OR ERROR FOR CRUISE {0} AND DEVICE {1}".format(
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

    if csvlog or (not filelog and not csvlog and not datelog):
        daterange2csv(cruise, filepattern,  mindate, maxdate)

    sql_datetime_update.sort()
    log(filelog, filepattern, datelog, mindate, maxdate,
        sql_datetime_update, sql_startend_update, cruise)


def listCruises(cruise_prefix, cruise_path):
    """
    Returns a list of cruises given a cruise prefix

    cruise_prefix: The cruise prefix to run dateparse on
    """
    SI_path = find_path(cruise_prefix)
    full_dir_list = sorted(os.listdir(cruise_path))

    if cruise_prefix == "OC":  # filters to just .tar directories
        roger_regex = re.compile(r'^' + cruise_prefix.lower() + '\d*\w$')
    elif cruise_prefix == "TN" or cruise_prefix == "SKQ" or cruise_prefix == "SR"\
            or cruise_prefix == "RR" or cruise_prefix == "SP":
        roger_regex = re.compile(r'^' + cruise_prefix + '\d*\w$')
    elif cruise_prefix == "RC":
        roger_regex = re.compile(r'^' + 'RC')
    elif cruise_prefix == "BH":
        roger_regex = re.compile(r'^' + 'BH')
    else:
        roger_regex = re.compile(r'^' + cruise_prefix + '.*tar$')
        #roger_regex = re.compile(r'^' + cruise_prefix + '\d*\w$')

    print(full_dir_list)
    dir_list = filter(lambda i: roger_regex.search(i), full_dir_list)
    print(dir_list)
    return dir_list


def RC_dateparser(cruise, shipment_path, csvlog, datelog, filelog):
    """
    Runs a date parse on Rachel Carson cruises (or cruises with similar structure)

    cruise_prefix: The cruise prefix to run dateparse on
    csvlog: True if printing to console, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwis
    """
    regex_scs = re.compile(r'scs$')
    full_sub_dir_list = sorted(os.listdir(shipment_path + cruise))
    subdir_list = filter(lambda i: regex_scs.search(i), full_sub_dir_list)
    regex_filetype = regex_identifier(cruise)
    for scs_dir in subdir_list:
        path = shipment_path + cruise + '/' + scs_dir
        directory_files = [f for f in listdir(
            path) if isfile(join(path, f))]
        directory_files = filter(
            lambda i: regex_filetype.search(i), directory_files)
        if len(directory_files) == 0:
            os.chdir(log_dir)
            logging.error(
                "Empty directory or other error for cruise {0}".format(cruise))
            os.chdir(script_dir)
            print("EMPTY OR ERROR FOR CRUISE {0}".format(cruise))
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
                if csvlog or (not filelog and not csvlog and not datelog):
                    daterange2csv(cruise, filepattern,  mindate, maxdate)
                log(filelog, saved_filepattern, datelog, mindate, maxdate,
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


def BH_dateparser(cruise, shipment_path, csvlog, datelog, filelog):
    """
    Runs a date parse on Blue Heron cruises

    cruise_prefix: The cruise prefix to run dateparse on
    csvlog: True if logging to csv, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    """
    regex_adcp = re.compile(r'ADCP')

    full_sub_dir_list = sorted(os.listdir(shipment_path + cruise))
    subdir_list = filter(lambda i: regex_adcp.search(i), full_sub_dir_list)
    regex_filetype = regex_identifier(cruise)

    for adcp_dir in subdir_list:
        path = shipment_path + cruise + '/' + adcp_dir + "/raw/gp90"
        directory_files = [f for f in listdir(
            path) if isfile(join(path, f))]
        directory_files = filter(
            lambda i: regex_filetype.search(i), directory_files)
        if len(directory_files) == 0:
            os.chdir(log_dir)
            logging.error(
                "Empty directory or other error for cruise {0}".format(cruise))
            os.chdir(script_dir)
            print("EMPTY OR ERROR FOR CRUISE {0}".format(cruise))
            return

        mindate, maxdate = datetime.datetime.today(), datetime.datetime(1901, 1, 1)

        sql_datetime_update = []
        sql_startend_update = ''

        directory_files.sort()

        for filename in directory_files:
            filepattern = filename.split('_')[0]
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
        if csvlog or (not filelog and not csvlog and not datelog):
            daterange2csv(cruise, "gp90",  mindate, maxdate)

        sql_datetime_update.sort()
        log(filelog, "gp90", datelog, mindate, maxdate,
            sql_datetime_update, sql_startend_update, cruise)



def cruiseDateParse(cruise, shipment_path, csvlog, datelog, filelog, SI_path=""):
    """
    Runs dateparse on all instruments of a single cruise

    cruise: The cruise to run dateparse on
    csvlog: True if logging dates to csv log file, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    """
    cruise_prefix = get_ship_abbreviation(cruise.upper())
    if SI_path == "":
        SI_path = find_path(cruise_prefix)
    path = shipment_path + cruise + SI_path

    try:
        instruments_list = os.walk(path).next()[1]
    except:
        os.chdir(log_dir)
        logging.error(
            "Unable to get instrument list for cruise {0} at location {1}".format(cruise, path))
        os.chdir(script_dir)
        print("Unable to get instrument list for cruise {0}".format(cruise))
        print(path)
        return
    for instrument in instruments_list:
        if instrument == 'events':
            pass
        dateparser(cruise, shipment_path, instrument, csvlog,
                   datelog, filelog, SI_path)


def daterange2csv(cruise, device, mindate, maxdate):
    if cruise[:2] == 'RC' and len(cruise) == 5:
        cruise = cruise[:2] + '0' + cruise[2:]
    cruise_abbrev = get_ship_abbreviation(cruise)
    f = open(
        "./{0}_{1}_dateranges.csv".format(isoDate, cruise_abbrev), "a+")
    if not f.read(1):
        f.write("cruise,devicetype,start_date,end_date\n")
    f.write('{0},{1},{2},{3}'.format(cruise, device, mindate, maxdate) + '\n')
    f.close()


def log(filelog, filepattern, datelog, mindate,
        maxdate, sql_datetime_update, sql_startend_update, cruise):
    """
    Writes generated SQL out to files or to the console

    csvlog: True if logging dates to csv log file, false otherwise
    datelog: True if creating SQL of min/max cruise range, false otherwise
    filelog: True if logging SQL to files, false otherwise
    mindate: The minimum file date
    maxdate: The maximum file date
    sql_datetime_update: The SQL generated for updating the date field
    sql_startend_update: The SQL generated for updating cruise bounds
    cruise: The cruise dateparse ran on
    """

    if (filelog):
        os.chdir(log_dir)
        logging.info("Creating SQL to update file date information.")
        os.chdir(script_dir)
        f = open("./" +
                 cruise + '_' + filepattern + ".sql", "w+")
        for each in sql_datetime_update:
            f.write(each + '\n')
        f.close()

    if (datelog):
        os.chdir(log_dir)
        logging.info("Creating SQL to update cruise min and max file range.")
        os.chdir(script_dir)
        print('MIN DATE: ' + str(mindate))
        print('MAX DATE: ' + str(maxdate))
        f = open("./" +
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


def regex_identifier(cruise, filepattern=''):
    """
    Identifies how to parse the file by cruise and filepattern

    cruise: The cruise ID
    filepattern: Usually the device type
    """
    if filepattern == "multibeam":
        return re.compile(r'\w+.all$')
    else:
        ship_abbreviation = get_ship_abbreviation(cruise)
        regex = regex_by_cruise[ship_abbreviation]
        return re.compile(regex)


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


def get_ship_abbreviation(cruise):  # returns 2-letter ship ID
    ship_abbreviation = ''

    for char in cruise: # iterates through cruise ID
        if char.isdigit() is False: # appends letters
            ship_abbreviation = ship_abbreviation + char
        else: # ignores digits
            break

    return ship_abbreviation
