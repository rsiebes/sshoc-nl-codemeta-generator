#!/usr/bin/env python3
"""
Show the exact prompt being sent to Gemini for keyword extraction.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Test repositories
test_repos = [
    "https://github.com/jrvosse/amalgame",
    "https://github.com/sodascience/osmenrich",
]

print("=" * 80)
print("Exact Prompts Sent to Gemini")
print("=" * 80)

for repo_url in test_repos:
    print(f"\n{'=' * 80}")
    print(f"Repository: {repo_url}")
    print(f"{'=' * 80}\n")
    
    # This is the exact prompt from gemini_extractor.py
    prompt = f"""Analyze the GitHub repository at {repo_url} and extract exactly 10 meaningful keywords that describe the project.

For each keyword, provide:
1. The keyword itself (e.g., 'OpenStreetMap', 'Python', 'Data Analysis')
2. Context clues explaining why it's relevant to this repository

Return the results as a JSON object with the structure:
{{
    "keywords": [
        {{"name": "keyword1", "context_clues": "explanation"}},
        {{"name": "keyword2", "context_clues": "explanation"}},
        ...
    ]
}}

Focus on:
- Programming languages used
- Main libraries and frameworks
- Problem domains and use cases
- Technologies and tools
- Key concepts and methodologies

Ensure all 10 keywords are relevant and non-redundant."""

    print(prompt)
    print()

print("=" * 80)
