

class OpenIDConnectError(RuntimeError):
    def __init__(self, message=None):
        if not message:
            message = getattr(self, 'message', '')

        super(OpenIDConnectError, self).__init__(message)


class InvalidIdToken(OpenIDConnectError, ValueError):
    message = 'id_token MUST be signed'


class UnsuppportedSigningMethod(OpenIDConnectError, ValueError):
    def __init__(self, unsupported_method, supported_methods):
        message = 'Signing method %s not supported, options are (%s)' % (
                unsupported_method, ', '.join(supported_methods))

        super(UnsuppportedSigningMethod, self).__init__(message)


class RequestError(OpenIDConnectError):
    def __init__(self, url, status_code):
        message = 'GET %s returned %s status code (200 expected)' % (url, status_code)
        super(RequestError, self).__init__(message)
