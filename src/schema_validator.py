#!/usr/bin/env python3
"""
Schema validation utilities for CodeMeta metadata.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

# CodeMeta 3.1 schema context
CODEMETA_CONTEXT = "https://codemeta.github.io/terms/"

# List of all valid CodeMeta 3.1 properties
VALID_PROPERTIES = {
    # Core properties
    "@context", "@type", "@id",
    # Schema.org properties
    "address", "affiliation", "applicationCategory", "applicationSubCategory",
    "author", "citation", "codeRepository", "contributor", "copyrightHolder",
    "copyrightYear", "dateCreated", "dateModified", "datePublished",
    "description", "downloadUrl", "editor", "email", "encoding", "endDate",
    "familyName", "fileFormat", "fileSize", "funder", "givenName", "hasPart",
    "identifier", "installUrl", "isAccessibleForFree", "isPartOf", "keywords",
    "license", "memoryRequirements", "name", "operatingSystem", "permissions",
    "position", "processorRequirements", "producer", "programmingLanguage",
    "provider", "publisher", "relatedLink", "releaseNotes", "review",
    "reviewAspect", "reviewBody", "roleName", "runtimePlatform", "sameAs",
    "softwareHelp", "softwareRequirements", "softwareVersion", "sponsor",
    "startDate", "storageRequirements", "supportingData", "targetProduct",
    "url", "version",
    # CodeMeta-specific properties
    "buildInstructions", "continuousIntegration", "developmentStatus",
    "embargoEndDate", "funding", "hasSourceCode", "isSourceCodeOf",
    "issueTracker", "maintainer", "readme", "referencePublication",
    "softwareSuggestions"
}

def validate_property(property_name: str) -> Tuple[bool, str]:
    """
    Validate if a property is a valid CodeMeta property.

    Args:
        property_name (str): The property name to validate.

    Returns:
        Tuple[bool, str]: A tuple of (is_valid, message).
    """
    if property_name in VALID_PROPERTIES:
        return True, f"Property '{property_name}' is valid."
    else:
        return False, f"Property '{property_name}' is not a valid CodeMeta property."

def validate_metadata(metadata: Dict) -> Tuple[bool, List[str]]:
    """
    Validate CodeMeta metadata against the CodeMeta 3.1 schema.

    Args:
        metadata (Dict): The metadata dictionary to validate.

    Returns:
        Tuple[bool, List[str]]: A tuple of (is_valid, list_of_errors).
    """
    errors = []

    # Check for required @context
    if "@context" not in metadata:
        errors.append("Missing required '@context' property.")
    elif metadata["@context"] != CODEMETA_CONTEXT:
        errors.append(f"Invalid '@context'. Expected '{CODEMETA_CONTEXT}', got '{metadata['@context']}'.")

    # Check for required @type
    if "@type" not in metadata:
        errors.append("Missing required '@type' property.")
    elif metadata["@type"] != "SoftwareSourceCode":
        errors.append(f"Invalid '@type'. Expected 'SoftwareSourceCode', got '{metadata['@type']}'.")

    # Check for invalid properties
    for property_name in metadata.keys():
        if property_name not in VALID_PROPERTIES:
            errors.append(f"Unknown property '{property_name}'.")

    is_valid = len(errors) == 0
    return is_valid, errors

def print_validation_report(metadata: Dict) -> None:
    """
    Print a validation report for the metadata.

    Args:
        metadata (Dict): The metadata dictionary to validate.
    """
    is_valid, errors = validate_metadata(metadata)

    print("\n" + "=" * 80)
    print("CODEMETA VALIDATION REPORT")
    print("=" * 80)

    if is_valid:
        print("\n✓ Metadata is VALID according to CodeMeta 3.1 schema.")
    else:
        print("\n✗ Metadata is INVALID. Errors found:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")

    print(f"\nProperties found: {len(metadata) - 2}")  # Excluding @context and @type
    print(f"Valid properties: {len([k for k in metadata.keys() if k in VALID_PROPERTIES])}")
    print(f"Invalid properties: {len([k for k in metadata.keys() if k not in VALID_PROPERTIES])}")

    print("\n" + "=" * 80)
