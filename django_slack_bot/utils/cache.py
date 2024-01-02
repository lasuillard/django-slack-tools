"""Utils for having fun with Django cache framework."""
from django_slack_bot import __version__


def generate_cache_key(key: str) -> str:
    """Generate an cache key for this package version."""
    return f"{__package__}:{__version__}:{key}"
