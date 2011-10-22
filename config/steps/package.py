# -*- coding: utf-8 -*-

from buildbot.process import factory, properties
from buildbot.steps import shell, transfer
from Erebot_buildbot.config.steps import common, helpers
from Erebot_buildbot.config.locks import PIRUM_LOCK
from Erebot_buildbot.config import misc
from Erebot_buildbot.src.steps import Link
from Erebot_buildbot.src import master

PACKAGE = factory.BuildFactory()
PACKAGE.addStep(common.clone)

PACKAGE.addStep(shell.Compile(
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
))

PACKAGE.addStep(shell.ShellCommand(
        command=properties.WithProperties(
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
    slavedest=properties.WithProperties('/tmp/buildbot.sign.%(buildnumber)d'),
    mode=0600,
))

PACKAGE.addStep(transfer.FileDownload(
    mastersrc='/home/qa/master/buildenv/certificate.p12',
    slavedest=properties.WithProperties('/tmp/buildbot.p12.%(buildnumber)d'),
    mode=0600,
))

PACKAGE.addStep(shell.ShellCommand(
    command=properties.WithProperties(
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
            # Makes buildbot answer "yes" when Pyrus
            # asks whether we want to sign the package,
            # and then answer with the passphrase.
            # We do it twice (for .tgz and .phar).
            "cat "
                "/tmp/buildbot.sign.%(buildnumber)d "
                "/tmp/buildbot.sign.%(buildnumber)d "
                "| "
                "phing release "
                "-Dstability=snapshot "
                "-Drelease.tmp=/tmp/release-%(buildnumber)d",
        ]) + "; " + " && ".join([
            "mv -f CREDITS.buildbot CREDITS",
            "rm -rf /tmp/release-%(buildnumber)d",
        ])
    ),
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': properties.WithProperties("%(bin_dir)s:${PATH}"),
    },
    description="snapshot",
    descriptionDone="snapshot",
    haltOnFailure=True,
    maxTime=10*60,
))

PACKAGE.addStep(shell.ShellCommand(
    command=properties.WithProperties(
        "rm -f /tmp/buildbot.sign.%(buildnumber)d "
            "/tmp/buildbot.p12.%(buildnumber)d"
    ),
    description=["buildenv", "cleanup"],
    descriptionDone=["buildenv", "cleanup"],
    haltOnFailure=True,
))

PACKAGE.addStep(shell.ShellCommand(
    command=properties.WithProperties(
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
    command=properties.WithProperties(
        "ls -1 %(project)s-*.{{tgz,tar,zip,phar}{,.pubkey},pem} 2> /dev/null"
    ),
    description="Got any package?",
    descriptionDone="Got any package?",
    extract_fn=helpers.find_packages(),
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
        slavesrc=properties.WithProperties("%%(pkg%s)s" % ext),
        masterdest=properties.WithProperties(
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
        href=properties.WithProperties(
            "%%(buildbotURL)s/get/%%(pkg%s)s" % ext,
            buildbotURL=lambda _: misc.BUILDBOT_URL.rstrip('/'),
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
        'PATH': properties.WithProperties("%(bin_dir)s:${PATH}"),
    },
    description=['PEAR', 'repos.', 'update'],
    descriptionDone=['PEAR', 'repos.', 'update'],
    locks=[PIRUM_LOCK.access('exclusive')],
))

