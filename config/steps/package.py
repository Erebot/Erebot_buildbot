# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell, transfer
from Erebot_buildbot.config.steps import common, helpers
from Erebot_buildbot.config.locks import PIRUM_LOCK
from Erebot_buildbot.config import misc
from Erebot_buildbot.src.steps import Link
from Erebot_buildbot.src import master

PACKAGE = factory.BuildFactory()
PACKAGE.addStep(common.erebot_path)
PACKAGE.addStep(common.clone)

PACKAGE.addStep(shell.Compile(
    command="phing",
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("%(EREBOT_PATH)s:${PATH}"),
    },
    warnOnWarnings=True,
    warnOnFailure=True,
    warningPattern="^\\[i18nStats\\] (.*?):([0-9]+): [Ww]arning: (.*)$",
    warningExtractor=
        shell.WarningCountingShellCommand.warnExtractFromRegexpGroups,
    maxTime=10 * 60,
))

PACKAGE.addStep(shell.ShellCommand(
        command=WithProperties(
        """
        for f in `ls -1 RELEASE-*`;
        do
            mv -v ${f} ${f}snapshot%(buildnumber)d;
        done
        """
        ),
        description=["prepare", "build"],
        descriptionDone=["prepare", "build"],
))

PACKAGE.addStep(transfer.FileDownload(
    mastersrc='/home/qa/master/buildenv/sign',
    slavedest=WithProperties('/tmp/buildbot.sign.%(buildnumber)d'),
    mode=0600,
))

PACKAGE.addStep(transfer.FileDownload(
    mastersrc='/home/qa/master/buildenv/certificate.p12',
    slavedest=WithProperties('/tmp/buildbot.p12.%(buildnumber)d'),
    mode=0600,
))

PACKAGE.addStep(shell.ShellCommand(
    command=WithProperties(
        " && ".join([
            "mv -f CREDITS CREDITS.buildbot",
            "echo 'Buildbot Continuous Integration [Ere-build-bot] "
                "<buildbot@erebot.net> (lead)' > CREDITS",
            "cat CREDITS.buildbot >> CREDITS",
            "mkdir -p /tmp/release-%(buildnumber)d",
            "pyrus.phar /tmp/release-%(buildnumber)d "
                "set handle Ere-build-bot",
            "pyrus.phar /tmp/release-%(buildnumber)d "
                "set openssl_cert /tmp/buildbot.p12.%(buildnumber)d",
            "phing release "
                " -Dstability=snapshot "
                " -Drelease.tmp=/tmp/release-%(buildnumber)d "
                " -Dpassfile=/tmp/buildbot.sign.%(buildnumber)d",
        ]) + "; " + " && ".join([
            "mv -f CREDITS.buildbot CREDITS",
            "rm -rf /tmp/release-%(buildnumber)d",
        ])
    ),
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("%(EREBOT_PATH)s:${PATH}"),
    },
    description="snapshot",
    descriptionDone="snapshot",
    haltOnFailure=True,
    maxTime=10*60,
))

PACKAGE.addStep(shell.ShellCommand(
    command=WithProperties(
        "rm -f /tmp/buildbot.sign.%(buildnumber)d "
            "/tmp/buildbot.p12.%(buildnumber)d"
    ),
    description=["buildenv", "cleanup"],
    descriptionDone=["buildenv", "cleanup"],
    haltOnFailure=True,
))

PACKAGE.addStep(shell.ShellCommand(
    command=WithProperties(
    """
    for f in `ls -1 RELEASE-*`;
    do
        mv -v ${f} ${f%%snapshot%(buildnumber)d};
    done
    """
    ),
    description=["finalize", "build"],
    descriptionDone=["finalize", "build"],
))

PACKAGE.addStep(shell.SetProperty(
    command=WithProperties(
        "ls -1 "
            "%(project)s-*.tgz "
            "%(project)s-*.tar "
            "%(project)s-*.zip "
            "%(project)s-*.phar "
            "%(project)s-*.pubkey "
            "%(project)s-*.pem "
        "2> /dev/null || :"
    ),
    description="Got any package?",
    descriptionDone="Got any package?",
    extract_fn=helpers.find_packages(),
))

# This step will always fail (and mark the whole build as failed)
# if not even one package was built during the snapshot step.
PACKAGE.addStep(shell.ShellCommand(
    command="! :",  # always exits with return value set to 1.
    haltOnFailure=True,
    description="Check packages",
    descriptionDone="Check packages",
    doStepIf=lambda step: not step.getProperty('found_packages')
))

for ext in (
    '.zip', '.zip.pubkey',
    '.tgz', '.tgz.pubkey',
    '.tar', '.tar.pubkey',
    '.phar', '.phar.pubkey',
    '.pem',
    ):
    if ext == '.pem' or ext.endswith('.pubkey'):
        maxsize = 20 * (1 << 10) # 20 KB
    else:
        maxsize = 50 * (1 << 20) # 50 MB

    PACKAGE.addStep(transfer.FileUpload(
        slavesrc=WithProperties("%%(pkg%s)s" % ext),
        masterdest=WithProperties(
            "/var/www/pear/get/%%(pkg%s)s" % ext
        ),
        mode=0644,
        doStepIf=helpers.get_package(ext),
        maxsize=maxsize
    ))

    if ext == '.pem':
        label = "Release certificate"
    elif ext.endswith('.pubkey'):
        label = "Signature (%s)" % ext
    else:
        label = "Package (%s)" % ext

    PACKAGE.addStep(Link(
        label=label,
        href=WithProperties(
            "%%(pear)s/get/%%(pkg%s)s" % ext,
            pear=lambda _: misc.PEAR_URL.rstrip('/'),
        ),
        doStepIf=helpers.get_package(ext),
    ))

PACKAGE.addStep(master.MasterShellCommand(
    command=" && ".join([
        "/var/www/clean-pear.sh",
        "php /home/qa/master/buildenv/git/Pirum/pirum build /var/www/pear",
        "rm -rf /tmp/pirum_*",
        "chmod -R a+r /var/www/pear/rest/",
        "find /var/www/pear/rest -type d -exec chmod a+x '{}' '+'"
    ]),
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("%(EREBOT_PATH)s:${PATH}"),
    },
    description=['PEAR', 'repos.', 'update'],
    descriptionDone=['PEAR', 'repos.', 'update'],
    locks=[PIRUM_LOCK.access('exclusive')],
))

