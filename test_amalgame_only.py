#!/usr/bin/env python3
"""
Test ONLY amalgame repository and show exact prompt and Gemini response.
"""

import os
import sys
import json
from dotenv import load_dotenv
from google import genai

sys.path.insert(0, '/home/ubuntu/sshoc-nl-codemeta-generator')

from src.helpers.gemini_schemas import KeywordList

load_dotenv()

repo_url = "https://github.com/jrvosse/amalgame"

print("=" * 80)
print("Testing ONLY amalgame Repository")
print("=" * 80)
print(f"\nRepository: {repo_url}\n")

# Get API key
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_GEMINI_API_KEY not found")
    sys.exit(1)

# Create the exact prompt
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

print("=" * 80)
print("EXACT PROMPT SENT TO GEMINI:")
print("=" * 80)
print(prompt)
print("\n" + "=" * 80)
print("GEMINI RESPONSE:")
print("=" * 80 + "\n")

# Call Gemini
client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config=genai.types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=KeywordList,
    ),
)

if response and response.parsed:
    keywords = response.parsed.keywords
    print(f"✓ Extracted {len(keywords)} keywords:\n")
    for i, keyword in enumerate(keywords, 1):
        print(f"{i:2d}. {keyword.name:30s} | {keyword.context_clues}")
else:
    print("✗ Failed to extract keywords")

print("\n" + "=" * 80)
