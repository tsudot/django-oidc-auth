

class OpenIDConnectError(RuntimeError):
    def __init__(self, message=None):
        if not message:
            message = getattr(self, 'message', '')

        super(OpenIDConnectError, self).__init__(message)


class InvalidIdToken(OpenIDConnectError, ValueError):
    message = 'id_token MUST be signed'


class UnsuppportedSigningmethod(OpenIDConnectError, ValueError):
    def __init__(self, unsupported_method, supported_methods):
        message = 'Signing method %s not supported, options are (%s)' % (
                unsupported_method, ', '.join(supported_methods))

        super(UnsuppportedSigningmethod, self).__init__(message)
