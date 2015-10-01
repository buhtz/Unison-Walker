#!/usr/bin/env python3

__author__ = 'Christian Buhtz'
__email__ = 'c.buhtz@posteo.jp'
__license__ = 'GPL'
__version__ = '0.0.1a'

import sys
import os.path
import argparse
import logging
from configobj import ConfigObj

# read commandline arguments
parser = argparse.ArgumentParser(description='Unison Walker {} -- Search for unnecessary unison backup files.'.format(__version__))
parser.add_argument('profile_name', metavar='PROFILE_NAME', help='Name of the unison profile to use.')
#parser.add_argument('--age', dest='age_in_days', help='The file age in days which make them "old".')

# store all arguments in objects/variables of the local namespace
locals().update(vars(parser.parse_args()))

# logging
logging.getLogger().setLevel(logging.DEBUG)

# defaults
backupprefix = '.bak'
filestokill = []
backuplocation = os.path.expanduser('~/.unison/backup/')
backupmax = 2

# the profile
if profile_name.endswith('.prf'):
    profile_name = profile_name[:-4]
profile_filename = os.path.expanduser('~/.unison/') + profile_name + '.prf'

# access profile file
logging.info('Open profile file {}...'.format(profile_filename))
try:
    #profile_file = ConfigObj(infile=profile_filename, file_error=True, create_empty=False)
    profile_file = open(profile_filename)
    logging.info('Successfull opened.')
except Exception as e:
    logging.error(e)
    sys.exit(1)

# read the profile file
for line in iter(profile_file):
    line = line.replace('\n', '')
    if line:
        # root
        if line.startswith('root'):
            if ':' in line: break
            backuproot = line.split('=')[1].strip()
            if backuproot[-1] is not '/':
                backuproot += '/'
        # backupprefix
        if line.startswith('backupprefix'):
            backupprefix = line.split('=')[1].strip()
        # maxbackups
        if line.startswith('maxbackups'):
            backupmax = int(line.split('=')[1].strip())

profile_file.close()

# walk throw backup location
for root, dirs, files in os.walk(backuplocation):
    for file in files:
        if not file.startswith(backupprefix):
            orgfile = os.path.join(root.replace(backuplocation, backuproot), file)
            if not os.path.exists(orgfile):
                # main backup-file
                filestokill += [os.path.join(root, file)]
                # older backups
                i = backupmax
                while i > 0:
                    fn = os.path.join(root, '{}.{}.{}'.format(backupprefix, i, file))
                    if os.path.exists(fn):
                        filestokill += [fn]
                    i -= 1

# print out all files kill
for k in filestokill:
    print(k)
sys.exit(0)

