"""Pydantic schemas for Wikidata concept matching with Gemini."""

from pydantic import BaseModel, Field


class ConceptMatch(BaseModel):
    """Represents a matched Wikidata concept for a keyword."""

    keyword: str = Field(
        ..., description="The original keyword from the repository"
    )
    concept_uri: str = Field(
        ..., description="The Wikidata concept URI (e.g., http://www.wikidata.org/entity/Q28865)"
    )
    label: str = Field(
        ..., description="The label/title of the matched concept"
    )
    description: str = Field(
        ..., description="The description of the matched concept"
    )
    confidence: str = Field(
        ..., description="Confidence level: 'high', 'medium', or 'low'"
    )
    reasoning: str = Field(
        ..., description="Brief explanation of why this match was selected"
    )


class ConceptMatchResult(BaseModel):
    """Container for a concept match result."""

    match: ConceptMatch = Field(
        ..., description="The matched concept for the keyword"
    )
