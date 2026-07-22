"""Template Engine — renders canonical resume JSON into templates.

Supports multiple template formats and hot-swappable templates.
"""

from app.services.templates.engine import TemplateEngine, TemplateInfo

__all__ = ["TemplateEngine", "TemplateInfo"]
