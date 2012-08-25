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
PACKAGE.addStep(common.fill_properties)
PACKAGE.addStep(common.erebot_path)
PACKAGE.addStep(common.clone)

PACKAGE.addStep(shell.Compile(
    command="phing -logger phing.listener.DefaultLogger -Dskip.update_catalog=false",
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    warnOnWarnings=True,
    warnOnFailure=True,
    warningPattern="^\\s*\\[i18nStats\\] (.*?):([0-9]+): [Ww]arning: (.*)$",
    warningExtractor=
        shell.WarningCountingShellCommand.warnExtractFromRegexpGroups,
    maxTime=10 * 60,
))

# This does not really belong to this builder,
# but still, it's quite convenient to put it here.
PACKAGE.addStep(shell.SetProperty(
    command=WithProperties(
        "/usr/bin/git diff -U0 data/i18n/%(shortProject)s.pot | "
        "/bin/grep -E '^[-+](\"(?!POT-Creation-Date:)|msgid)'"
    ),
    extract_fn=lambda rc, stdout, stderr: {'i18n update': not rc},
    description=["Checking", "i18n", "template"],
    descriptionDone=["Check", "i18n", "template"],
    warnOnWarnings=False,
    warnOnFailure=False,
    flunkOnWarnings=False,
    flunkOnFailure=False,
))

# This does not really belong to this builder,
# but still, it's quite convenient to put it here.
PACKAGE.addStep(shell.ShellCommand(
    command=WithProperties(
        "/usr/bin/git commit -m 'Update i18n template using "
            "%(got_revision)s [%(buildnumber)d]\n\n[ci skip]' "
            "data/i18n/%(shortProject)s.pot && "
        "/usr/bin/git push %(rw_repository)s %(branch)s"
    ),
    # Push a new version of the translation template,
    # but only if there are real changes (ignoring
    # changes that only affect comments or the POT's
    # creation date).
    doStepIf=lambda step: step.getProperty('i18n update'),
    description=["Updating", "i18n", "template"],
    descriptionDone=["Update", "i18n", "template"],
))

PACKAGE.addStep(shell.ShellCommand(
        command=WithProperties(
        """
        for f in `ls -1 RELEASE-*`;
        do
            /bin/mv -v ${f} ${f}snapshot%(buildnumber)d;
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
            "/bin/mv -f CREDITS CREDITS.buildbot",
            "/bin/echo 'Buildbot Continuous Integration [Ere-build-bot] "
                "<buildbot@erebot.net> (lead)' > CREDITS",
            "/bin/cat CREDITS.buildbot >> CREDITS",
            "/bin/mkdir -p /tmp/release-%(buildnumber)d",
            "pyrus.phar /tmp/release-%(buildnumber)d "
                "set handle Ere-build-bot",
            "pyrus.phar /tmp/release-%(buildnumber)d "
                "set openssl_cert /tmp/buildbot.p12.%(buildnumber)d",
            "phing release "
                " -Dstability=snapshot "
                " -Drelease.tmp=/tmp/release-%(buildnumber)d "
                " -Dpassfile=/tmp/buildbot.sign.%(buildnumber)d",
        ]) + "; " + " && ".join([
            "/bin/mv -f CREDITS.buildbot CREDITS",
            "/bin/rm -rf /tmp/release-%(buildnumber)d",
        ])
    ),
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    description="snapshot",
    descriptionDone="snapshot",
    haltOnFailure=True,
    maxTime=10 * 60,
))

PACKAGE.addStep(shell.ShellCommand(
    command=WithProperties(
        "/bin/rm -f /tmp/buildbot.sign.%(buildnumber)d "
            "/tmp/buildbot.p12.%(buildnumber)d"
    ),
    description=["buildenv", "cleanup"],
    descriptionDone=["buildenv", "cleanup"],
    haltOnFailure=True,
    alwaysRun=True,
))

PACKAGE.addStep(shell.ShellCommand(
    command=WithProperties(
    """
    for f in `ls -1 RELEASE-*`;
    do
        /bin/mv -v ${f} ${f%%snapshot%(buildnumber)d};
    done
    """
    ),
    description=["finalize", "build"],
    descriptionDone=["finalize", "build"],
))

PACKAGE.addStep(shell.SetProperty(
    command=WithProperties(
        "/bin/ls -1 "
            "%(shortProject)s-*.tgz "
            "%(shortProject)s-*.tar "
            "%(shortProject)s-*.zip "
            "%(shortProject)s-*.phar "
            "%(shortProject)s-*.pubkey "
            "%(shortProject)s-*.pem "
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
    ):
    if ext.endswith('.pubkey'):
        maxsize = 20 * (1 << 10) # 20 KB
    else:
        maxsize = 50 * (1 << 20) # 50 MB

    PACKAGE.addStep(transfer.FileUpload(
        slavesrc=WithProperties("%%(pkg%s:-)s" % ext),
        masterdest=WithProperties(
            "/var/www/pear/get/%%(pkg%s:-)s" % ext
        ),
        mode=0644,
        doStepIf=helpers.get_package(ext),
        maxsize=maxsize
    ))

    if ext.endswith('.pubkey'):
        label = "Signature (%s)" % ext
    else:
        label = "Package (%s)" % ext

    PACKAGE.addStep(Link(
        label=label,
        href=WithProperties(
            "%%(pear)s/get/%%(pkg%s:-)s" % ext,
            pear=lambda _: misc.PEAR_URL.rstrip('/'),
        ),
        doStepIf=helpers.get_package(ext),
    ))

PACKAGE.addStep(master.MasterShellCommand(
    command=WithProperties(
        "/bin/ln -sf '../certificate.pem' '/var/www/pear/get/%(pkg.pem:-)s'"
    ),
    description=['Linking', 'to', 'certificate'],
    descriptionDone=['Link', 'to', 'certificate'],
    doStepIf=helpers.get_package('.pem'),
))

PACKAGE.addStep(Link(
    label="Release certificate",
    href=WithProperties(
        "%(pear)s/get/%(pkg.pem:-)s",
        pear=lambda _: misc.PEAR_URL.rstrip('/'),
    ),
    doStepIf=helpers.get_package('.pem'),
))

PACKAGE.addStep(master.MasterShellCommand(
    command=" && ".join([
        # update-pear.sh takes care of removing old packages
        # from and adding new ones to the PEAR repository.
        "/var/www/update-pear.sh",
        "/bin/rm -rf /tmp/pirum_*",

        # Update permissions:
        # - all files should be readable by anybody
        # - anybody may browse through any directory
        "/bin/chmod -R a+r /var/www/pear/rest/",
        "/usr/bin/find /var/www/pear/rest -type d -exec chmod a+x '{}' '+'"
    ]),
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    description=['PEAR', 'repos.', 'update'],
    descriptionDone=['PEAR', 'repos.', 'update'],
    locks=[PIRUM_LOCK.access('exclusive')],
))

