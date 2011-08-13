# -*- coding: utf-8 -*-

from buildbot.process import factory
from Erebot_buildbot.config.steps import common

PDF_DOC = factory.BuildFactory()
PDF_DOC.addStep(common.clone)

