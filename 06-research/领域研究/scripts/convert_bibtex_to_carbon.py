#!/usr/bin/env python3
"""
Convert BibTeX references to Carbon journal (Elsevier) format
"""
import bibtexparser
from pathlib import Path

def format_authors(authors):
    """Format authors for Carbon journal"""
    author_list = authors.split(' and ')

    if len(author_list) > 6:
        # Use et al. for more than 6 authors
        first_three = [format_single_author(a) for a in author_list[:3]]
        return ', '.join(first_three) + ', et al.'
    else:
        formatted = [format_single_author(a) for a in author_list]
        return ', '.join(formatted)

def format_single_author(author):
    """Format single author name: 'Lin, Jian' -> 'Lin J'"""
    author = author.strip()
    if ',' in author:
        parts = author.split(',')
        last_name = parts[0].strip()
        first_name = parts[1].strip()
        # Get initials
        initials = ''.join([name[0].upper() for name in first_name.split() if name])
        return f'{last_name} {initials}'
    else:
        # Already in correct format or single name
        return author

def format_carbon_reference(entry):
    """Format a single reference in Carbon journal style"""
    ref_type = entry['ENTRYTYPE']

    if ref_type == 'article':
        # Journal article
        authors = format_authors(entry.get('author', ''))
        title = entry.get('title', '').strip()
        journal = entry.get('journal', '').strip()
        year = entry.get('year', '')
        volume = entry.get('volume', '')
        number = entry.get('number', '')
        pages = entry.get('pages', '').replace('--', '-')

        # Build reference
        ref = f"{authors}. {title}. "

        if number:
            ref += f"{journal}. {year};{volume}({number}):{pages}."
        else:
            ref += f"{journal}. {year};{volume}:{pages}."

        return ref

    elif ref_type == 'book':
        # Book
        authors = format_authors(entry.get('author', ''))
        title = entry.get('title', '').strip()
        publisher = entry.get('publisher', '').strip()
        year = entry.get('year', '')

        return f"{authors}. {title}. {publisher}; {year}."

    elif ref_type == 'inproceedings':
        # Conference proceedings
        authors = format_authors(entry.get('author', ''))
        title = entry.get('title', '').strip()
        booktitle = entry.get('booktitle', '').strip()
        year = entry.get('year', '')
        pages = entry.get('pages', '').replace('--', '-')

        return f"{authors}. {title}. In: {booktitle}. {year}. p. {pages}."

    elif ref_type == 'misc' or ref_type == 'article':
        # arXiv or other
        authors = format_authors(entry.get('author', ''))
        title = entry.get('title', '').strip()
        journal = entry.get('journal', entry.get('eprint', 'arXiv preprint')).strip()
        year = entry.get('year', '')

        if 'arXiv' in journal or entry.get('eprint'):
            eprint = entry.get('eprint', '')
            return f"{authors}. {title}. arXiv preprint {eprint}. {year}."
        else:
            return f"{authors}. {title}. {journal}. {year}."

    else:
        # Fallback
        return f"Unknown type: {entry.get('ID', '')}"

def main():
    bib_file = Path("D:/OpenClaw/workspace/11-research/paper/references_formatted.bib")
    output_file = Path("D:/OpenClaw/workspace/11-research/paper/references_carbon_format.txt")

    with open(bib_file, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f)

    entries = bib_database.entries

    print("=" * 70)
    print("BibTeX to Carbon Journal Format Converter")
    print("=" * 70)
    print(f"\nTotal entries: {len(entries)}\n")

    # Sort entries by ID to maintain order
    entries_sorted = sorted(entries, key=lambda x: x.get('ID', ''))

    output_lines = []

    for i, entry in enumerate(entries_sorted, 1):
        ref_text = format_carbon_reference(entry)
        formatted_ref = f"[{i}] {ref_text}"
        output_lines.append(formatted_ref)

        print(f"[{i}] OK")
        # Print first 100 chars for verification
        print(f"    {ref_text[:100]}...")
        print()

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Carbon Journal Reference Format\n")
        f.write(f"# Generated: 2026-03-06\n")
        f.write(f"# Total: {len(entries)} references\n\n")
        f.write('\n'.join(output_lines))

    print("=" * 70)
    print(f"[OK] Conversion complete!")
    print(f"Output file: {output_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
