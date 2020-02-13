# config.py
# Created by David Dempsey
# email: ddempsey@ucsd.edu
#
# ## Purpose:
# Important information for R2R scripts. Be mindful changing these values.

HLY_cruise_path = "/mnt/gdc/data/r2r/scratch/mil.uscg/"
SIO_cruise_path = "/mnt/gdc/data/r2r/scratch/edu.ucsd.sio/"
OC_cruise_path = "/mnt/gdc/data/r2r/scratch/edu.oregonstate/"
codedir = "/mnt/gdc/code/scripts/"
operator_uaf = "edu.uaf"
operator_sio = "edu.ucsd.sio/SR_2019"
operator_hly = "mil.uscg/2019"
operator_osu = "edu.oregonstate"
shipment_id = "100010"
scratch_dir = "/mnt/gdc/data/r2r/scratch/"
# datadir_local = scratch_dir + operator_uaf + shipment_id
datadir_local = scratch_dir #CHANGE!!
datadir_SIO = "/localdisk2/R2R/data"
datadir_OSU = "/mnt/data07/2019"
datadir_UAF = "SKQDATA/"
log_dir = "/mnt/gdc/code/scripts/log_files"
archive_dir = "/localdisk2/R2R/archive"
size_per_part = '5000M'
ships = {
    'SP': 'Sproul',
    'RR': 'Revelle',
    'SR': 'SallyRide',
    'HLY': 'Healy',
    'FL': 'Flip',
    'OC': 'Oceanus',
    'SKQ': 'Sikuliaq'
}
ship_directory = {
    'Healy': '/mnt/gdc/data/r2r/scratch/mil.uscg',
    'SallyRide': '/mnt/gdc/data/r2r/scratch/edu.ucsd.sio',
    'Sikuliaq': '/mnt/gdc/data/r2r/scratch/edu.ucsd.sio',
    'Sproul': '/mnt/gdc/data/r2r/scratch/edu.ucsd.sio',
    'Oceanus': '/mnt/gdc/data/r2r/scratch/edu.oregonstate'
}
scripps_ships = ['SP', 'RR', 'SR', 'HLY', 'FL']
orgs = ['SIO', 'OSU', 'UAF']
rsync_by_org = {
    'SIO': ['nohup rsync --archive \
rsync://somts.ucsd.edu/cruise_data/{ship_title}/\
{cruise_title}.tar.bz2.md5.txt {dir}/{ship_title}',
            'nohup rsync --archive  \
rsync://somts.ucsd.edu/cruise_data/{ship_title}/{cruise_title}.tar.bz2 \
{dir}/{ship_title} > {dir}/{ship_title}/{cruise_title}.rsynclist.txt'],
    'OSU': 'nohup rsync -are ssh r2r@untangle.coas.oregonstate.edu:{dir}/{cruise_title} ' + ship_directory['Oceanus'],
  'UAF': 'nohup rsync -av --progress share.sikuliaq.alaska.edu::SKQDATA/\
{cruise_title}' + ship_directory['Sikuliaq'] + ' &> {dir}/{ship_title}/\
{cruise_title}.txt'
}
unread_args = ['.', '-', '/']
org_from_cruise = {
    'SP': 'SIO',
    'RR': 'SIO',
    'SR': 'SIO',
    'HLY': 'SIO',
    'FL': 'SIO',
    'OC': 'OSU',
    'SKQ': 'UAF'
}
unread_args = ['.', '-', '/']
op_from_cruise = {
    'SP': operator_sio,
    'RR': operator_sio,
    'SR': operator_sio,
    'HLY': operator_hly,
    'FL': operator_sio,
    'OC': operator_osu,
    'SKQ': operator_uaf
}
path_identifier = {
    'HLY': HLY_cruise_path,
    'SP': SIO_cruise_path,
    'RR': SIO_cruise_path,
    'SR': SIO_cruise_path,
    'OC': OC_cruise_path
}
SI_identifier = {
    'HLY': "/data/sensor/serial_logger",
    'SP': "/data/SerialInstruments",
    'RR': "/data/SerialInstruments",
    'SR': "/data/SerialInstruments"
}
