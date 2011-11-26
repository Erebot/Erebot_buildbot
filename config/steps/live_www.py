# -*- coding: utf-8 -*-

from buildbot.process import factory
from Erebot_buildbot.src import master

LIVE_WWW = factory.BuildFactory()
LIVE_WWW.addStep(master.MasterShellCommand(
    command=" && ".join([
        "cd /var/www/Erebot/erebot"
        "git pull"
    ]),
    description=["Updating"],
    descriptionDone=["Updated"],
))

LIVE_WWW.addStep(master.MasterShellCommand(
    command=" && ".join([
        "cd /var/www/Erebot/erebot",
        "git log -1 --pretty=oneline --no-color | cut -d ' ' -f 1"
    ]),
    description=["Revision"],
    descriptionDone=["Revision"],
    extract_fn=lambda rc, stdout, stderr: {'got_revision': stdout},
    strip=True,
))

