# -*- coding: utf-8 -*-

from buildbot.process import factory, properties
from buildbot.steps import shell, transfer
from Erebot_buildbot.config.steps import common, helpers
from Erebot_buildbot.src import master

LIVE = factory.BuildFactory()

# Stop or kill any previous instance of the bot.
LIVE.addStep(shell.ShellCommand(
    command="""
if [ -f Erebot.pid ]
then
    kill -TERM `cat Erebot.pid` 2> /dev/null;
    sleep 5;
    kill -KILL `cat Erebot.pid` 2> /dev/null;
    rm -f Erebot.pid;
fi
""",
    maxTime=30,
))

LIVE.addStep(common.clone)

LIVE.addStep(master.MasterShellCommand(
    command=" && ".join([
        "rm -f /tmp/Erebot-config.tar.gz",
        "cd Erebot_buildbot/Erebot-config/",
        "tar czvf /tmp/Erebot-config.tar.gz Erebot.xml conf.d/",
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
        "tar zxvf Erebot-config.tar.gz",
        "rm -f Erebot-config.tar.gz",
    ]),
    description=["Unpack", 'config'],
    descriptionDone=["Unpack", 'config'],
    maxTime=5 * 60,
))

# Start new instance.
LIVE.addStep(shell.ShellCommand(
    command="php scripts/Erebot --daemon --pidfile Erebot.pid",
    env={
        'PATH': properties.WithProperties("%(bin_dir)s:${PATH}"),
    },
    description=["Start", "Erebot"],
    descriptionDone=["Start", "Erebot"],
    maxTime=60,
))

# Give it a little time to start properly.
LIVE.addStep(shell.ShellCommand(
    command="sleep 10",
    description="Pause",
    descriptionDone="Pause",
))

# Check that it is still running.
LIVE.addStep(shell.ShellCommand(
    command="kill -0 `cat Erebot.pid`",
    description=["Check", "instance"],
    descriptionDone=["Check", "instance"],
))

