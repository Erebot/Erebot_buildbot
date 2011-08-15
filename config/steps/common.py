# -*- coding: utf-8 -*-

from buildbot.steps import source

clone = source.Git(
    mode='clobber',
    repourl='%s.git',
    submodules=True,
    progress=True,
)

