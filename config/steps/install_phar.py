# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell, transfer
from Erebot_buildbot.config.steps import common
from Erebot_buildbot.config import misc

INSTALL_PHAR = factory.BuildFactory()
INSTALL_PHAR.addStep(common.fill_properties)
INSTALL_PHAR.addStep(common.erebot_path)

INSTALL_PHAR.addStep(transfer.FileDownload(
    mastersrc="Erebot_buildbot/class3.crt",
    slavedest="CAcert-class3.crt",
))

INSTALL_PHAR.addStep(shell.ShellCommand(
    command=WithProperties(
        " && ".join([
            "/bin/rm -vrf modules",
            "/bin/mkdir -v modules",
            "/usr/bin/curl -L --remote-name-all --cacert CAcert-class3.crt "
                "'%(repos)s/get/%(shortProject)s-%(release)sdev%(pkgBuildnumber)s.phar' "
                "'%(repos)s/get/%(shortProject)s-%(release)sdev%(pkgBuildnumber)s.phar.pubkey' "
                "'%(repos)s/get/%(shortProject)s-%(release)sdev%(pkgBuildnumber)s.pem' ",
        ]),
        repos=lambda _dummy: misc.PEAR_URL,
    ),
    description="Preparing",
    descriptionDone="Prepare",
))

INSTALL_PHAR.addStep(shell.ShellCommand(
    command=WithProperties(
        "php -f '%(shortProject)s-%(release)sdev%(pkgBuildnumber)s.phar'",
    ),
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    description=["Verifying", "integrity"],
    descriptionDone=["Integrity", "check"],
))

