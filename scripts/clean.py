#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean up what I got from Case
"""

from airtight.cli import configure_commandline
from bs4 import BeautifulSoup
import logging
from os import walk
from pathlib import Path

dryrun = False
logger = logging.getLogger(__name__)

DEFAULT_LOG_LEVEL = logging.WARNING
OPTIONAL_ARGUMENTS = [
    ['-l', '--loglevel', 'NOTSET',
        'desired logging level (' +
        'case-insensitive string: DEBUG, INFO, WARNING, or ERROR',
        False],
    ['-v', '--verbose', False, 'verbose output (logging level == INFO)',
        False],
    ['-w', '--veryverbose', False,
        'very verbose output (logging level == DEBUG)', False],
    ['-d', '--dryrun', False, 'do not change anything', False]
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
    ['where', str, 'top-level directory']
]


def main(**kwargs):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    global dryrun
    dryrun = kwargs['dryrun']
    where = Path(kwargs['where']).resolve()
    logger.debug('where: {}'.format(where))
    #for root, dirs, files in os.walk():


if __name__ == "__main__":
    main(**configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL))
