# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell
from Erebot_buildbot.config.steps import common
from Erebot_buildbot.config import misc
from Erebot_buildbot.src.steps import CountingShellCommand

INSTALL_PYRUS = factory.BuildFactory()
INSTALL_PYRUS.addStep(common.fill_properties)
INSTALL_PYRUS.addStep(common.erebot_path)

INSTALL_PYRUS.addStep(shell.ShellCommand(
    command=WithProperties(
        " && ".join([
            "/bin/rm -vrf pyrus",
            "/bin/mkdir -pv pyrus/bin",
            "pyrus.phar pyrus/ di %(channel)s",
            "pyrus.phar pyrus/ set bin_dir `readlink -e pyrus/bin`",
            "pyrus.phar pyrus/ set preferred_state devel",
            "pyrus.phar pyrus/ set auto_discover 1",
        ]),
        channel=lambda _dummy: misc.PEAR_CHANNEL,
    ),
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    description="Preparing",
    descriptionDone="Prepare",
))

INSTALL_PYRUS.addStep(CountingShellCommand(
    command=WithProperties(
        "pyrus.phar pyrus/ i "
            "%(channel)s/%(shortProject)s-%(release)sdev%(pkgBuildnumber)s",
        channel=lambda _dummy: misc.PEAR_CHANNEL,
    ),
    errorPattern="^.*Exception.*$",
    warnOnWarnings=True,
    flunkOnFailure=True,
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    description=["Installing", "package"],
    descriptionDone=["Install", "package"],
))
