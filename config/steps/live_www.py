# -*- coding: utf-8 -*-

from buildbot.process import factory
from Erebot_buildbot.src import master

LIVE_WWW = factory.BuildFactory()
LIVE_WWW.addStep(master.MasterShellCommand(
    command="cd /var/www/Erebot/erebot && git pull",
    description=["Updating"],
    descriptionDone=["Updated"],
))

