# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell
from Erebot_buildbot.config.steps import common
from Erebot_buildbot.src.steps import CountingShellCommand

QA = factory.BuildFactory()
QA.addStep(common.fill_properties)
QA.addStep(common.erebot_path)
QA.addStep(common.clone)
QA.addStep(common.composer_install)
QA.addStep(common.dependencies_install)

QA.addStep(shell.ShellCommand(
    command="php composer.phar require '%s'" % "' '".join([
        'squizlabs/php_codesniffer>=1.2.2',
        'sebastian/phpcpd=*',
        'phpmd/phpmd=*',
    ]),
    description=["installing", "additional", "dependencies"],
    descriptionDone=["install", "additional", "dependencies"],
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    maxTime=10*60,
))

QA.addStep(CountingShellCommand(
    command="vendor/bin/phing qa_codesniffer",
    description="CodeSniffer",
    descriptionDone="CodeSniffer",
    warnOnWarnings=True,
    flunkOnFailure=True,
    warningPattern="^.*?WARNING in line ()([0-9]+) column [0-9]+: (.*)$",
    warningExtractor=CountingShellCommand.extractFromRegexpGroups,
    errorPattern="^.*?ERROR in line ()([0-9]+) column [0-9]+: (.*)$",
    errorExtractor=CountingShellCommand.extractFromRegexpGroups,
    env={
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    maxTime=5 * 60,
))

QA.addStep(shell.ShellCommand(
    command="vendor/bin/phing qa_duplicates",
    description="Duplicates",
    descriptionDone="Duplicates",
    warnOnWarnings=True,
    env={
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    maxTime=5 * 60,
))

QA.addStep(shell.WarningCountingShellCommand(
    command="vendor/bin/phing qa_mess",
    description="Mess",
    descriptionDone="Mess",
    warnOnWarnings=True,
    warnOnFailure=True,
    warningPattern="^(/.*?):([0-9]+)\s+(.*)$",
    warningExtractor=
        shell.WarningCountingShellCommand.warnExtractFromRegexpGroups,
    env={
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    maxTime=5* 60,
))

