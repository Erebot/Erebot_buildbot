# -*- coding: utf-8 -*-

from buildbot.process import factory, properties
from buildbot.steps import shell
from Erebot_buildbot.config.steps import common, helpers
from Erebot_buildbot.config.locks import PIRUM_LOCK

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
            "mkdir -p /tmp/release-%(buildername)s-%(buildnumber)d",
            "%(pyrus_bin)s /tmp/release-%(buildnumber)d set handle Ere-build-bot",
            "%(pyrus_bin)s /tmp/release-%(buildnumber)d set openssl_cert /tmp/buildbot.p12",
            "cat /tmp/buildbot.sign.%(buildnumber)d | phing release -Dstability=snapshot",
        ]) + "; " + " && ".join([
            "mv -f CREDITS.buildbot CREDITS",
            "rm -rf /tmp/release-%(buildnumber)d",
        ])
    ),
    description="snapshot",
    descriptionDone="snapshot",
    haltOnFailure=True,
    maxTime=10*60,
    locks=[pirum_lock.access('exclusive')],
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
    command=properties.WithProperties("ls -1 %(project)s-*.tgz"),
    description="version",
    descriptionDone="version",
    extract_fn=helpers.get_pear_pkg,
))

PACKAGE.addStep(transfer.FileUpload(
    slavesrc=properties.WithProperties("%(pear_pkg)s.tgz"),
    masterdest=properties.WithProperties(
        "/var/www/pear/get/%(pear_pkg)s.tgz"
    ),
    mode=0644,
    doStepIf=helpers.has_pear_pkg,
    maxsize=50 * (1 << 20), # 50 MiB
))

PACKAGE.addStep(transfer.FileUpload(
    slavesrc=properties.WithProperties("%(pear_pkg)s.tgz.pubkey"),
    masterdest=properties.WithProperties(
        "/var/www/pear/get/%(pear_pkg)s.tgz.pubkey"
    ),
    mode=0644,
    doStepIf=helpers.has_pear_pkg,
    maxsize=20 * (1 << 10), # 20 KiB
))

PACKAGE.addStep(transfer.FileUpload(
    slavesrc=properties.WithProperties("%(pear_pkg)s.pem"),
    masterdest=properties.WithProperties(
        "/var/www/pear/get/%(pear_pkg)s.pem"
    ),
    mode=0644,
    doStepIf=helpers.has_pear_pkg,
    maxsize=20 * (1 << 10), # 20 KiB
))

PACKAGE.addStep(Link(
    label="PEAR Package",
    href=properties.WithProperties(
        "http://pear.erebot.net/get/%(pear_pkg)s.tgz"
    ),
    doStepIf=helpers.has_pear_pkg,
))

PACKAGE.addStep(master.MasterShellCommand(
    command="&&".join([
        "/var/www/clean-pear.sh",
        "/usr/bin/pirum build /var/www/pear",
        "rm -rf /tmp/pirum_*",
        "chmod -R a+r /var/www/pear/rest/",
        "find /var/www/pear/rest -type d -exec chmod a+x '{}' '+'"
    ]),
    description=['PEAR', 'repos.', 'update'],
    descriptionDone=['PEAR', 'repos.', 'update'],
    doStepIf=helpers.has_pear_pkg,
    locks=[PIRUM_LOCK.access('exclusive')],
))

