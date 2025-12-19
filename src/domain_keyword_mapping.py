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
