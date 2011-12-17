# -*- coding: utf-8 -*-

from buildbot.process.properties import WithProperties
from buildbot.steps.source import Git
from buildbot.steps.slave import SetPropertiesFromEnv
from buildbot.steps.shell import SetProperty

def convert_repourl(rw):
    """
    Returns a function capable of returning the read-only or read-write
    git URL for an HTTP repository as returned by the github hook.
    """

    def _rw(repository):
        """
        Converts the (read-only) repository received by the github hook
        into a read/write URL.

        Eg. "https://github.com/fpoirotte/Erebot"
        becomes "git@github.com:fpoirotte/Erebot.git".
        """
        return 'git@%s:%s.git' % tuple(repository.split('://', 1)[1].split('/', 1))

    def _ro(repository):
        """
        Converts the (read-only) HTTP repository received by the github hook
        into a read-only git URL.

        Eg. "https://github.com/fpoirotte/Erebot"
        becomes "git://github.com/fpoirotte/Erebot.git".
        """
        return 'git://%s.git' % repository.split('://', 1)[1]
    return rw and _rw or _ro


def _extract_repositories(rc, stdout, stderr):
    return {
        "ro_repository": convert_repourl(0)(stdout.strip()),
        "rw_repository": convert_repourl(1)(stdout.strip()),
    }

clone = Git(
    mode='clobber',
    repourl=convert_repourl(0),
    submodules=True,
    progress=True,
)

clone_rw = Git(
    mode='clobber',
    repourl=convert_repourl(1),
    submodules=True,
    progress=True,
)

extract_repositories = SetProperty(
    command=WithProperties("echo %(repository)s"),
    extract_fn=_extract_repositories,
)

erebot_path = SetPropertiesFromEnv(variables=['EREBOT_PATH'])
