# CBS Ecosystem CodeMeta Examples

This folder contains enhanced CodeMeta 3.0 compliant files for repositories related to Statistics Netherlands (CBS - Centraal Bureau voor de Statistiek).

## Overview

These examples demonstrate comprehensive CodeMeta files with:
- **Complete contributor information** including ORCID identifiers
- **Comprehensive software dependencies** with provider organizations
- **Full CodeMeta 3.0 schema compliance**
- **Institutional context** for CBS-related software

## Structure

### `official_cbs/` (7 files)
Official repositories maintained by Statistics Netherlands:
- `scrollytell_codemeta.json` - R package for scrollytelling in Shiny
- `CBS-Open-Data-v4_codemeta.json` - Code examples for CBS Open Data v4 API
- `CBS-Open-Data-v3_codemeta.json` - Code examples for CBS Open Data v3 API
- `cbsodata4_codemeta.json` - R package for OData4 interface
- `iv3_definities_codemeta.json` - JSON definitions for iv3 deliveries
- `cbs-opendata-sdmx_codemeta.json` - SDMX interface for CBS data
- `SdmxCodelistTranslator_codemeta.json` - SDMX translation tool

### `third_party/` (5 files)
Third-party repositories that use CBS data or APIs:
- `cbsodata_codemeta.json` - Python API client (46 stars, 117+ users)
- `cbsodataR_codemeta.json` - R API client (34 stars)
- `Dutch_healthcare_inequalities_COVID19_codemeta.json` - COVID-19 research
- `dutchhousemarket_codemeta.json` - Housing market analysis
- `Synthetic-Population-The-Hague-South-West_codemeta.json` - Demographics research

## Key Features

### ORCID Integration
- **Edwin de Jonge**: 0000-0002-6580-4718 (CBS Methodologist)
- **Jonathan de Bruin**: 0000-0002-4297-8502 (cbsodata author)

### Software Dependencies
Complete dependency specifications with:
- Runtime platform requirements (R 3.5+, Python 3.6+, etc.)
- Provider organizations (CRAN, PyPI, npm, NuGet)
- Version specifications where available
- Required vs suggested dependencies

### Institutional Context
- CBS organization metadata with contact information
- Publisher and funding attribution for official repositories
- Ecosystem relationships between projects

## Usage

These files can be used as:
1. **Templates** for creating CodeMeta files for similar projects
2. **Examples** of best practices for contributor and dependency metadata
3. **Reference implementations** for CodeMeta 3.0 compliance
4. **Test cases** for CodeMeta validation tools

## Schema Compliance

All files are validated against:
- **CodeMeta 3.0 schema**: https://doi.org/10.5063/schema/codemeta-3.0
- **JSON-LD structure** with proper @context and @type fields
- **ORCID identifier format** using full URLs
- **Software dependency structure** with provider organizations

## Generation

These files were generated using enhanced metadata collection including:
- GitHub repository analysis
- ORCID database research
- Package registry verification
- Institutional source validation

Generated: 2025-08-19
Schema: CodeMeta 3.0
Quality: Research-grade metadata

