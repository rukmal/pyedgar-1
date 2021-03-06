# -*- coding: utf-8 -*-
"""
Utilities for general EDGAR website tasks.

:copyright: © 2018 by Mac Gaulin
:license: MIT, see LICENSE for more details.
"""
import os
import re
import logging

__logger = logging.getLogger(__name__)

# This is platform specific. Probably a better solution than hard coding...
FEED_ROOT = '/data/storage/edgar/feeds/'
FEED_CACHE_ROOT = '/data/backup/edgar/feeds/'
INDEX_ROOT = '/data/storage/edgar/indices/'
ACCESSION_RE = re.compile(r'(?P<accession>\d{10}-?\d\d-?\d{6})', re.I)

def get_filing_path(cik, accession):
    """Return filepath to local copy of EDGAR filing. Filing document is .txt
    file with full submission, including main filing and exhibits/attachments.

    :param cik: The root directory at which to start searching.
    :param string accession: 18 digit accession string (optionally with dashes).

    :return: Full path to local filing document.
    :rtype: string
    """
    if not cik or not accession:
        raise ValueError("Requires non-missing CIK({}) and Accession({})"
                         .format(cik, accession))
    try:
        cik_full = "{:010d}".format(int(cik))
    except ValueError:
        return None # CIK not in integer format.
    try:
        clean_ac = ACCESSION_RE.search(accession).group('accession')
        if len(clean_ac) == 18: # no dashes found. Add dashes.
            clean_ac = clean_ac[:10] + '-' + clean_ac[10:12] + '-' + clean_ac[12:]
    except AttributeError: # no .group found.
        clean_ac = accession

    path = os.path.join(FEED_ROOT, *[cik_full[i:i+2] for i in range(0,10,2)] )

    return os.path.join(path, clean_ac + '.txt')

def walk_files(root_dir, filename_regex=None, return_dirs=False):
    """Iteratively walk directories and files, returning full paths.

    :param str root_dir: The root directory at which to start searching.
    :param re filename_regex: Regular expression (or string pattern) to which
              files or directories must match.
    :param bool return_dirs: Return directories as well as files.

    :return: Full path to filename or directory that matches optional regex.
    :rtype: string
    """
    if filename_regex is not None:
        try:
            # One can chain re.compile calls. This obviates checking type.
            filename_regex = re.compile(filename_regex)
        except (re.error, TypeError) as e:
            __logger.error("Regular expression provided is invalid!")
            raise(e)
    for r,ds,fs in os.walk(root_dir):
        if return_dirs:
            for d in ds:
                if filename_regex is not None and not filename_regex.search(d):
                    continue
                yield os.path.join(r,d)
        for f in fs:
            if filename_regex is not None and not filename_regex.search(f):
                continue
            yield os.path.join(r,f)
