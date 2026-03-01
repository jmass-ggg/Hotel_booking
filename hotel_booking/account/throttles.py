from rest_framework.throttling import SimpleRateThrottle

class LoginRateThrottle(SimpleRateThrottle):
    scope="login"
    def get_cache_key(self, request, view):
        ip = self.get_ident(request)
        if not ip:
            return None
        return self.cache_format % {"scope": self.scope, "ident": ip}

class RegisterRateThrottle(SimpleRateThrottle):
    scope = "register"

    def get_cache_key(self, request, view):
        ip = self.get_ident(request)
        if not ip:
            return None
        return self.cache_format % {"scope": self.scope, "ident": ip}