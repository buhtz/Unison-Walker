#!/usr/bin/env python3

"""
    A helper script for the file syncronization software "Unison". It take care of unnecessary
    backup-files created but never deleted by Unison.
"""

__author__ = 'Christian Buhtz'
__date__ = 'September 2015'
__maintainer__ = __author__
__email__ = 'c.buhtz@posteo.jp'
__license__ = 'GPLv3'
__version__ = '0.0.1a'


#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os.path
import argparse
import logging
from datetime import datetime, timedelta
from configobj import ConfigObj

# read commandline arguments
parser = argparse.ArgumentParser(description='Unison Walker {} -- Search for unnecessary unison backup files.'.format(__version__))
parser.add_argument('profile_name', metavar='PROFILE_NAME', type=str, help='Name of the unison profile to use.')
parser.add_argument('age_in_days', metavar='AGE_IN_DAYS', type=int, help='The file age in days which make them "old".')
parser.add_argument('-d', '--debug', action='store_true', dest='debugon', help='Switch on debug mode. Give more messages on standard output.')

# store all arguments in objects/variables of the local namespace
locals().update(vars(parser.parse_args()))

# logging
if debugon:
    logging.getLogger().setLevel(logging.DEBUG)

# defaults
backupprefix = '.bak'
filestokill = []
backupdir = os.path.expanduser('~/.unison/backup/')
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
        # backupdir
        if line.startswith('backupdir'):
            backupdir = line.split('=')[1].strip()
            if backupdir[-1] != os.path.sep:
                backupdir += os.path.sep
        # backupprefix
        if line.startswith('backupprefix'):
            backupprefix = line.split('=')[1].strip()
        # maxbackups
        if line.startswith('maxbackups'):
            backupmax = int(line.split('=')[1].strip())

profile_file.close()


def _IsUnnecessary(orgfile, tokill):
    """
        Return True if 'orgfile' doesn't exist and the last access time of 'tokill' is older then
        the specified 'age_in_days' 
        Else return False.
    """
    if os.path.exists(orgfile):
        return False

    delta = datetime.now() - datetime.fromtimestamp(os.path.getatime(tokill))
    maxdelta = timedelta(days=int(age_in_days))
    if maxdelta > delta:
        return False

    return True


# walk throw backup location
for root, dirs, files in os.walk(backupdir):
    for file in files:
        if not file.startswith(backupprefix):
            orgfile = os.path.join(root.replace(backupdir, backuproot), file)
            tokill = os.path.join(root, file)
            # unnecessary?
            if _IsUnnecessary(orgfile, tokill):
                # main backup-file
                filestokill += [tokill]
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


