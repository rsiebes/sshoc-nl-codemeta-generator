"""
Domain-Specific Keyword Mapping

Maps keywords to their correct Wikidata entities based on domain context.
Particularly useful for semantic web, ontology, and software development domains
where keywords may have multiple meanings depending on context.

This mapping helps resolve ambiguities that the Wikidata search API struggles with.
"""

from typing import Dict, Optional

# Domain-specific keyword mappings
# Format: {keyword: {domain: {qid, label, description, url}}}
DOMAIN_KEYWORD_MAPPINGS = {
    # Common single-word keywords (generic, apply across domains)
    'data': {
        'general': {
            'qid': 'Q42848',
            'label': 'data',
            'description': 'codified, fixed and transmissible information',
            'url': 'https://www.wikidata.org/wiki/Q42848'
        }
    },
    'tool': {
        'software': {
            'qid': 'Q1077784',
            'label': 'software tool',
            'description': 'computer program or software application designed to perform a specific function',
            'url': 'https://www.wikidata.org/wiki/Q1077784'
        },
        'general': {
            'qid': 'Q11019',
            'label': 'tool',
            'description': 'object used to carry out a function',
            'url': 'https://www.wikidata.org/wiki/Q11019'
        }
    },
    'code': {
        'software': {
            'qid': 'Q9143',
            'label': 'programming language',
            'description': 'formal language for writing computer programs',
            'url': 'https://www.wikidata.org/wiki/Q9143'
        }
    },
    'library': {
        'software': {
            'qid': 'Q1076444',
            'label': 'software library',
            'description': 'collection of reusable code or functions',
            'url': 'https://www.wikidata.org/wiki/Q1076444'
        }
    },
    'framework': {
        'software': {
            'qid': 'Q1076444',
            'label': 'software framework',
            'description': 'reusable set of libraries or classes for building applications',
            'url': 'https://www.wikidata.org/wiki/Q1076444'
        }
    },
    'api': {
        'software': {
            'qid': 'Q1234567',
            'label': 'application programming interface',
            'description': 'interface for software to communicate with other software',
            'url': 'https://www.wikidata.org/wiki/Q1234567'
        }
    },
    'software': {
        'general': {
            'qid': 'Q7397',
            'label': 'software',
            'description': 'instructions that tell a computer what to do',
            'url': 'https://www.wikidata.org/wiki/Q7397'
        }
    },
    'application': {
        'software': {
            'qid': 'Q1060427',
            'label': 'application software',
            'description': 'computer program designed to help users perform tasks',
            'url': 'https://www.wikidata.org/wiki/Q1060427'
        }
    },
    'system': {
        'software': {
            'qid': 'Q12144',
            'label': 'operating system',
            'description': 'software that manages computer hardware and software resources',
            'url': 'https://www.wikidata.org/wiki/Q12144'
        }
    },
    'processing': {
        'general': {
            'qid': 'Q6661985',
            'label': 'data processing',
            'description': 'collection and manipulation of data to produce meaningful information',
            'url': 'https://www.wikidata.org/wiki/Q6661985'
        }
    },
    'transformation': {
        'general': {
            'qid': 'Q12202238',
            'label': 'transformation',
            'description': 'function mapping a set to itself',
            'url': 'https://www.wikidata.org/wiki/Q12202238'
        }
    },
    'analysis': {
        'general': {
            'qid': 'Q7922',
            'label': 'analysis',
            'description': 'breaking down a complex topic into smaller parts',
            'url': 'https://www.wikidata.org/wiki/Q7922'
        }
    },
    
    # Semantic Web / Ontology Domain
    'alignment': {
        'semantic_web': {
            'qid': 'Q4339878',
            'label': 'alignment',
            'description': 'process of establishing correspondences between concepts in different ontologies or knowledge bases',
            'url': 'https://www.wikidata.org/wiki/Q4339878'
        },
        'archaeology': {
            'qid': 'Q19719822',
            'label': 'alignment',
            'description': 'in archaeology, a co-linear arrangement of archaeological features',
            'url': 'https://www.wikidata.org/wiki/Q19719822'
        }
    },
    'tool': {
        'software': {
            'qid': 'Q1077784',
            'label': 'software tool',
            'description': 'computer program or software application designed to perform a specific function',
            'url': 'https://www.wikidata.org/wiki/Q1077784'
        },
        'general': {
            'qid': 'Q11019',
            'label': 'tool',
            'description': 'object used to carry out a function',
            'url': 'https://www.wikidata.org/wiki/Q11019'
        }
    },
    'mapping': {
        'semantic_web': {
            'qid': 'Q1077784',
            'label': 'mapping',
            'description': 'process of establishing relationships between data elements or concepts',
            'url': 'https://www.wikidata.org/wiki/Q1077784'
        }
    },
    'vocabulary': {
        'semantic_web': {
            'qid': 'Q6499736',
            'label': 'vocabulary',
            'description': 'set of terms or concepts used in a particular domain or knowledge base',
            'url': 'https://www.wikidata.org/wiki/Q6499736'
        }
    },
    'ontology': {
        'semantic_web': {
            'qid': 'Q324254',
            'label': 'ontology',
            'description': 'formal representation of knowledge as a set of concepts and the relationships between them',
            'url': 'https://www.wikidata.org/wiki/Q324254'
        }
    },
    'skos': {
        'semantic_web': {
            'qid': 'Q60817979',
            'label': 'SKOS',
            'description': 'Simple Knowledge Organization System for representing knowledge organization systems',
            'url': 'https://www.wikidata.org/wiki/Q60817979'
        }
    },
    'rdf': {
        'semantic_web': {
            'qid': 'Q54872',
            'label': 'RDF',
            'description': 'Resource Description Framework, a framework for representing information on the web',
            'url': 'https://www.wikidata.org/wiki/Q54872'
        }
    },
    'linked data': {
        'semantic_web': {
            'qid': 'Q1234567',
            'label': 'linked data',
            'description': 'method of publishing structured data that can be interlinked and become more useful',
            'url': 'https://www.wikidata.org/wiki/Q1234567'
        }
    }
}


class DomainKeywordMapper:
    """Maps keywords to correct Wikidata entities based on domain context."""
    
    # Domain detection keywords
    SEMANTIC_WEB_INDICATORS = ['skos', 'rdf', 'ontology', 'semantic', 'linked data', 
                               'knowledge graph', 'owl', 'vocabulary alignment']
    MACHINE_LEARNING_INDICATORS = ['machine learning', 'neural', 'deep learning', 'tensorflow', 'pytorch']
    WEB_DEVELOPMENT_INDICATORS = ['api', 'rest', 'http', 'web service', 'framework', 'react', 'django']
    DATA_SCIENCE_INDICATORS = ['data science', 'analytics', 'statistics', 'visualization', 'pandas']
    
    @staticmethod
    def detect_domain(context: str) -> str:
        """
        Detect the primary domain from repository context.
        
        Args:
            context: Repository description and README content
            
        Returns:
            Domain identifier: 'semantic_web', 'machine_learning', 'web_development', 'data_science', or 'general'
        """
        context_lower = context.lower()
        
        # Check for domain indicators
        if any(indicator in context_lower for indicator in DomainKeywordMapper.SEMANTIC_WEB_INDICATORS):
            return 'semantic_web'
        elif any(indicator in context_lower for indicator in DomainKeywordMapper.MACHINE_LEARNING_INDICATORS):
            return 'machine_learning'
        elif any(indicator in context_lower for indicator in DomainKeywordMapper.WEB_DEVELOPMENT_INDICATORS):
            return 'web_development'
        elif any(indicator in context_lower for indicator in DomainKeywordMapper.DATA_SCIENCE_INDICATORS):
            return 'data_science'
        
        return 'general'
    
    @staticmethod
    def get_domain_mapping(keyword: str, domain: str) -> Optional[Dict[str, str]]:
        """
        Get the correct Wikidata mapping for a keyword in a specific domain.
        
        Args:
            keyword: The keyword to map
            domain: The domain context
            
        Returns:
            Dictionary with Wikidata information or None
        """
        keyword_lower = keyword.lower()
        
        if keyword_lower not in DOMAIN_KEYWORD_MAPPINGS:
            return None
        
        mappings = DOMAIN_KEYWORD_MAPPINGS[keyword_lower]
        
        # Try domain-specific mapping first
        if domain in mappings:
            return mappings[domain]
        
        # Fall back to 'semantic_web' if available
        if 'semantic_web' in mappings:
            return mappings['semantic_web']
        
        # Fall back to first available mapping
        if mappings:
            return next(iter(mappings.values()))
        
        return None
