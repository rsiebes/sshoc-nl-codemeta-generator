# Codemeta 3.1 Generator - Architecture

## Overview

The Codemeta 3.1 Generator is built using a modular architecture where each metadata element category is handled by a dedicated Python module. This design ensures maintainability, testability, and extensibility.

## Module Organization

### Core Modules

#### 1. **scraper.py** - GitHub Web Scraper
- **Responsibility**: Extract raw data from GitHub repository pages
- **Key Classes**: `GitHubScraper`
- **Methods**:
  - `parse_repo_url()`: Parse GitHub URLs
  - `get_repo_metadata()`: Extract all available metadata
  - `fetch_page()`: Fetch and parse HTML pages
  - Helper methods for specific data extraction

#### 2. **core_metadata.py** - Basic Metadata
- **Responsibility**: Handle fundamental software metadata
- **Properties**:
  - name
  - description
  - version
  - identifier
  - url
  - codeRepository
  - keywords
- **Key Classes**: `CoreMetadata`
- **Methods**:
  - `extract()`: Extract from scraper data
  - `validate()`: Validate required fields
  - `to_dict()`: Convert to dictionary format

#### 3. **dates.py** - Date Management
- **Responsibility**: Handle all date-related metadata
- **Properties**:
  - dateCreated
  - dateModified
  - datePublished
  - embargoEndDate
- **Key Classes**: `DateMetadata`
- **Methods**:
  - `extract()`: Parse dates from various formats
  - `normalize()`: Convert to ISO 8601 format
  - `to_dict()`: Convert to dictionary format

#### 4. **people.py** - People and Roles
- **Responsibility**: Extract and structure author, contributor, and maintainer information
- **Properties**:
  - author (with @list container)
  - contributor
  - maintainer
  - copyrightHolder
  - funder
  - sponsor
  - publisher
  - editor
- **Key Classes**: `Person`, `PeopleMetadata`
- **Methods**:
  - `extract_authors()`: Get authors from repository
  - `extract_contributors()`: Get contributors
  - `extract_maintainers()`: Get maintainers
  - `enrich_person()`: Add ORCID and other identifiers
  - `to_dict()`: Convert to dictionary format

#### 5. **technical.py** - Technical Requirements
- **Responsibility**: Handle technical metadata and requirements
- **Properties**:
  - programmingLanguage
  - operatingSystem
  - runtimePlatform
  - softwareRequirements
  - softwareSuggestions
  - processorRequirements
  - memoryRequirements
  - storageRequirements
- **Key Classes**: `TechnicalMetadata`
- **Methods**:
  - `extract_languages()`: Detect programming languages
  - `extract_requirements()`: Parse dependencies
  - `extract_os_requirements()`: Determine OS requirements
  - `to_dict()`: Convert to dictionary format

#### 6. **licensing.py** - License and Copyright
- **Responsibility**: Handle licensing and copyright information
- **Properties**:
  - license
  - copyrightYear
  - isAccessibleForFree
  - permissions
- **Key Classes**: `LicenseMetadata`
- **Methods**:
  - `extract_license()`: Identify license from repository
  - `map_to_spdx()`: Map to SPDX identifier
  - `to_dict()`: Convert to dictionary format

#### 7. **documentation.py** - Documentation Links
- **Responsibility**: Handle documentation-related metadata
- **Properties**:
  - softwareHelp
  - readme
  - releaseNotes
  - buildInstructions
  - issueTracker
- **Key Classes**: `DocumentationMetadata`
- **Methods**:
  - `extract_readme()`: Get README URL
  - `extract_build_instructions()`: Extract build info
  - `extract_release_notes()`: Get release notes
  - `to_dict()`: Convert to dictionary format

#### 8. **development.py** - Development Status
- **Responsibility**: Handle development-related metadata
- **Properties**:
  - developmentStatus
  - continuousIntegration
  - review
  - reviewAspect
  - reviewBody
- **Key Classes**: `DevelopmentMetadata`
- **Methods**:
  - `infer_development_status()`: Determine status from repository
  - `extract_ci_info()`: Find CI/CD configuration
  - `to_dict()`: Convert to dictionary format

#### 9. **references.py** - References and Links
- **Responsibility**: Handle citations and related resources
- **Properties**:
  - citation
  - referencePublication
  - relatedLink
  - sameAs
  - isPartOf
  - hasPart
  - supportingData
- **Key Classes**: `ReferenceMetadata`
- **Methods**:
  - `extract_citations()`: Find citations in README
  - `extract_publications()`: Find reference publications
  - `extract_related_links()`: Find related resources
  - `to_dict()`: Convert to dictionary format

#### 10. **categories.py** - Categories and Keywords
- **Responsibility**: Handle categorization metadata
- **Properties**:
  - applicationCategory
  - applicationSubCategory
  - keywords
- **Key Classes**: `CategoryMetadata`
- **Methods**:
  - `infer_categories()`: Determine categories
  - `extract_keywords()`: Get keywords from topics
  - `to_dict()`: Convert to dictionary format

#### 11. **validator.py** - Schema Validation
- **Responsibility**: Validate metadata against Codemeta 3.1 schema
- **Key Classes**: `CodeMetaValidator`
- **Methods**:
  - `validate()`: Validate complete metadata
  - `validate_required()`: Check required fields
  - `validate_types()`: Check field types
  - `validate_format()`: Check field formats
  - `get_errors()`: Return validation errors
  - `get_warnings()`: Return validation warnings

#### 12. **output.py** - Output Generation
- **Responsibility**: Generate JSON-LD output
- **Key Classes**: `CodeMetaOutput`
- **Methods**:
  - `generate_jsonld()`: Create JSON-LD structure
  - `add_context()`: Add @context
  - `save_to_file()`: Save to JSON file
  - `to_json()`: Convert to JSON string

#### 13. **generator.py** - Main Orchestrator
- **Responsibility**: Coordinate all modules and manage the generation workflow
- **Key Classes**: `CodeMetaGenerator`
- **Methods**:
  - `generate()`: Main generation method
  - `generate_from_url()`: Generate from GitHub URL
  - `validate()`: Validate output
  - `save()`: Save to file

## Data Flow

```
GitHub Repository URL
        ↓
    Scraper
        ↓
Raw Metadata Dictionary
        ↓
┌─────────────────────────────────────────┐
│  Parallel Module Processing             │
├─────────────────────────────────────────┤
│ ├─ CoreMetadata                         │
│ ├─ DateMetadata                         │
│ ├─ PeopleMetadata                       │
│ ├─ TechnicalMetadata                    │
│ ├─ LicenseMetadata                      │
│ ├─ DocumentationMetadata                │
│ ├─ DevelopmentMetadata                  │
│ ├─ ReferenceMetadata                    │
│ └─ CategoryMetadata                     │
└─────────────────────────────────────────┘
        ↓
    Aggregation
        ↓
Complete Metadata Dictionary
        ↓
    Validator
        ↓
Validated Metadata
        ↓
    Output Generator
        ↓
JSON-LD File (codemeta.json)
```

## Module Interaction Pattern

Each metadata module follows a consistent pattern:

```python
class MetadataModule:
    def __init__(self, raw_data: Dict):
        self.raw_data = raw_data
        self.metadata = {}
        self.errors = []
        self.warnings = []

    def extract(self) -> Dict:
        """Extract metadata from raw data"""
        # Implementation specific to module
        return self.metadata

    def validate(self) -> bool:
        """Validate extracted metadata"""
        # Check required fields, types, formats
        return len(self.errors) == 0

    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        return self.metadata

    def get_errors(self) -> List[str]:
        """Return validation errors"""
        return self.errors

    def get_warnings(self) -> List[str]:
        """Return validation warnings"""
        return self.warnings
```

## Codemeta 3.1 JSON-LD Context

The output includes the proper JSON-LD context:

```json
{
  "@context": {
    "schema": "http://schema.org/",
    "codemeta": "https://codemeta.github.io/terms/",
    ...
  },
  "@type": "SoftwareSourceCode",
  ...
}
```

## Error Handling Strategy

- **Scraper Errors**: Log and continue with available data
- **Extraction Errors**: Collect warnings, skip problematic fields
- **Validation Errors**: Report missing required fields
- **Output Errors**: Ensure valid JSON-LD even with incomplete data

## Testing Strategy

Each module has corresponding tests:
- Unit tests for individual methods
- Integration tests for module interactions
- Validation tests against Codemeta schema
- End-to-end tests with real repositories

## Extension Points

The modular design allows for easy extension:
- Add new metadata modules for additional properties
- Extend scraper for additional data sources
- Customize validation rules
- Add new output formats
