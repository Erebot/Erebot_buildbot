# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell, transfer
from Erebot_buildbot.config.steps import common, helpers
from Erebot_buildbot.src.steps import Link, PHPUnit

TESTS = factory.BuildFactory()
TESTS.addStep(common.fill_properties)
TESTS.addStep(common.erebot_path)
TESTS.addStep(common.clone)
TESTS.addStep(common.composer_cleanup_posix)
TESTS.addStep(common.composer_cleanup_win)
TESTS.addStep(common.composer_install)
TESTS.addStep(common.composer_deps)

TESTS.addStep(shell.ShellCommand(
    command="php composer.phar require %s" % ' '.join([
            'phpunit/phpunit=*',
    ]),
    description=["installing", "additional", "dependencies"],
    descriptionDone=["install", "additional", "dependencies"],
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
        'APPDATA': WithProperties("%(APPDATA:-${USERPROFILE}\\Application Data\\)"),
    },
    maxTime=10*60,
))

# Prepare for the tests. Eg. the Core's unittests require
# the translations be available and other modules also do
# some additional work (eg. generate a parser).
TESTS.addStep(shell.Compile(
    command="vendor/bin/phing -logger phing.listener.DefaultLogger prepare_test",
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    warnOnWarnings=True,
    flunkOnFailure=True,
    warningPattern="^\\s*\\[i18nStats\\] (.*?):([0-9]+): [Ww]arning: (.*)$",
    warningExtractor=
        shell.WarningCountingShellCommand.warnExtractFromRegexpGroups,
    maxTime=10 * 60,
))

# Skip tests when there is no PHPn_PATH or PHPn_DESC.
def _path_checker(i):
    def _inner(s):
        return (
            s.build.slavebuilder.slave.slave_environ.get('PHP%d_PATH' % i) and
            s.build.slavebuilder.slave.slave_environ.get('PHP%d_DESC' % i)
        )
    return _inner

for i in xrange(1, common.nb_versions + 1):
    # Lint the code with each version of PHP installed.
    TESTS.addStep(shell.ShellCommand(
        command="vendor/bin/phing -logger phing.listener.DefaultLogger qa_lint",
        description=[WithProperties("lint  %%(PHP%d_DESC:-)s" % i)],
        descriptionDone=[WithProperties("lint  %%(PHP%d_DESC:-)s" % i)],
        warnOnWarnings=True,
        env={
            'PATH': WithProperties("${PHP%d_PATH}:${PATH}" % i),
        },
        doStepIf=_path_checker(i),
        maxTime=5 * 60,
    ))

    TESTS.addStep(PHPUnit(
        command="vendor/bin/phing -logger phing.listener.DefaultLogger bare_test",
        description=[WithProperties("PHP  %%(PHP%d_DESC:-)s" % i)],
        descriptionDone=[WithProperties("PHP  %%(PHP%d_DESC:-)s" % i)],
        warnOnWarnings=True,
        env={
            'PATH': WithProperties("${PHP%d_PATH}:${PATH}" % i),
        },
        maxTime=10 * 60,
        doStepIf=_path_checker(i),
    ))

# Only report coverage data for the slave running on the host itself.
# Also, only upload code coverage reports when all tests pass.
def _must_transfer_coverage(s):
    slaves = ('Debian (x64)', )
    passed = s.getProperty('Passed', None)
    return s.getSlaveName() in slaves and passed

TESTS.addStep(transfer.DirectoryUpload(
    slavesrc="docs/coverage/",
    masterdest=WithProperties("public_html/doc/coverage/%(shortProject)s/"),
    doStepIf=_must_transfer_coverage,
    maxsize=10 * (1 << 20), # 10 MiB
))

