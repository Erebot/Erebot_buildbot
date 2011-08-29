# -*- encoding: utf-8 -*-

#from lxml import etree

import re
from twisted.python import log
from buildbot.steps.shell import ShellCommand
from buildbot.process.buildstep import BuildStep, LogLineObserver
from buildbot.status.builder import SUCCESS, WARNINGS, FAILURE, SKIPPED, \
                                     EXCEPTION, STDOUT, STDERR

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

class CountingShellCommand(ShellCommand):
    errorCount = 0
    errorPattern = '.*error[: ].*'
    warnCount = 0
    warningPattern = '.*warning[: ].*'

    # The defaults work for GNU Make.
    directoryEnterPattern = "make.*: Entering directory [\"`'](.*)['`\"]"
    directoryLeavePattern = "make.*: Leaving directory"
    suppressionFile = None

    commentEmptyLineRe = re.compile(r"^\s*(\#.*)?$")
    suppressionLineRe = re.compile(r"^\s*(.+?)\s*:\s*(.+?)\s*(?:[:]\s*([0-9]+)(?:-([0-9]+))?\s*)?$")

    def __init__(self, workdir=None,
                 errorPattern=None, errorExtractor=None,
                 warningPattern=None, warningExtractor=None,
                 directoryEnterPattern=None, directoryLeavePattern=None,
                 suppressionFile=None, **kwargs):
        self.workdir = workdir
        # See if we've been given a regular expression to use to match
        # warnings. If not, use a default that assumes any line with "warning"
        # present is a warning. This may lead to false positives in some cases.
        if warningPattern:
            self.warningPattern = warningPattern
        if errorPattern:
            self.errorPattern = errorPattern

        if directoryEnterPattern:
            self.directoryEnterPattern = directoryEnterPattern
        if directoryLeavePattern:
            self.directoryLeavePattern = directoryLeavePattern
        if suppressionFile:
            self.suppressionFile = suppressionFile

        if errorExtractor:
            self.errorExtractor = errorExtractor
        else:
            self.errorExtractor = CountingShellCommand.extractWholeLine

        if warningExtractor:
            self.warningExtractor = warningExtractor
        else:
            self.warningExtractor = CountingShellCommand.extractWholeLine

        # And upcall to let the base class do its work
        ShellCommand.__init__(self, workdir=workdir, **kwargs)

        self.addFactoryArguments(errorPattern=errorPattern,
                                 warningPattern=warningPattern,
                                 directoryEnterPattern=directoryEnterPattern,
                                 directoryLeavePattern=directoryLeavePattern,
                                 errorExtractor=errorExtractor,
                                 warningExtractor=warningExtractor,
                                 suppressionFile=suppressionFile)
        self.suppressions = []
        self.directoryStack = []

    def addSuppression(self, suppressionList):
        """
        This method can be used to add patters of warnings that should
        not be counted.

        It takes a single argument, a list of patterns.

        Each pattern is a 4-tuple (FILE-RE, WARN-RE, START, END).

        FILE-RE is a regular expression (string or compiled regexp), or None.
        If None, the pattern matches all files, else only files matching the
        regexp. If directoryEnterPattern is specified in the class constructor,
        matching is against the full path name, eg. src/main.c.

        WARN-RE is similarly a regular expression matched against the
        text of the warning, or None to match all warnings.

        START and END form an inclusive line number range to match against. If
        START is None, there is no lower bound, similarly if END is none there
        is no upper bound."""

        for fileRe, lineRe, start, end in suppressionList:
            if fileRe != None and isinstance(fileRe, str):
                fileRe = re.compile(fileRe)
            if lineRe != None and isinstance(lineRe, str):
                lineRe = re.compile(lineRe)
            self.suppressions.append((fileRe, lineRe, start, end))

    def extractWholeLine(self, line, match):
        """
        Extract warning text as the whole line.
        No file names or line numbers."""
        return (None, None, line)

    def extractFromRegexpGroups(self, line, match):
        """
        Extract file name, line number, and warning text as groups (1,2,3)
        of warningPattern match."""
        file = match.group(1)
        lineNo = match.group(2)
        if lineNo != None:
            lineNo = int(lineNo)
        text = match.group(3)
        return (file, lineNo, text)

    def maybeAddWarning(self, stack, line, match, is_error):
        if self.suppressions:
            if is_error:
                (file, lineNo, text) = self.errorExtractor(self, line, match)
            else:
                (file, lineNo, text) = self.warnExtractor(self, line, match)

            if file != None and file != "" and self.directoryStack:
                currentDirectory = self.directoryStack[-1]
                if currentDirectory != None and currentDirectory != "":
                    file = "%s/%s" % (currentDirectory, file)

            # Skip adding the warning if any suppression matches.
            for fileRe, warnRe, start, end in self.suppressions:
                if ( (file == None or fileRe == None or fileRe.search(file)) and
                     (warnRe == None or  warnRe.search(text)) and
                     ((start == None and end == None) or
                      (lineNo != None and start <= lineNo and end >= lineNo)) ):
                    return

        stack.append(line)
        if is_error:
            self.warnCount += 1
        else:
            self.errorCount += 1

    def createSummary(self, log):
        """
        Match log lines against warningPattern.

        Warnings are collected into another log for this step, and the
        build-wide 'warnings-count' is updated."""

        self.warnCount = 0
        self.errorCount = 0

        # Now compile a regular expression from whichever warning pattern we're
        # using
        if (not self.warningPattern) and (not self.errorPattern):
            return

        wre = self.warningPattern
        if isinstance(wre, str):
            wre = re.compile(wre)

        ere = self.errorPattern
        if isinstance(ere, str):
            ere = re.compile(ere)

        directoryEnterRe = self.directoryEnterPattern
        if directoryEnterRe != None and isinstance(directoryEnterRe, str):
            directoryEnterRe = re.compile(directoryEnterRe)

        directoryLeaveRe = self.directoryLeavePattern
        if directoryLeaveRe != None and isinstance(directoryLeaveRe, str):
            directoryLeaveRe = re.compile(directoryLeaveRe)

        # Check if each line in the output from this command matched our
        # warnings regular expressions. If did, bump the warnings count and
        # add the line to the collection of lines with warnings
        errors = []
        warnings = []
        # TODO: use log.readlines(), except we need to decide about stdout vs
        # stderr
        for line in log.getText().split("\n"):
            if directoryEnterRe:
                match = directoryEnterRe.search(line)
                if match:
                    self.directoryStack.append(match.group(1))
                if (directoryLeaveRe and
                    self.directoryStack and
                    directoryLeaveRe.search(line)):
                        self.directoryStack.pop()

            match = ere.match(line)
            if match:
                self.maybeAddWarning(errors, line, match, True)
            else:
                match = wre.match(line)
                if match:
                    self.maybeAddWarning(warnings, line, match, False)

        # If there were any warnings, make the log if lines with warnings
        # available
        if self.warnCount:
            self.addCompleteLog("warnings (%d)" % self.warnCount,
                    "\n".join(warnings) + "\n")

        if self.errorCount:
            self.addCompleteLog("errors (%d)" % self.errorCount,
                    "\n".join(errors) + "\n")

        warnings_stat = self.step_status.getStatistic('warnings', 0)
        self.step_status.setStatistic('warnings', warnings_stat + self.warnCount)

        try:
            old_count = self.getProperty("warnings-count")
        except KeyError:
            old_count = 0
        self.setProperty("warnings-count", old_count + self.warnCount, "CountingShellCommand")

        errors_stat = self.step_status.getStatistic('errors', 0)
        self.step_status.setStatistic('errors', errors_stat + self.errorCount)

        try:
            old_count = self.getProperty("errors-count")
        except KeyError:
            old_count = 0
        self.setProperty("errors-count", old_count + self.errorCount, "CountingShellCommand")


    def evaluateCommand(self, cmd):
        if cmd.rc != 0:
            return FAILURE
        if self.errorCount:
            return FAILURE
        if self.warnCount:
            return WARNINGS
        return SUCCESS

