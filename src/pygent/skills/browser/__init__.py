"""Browser skill for fetching and inspecting web pages."""

from pygent.skills.browser.skill import BrowserSkill
from pygent.skills.browser.tools import FindTextTool, OpenURLTool

__all__ = [
    "BrowserSkill",
    "FindTextTool",
    "OpenURLTool",
]
