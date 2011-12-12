# -*- coding: utf-8 -*-

from buildbot.steps.source import Git
from buildbot.steps.slave import SetPropertiesFromEnv

def convert_repourl(repository):
    """
    Converts the (read-only) repository received by the github hook
    into a read/write URL.

    Eg. "https://github.com/fpoirotte/Erebot"
    becomes "git@github.com:fpoirotte/Erebot.git".
    """
    return 'git@%s:%s.git' % tuple(repository.split('://', 1)[1].split('/', 1))

clone = Git(
    mode='clobber',
    repourl=convert_repourl,
    submodules=True,
    progress=True,
)

erebot_path = SetPropertiesFromEnv(variables=['EREBOT_PATH'])
