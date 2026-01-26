"""Enrich author information using GitHub profiles and DBpedia mappings."""

import json
from typing import Optional

from src.core import get_logger
from src.helpers.github_affiliation_extractor import extract_affiliation_from_github
from src.helpers.dbpedia_mapper import map_organization_to_dbpedia

logger = get_logger(__name__)


def enrich_authors_with_github(authors_json: str) -> Optional[str]:
    """
    Enrich author information using GitHub profiles.

    Extracts affiliation information from GitHub user profiles and maps to DBpedia URIs.

    Args:
        authors_json: JSON string with authors data from extract_unique_authors()

    Returns:
        JSON string with enriched author data in CodeMeta format, or None if enrichment fails
    """
    try:
        authors_data = json.loads(authors_json)
        authors = authors_data.get('authors', [])

        enriched_authors = []

        for author in authors:
            name = author.get('name')
            email = author.get('email')
            login = author.get('login')

            if not name or not login:
                logger.warning(f"Skipping author with missing name or login: {author}")
                continue

            # Extract affiliation from GitHub profile
            affiliation_data = extract_affiliation_from_github(login)

            # Build Person object
            person = {
                "@type": "Person",
                "name": name,
            }

            # Add email if available
            if email:
                person["email"] = email

            # Add affiliation if found
            if affiliation_data and affiliation_data.get('name'):
                org_name = affiliation_data['name']
                dbpedia_uri = map_organization_to_dbpedia(org_name)

                if dbpedia_uri:
                    person["affiliation"] = {
                        "@type": "Organization",
                        "name": org_name,
                        "@id": dbpedia_uri,
                    }
                    logger.debug(f"Added affiliation for {name}: {org_name} ({dbpedia_uri})")
                else:
                    # Still add affiliation even if DBpedia URI not found
                    person["affiliation"] = {
                        "@type": "Organization",
                        "name": org_name,
                    }
                    logger.debug(f"Added affiliation for {name}: {org_name} (no DBpedia URI)")
            else:
                logger.debug(f"No affiliation found for {name} (GitHub: {login})")

            enriched_authors.append(person)

        # Build response in CodeMeta format
        response = {
            "author": enriched_authors
        }

        logger.info(f"Enriched {len(enriched_authors)} authors with GitHub affiliations")

        return json.dumps(response)

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing authors JSON: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error enriching authors with GitHub: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return None


if __name__ == '__main__':
    # Test the function
    import sys
    sys.path.insert(0, '.')

    print("Testing GitHub-based author enrichment...\n")

    # Test with amalgame authors
    from src.helpers import extract_unique_authors

    repo_url = "https://github.com/jrvosse/amalgame"
    print(f"Repository: {repo_url}\n")

    authors_json = extract_unique_authors(repo_url)
    if authors_json:
        print("Original authors:")
        print(json.dumps(json.loads(authors_json), indent=2))

        print("\n" + "=" * 80)
        print("Enriched authors:")
        enriched_json = enrich_authors_with_github(authors_json)
        if enriched_json:
            print(json.dumps(json.loads(enriched_json), indent=2))
        else:
            print("Failed to enrich authors")
