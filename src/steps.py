# -*- encoding: utf-8 -*-

#from lxml import etree

from buildbot.steps.shell import ShellCommand
from buildbot.process.buildstep import BuildStep, LogLineObserver
from buildbot.status.builder import SUCCESS, WARNINGS, FAILURE, SKIPPED, \
     EXCEPTION

class Link(BuildStep):
    name = "Link"

    def __init__(self, label, href, **kwargs):
        BuildStep.__init__(self, **kwargs)
        self.addFactoryArguments(label=label)
        self.addFactoryArguments(href=href)
        self.label = label
        self.href = href

    def start(self):
        properties = self.build.getProperties()
        href = properties.render(self.href)
        self.addURL(self.label, href)
        self.finished(SUCCESS)

class PHPUnit(ShellCommand, LogLineObserver):
    name = 'PHPUnit'

    def __init__(self, **kwargs):
        ShellCommand.__init__(self, **kwargs)
        LogLineObserver.__init__(self)
        self.addLogObserver('stdio', self)
        self.metrics = {
            "run": 0,
            "Failures": 0,
            "Errors": 0,
            "Incomplete": 0,
            "Skipped": 0,
            "Time elapsed": 0,
        }
        self.progressMetrics += tuple(self.metrics.keys())
        self.phpError = False

    def outLineReceived(self, line):
        if 'PHP Error' in line:
            self.phpError = True
        if self.phpError:
            return
        if '[phpunit]' not in line or ' Tests ' not in line:
            return
        (ign, sep, rest) = line.partition(' Tests ')
        if not rest:
            return
        (rest, sep, ign) = rest.rpartition('\033')
        if not rest:
            return
        rest = rest.split(', ')
        metrics = {}
        for i in rest:
            metric, value = i.split(': ')
            value = float(value.rstrip(' s'))
            metrics[metric] = value

        for metric, value in metrics.iteritems():
            if value > 0:
                self.metrics[metric] += value
                self.step.setProgress(metric, self.metrics[metric])

    def evaluateCommand(self, cmd):
        self.setProperty('Passed', False)
        if cmd.rc != 0:
            return FAILURE
        if self.phpError:
            return FAILURE
        if self.metrics['Failures']:
            return FAILURE
        if self.metrics['Errors']:
            return EXCEPTION

        self.setProperty('Passed', True)
        if self.metrics['Skipped'] or self.metrics['Incomplete']:
            return WARNINGS
        if not self.metrics['run']:
            return WARNINGS
        return SUCCESS

#class Xslt(BuildStep):
#    name = "xslt"

#    def __init__(self, infile, outfile, xslt_file, **kwargs):
#        BuildStep.__init__(self, **kwargs)
#        self.addFactoryArguments(infile=infile)
#        self.addFactoryArguments(outfile=outfile)
#        self.addFactoryArguments(xslt_file=xslt_file)
#        self.infile = infile
#        self.outfile = outfile
#        self.xslt_file = xslt_file

#    def start(self):
#        properties = self.build.getProperties()
#        infile = properties.render(self.infile)
#        outfile = properties.render(self.outfile)
#        xslt_file = properties.render(self.xslt_file)

#        try:
#            infile_desc = file(infile, 'r')
#        except:
#            return self.finished(FAILURE)

#        try:
#            infile_tree = etree.parse(infile_desc.read())
#        except:
#            return self.finished(FAILURE)
#        finally:
#            infile_desc.close()

#        try:
#            xslt_desc = file(xslt_file, 'r')
#        except:
#            del infile_tree
#            return self.finished(FAILURE)

#        try:
#            xslt = etree.XSLT(etree.parse(xslt_desc.read()))
#        except:
#            del infile_tree
#            return self.finished(FAILURE)
#        finally:
#            xslt_desc.close()

#        try:
#            outfile_tree = xslt(infile_tree)
#        except:
#            return self.finished(FAILURE)
#        finally:
#            del xslt
#            del infile_tree

#        try:
#            outfile_desc = file(outfile, 'w')
#        except:
#            del outfile_tree
#            return self.finished(FAILURE)

#        try:
#            outfile_desc.write(etree.tostring(outfile_tree))
#        except:
#            del outfile_tree
#            return self.finished(FAILURE)
#        finally:
#            outfile_desc.close()

#        self.finished(SUCCESS)

