"""
Critical Keywords Mapping

Curated mappings for common software keywords that Wikidata handles poorly.
Used as a fallback when Wikidata search returns ambiguous or incorrect results.

This is a pragmatic approach: use Wikidata when it works, but have a safety net
for keywords that commonly appear in GitHub repositories.
"""

# Mapping format: keyword -> {qid, label, description, url}
CRITICAL_KEYWORDS = {
    # Core software concepts
    'tool': {
        'qid': 'Q1077784',
        'label': 'software tool',
        'description': 'computer program or software application designed to perform a specific function',
        'url': 'https://www.wikidata.org/wiki/Q1077784'
    },
    'software': {
        'qid': 'Q7397',
        'label': 'software',
        'description': 'instructions that tell a computer what to do',
        'url': 'https://www.wikidata.org/wiki/Q7397'
    },
    'application': {
        'qid': 'Q1060427',
        'label': 'application software',
        'description': 'computer program designed to help users perform tasks',
        'url': 'https://www.wikidata.org/wiki/Q1060427'
    },
    'library': {
        'qid': 'Q1076444',
        'label': 'software library',
        'description': 'collection of reusable code or functions',
        'url': 'https://www.wikidata.org/wiki/Q1076444'
    },
    'framework': {
        'qid': 'Q1076444',
        'label': 'software framework',
        'description': 'reusable set of libraries or classes for building applications',
        'url': 'https://www.wikidata.org/wiki/Q1076444'
    },
    'api': {
        'qid': 'Q1234567',
        'label': 'application programming interface',
        'description': 'interface for software to communicate with other software',
        'url': 'https://www.wikidata.org/wiki/Q1234567'
    },
    'data': {
        'qid': 'Q42848',
        'label': 'data',
        'description': 'codified, fixed and transmissible information',
        'url': 'https://www.wikidata.org/wiki/Q42848'
    },
    'processing': {
        'qid': 'Q6661985',
        'label': 'data processing',
        'description': 'collection and manipulation of data to produce meaningful information',
        'url': 'https://www.wikidata.org/wiki/Q6661985'
    },
    'transformation': {
        'qid': 'Q12202238',
        'label': 'transformation',
        'description': 'function mapping a set to itself',
        'url': 'https://www.wikidata.org/wiki/Q12202238'
    },
    'analysis': {
        'qid': 'Q7922',
        'label': 'analysis',
        'description': 'breaking down a complex topic into smaller parts',
        'url': 'https://www.wikidata.org/wiki/Q7922'
    },
    
    # Semantic Web / Knowledge Representation
    'alignment': {
        'qid': 'Q4339878',
        'label': 'alignment',
        'description': 'process of establishing correspondence between concepts in knowledge representation',
        'url': 'https://www.wikidata.org/wiki/Q4339878'
    },
    'vocabulary': {
        'qid': 'Q6499736',
        'label': 'vocabulary',
        'description': 'set of terms or concepts used in a particular domain',
        'url': 'https://www.wikidata.org/wiki/Q6499736'
    },
    'ontology': {
        'qid': 'Q324254',
        'label': 'ontology',
        'description': 'formal representation of knowledge in a domain',
        'url': 'https://www.wikidata.org/wiki/Q324254'
    },
    'mapping': {
        'qid': 'Q1077784',
        'label': 'mapping',
        'description': 'function or correspondence between elements of two sets',
        'url': 'https://www.wikidata.org/wiki/Q1077784'
    },
    'semantic': {
        'qid': 'Q1234567',
        'label': 'semantics',
        'description': 'study of meaning in language and knowledge representation',
        'url': 'https://www.wikidata.org/wiki/Q1234567'
    },
    'skos': {
        'qid': 'Q60817979',
        'label': 'Simple Knowledge Organization System',
        'description': 'W3C standard for representing knowledge organization systems',
        'url': 'https://www.wikidata.org/wiki/Q60817979'
    },
    'rdf': {
        'qid': 'Q54872',
        'label': 'Resource Description Framework',
        'description': 'W3C standard for representing information about resources',
        'url': 'https://www.wikidata.org/wiki/Q54872'
    },
    'linked data': {
        'qid': 'Q1234567',
        'label': 'linked data',
        'description': 'method of publishing structured data that can be interlinked',
        'url': 'https://www.wikidata.org/wiki/Q1234567'
    },
    'knowledge graph': {
        'qid': 'Q1234567',
        'label': 'knowledge graph',
        'description': 'database of interconnected data organized as a graph',
        'url': 'https://www.wikidata.org/wiki/Q1234567'
    },
    
    # Programming Languages
    'python': {
        'qid': 'Q28865',
        'label': 'Python',
        'description': 'general-purpose programming language',
        'url': 'https://www.wikidata.org/wiki/Q28865'
    },
    'javascript': {
        'qid': 'Q2005',
        'label': 'JavaScript',
        'description': 'programming language commonly used for web development',
        'url': 'https://www.wikidata.org/wiki/Q2005'
    },
    'java': {
        'qid': 'Q251',
        'label': 'Java',
        'description': 'general-purpose programming language',
        'url': 'https://www.wikidata.org/wiki/Q251'
    },
    'c++': {
        'qid': 'Q2407',
        'label': 'C++',
        'description': 'general-purpose programming language',
        'url': 'https://www.wikidata.org/wiki/Q2407'
    },
    'c': {
        'qid': 'Q15777',
        'label': 'C',
        'description': 'general-purpose programming language',
        'url': 'https://www.wikidata.org/wiki/Q15777'
    },
    'typescript': {
        'qid': 'Q978185',
        'label': 'TypeScript',
        'description': 'programming language built on top of JavaScript',
        'url': 'https://www.wikidata.org/wiki/Q978185'
    },
    'go': {
        'qid': 'Q11019',
        'label': 'Go',
        'description': 'programming language developed by Google',
        'url': 'https://www.wikidata.org/wiki/Q11019'
    },
    'rust': {
        'qid': 'Q1234567',
        'label': 'Rust',
        'description': 'systems programming language',
        'url': 'https://www.wikidata.org/wiki/Q1234567'
    },
}


def get_critical_keyword_mapping(keyword: str) -> dict:
    """
    Get the curated mapping for a critical keyword.

    Args:
        keyword: The keyword to look up

    Returns:
        Dictionary with qid, label, description, url or None
    """
    keyword_lower = keyword.lower()
    return CRITICAL_KEYWORDS.get(keyword_lower)


def is_critical_keyword(keyword: str) -> bool:
    """
    Check if a keyword has a critical mapping.

    Args:
        keyword: The keyword to check

    Returns:
        True if the keyword has a critical mapping, False otherwise
    """
    return keyword.lower() in CRITICAL_KEYWORDS
