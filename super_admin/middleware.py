#middleware.py
import logging
from django.utils.deprecation import MiddlewareMixin
from contextvars import ContextVar
from contextlib import contextmanager
from functools import wraps

logger = logging.getLogger("django")

# Async-safe per-request holder
_current_user = ContextVar("_current_user", default=None)

def set_current_user(user):
    return _current_user.set(user if getattr(user, "is_authenticated", False) else None)

def reset_current_user(token):
    if token is not None:
        _current_user.reset(token)

def get_current_user():
    return _current_user.get()

@contextmanager
def actor_context(user):
    """
    Ensure get_current_user() returns `user` while inside this block.
    Wrap serializer.save() with this.
    """
    token = set_current_user(user)
    try:
        yield
    finally:
        reset_current_user(token)

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.info(f"Request: {request.method} {request.path}")

    def process_response(self, request, response):
        logger.info(f"Response: {response.status_code} {request.path}")
        return response

# Optional helpers (useful for FBV/CBV)
def with_current_user(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        with actor_context(request.user):
            return view_func(request, *args, **kwargs)
    return _wrapped

class WithCurrentUserMixin:
    def initial(self, request, *args, **kwargs):
        self.__actor_cm__ = actor_context(request.user)
        self.__actor_cm__.__enter__()
        return super().initial(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        try:
            return super().finalize_response(request, response, *args, **kwargs)
        finally:
            cm = getattr(self, "__actor_cm__", None)
            if cm:
                cm.__exit__(None, None, None)
