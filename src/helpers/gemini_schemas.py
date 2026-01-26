"""Pydantic schemas for Gemini API structured output."""

from typing import List

from pydantic import BaseModel, Field


class Keyword(BaseModel):
    """Represents a single keyword with context information."""

    name: str = Field(
        ..., description="The keyword itself (e.g., 'OpenStreetMap', 'Python')"
    )
    context_clues: str = Field(
        ..., description="Why it's relevant to the repository"
    )


class KeywordList(BaseModel):
    """Container for a list of keywords extracted from a repository."""

    keywords: List[Keyword] = Field(
        ..., description="List of keywords extracted from the repository"
    )
