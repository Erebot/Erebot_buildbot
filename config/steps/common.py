# -*- coding: utf-8 -*-

from buildbot.steps.source import Git
from buildbot.steps.slave import SetPropertiesFromEnv

clone = Git(
    mode='clobber',
    repourl='%s.git',
    submodules=True,
    progress=True,
)

erebot_path = SetPropertiesFromEnv(variables=['EREBOT_PATH'])
