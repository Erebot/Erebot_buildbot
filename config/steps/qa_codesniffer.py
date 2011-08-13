# -*- coding: utf-8 -*-

from buildbot.process import factory
from Erebot_buildbot.config.steps import common

QA_CODESNIFFER = factory.BuildFactory()
QA_CODESNIFFER.addStep(common.clone)

