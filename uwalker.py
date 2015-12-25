#!/usr/bin/env python3

"""
    A helper script for the file syncronization software 'Unison'. It take
    care of unnecessary backup-files created but never deleted by Unison.
"""
import sys
import os.path
import argparse
import logging
import humanize
from datetime import datetime, timedelta
from configobj import ConfigObj

__author__ = 'Christian Buhtz'
__date__ = 'September 2015'
__maintainer__ = __author__
__email__ = 'c.buhtz@posteo.jp'
__license__ = 'GPLv3'
__app_name__ = 'Unison Walker'
__version__ = '0.0.2a'

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


def _createArgumentParser(addToGlobal=True):
    """
        Parse all programm arguments from 'sys.argv' and store them to global
        namespace if 'addToGlobal' is True.
        Return the parser instance.
    """
    parser = argparse.ArgumentParser(description='{} {} -- Search for unne'
                                     'cessary unison backup files.'
                                     .format(__app_name__, __version__))
    parser.add_argument('profile_name', metavar='PROFILE_NAME', type=str,
                        help='Name of the unison profile to use.')
    parser.add_argument('age_in_days', metavar='AGE_IN_DAYS', type=int,
                        help='The file age in days which make them "old".')
    parser.add_argument('-o', '--out', metavar='FILE', type=str, dest='argOut',
                        help='File to store the result in. (Default: STDOUT)')
    parser.add_argument('-i', '--info', action='store_true', dest='argInfo',
                        default=False, help='Show informations about the '
                        'result.')
    parser.add_argument('-d', '--debug', action='store_true',
                        dest='argDebugon', help='Switch on debug mode. '
                        'Give more messages on standard output and '
                        'implicite --info.')

    if addToGlobal:
        globals().update(vars(parser.parse_args()))

    return parser


def _setupLogging():
    """
        Setup the logging behaviour.
    """
    global argDebugon
    logformat = '%(levelname)-9s: %(message)s'

    if argDebugon is True:
        logging.basicConfig(format=logformat, level=logging.DEBUG)
        logging.debug('Debug mode on.')
    elif argInfo is True:
        logging.basicConfig(format=logformat, level=logging.INFO)
    else:
        logging.basicConfig(format=logformat, level=logging.WARNING)


def _IsUnnecessary(orgfile, relevant):
    """
        Check if the backup file 'relevant' is relevant to be treated (e.g.
        removed).
        Return True if 'orgfile' doesn't exist and the last access time of
        'relevant' is older then the specified 'age_in_days'.
        Otherwise return False.
    """
    # The original file still exists. So we need a backup.
    if os.path.exists(orgfile):
        return False

    if os.path.exists(relevant) is False:
        if os.path.lexists(relevant):  # broken symbolik link?
            return True
        else:
            # this should never happen
            raise Exception('Original and backup file does not seam to exist. '
                            'Please contact the developer per mail at {} '
                            'with that error message!'.format(__email__))
            return False

    # age of 'relevant' file depending on its last access time
    lastAccess = os.path.getatime(relevant)
    relevantAge = datetime.now() - datetime.fromtimestamp(lastAccess)
    thresholdAge = timedelta(days=int(age_in_days))
    if thresholdAge > relevantAge:
        return False

    return True


def _readProfileFile():
    """
        Read the per programm argument specified profile file.
        This parameters are read:
         - root
         - backupdir
         - backupprefix
         - maxbackups
         - backuploc
        If 'backuploc' is not 'central' then the application will exit here.
    """
    global profile_name
    global backuproot
    global backupdir
    global backupprefix
    global backupmax

    # the profile
    if profile_name.endswith('.prf'):
        profile_name = profile_name[:-4]
    profile_filename = os.path.expanduser('~/.unison/') + profile_name + '.prf'

    # access profile file
    logging.info('Open profile file {}...'.format(profile_filename))
    with open(profile_filename) as profile_file:
        logging.info('Successfull opened.')

        # read the profile file
        for line in iter(profile_file):
            line = line.replace('\n', '')
            if line:
                # root
                if line.startswith('root'):
                    if ':' in line:
                        break
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
                # backuploc
                if line.startswith('backuploc'):
                    backuploc = line.split('=')[1].strip()
                    # only central profiles are supported
                    if backuploc != 'central':
                        logging.error('Only "central" backup locations are'
                                      'supported. See "backuploc" in your '
                                      'profile file.')
                        sys.exit(-1)

    logging.debug('Read from {}:'.format(profile_filename))
    logging.debug('backuproot: {}'.format(backuproot))
    logging.debug('backupdir: {}'.format(backupdir))
    logging.debug('backupprefix: {}'.format(backupprefix))
    logging.debug('backupmax: {}'.format(backupmax))


def _findRelevantFiles():
    """
        Look in the backup location for relevant and unnecessary files and
        return them as a list.
        See '_IsUnnecessary()' to find out how 'unnecessary' is defined.
    """
    global backupprefix
    global backupdir
    global backupmax
    global backuproot
    relevantFiles = []

    # walk in the central backup folder
    for root, dirs, files in os.walk(backupdir):
        # each file
        for f in files:
            orgfile = os.path.join(root.replace(backupdir, backuproot), f)
            relfile = os.path.join(root, f)

            # unnecessary?
            if _IsUnnecessary(orgfile, relfile):
                # main backup-file
                relevantFiles.append(relfile)
                # older backups
                i = backupmax
                while i > 0:
                    fn = os.path.join(root, '{}.{}.{}'
                                      .format(backupprefix, i, f))
                    if os.path.exists(fn):
                        relevantFiles.append(fn)
                    i -= 1

    return relevantFiles


def _output(relevantFiles):
    """
        Write/Print the 'relevantFiles' to STDOUT or to a file specified by
        '--out'.
        Filenames with encoding problems are removed from the list with a
        warning message.
    """
    global argOut
    total_size = 0

    if argOut:
        outfile = open(argOut, 'w')
    else:
        outfile = sys.stdout

    for f in relevantFiles[:]:
        # size
        try:
            # cumulate the size
            total_size += os.path.getsize(f)
        except FileNotFoundError as err:
            # this can happen when it is a broken symbolic link
            pass

        # name
        try:
            outfile.write(f + '\n')
        except UnicodeEncodeError as err:
            saveName = f.encode(sys.getfilesystemencoding(),
                                errors='surrogateescape').decode('latin-1')
            logging.warning('There is a encoding problem with a filename. It '
                            'will be removed from the list of relevant files.'
                            ' Please handle that problem yourself. This '
                            '"could" be the file: {}'
                            .format(saveName))
            # alternative: repr(f)[1:-1]
            relevantFiles.remove(f)

    logging.info('Total size of {} relevant files: {}'
                 .format(len(relevantFiles), humanize.naturalsize(total_size)))


if __name__ == '__main__':
    # parse arguments and setup the logging system
    _createArgumentParser()
    _setupLogging()

    # defaults
    global backupprefix
    global backupdir
    global backupmax
    global backuproot
    backupprefix = '.bak'
    backupdir = os.path.expanduser('~/.unison/backup/')
    backupmax = 2
    backuproot = None

    # read profile file
    _readProfileFile()

    # find relevant files
    relevantFiles = _findRelevantFiles()

    # print the result
    _output(relevantFiles)

    # bye bye
    sys.exit()
