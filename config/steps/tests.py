# -*- coding: utf-8 -*-

from buildbot.process import factory, properties
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
        'PATH': "%(bin_dir)s:${PATH}",
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
        'PATH': "%(bin_dir)s:${PATH}",
    },
    maxTime=10 * 60,
))

TESTS.addStep(PHPUnit(
    command="phing test",
    description="tests",
    descriptionDone="tests",
    warnOnWarnings=True,
    env={
        'PATH': "%(bin_dir)s:${PATH}",
    },
    maxTime=10 * 60,
    doStepIf=helpers.if_buildslave('Debian 6 - PHP 5.2'),
))

TESTS.addStep(transfer.DirectoryUpload(
    slavesrc="docs/coverage/",
    masterdest=
        properties.WithProperties("public_html/doc/coverage/%(project)s/"),
    # Only upload the code coverage
    # information when the tests passed.
    doStepIf=lambda step: step.getProperty('Passed'),
    maxsize=10 * (1 << 20), # 10 MiB
))

