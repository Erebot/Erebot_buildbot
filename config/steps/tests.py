# -*- coding: utf-8 -*-

from buildbot.process import factory, properties
from buildbot.steps import shell, transfer
from Erebot_buildbot.config.steps import common, helpers
from Erebot_buildbot.src.steps import Link, PHPUnit

TESTS = factory.BuildFactory()
TESTS.addStep(common.clone)

# For the core, we must compile the translations
# before the tests are run because they depend on that.
TESTS.addStep(shell.Compile(
    command="phing",
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': properties.WithProperties("%(bin_dir)s:${PATH}"),
    },
    warnOnWarnings=True,
    warnOnFailure=True,
    warningPattern="^\\[i18nStats\\] (.*?):([0-9]+): [Ww]arning: (.*)$",
    warningExtractor=
        shell.WarningCountingShellCommand.warnExtractFromRegexpGroups,
    maxTime=10 * 60,
    doStepIf=helpers.if_component('Erebot'),
))

TESTS.addStep(PHPUnit(
    command="phing test",
    description="tests",
    descriptionDone="tests",
    warnOnWarnings=True,
    env={
        'PATH': properties.WithProperties("%(bin_dir)s:${PATH}"),
    },
    maxTime=10 * 60,
))

TESTS.addStep(PHPUnit(
    command="phing test",
    description="tests",
    descriptionDone="tests",
    warnOnWarnings=True,
    env={
        'PATH': properties.WithProperties("%(bin_dir)s:${PATH}"),
    },
    maxTime=10 * 60,
    doStepIf=helpers.if_buildslave(),
))


# Use only the PHP 5.2 setup to report coverage data.
# Also, only upload code coverage reports for passing tests.
def must_transfer_coverage(step):
    slaves = ('Debian 6 - PHP 5.2', )
    return step.getSlaveName() in slaves and step.getProperty('Passed')

TESTS.addStep(transfer.DirectoryUpload(
    slavesrc="docs/coverage/",
    masterdest=
        properties.WithProperties("public_html/doc/coverage/%(project)s/"),
    doStepIf=must_transfer_coverage,
    maxsize=10 * (1 << 20), # 10 MiB
))

