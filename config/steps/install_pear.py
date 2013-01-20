# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell
from Erebot_buildbot.config.steps import common
from Erebot_buildbot.config import misc
from Erebot_buildbot.src.steps import CountingShellCommand

INSTALL_PEAR = factory.BuildFactory()
INSTALL_PEAR.addStep(common.fill_properties)
INSTALL_PEAR.addStep(common.erebot_path)

INSTALL_PEAR.addStep(shell.ShellCommand(
    command=WithProperties(
        " && ".join([
            "/bin/rm -vrf pear .pearrc",
            "pear config-create `readlink -e ./` .pearrc",
            "/bin/mkdir -pv pear/bin",
            "pear -c .pearrc config-set bin_dir `readlink -e pear/bin`",
            "pear -c .pearrc config-set preferred_state devel",
            "pear -c .pearrc channel-update pear.php.net",
            "pear -c .pearrc install -o PEAR",
            "pear -c .pearrc channel-discover %(channel)s",
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

INSTALL_PEAR.addStep(CountingShellCommand(
    command=WithProperties(
        "pear -c .pearrc install --onlyreqdeps "
            "%(channel)s/%(shortProject)s-%(release)sdev%(pkgBuildnumber)s",
        channel=lambda _dummy: misc.PEAR_CHANNEL,
    ),
    errorPattern="^[Ff]ailed.*$",
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
    maxTime=10 * 60,
))
