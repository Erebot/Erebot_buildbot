# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell, transfer
from Erebot_buildbot.config.steps import common
from Erebot_buildbot.src.steps import Link

I18N = factory.BuildFactory()
I18N.addStep(common.fill_properties)
I18N.addStep(common.erebot_path)
I18N.addStep(common.clone_rw)

# Create a directory for the new locale.
I18N.addStep(shell.ShellCommand(
    command=[
        '/bin/mkdir', '-p',
        WithProperties('data/i18n/%(locale)s/LC_MESSAGES/'),
    ],
    description=['Preparing', 'locale'],
    descriptionDone=['Prepare', 'locale'],
))
# Copy API credentials.
I18N.addStep(transfer.FileDownload(
    mastersrc="netrc",
    slavedest=WithProperties(".netrc"),
))
# Download the reviewed .PO into that directory.
I18N.addStep(shell.ShellCommand(
    command=[
        '/usr/bin/wget', '-O',
        WithProperties('data/i18n/%(locale)s/LC_MESSAGES/%(shortProject)s.po'),
        WithProperties(
            'https://www.transifex.net/api/2/project/%(ghUser)s/resource/'
                '%(shortProject)s/translation/%(locale)s/?file=1&mode=reviewed'
        ),
    ],
    env={
        'HOME': WithProperties('%(workdir)s/build'),
    },
    description=['D/Ling', 'translations'],
    descriptionDone=['D/L', 'translations'],
))
# Remove API credentials.
I18N.addStep(shell.ShellCommand(
    command=['/bin/rm', '.netrc'],
    description=['Cleaning', 'up'],
    descriptionDone=['Cleanup'],
    alwaysRun=True,
))
# Commit the new translations.
I18N.addStep(shell.ShellCommand(
    command=[
        '/usr/bin/git',
        'commit',
        '-m',
        WithProperties('i18n update for %(locale)s (%(percent)s%% done)'),
        WithProperties('data/i18n/%(locale)s/LC_MESSAGES/%(shortProject)s.po'),
    ],
    description=['Committing'],
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

