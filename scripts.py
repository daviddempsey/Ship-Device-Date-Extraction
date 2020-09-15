#!/usr/bin/env python

# scripts.py
# Created by David Dempsey
# email: ddempsey@ucsd.edu
#
# ## Purpose:
# Miscellaneous functions used across multiple scripts.
# Be mindful editing these

from config import *
from datetime import datetime
import os


def get_ship_abbreviation(cruise):  # returns 2-letter ship ID
    ship_abbreviation = ''

    for char in cruise: # iterates through cruise ID
        if char.isdigit() is False: # appends letters
            ship_abbreviation = ship_abbreviation + char
        else: # ignores digits
            break

    return ship_abbreviation


def list_from_abbreviation(args):  # lists cruises by ship
    if 'SKQ' in args: # lists SKQ cruises
        if '-v' in args:
            print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S: ')
                  + "Listing SKQ cruises")

        list_SKQ() # lists out all possible cruises that can be ran

        if '-v' in args:
            print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S: ')
                  + "Finished listing SKQ cruises")

    else: # lists SIO cruises (needs to be updates to include other orgs)
        for each in args: # iterates through arguments
            if each in scripps_ships: # checks if SIO ship
                ship = ships[each] # identifies ship
                if '-v' in args:
                    print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S: ')
                          + "Listing SIO cruises")

                    # lists out all SIO cruises that can be rsynced
                list_SIO(ship)

                if '-v' in args:
                    print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S: ')
                              + "Finished listing SIO cruises")

            else: # unknown organization, cannot be listed
                if '-v' in args:
                    print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S: ')
                          + "Unknown organization parameter")


def list_SKQ():  # lists Sikuliaq cruises
    os.system('rsync share.sikuliaq.alaska.edu::SKQDATA/')


def list_SIO(ship):  # lists Scripps cruises by ship
    os.system('rsync --archive \
    rsync://somts.ucsd.edu/cruise_data/{}'.format(ship))


def extract_tar_bz2(cruise): # extracts tarred cruise data
    tar_file = cruise + '.tar.bz2' # file name of zipped tar
    ship_abbreviation = get_ship_abbreviation(cruise) # grabs ship abbrev
    ship = ships[ship_abbreviation] # gets ship name
    output = 0 # stores output of tar operation

    # extracts zipped tar of Scripps vessel
    if ship_abbreviation in scripps_ships:
        os.chdir('{}/{}'.format(datadir_local, ship))
        output = os.system('tar xjf ' + tar_file)
        if output != 0:  # checks if there was an error extracting the tar.bz2
            return 1
        os.chdir('{}/{}/{}'.format(datadir_local, ship, cruise))
        os.system('chmod -R +rw ./*')  # changes permissions on files
        os.system('chgrp -R gdc ./*')
    else:
        print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S: ') +
              'Cannot extract tar.bz2 file for specified cruise')
        output = 1
    return output


def unbzip(cruise_file_path):  # unbzips a .bz2 file
    os.system('bzip2 -dk {}'.format(cruise_file_path))


def auto_identify(cruise):
    ship = ships[get_ship_abbreviation(cruise).upper()]
    org = org_from_cruise[get_ship_abbreviation(cruise).upper()]
    return ship, org


def read_from_list(list, function, args):
    os.chdir(codedir);
    file = open('{}'.format(list), 'r')  # opens list of cruises
    list = [line.rstrip('\n') for line in file]   # splits cruises into a list
    if '-v' in args:
        print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S: ') +
              "Pulling cruises from list")
    for cruise in list:
        function(cruise)
    if '-v' in args:
        print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S: ') +
              "Script finished executing")
