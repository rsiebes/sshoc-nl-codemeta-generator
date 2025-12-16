"""
Curated Software Vocabulary

This module provides a curated vocabulary of popular modern software projects,
frameworks, languages, and tools that may not be well-represented in Wikidata.

These entries are manually curated based on popularity and relevance.
Each entry includes:
- Label: Project name
- Description: Brief description
- URL: Official or Wikipedia URL
- QID: Wikidata QID if available, or custom ID (e.g., "CUSTOM:python")
"""

# Curated vocabulary of popular modern software
CURATED_VOCABULARY = {
    'programming_languages': {
        'Python': {
            'label': 'Python',
            'description': 'High-level, interpreted programming language known for simplicity and readability',
            'url': 'https://www.wikidata.org/wiki/Q28865',
            'qid': 'Q28865'
        },
        'JavaScript': {
            'label': 'JavaScript',
            'description': 'Lightweight, interpreted programming language primarily used for web development',
            'url': 'https://www.wikidata.org/wiki/Q2005',
            'qid': 'Q2005'
        },
        'TypeScript': {
            'label': 'TypeScript',
            'description': 'Typed superset of JavaScript that compiles to plain JavaScript',
            'url': 'https://www.wikidata.org/wiki/Q4782057',
            'qid': 'Q4782057'
        },
        'Go': {
            'label': 'Go',
            'description': 'Compiled programming language designed for simplicity and efficiency',
            'url': 'https://www.wikidata.org/wiki/Q11019',
            'qid': 'Q11019'
        },
        'Rust': {
            'label': 'Rust',
            'description': 'Systems programming language focusing on safety and performance',
            'url': 'https://www.wikidata.org/wiki/Q40831',
            'qid': 'Q40831'
        },
        'C++': {
            'label': 'C++',
            'description': 'General-purpose programming language with object-oriented features',
            'url': 'https://www.wikidata.org/wiki/Q2407',
            'qid': 'Q2407'
        },
        'C#': {
            'label': 'C#',
            'description': 'Modern object-oriented programming language developed by Microsoft',
            'url': 'https://www.wikidata.org/wiki/Q2344',
            'qid': 'Q2344'
        },
        'Ruby': {
            'label': 'Ruby',
            'description': 'Dynamic, open source programming language with focus on simplicity',
            'url': 'https://www.wikidata.org/wiki/Q161053',
            'qid': 'Q161053'
        },
        'PHP': {
            'label': 'PHP',
            'description': 'Server-side scripting language designed for web development',
            'url': 'https://www.wikidata.org/wiki/Q59',
            'qid': 'Q59'
        },
        'Swift': {
            'label': 'Swift',
            'description': 'Programming language for iOS, macOS, watchOS, and tvOS development',
            'url': 'https://www.wikidata.org/wiki/Q15407381',
            'qid': 'Q15407381'
        },
    },
    'frameworks': {
        'Flask': {
            'label': 'Flask',
            'description': 'Lightweight Python web application framework',
            'url': 'https://flask.palletsprojects.com/',
            'qid': 'CUSTOM:flask'
        },
        'Django': {
            'label': 'Django',
            'description': 'High-level Python web framework for rapid development',
            'url': 'https://www.djangoproject.com/',
            'qid': 'CUSTOM:django'
        },
        'React': {
            'label': 'React',
            'description': 'JavaScript library for building user interfaces with reusable components',
            'url': 'https://react.dev/',
            'qid': 'CUSTOM:react'
        },
        'Vue.js': {
            'label': 'Vue.js',
            'description': 'Progressive JavaScript framework for building user interfaces',
            'url': 'https://vuejs.org/',
            'qid': 'CUSTOM:vuejs'
        },
        'Angular': {
            'label': 'Angular',
            'description': 'TypeScript-based web application framework by Google',
            'url': 'https://angular.io/',
            'qid': 'CUSTOM:angular'
        },
        'Express.js': {
            'label': 'Express.js',
            'description': 'Fast, unopinionated web application framework for Node.js',
            'url': 'https://expressjs.com/',
            'qid': 'CUSTOM:expressjs'
        },
        'FastAPI': {
            'label': 'FastAPI',
            'description': 'Modern, fast web framework for building APIs with Python',
            'url': 'https://fastapi.tiangolo.com/',
            'qid': 'CUSTOM:fastapi'
        },
        'Spring': {
            'label': 'Spring',
            'description': 'Comprehensive framework for building Java applications',
            'url': 'https://spring.io/',
            'qid': 'CUSTOM:spring'
        },
    },
    'runtimes_and_platforms': {
        'Node.js': {
            'label': 'Node.js',
            'description': 'JavaScript runtime built on Chrome\'s V8 engine for server-side development',
            'url': 'https://nodejs.org/',
            'qid': 'CUSTOM:nodejs'
        },
        '.NET': {
            'label': '.NET',
            'description': 'Free, cross-platform framework for building applications',
            'url': 'https://dotnet.microsoft.com/',
            'qid': 'CUSTOM:dotnet'
        },
        'Java Virtual Machine': {
            'label': 'Java Virtual Machine',
            'description': 'Abstract computing machine that enables a computer to run programs',
            'url': 'https://www.wikidata.org/wiki/Q494183',
            'qid': 'Q494183'
        },
    },
    'tools_and_platforms': {
        'Docker': {
            'label': 'Docker',
            'description': 'Containerization platform for packaging and deploying applications',
            'url': 'https://www.docker.com/',
            'qid': 'CUSTOM:docker'
        },
        'Kubernetes': {
            'label': 'Kubernetes',
            'description': 'Open-source container orchestration platform',
            'url': 'https://kubernetes.io/',
            'qid': 'CUSTOM:kubernetes'
        },
        'Git': {
            'label': 'Git',
            'description': 'Distributed version control system',
            'url': 'https://www.wikidata.org/wiki/Q186055',
            'qid': 'Q186055'
        },
        'GitHub': {
            'label': 'GitHub',
            'description': 'Web-based hosting service for version control using Git',
            'url': 'https://www.wikidata.org/wiki/Q364622',
            'qid': 'Q364622'
        },
        'Jenkins': {
            'label': 'Jenkins',
            'description': 'Open-source automation server for continuous integration',
            'url': 'https://www.jenkins.io/',
            'qid': 'CUSTOM:jenkins'
        },
        'GitLab': {
            'label': 'GitLab',
            'description': 'Web-based DevOps platform with Git repository management',
            'url': 'https://about.gitlab.com/',
            'qid': 'CUSTOM:gitlab'
        },
    },
    'databases': {
        'PostgreSQL': {
            'label': 'PostgreSQL',
            'description': 'Powerful, open-source relational database system',
            'url': 'https://www.wikidata.org/wiki/Q936',
            'qid': 'Q936'
        },
        'MySQL': {
            'label': 'MySQL',
            'description': 'Popular open-source relational database management system',
            'url': 'https://www.wikidata.org/wiki/Q7300',
            'qid': 'Q7300'
        },
        'MongoDB': {
            'label': 'MongoDB',
            'description': 'NoSQL document-oriented database',
            'url': 'https://www.mongodb.com/',
            'qid': 'CUSTOM:mongodb'
        },
        'Redis': {
            'label': 'Redis',
            'description': 'In-memory data structure store used for caching and sessions',
            'url': 'https://redis.io/',
            'qid': 'CUSTOM:redis'
        },
        'Elasticsearch': {
            'label': 'Elasticsearch',
            'description': 'Search and analytics engine built on top of Lucene',
            'url': 'https://www.elastic.co/elasticsearch/',
            'qid': 'CUSTOM:elasticsearch'
        },
    },
    'machine_learning': {
        'TensorFlow': {
            'label': 'TensorFlow',
            'description': 'Open-source machine learning framework by Google',
            'url': 'https://www.tensorflow.org/',
            'qid': 'CUSTOM:tensorflow'
        },
        'PyTorch': {
            'label': 'PyTorch',
            'description': 'Open-source machine learning framework with dynamic computation graphs',
            'url': 'https://pytorch.org/',
            'qid': 'CUSTOM:pytorch'
        },
        'Scikit-learn': {
            'label': 'Scikit-learn',
            'description': 'Python machine learning library for data analysis and modeling',
            'url': 'https://scikit-learn.org/',
            'qid': 'CUSTOM:scikitlearn'
        },
        'Keras': {
            'label': 'Keras',
            'description': 'High-level neural networks API for deep learning',
            'url': 'https://keras.io/',
            'qid': 'CUSTOM:keras'
        },
    },
    'operating_systems': {
        'Linux': {
            'label': 'Linux',
            'description': 'Free and open-source Unix-like operating system kernel',
            'url': 'https://www.wikidata.org/wiki/Q388',
            'qid': 'Q388'
        },
        'Windows': {
            'label': 'Windows',
            'description': 'Operating system developed by Microsoft',
            'url': 'https://www.wikidata.org/wiki/Q1406',
            'qid': 'Q1406'
        },
        'macOS': {
            'label': 'macOS',
            'description': 'Operating system for Apple Macintosh computers',
            'url': 'https://www.wikidata.org/wiki/Q14116',
            'qid': 'Q14116'
        },
        'iOS': {
            'label': 'iOS',
            'description': 'Mobile operating system for Apple devices',
            'url': 'https://www.wikidata.org/wiki/Q16769',
            'qid': 'Q16769'
        },
        'Android': {
            'label': 'Android',
            'description': 'Mobile operating system based on Linux kernel',
            'url': 'https://www.wikidata.org/wiki/Q94',
            'qid': 'Q94'
        },
    },
}


def get_curated_vocabulary():
    """
    Get the complete curated vocabulary.
    
    Returns:
        Dictionary with all curated software entries
    """
    return CURATED_VOCABULARY


def find_in_curated_vocabulary(search_term: str):
    """
    Find a software entry in the curated vocabulary.
    
    Args:
        search_term: Term to search for
        
    Returns:
        Matching entry metadata, or None if not found
    """
    search_term_lower = search_term.lower()
    best_match = None
    best_match_score = 0
    
    for category, items in CURATED_VOCABULARY.items():
        for name, metadata in items.items():
            name_lower = name.lower()
            
            # Exact match (highest priority)
            if search_term_lower == name_lower:
                return metadata
            
            # Partial match scoring
            if search_term_lower in name_lower:
                score = len(search_term) / len(name)
                if score > best_match_score:
                    best_match_score = score
                    best_match = metadata
    
    return best_match


def get_curated_vocabulary_stats():
    """
    Get statistics about the curated vocabulary.
    
    Returns:
        Dictionary with vocabulary statistics
    """
    stats = {
        'categories': {},
        'total_items': 0,
    }
    
    for category, items in CURATED_VOCABULARY.items():
        count = len(items)
        stats['categories'][category] = count
        stats['total_items'] += count
    
    return stats
