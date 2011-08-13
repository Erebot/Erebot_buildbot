# -*- coding: utf-8 -*-

from zope.interface import Interface, implements
from buildbot.status.web.auth import IAuth, AuthBase, \
    BasicAuth as OrigBasicAuth, \
    HTPasswdAuth as OrigHTPasswdAuth

class AndAuth(AuthBase):
    implements(IAuth)

    def __init__(self, authenticators):
        self.authenticators = authenticators

    def authenticate(self, request):
        for authenticator in self.authenticators:
            if not authenticator.authenticate(request):
                self.err = authenticator.errmsg()
                return False
        return True

class OrAuth(AuthBase):
    implements(IAuth)

    def __init__(self, authenticators):
        self.authenticators = authenticators

    def authenticate(self, request):
        for authenticator in self.authenticators:
            if authenticator.authenticate(request):
                self.err = ""
                return True
        self.err = "Found no way to authenticate user."
        return False

class CertificateAuth(AuthBase):
    implements(IAuth)

    def __init__(self, validity_header, identity_header, users, field='CN'):
        self.users = list(users)
        self.validity_header = validity_header
        self.identity_header = identity_header
        self.field = field

    def authenticate(self, request):
        if not request.requestHeaders.getRawHeaders(self.validity_header, [None])[0]:
            self.err = "Invalid certificate"
            return False

        cert = request.requestHeaders.getRawHeaders(self.identity_header, [None])[0]
        if not cert or not cert.startswith('/'):
            self.err = "Invalid certificate"
            return False

        cert = cert[1:]

        result = {}
        for part in cert.split('/'):
            key, sep, value = part.partition('=')
            if not sep:
                self.err = "Invalid certificate"
                return False
            if key not in result:
                result[key] = []
            result[key].append(value)

        if len(result[self.field]) != 1:
            self.err = "Invalid value for field %s" % self.field
            return False

        if result[self.field][0] not in self.users:
            self.err = "Unauthorized certificate"
            return False

        self.err = ""
        return True

class BasicAuth(OrigBasicAuth):
    def authenticate(self, request):
        user = request.args.get("username", ["<unknown>"])[0]
        passwd = request.args.get("passwd", ["<no-password>"])[0]
        if user == "<unknown>" or passwd == "<no-password>":
            self.err = "Invalid username or password"
            return False
        return OrigBasicAuth.authenticate(self, user, passwd)

class HTPasswdAuth(OrigHTPasswdAuth):
    def authenticate(self, request):
        user = request.args.get("username", ["<unknown>"])[0]
        passwd = request.args.get("passwd", ["<no-password>"])[0]
        if user == "<unknown>" or passwd == "<no-password>":
            self.err = "Invalid username or password"
            return False
        return OrigHTPasswdAuth.authenticate(self, user, passwd)

