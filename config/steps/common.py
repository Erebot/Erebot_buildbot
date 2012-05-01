# -*- coding: utf-8 -*-

from buildbot.process.properties import WithProperties
from buildbot.steps.source import Git
from Erebot_buildbot.src.steps import MorphProperties, SetPropertiesFromEnv
from Erebot_buildbot.config import misc

def _fill_props(properties):
    project = properties.getProperty('project')
    if project and not properties.getProperty('repository'):
        # Deduce the repository from a project name (w/ account name).
        properties.setProperty(
            'repository',
            "%s/%s" % (misc.GITHUB_BASE.rstrip('/'), properties['project']),
            'MorphProperties'
        )
    elif properties.getProperty('repository') and not project:
        # Deduce the project name (w/ account name) from a repository URL.
        repo = properties['repository'].rstrip('/')
        project = '/'.join(repo.split('/')[-2:])
        if project.endswith('.git'):
            project = project[:-4]
        if project:
            properties.setProperty('project', project, 'MorphProperties')

    # GitHub account hosting the repository.
    properties.setProperty(
        'ghUser',
        project.partition('/')[0],
        'MorphProperties'
    )
    # GitHub project (repository) to use (w/o account name).
    properties.setProperty(
        'shortProject',
        project.rpartition('/')[2],
        'MorphProperties'
    )
    # Read-only URL to repository.
    properties.setProperty(
        'ro_repository',
        convert_repourl(0)(properties['repository']),
        'Repositories'
    )
    # Read/write URL to repository.
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


# This wrapper is required on buildbot 0.8.3pl1 due to a bogus assert.
class GitWithProperties(WithProperties):
    def __call__(self, repo):
        return self

clone = Git(
    mode='clobber',
    repourl=GitWithProperties("%(ro_repository)s"),
    submodules=True,
    progress=True,
)

clone_rw = Git(
    mode='clobber',
    repourl=GitWithProperties("%(rw_repository)s"),
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

