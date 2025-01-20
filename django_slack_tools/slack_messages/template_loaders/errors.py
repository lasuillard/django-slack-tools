# noqa: D100


class TemplateLoadError(Exception):
    """Base class for template loader errors."""


class TemplateNotFoundError(TemplateLoadError):
    """Template not found error."""
