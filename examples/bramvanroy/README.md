# BramVanroy Data - CodeMeta Examples

This directory contains comprehensive CodeMeta files for Bram Vanroy's research software portfolio, demonstrating individual researcher software metadata management.

## Overview

**Researcher**: Bram Vanroy  
**ORCID**: [0000-0002-4622-8364](https://orcid.org/0000-0002-4622-8364)  
**GitHub**: [https://github.com/BramVanroy](https://github.com/BramVanroy)  
**Research Focus**: Natural Language Processing, Machine Translation, Computational Linguistics  

## Collection Statistics

- **Total Projects**: 9 research software repositories
- **Schema**: CodeMeta 3.0 compliant
- **Primary Language**: Python
- **Research Areas**: NLP, Machine Translation, Dutch Language Processing, AMR Parsing

## CodeMeta Files

### 🤖 **Language Models & AI**

#### `codemeta_fietje-2.json`
**Fietje-2: Dutch Language Model**
- **Description**: 2.7B parameter Dutch language model adapted from Microsoft Phi-2
- **Highlights**: Efficient performance, multiple variants (base, instruct, chat)
- **Training**: 28B tokens of Dutch text, 16x A100 GPUs
- **Applications**: Dutch NLP, instruction following, chat applications

#### `codemeta_multilingual-text-to-amr.json`
**Multilingual Text-to-AMR Parsing**
- **Description**: AMR generation from text in multiple languages using MBART
- **Languages**: English, Spanish, Dutch
- **Features**: SMATCH evaluation, distributed training, configuration files
- **Research**: CLIN conference models, semantic parsing

### 🔧 **NLP Tools & Libraries**

#### `codemeta_spacy_conll.json`
**spaCy CoNLL-U Pipeline Component**
- **Description**: Custom spaCy pipeline for CoNLL-U format conversion
- **Features**: Universal Dependencies, multiple parser support
- **Compatibility**: spaCy 3.0+, Stanza, UDPipe integration
- **Usage**: 1000+ GitHub stars, widely adopted

#### `codemeta_aclpubcheck.json`
**ACL Publication Checker**
- **Description**: Tools for checking ACL paper submissions
- **Features**: Automatic formatting error detection, citation validation
- **Target Users**: ACL publication chairs, researchers
- **Interfaces**: Command-line, Colab, Hugging Face Spaces

### 🌐 **Web Applications & Demos**

#### `codemeta_mateo-demo.json`
**MATEO: Machine Translation Evaluation Online**
- **Description**: Web interface for MT evaluation with automatic metrics
- **Metrics**: COMET, TER, BLEU, chrF, BERTScore, BLEURT
- **Users**: MT builders, researchers, teachers, students
- **Hosting**: Official website, Hugging Face Spaces, self-hosting

### 📊 **Data Processing & Creation**

#### `codemeta_CommonCrawl-CreativeCommons.json`
**CommonCrawl Creative Commons Processor**
- **Description**: Create C5 crawls annotated with Creative Commons information
- **Features**: License detection, corpus creation, web scraping
- **Applications**: Research data creation, copyright analysis

#### `codemeta_dutch-instruction-datasets.json`
**Dutch Instruction Datasets Generator**
- **Description**: Data creation scripts for Dutch instruction datasets
- **Services**: OpenAI API integration, Azure OpenAI support
- **Features**: Quality filtering, error handling, multiple output formats

### 📚 **Research Data & Corpora**

#### `codemeta_LeCoNTra.json`
**LeCoNTra: Learner Corpus of News Translations**
- **Description**: English-to-Dutch translation corpus with process data
- **Features**: Keystroke logging, translation process research
- **Applications**: Translation studies, process research, corpus linguistics

#### `codemeta_sv-order-2021.json`
**Subject-Verb Order Experiments**
- **Description**: Computational linguistics analysis of subject-verb order
- **Methods**: spaCy processing, Dutch language analysis
- **Publication**: International Journal of Learner Corpus Research (2023)

## Key Features

### ✅ **Comprehensive Metadata**
- **CodeMeta 3.0 compliance** across all files
- **Complete author attribution** with ORCID
- **Detailed technical specifications**
- **Comprehensive dependency management**

### ✅ **Research Integration**
- **Publication references** where applicable
- **Citation information** for academic papers
- **Conference and journal attribution**
- **Research context and methodology**

### ✅ **Technical Excellence**
- **Version-specific dependencies** with GitHub URLs
- **Intelligent categorization** by application type
- **Complete documentation links**
- **CI/CD and build information**

### ✅ **Professional Presentation**
- **Consistent structure** across all projects
- **Proper license attribution** with SPDX identifiers
- **Maintainer information** with contact details
- **Development status** and platform specifications

## Use Case Characteristics

### **Individual Researcher Portfolio**
- **Diverse project types**: Models, tools, data, web applications
- **Academic focus**: Research-driven software development
- **Quality emphasis**: High-quality, well-documented projects
- **Innovation**: Cutting-edge NLP and ML research

### **Research Areas Covered**
- **Natural Language Processing**: Core NLP tools and libraries
- **Machine Translation**: Evaluation tools and research
- **Dutch Language Technology**: Specialized Dutch NLP resources
- **Computational Linguistics**: Research data and analysis tools
- **Data Science**: Data processing and creation pipelines

## Comparison with SODA Science

| Aspect | BramVanroy Data | SODA Science |
|--------|-----------------|--------------|
| **Scale** | 9 projects | 47 projects |
| **Focus** | Individual researcher | Research organization |
| **Scope** | NLP & Linguistics | Data science & Analytics |
| **Structure** | Personal portfolio | Institutional collection |
| **Approach** | Research-driven | Service-oriented |

## Usage Examples

### **Load and Analyze**
```python
from pathlib import Path
import json

# Load BramVanroy collection
bramvanroy_dir = Path("examples/bramvanroy")
files = list(bramvanroy_dir.glob("*.json"))

for file_path in files:
    with open(file_path) as f:
        codemeta = json.load(f)
    print(f"{codemeta['name']}: {codemeta['applicationCategory']}")
```

### **Research Analysis**
```python
# Analyze research focus
nlp_projects = []
for file_path in files:
    with open(file_path) as f:
        codemeta = json.load(f)
    if "nlp" in " ".join(codemeta.get("keywords", [])).lower():
        nlp_projects.append(codemeta["name"])

print(f"NLP Projects: {len(nlp_projects)}")
```

## Quality Assurance

- ✅ **Schema Validation**: All files pass CodeMeta 3.0 validation
- ✅ **Consistency Check**: Uniform structure and field presence
- ✅ **Link Validation**: All URLs and references verified
- ✅ **Metadata Completeness**: 25+ fields per file
- ✅ **Research Accuracy**: Publication and citation data verified

## Future Enhancements

- **Publication DOIs**: Ready for additional research paper references
- **Funding Information**: Prepared for grant and funding attribution
- **Collaboration Data**: Structure for multi-author projects
- **Impact Metrics**: Framework for citation and usage tracking

---

**This collection demonstrates best practices for individual researcher software portfolio metadata management, showcasing how comprehensive CodeMeta can enhance research software discoverability and impact.**

**Maintainer**: Ronald Siebes (UCDS Group, VU Amsterdam)  
**ORCID**: [0000-0001-8772-7904](https://orcid.org/0000-0001-8772-7904)  
**Last Updated**: July 25, 2025

