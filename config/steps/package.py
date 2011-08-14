# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.steps import shell
from Erebot_buildbot.config.steps import common

PACKAGE = factory.BuildFactory()
PACKAGE.addStep(common.clone)
PACKAGE.addStep(shell.Compile(
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
))

