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
            rev = properties.getProperty(src)
            properties.setProperty(dest, res, 'UpdateRevision')
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

for component in misc.COMPONENTS:
    if component.startswith('Erebot/Erebot_Module_'):
        LIVE.addStep(shell.ShellCommand(
            command='/bin/rm -rf build/vendor/%s' % component.partition('/')[2],
            description=["Cleanup:", component],
            descriptionDone=["Cleanup:", component],
        ))

LIVE.addStep(common.clone)
LIVE.addStep(MorphProperties(
    morph_fn=_got_revision('got_revision', 'got_revision[Erebot]')
))
LIVE.addStep(shell.Compile(
    command="phing",
    env={
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    warnOnWarnings=True,
    warnOnFailure=True,
    maxTime=5 * 60,
))

for component in misc.COMPONENTS:
    if component.startswith('Erebot/Erebot_Module_'):
        LIVE.addStep(source.Git(
            workdir='build/vendor/%s' % component.partition('/')[2],
            mode='clobber',
            repourl=common.convert_repourl(0)(
                '%s/%s' % (misc.GITHUB_BASE.rstrip('/'), component)
            ),
            submodules=True,
            progress=True,
            alwaysUseLatest=True,   # Would fail otherwise.
        ))
        LIVE.addStep(MorphProperties(
            morph_fn=_got_revision(
                'got_revision',
                'got_revision[%s]' % (component, )
            )
        ))

        LIVE.addStep(shell.Compile(
            command=(
                "cd vendor/%s && "
                # Build the translations.
                "phing"
            ) % component.partition('/')[2],
            env={
                'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
            },
            warnOnWarnings=True,
            warnOnFailure=True,
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

LIVE.addStep(shell.ShellCommand(
    command="; ".join([
        "pear channel-update pear.php.net", # Update protocols if needed.
        "pear i pear/Console_CommandLine",
        "pear i pear/File_Gettext",
        ":",                                # Never fail.
    ]),
    env={
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    description=["PEAR", 'deps'],
    descriptionDone=["PEAR", 'deps'],
    maxTime=5 * 60,
))

# Start new instance.
LIVE.addStep(shell.ShellCommand(
    command=
        "php "
            "-d error_log=syslog "
            "-d log_errors=On "
            "-d ignore_repeated_errors=On "
        "scripts/Erebot "
            "--daemon "
            "--pidfile /tmp/Erebot.pid "
            "< /dev/null "
            "> /dev/null "
            "2>&1",
    env={
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
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

# Copy the revision back.
LIVE.addStep(MorphProperties(
    morph_fn=_got_revision('got_revision[Erebot]', 'got_revision')
))
