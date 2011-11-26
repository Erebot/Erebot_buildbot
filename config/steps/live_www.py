# -*- coding: utf-8 -*-

from buildbot.process import factory
from Erebot_buildbot.src import master

LIVE_WWW = factory.BuildFactory()
LIVE_WWW.addStep(shell.MasterShellCommand(
    command="cd /var/www/Erebot/erebot && git pull",
    maxTime=5*60,
    description=["Updating"],
    descriptionDone=["Updated"],
))

