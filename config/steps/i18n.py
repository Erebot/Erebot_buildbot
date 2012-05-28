# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell, transfer
from Erebot_buildbot.config.steps import common
from Erebot_buildbot.src.steps import FetchI18n, AddI18n, CommitI18n

I18N = factory.BuildFactory()
I18N.addStep(common.fill_properties)
I18N.addStep(common.erebot_path)
I18N.addStep(common.clone_rw)

# Copy API credentials.
I18N.addStep(transfer.FileDownload(
    mastersrc="netrc",
    slavedest=WithProperties(".netrc"),
))
# Download the reviewed .PO files.
I18N.addStep(FetchI18n(
    env={
        'HOME': WithProperties('%(workdir)s/build'),
    },
    description=['D/Ling', 'translations'],
    descriptionDone=['wget'],
))
# Remove API credentials.
I18N.addStep(shell.ShellCommand(
    command=['/bin/rm', '.netrc'],
    description=['Cleaning', 'up'],
    descriptionDone=['Cleanup'],
    alwaysRun=True,
))
# Add the new translations.
I18N.addStep(AddI18n(
    description=['Adding', 'translations'],
    descriptionDone=['git add'],
))
# Commit them.
I18N.addStep(CommitI18n(
    description=['Committing', 'translations'],
    descriptionDone=['git commit'],
))
# Push the result to GitHub.
I18N.addStep(shell.ShellCommand(
    command=[
        '/usr/bin/git',
        'push',
        WithProperties('%(rw_repository)s'),
        'master',
    ],
    description=['Pushing'],
    descriptionDone=['git push'],
))

