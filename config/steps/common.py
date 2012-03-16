# -*- coding: utf-8 -*-

from buildbot.process.properties import WithProperties as _WithProperties
from buildbot.steps.source import Git
from buildbot.steps.shell import SetProperty
from Erebot_buildbot.src.steps import MorphProperties, SetPropertiesFromEnv
from Erebot_buildbot.config import misc

def _fill_props(properties):
    if properties.getProperty('project') and \
        not properties.getProperty('repository'):
        properties.setProperty(
            'repository',
            "%s/%s" % (misc.GITHUB_BASE.rstrip('/'), properties['project']),
            'MorphProperties'
        )
    elif properties.getProperty('repository') and \
        not properties.getProperty('project'):
        repo = properties['repository'].rstrip('/')
        project = repo.rpartition('/')[2]
        if project.endswith('.git'):
            project = project[:-4]
        if project:
            properties.setProperty('project', project, 'MorphProperties')
    properties.setProperty(
        'ro_repository',
        convert_repourl(0)(properties['repository']),
        'Repositories'
    )
    properties.setProperty(
        'rw_repository',
        convert_repourl(1)(properties['repository']),
        'Repositories'
    )

def convert_repourl(rw):
    """
    Returns a function capable of returning the read-only or read-write
    git URL for an HTTP repository as returned by the github hook.
    """

    def _rw(repository):
        """
        Converts the (read-only) repository received by the github hook
        into a read/write URL.

        Eg. "https://github.com/Erebot/Erebot"
        becomes "git@github.com:Erebot/Erebot.git".
        """
        return 'git@%s:%s.git' % \
            tuple(repository.split('://', 1)[1].split('/', 1))

    def _ro(repository):
        """
        Converts the (read-only) HTTP repository received by the github hook
        into a read-only git URL.

        Eg. "https://github.com/Erebot/Erebot"
        becomes "git://github.com/Erebot/Erebot.git".
        """
        return 'git://%s.git' % repository.split('://', 1)[1]
    return rw and _rw or _ro


# This function is required on buildbot 0.8.3pl1 due to a bogus assert.
def _git_repository(repo):
    def _inner(_dummy):
        return WithProperties(repo)
    return _inner

clone = Git(
    mode='clobber',
    repourl=_git_repository("%(ro_repository)s"),
    submodules=True,
    progress=True,
)

clone_rw = Git(
    mode='clobber',
    # The lambda is required on buildbot 0.8.3pl1 due to a bogus assert.
    repourl=_git_repository("%(rw_repository)s"),
    submodules=True,
    progress=True,
)

fill_properties = MorphProperties(morph_fn=_fill_props)

nb_versions = 10
_slaves_props = []
for _i in xrange(1, nb_versions + 1):
#    _slaves_props.append('PHP%d_PATH' % _i)
    _slaves_props.append('PHP%d_DESC' % _i)
erebot_path = SetPropertiesFromEnv(variables=['PHP_MAIN'] + _slaves_props)

