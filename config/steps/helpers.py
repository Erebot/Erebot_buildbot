# -*- coding: utf-8 -*-

def find_packages():
    def _extractor(rc, stdout, stderr):
        lines = stdout.splitlines()
        exts = ['.zip', '.tar', '.tgz', '.phar']
        for ext in exts[:]:
            exts.append(ext + '.pubkey')
        exts.append('.pem')
        prefix = None
        props = {}

        for line in lines:
            for ext in exts:
                if line.endswith(ext):
                    prop_ext = 'pkg' + ext
                    pfx = line[:-len(ext)]
                    if prefix is None:
                        prefix = pfx
                    elif pfx != prefix:
                        raise ValueError("Invalid prefix")
                    elif prop_ext in props:
                        raise ValueError("Extension %s already found" % ext)
                    props[prop_ext] = line
        return props
    return _extractor

def get_package(ext):
    ext = ext.lstrip('.')
    # step.getProperty(foo, bar) is not supported
    # by older versions of buildbot (< 0.8.4 ?).
    def _getter(step):
        props = step.build.getProperties()
        return props.getProperty('pkg.' + ext, None)
    return _getter

def if_component(component):
    def _inner(step):
        return component == step.getProperty('project')
    return _inner

def if_buildslave(buildslave):
    def _inner(step):
        return buildslave == step.getSlaveName()
    return _inner

def with_links(links, f=None):
    def _inner(step):
        if isinstance(links, dict):
            it = links.iteritems()
        else:
            it = links
        for (name, url) in it:
            step.addURL(name, url)

        if f is None:
            return True
        return f(step)
    return _inner

def negate(f):
    def _inner(step):
        return not f(step)
    return _inner

def pass_all(*fs):
    def _inner(step):
        for f in fs:
            if not f(step):
                return False
        return True
    return _inner

def pass_any(*fs):
    def _inner(step):
        for f in fs:
            if f(step):
                return True
        return False
    return _inner

