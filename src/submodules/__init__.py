"""Submodules for handling specific Codemeta schema elements."""

from .name import NameSubmodule
from .description import DescriptionSubmodule
from .url import UrlSubmodule
from .code_repository import CodeRepositorySubmodule
from .version import VersionSubmodule
from .identifier import IdentifierSubmodule
from .keywords import KeywordsSubmodule

__all__ = [
    "NameSubmodule",
    "DescriptionSubmodule",
    "UrlSubmodule",
    "CodeRepositorySubmodule",
    "VersionSubmodule",
    "IdentifierSubmodule",
    "KeywordsSubmodule",
]
