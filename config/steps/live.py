# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell, transfer, source
from Erebot_buildbot.config.steps import common, helpers
from Erebot_buildbot.config import misc
from Erebot_buildbot.src import master
from Erebot_buildbot.src.steps import MorphProperties

def _got_revision(src, dest):
    def _inner(properties):
        try:
            revision = properties.getProperty(src)
            properties.setProperty(dest, revision, 'UpdateRevision')
        except KeyError:
            pass
    return _inner

LIVE = factory.BuildFactory()
LIVE.addStep(common.fill_properties)
LIVE.addStep(common.erebot_path)

# Stop or kill any previous instance of the bot.
LIVE.addStep(shell.ShellCommand(
    command="""
if [ -f /tmp/Erebot.pid ]
then
    /bin/kill -TERM `cat /tmp/Erebot.pid` 2> /dev/null;
    /bin/sleep 5;
    /bin/kill -KILL `cat /tmp/Erebot.pid` 2> /dev/null;
    /bin/rm -f /tmp/Erebot.pid;
fi
""",
    maxTime=30,
    description=["Stop", "previous"],
    descriptionDone=["Stop", "previous"],
))

LIVE.addStep(shell.ShellCommand(
    command='/bin/rm -rf *',
    description=["Cleanup"],
    descriptionDone=["Cleanup"],
))

# Download latest phar archive of Erebot.
LIVE.addStep(shell.ShellCommand(
    command=(
        "/usr/bin/curl '-#' -q --remote-time "
        "--tlsv1 --location --remote-name-all "
        "%(pear)s/get/Erebot-latest.phar "
        "%(pear)s/get/Erebot-latest.phar.pubkey "
        "%(pear)s/get/Erebot-latest.pem" % {
            'pear': misc.PEAR_URL.rstrip('/'),
        }
    ),
    maxTime=5 * 60,
    description=["Getting", 'Erebot-latest.phar'],
    descriptionDone=["Get", 'Erebot-latest.phar'],
))

LIVE.addStep(shell.ShellCommand(
    command="/bin/mkdir modules",
))

# Download latest phar archives for modules.
LIVE.addStep(shell.ShellCommand(
    command=(
        "/usr/bin/curl '-#' -q --remote-time "
        "--tlsv1 --location --remote-name-all "
        + ' '.join(
            "%(pear)s/get/%(component)s-latest.phar "
            "%(pear)s/get/%(component)s-latest.phar.pubkey "
            "%(pear)s/get/%(component)s-latest.pem" % {
                'pear': misc.PEAR_URL.rstrip('/'),
                'component': c.partition('/')[2]
            }
            for c in misc.COMPONENTS
            if c.startswith('Erebot/Erebot_Module_')
        )
    ),
    description=["Getting", "modules'", '.phar'],
    descriptionDone=["Get", "modules'", '.phar'],
    workdir='build/modules/',
    maxTime=5 * 60,
))

LIVE.addStep(master.MasterShellCommand(
    command=" && ".join([
        "/bin/rm -f /tmp/Erebot-config.tar.gz",
        "cd Erebot_buildbot/Erebot-config/",
        "/bin/tar czvf /tmp/Erebot-config.tar.gz Erebot.xml conf.d/",
    ]),
    description="Config",
    descriptionDone="Config",
))

LIVE.addStep(transfer.FileDownload(
    mastersrc="/tmp/Erebot-config.tar.gz",
    slavedest="Erebot-config.tar.gz",
))

LIVE.addStep(shell.ShellCommand(
    command=" && ".join([
        "/bin/tar zxvf Erebot-config.tar.gz",
        "/bin/rm -f Erebot-config.tar.gz",
    ]),
    description=["Unpack", 'config'],
    descriptionDone=["Unpack", 'config'],
    maxTime=5 * 60,
))

# Start new instance.
LIVE.addStep(shell.ShellCommand(
    command=
        "php "
            "-d error_log=syslog "
            "-d log_errors=On "
            "-d ignore_repeated_errors=On "
        "-f Erebot-latest.phar -- "
            "--daemon "
            "--pidfile /tmp/Erebot.pid "
            "< /dev/null "
            "> /dev/null "
            "2>&1",
    env={
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
        'LANG': None,
        'LANGUAGE': None,
        'LC_MESSAGES': 'fr_FR.UTF-8',
        'LC_MONETARY': 'fr_FR.UTF-8',
        'LC_NUMERIC': 'fr_FR.UTF-8',
        'LC_TIME': 'fr_FR.UTF-8',
    },
    description=["Start", "Erebot"],
    descriptionDone=["Start", "Erebot"],
    maxTime=10,
))

# Give it a little time to start properly.
LIVE.addStep(shell.ShellCommand(
    command="/bin/sleep 10",
    description="Pause",
    descriptionDone="Pause",
))

# Check that it is still running.
LIVE.addStep(shell.ShellCommand(
    command="/bin/kill -0 `cat /tmp/Erebot.pid`",
    description=["Check", "instance"],
    descriptionDone=["Check", "instance"],
))
