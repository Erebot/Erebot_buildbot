# -*- coding: utf-8 -*-
from buildbot.process.factory import BuildFactory

class MultiProjectBuildFactory(BuildFactory):
    """
    The L{MultiProjectBuildFactory} class can be used to define
    a different factory for each project.
    """
    def __init__(self, factories):
        if not isinstance(factories, dict):
            raise ValueError('Expected a dict mapping projects to factories')
        for project, factory in factories.iteritems():
            if not isinstance(factory, BuildFactory):
                raise ValueError('Invalid BuildFactory for project %s', project)
        self.factories = factories
        self.empty_factory = BuildFactory()

    @property
    def steps(self):
        substeps = []
        for factory in self.factories.itervalues():
            substeps.extend(factory.steps)
        return substeps

    def addStep(self, *args, **kwargs):
        raise NotImplementedError('You cannot add a step to a MultiProjectBuildFactory, add the step to a subfactory instead.')

    def newBuild(self, request):
        """Create a new Build instance.
        @param request: a list of L{base.BuildRequest}
            describing what is to be built
        """
        b = self.buildClass(request)
        b.useProgress = self.useProgress
        b.workdir = self.workdir
        project = request[0].source.project
        b.setStepFactories(self.factories.get(project, self.empty_factory))
        return b

