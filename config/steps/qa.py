# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.steps import shell
from Erebot_buildbot.config.steps import common

QA = factory.BuildFactory()
QA.addStep(common.clone)

QA.addStep(shell.ShellCommand(
    command="phing qa_lint",
    description="lint",
    descriptionDone="lint",
    warnOnWarnings=True,
    env={
        'PATH': '%(bin_dir)s:${PATH}'
    },
    maxTime=5 * 60,
))

QA.addStep(shell.ShellCommand(
    command="phing qa_codesniffer",
    description="CodeSniffer",
    descriptionDone="CodeSniffer",
    warnOnWarnings=True,
    env={
        'PATH': '%(bin_dir)s:${PATH}'
    },
    maxTime=5 * 60,
))

QA.addStep(shell.ShellCommand(
    command="phing qa_duplicates",
    description="Duplicates",
    descriptionDone="Duplicates",
    warnOnWarnings=True,
    env={
        'PATH': '%(bin_dir)s:${PATH}'
    },
    maxTime=5 * 60,
))

QA.addStep(shell.ShellCommand(
    command="phing qa_mess",
    description="Mess",
    descriptionDone="Mess",
    warnOnWarnings=True,
    env={
        'PATH': '%(bin_dir)s:${PATH}'
    },
    maxTime=5* 60,
))

