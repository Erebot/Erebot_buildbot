# -*- coding: utf-8 -*-

from buildbot.process.properties import WithProperties
from buildbot.steps.source import Git
from buildbot.steps.slave import SetPropertiesFromEnv
from buildbot.steps.shell import SetProperty

def convert_repourl(repository):
    """
    Converts the (read-only) repository received by the github hook
    into a read/write URL.

    Eg. "https://github.com/fpoirotte/Erebot"
    becomes "git@github.com:fpoirotte/Erebot.git".
    """
    return 'git@%s:%s.git' % tuple(repository.split('://', 1)[1].split('/', 1))

def _extract_repository(rc, stdout, stderr):
    return {
        "rw_repository": convert_repourl(stdout.strip()),
    }

clone = Git(
    mode='clobber',
    repourl=convert_repourl,
    submodules=True,
    progress=True,
)

real_repository = SetProperty(
    command=WithProperties("echo %(repository)s"),
    extract_fn=_extract_repository,
)

erebot_path = SetPropertiesFromEnv(variables=['EREBOT_PATH'])
