# -*- coding: utf-8 -*-

from framework.contexts.configuration import Configuration as _conf
from framework.contexts.logger import Logger as _log

import fnmatch
import glob
import itertools
import os

try:
    import filetype

except ImportError as exc:
    _log.fault("Missing dependency <{0}>. Try <pip install {0}> or manually build the required module to fix the issue.".format(exc.name))

__all__ = [
    "guess_file_type",
    "expand_files",
    "enumerate_matching_files",
    "matches_patterns"
]

def create_local_directory(directory, mask=0o700):
    """
    .. py:function:: create_local_directory(directory, mask=0o700)

    Creates a local case directory on the filesystem.

    :param directory: absolute path to the directory to create
    :type directory: str

    :param mask: permissions bit mask to apply for the newly created :code:`directory` and its parents if necessary
    :type mask: oct
    """

    try:
        os.makedirs(directory, mode=mask)
        _log.debug("Created local directory <{}>.".format(directory))

    except FileExistsError:
        _log.fault("Failed to create local directory due to existing object <{}>.".format(directory), post_mortem=True)

    except (
        OSError,
        Exception):

        _log.fault("Failed to create local directory <{}>.".format(directory), post_mortem=True)

def expand_files(feed, recursive=False, include=_conf.DEFAULTS["INCLUSION_FILTERS"], exclude=_conf.DEFAULTS["EXCLUSION_FILTERS"]):
    """
    .. py:function:: _expand_files(feed, recursive=False, include=_conf.DEFAULTS["INCLUSION_FILTERS"], exclude=_conf.DEFAULTS["EXCLUSION_FILTERS"])

    Iterates through file(s) and directory(ies) to retrieve the complete list of file(s).

    :param feed: list of files and directories
    :type feed: list

    :param recursive: search files recursively
    :type recursive: bool

    :param include: list of wildcard patterns to include
    :type include: list

    :param exclude: list of wildcard patterns to exclude
    :type exclude: list

    :return: flattened list of existing files
    :rtype: list
    """

    feedback = []

    for item in [os.path.abspath(_) for _ in feed]:
        if os.path.isfile(item):
            if matches_patterns(os.path.basename(item), patterns=include):
                if not exclude or (exclude and not matches_patterns(os.path.basename(item), patterns=exclude)):
                    feedback.append(item)

        elif os.path.isdir(item):
            for file in [os.path.abspath(_) for _ in enumerate_matching_files(item, include, recursive=recursive)]:
                if os.path.isfile(file):
                    if matches_patterns(os.path.basename(file), patterns=include):
                        if not exclude or (exclude and not matches_patterns(os.path.basename(file), patterns=exclude)):
                            feedback.append(file)

        else:
            _log.error("Object not found <{}>.".format(item))

    return feedback

def guess_file_type(target):
    """
    .. py:function:: guess_file_type(target)

    Retrieve the MIME-type and extension of :code:`target` through magic numbers/bytes and other methods.

    :param target: absolute path to the file
    :type target: str

    :return: tuple containing the extension and MIME-type of the given file
    :rtype: tuple
    """

    try:
        return filetype.guess(os.path.abspath(target))

    except TypeError:
        return None

def enumerate_matching_files(reference, patterns, recursive=False):
    """
    .. py:function:: enumerate_matching_files(reference, patterns)

    Returns an iterator pointing to the matching file(s) based on shell-like pattern(s).

    :param reference: absolute path to the rulesets directory
    :type reference: str

    :param patterns: list of globbing filter(s) to apply for the search
    :type patterns: list

    :param recursive: set to True to walk directory(ies) recursively
    :type recursive: bool

    :return: set containing the absolute path(s) of the matching file(s)
    :rtype: set
    """

    return set(itertools.chain.from_iterable(glob.iglob(os.path.join(reference, "**" if recursive else "", pattern), recursive=recursive) for pattern in patterns))

def matches_patterns(file, patterns=[]):
    """
    .. py:function:: matches_patterns(file, patterns=[])

    Tests whether a given file matches one or more wildcard pattern(s).

    :param file: name of the file to test
    :type file: str

    :param patterns: list of wildcard patterns as strings
    :type patterns: list

    :return: True if the file matches one or more of the given patterns, else False
    :rtype: bool
    """

    return any(fnmatch.fnmatch(file, pattern) for pattern in patterns)
