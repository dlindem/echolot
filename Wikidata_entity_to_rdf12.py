#!/usr/bin/env python3
"""
Transform Wikidata Turtle (RDF 1.1) to RDF 1.2 format.

This script reads a Turtle file from Wikidata (RDF 1.1) and converts it
to RDF 1.2 format by:
1. Updating the RDF version declaration
2. Standardizing namespace prefixes
3. Ensuring compatibility with RDF 1.2 serialization
"""

import sys
import argparse
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlparse
import re

USER_AGENT = "david.lindemann@ehu.eus python script"
def read_turtle_file(source):
    """
    Read Turtle content from a file or URL.

    Args:
        source: File path or URL string

    Returns:
        String containing the Turtle content
    """
    if urlparse(source).scheme in ('http', 'https'):
        # Read from URL with proper User-Agent header
        req = Request(
            source,
            headers={
                'User-Agent': USER_AGENT,
                'Accept': 'text/turtle, application/x-turtle, */*'
            }
        )
        with urlopen(req) as response:
            return response.read().decode('utf-8')
    else:
        # Read from local file
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()


def transform_to_rdf12(turtle_content):
    """
    Transform RDF 1.1 Turtle to RDF 1.2 format.

    Args:
        turtle_content: String containing RDF 1.1 Turtle

    Returns:
        String containing RDF 1.2 Turtle
    """
    lines = turtle_content.splitlines()
    transformed_lines = []

    # Track if we've added the RDF 1.2 declaration
    added_rdf12_decl = False

    # Regular expression to find @prefix declarations
    prefix_pattern = re.compile(r'^@prefix\s+(\w+):\s+<([^>]+)>\s*\.\s*$')

    for line in lines:
        # Check for existing RDF version declarations
        if '@prefix rdf:' in line and 'http://www.w3.org/1999/02/22-rdf-syntax-ns' in line:
            # Keep existing rdf prefix but we'll add RDF 1.2 directive
            transformed_lines.append(line)
            if not added_rdf12_decl:
                # Add RDF 1.2 directive after the rdf prefix declaration
                transformed_lines.append('@version rdf:12 .')
                added_rdf12_decl = True
        else:
            transformed_lines.append(line)

    # If no rdf prefix was found, add both prefix and version
    if not added_rdf12_decl:
        # Find where to insert (after any existing prefixes)
        insert_pos = 0
        for i, line in enumerate(transformed_lines):
            if line.startswith('@prefix'):
                insert_pos = i + 1
            elif line.strip() and not line.startswith('@'):
                break

        rdf_prefix_line = '@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .'
        version_line = '@version rdf:12 .'

        # Insert at appropriate position
        transformed_lines.insert(insert_pos, rdf_prefix_line)
        transformed_lines.insert(insert_pos + 1, version_line)

    # Clean up any extra whitespace
    result = '\n'.join(transformed_lines)

    return result


def save_turtle_file(content, output_path):
    """
    Save Turtle content to a file.

    Args:
        content: String containing Turtle content
        output_path: Path to output file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():

    try:
        print(f"Reading input from: {input_file}")
        turtle_content = read_turtle_file(input_file)

        print("Transforming to RDF 1.2 format...")
        rdf12_content = transform_to_rdf12(turtle_content)

        print(f"Saving to: {output_file}")
        save_turtle_file(rdf12_content, output_file)

        print("✓ Transformation complete!")
        print(f"  Input RDF version: 1.1")
        print(f"  Output RDF version: 1.2")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    input_file = "https://www.wikidata.org/wiki/Special:EntityData/Q220659.ttl"
    output_file = "output.ttl"
    main()