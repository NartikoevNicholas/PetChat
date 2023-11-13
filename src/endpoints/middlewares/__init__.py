from .rate_limiter_middleware import RateLimiterMiddleware


middlewares = [
    RateLimiterMiddleware()
]

__all__ = [
    'middlewares'
]
