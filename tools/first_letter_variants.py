#!/usr/bin/env python3
"""Find words that differ only in their first letter, focusing on low-frequency variants.

This script reads vocab_counts.txt and finds words that:
1. Have count of 1-2 (low frequency)
2. Match a higher-frequency word exactly except for the first letter
3. Outputs potential first-letter spelling mistakes

Usage:
    python first_letter_variants.py vocab_counts.txt [output_file]
"""
from pathlib import Path
import sys
import argparse
from collections import defaultdict


def read_vocab(path: Path):
    """Read vocabulary and counts from TSV file, tracking true line numbers for low-freq words."""
    low_freq = {}  # word -> (count, line_number)
    high_freq = {}  # word -> count
    with path.open(encoding='utf-8') as f:
        header = f.readline()  # Skip header
        line_number = 2  # Start at 2 (first data line)
        for line in f:
            stripped = line.rstrip('\n')
            parts = stripped.split('\t')
            if len(parts) < 2 or not parts[0].strip():
                line_number += 1
                continue
            word, count = parts[0], int(parts[1])
            if count <= 2:
                low_freq[word] = (count, line_number)
            else:
                high_freq[word] = count
            line_number += 1
    return low_freq, high_freq

# New: Map word to first line number in .yet file
def build_yet_word_line_map(yet_path: Path):
    """Scan .yet file and return a dict: word -> first line number (1-based)."""
    import re
    word_line = {}
    with yet_path.open(encoding='utf-8') as f:
        for idx, line in enumerate(f, start=1):
            # Extract words (simple split, can be improved)
            for word in re.findall(r"[\w'-]+", line):
                word_lower = word.lower()
                if word_lower not in word_line:
                    word_line[word_lower] = idx
    return word_line


def find_first_letter_variants(low_freq: dict, high_freq: dict, yet_word_line=None):
    """Find low-frequency words that match high-frequency words except for first letter.
    low_freq: word -> (count, line_number)
    high_freq: word -> count
    yet_word_line: dict word->line in .yet file (optional)
    """
    # Group high-frequency words by their tail (everything after first letter)
    high_freq_by_tail = defaultdict(list)
    for word, count in high_freq.items():
        if len(word) > 1:
            tail = word[1:]
            high_freq_by_tail[tail].append((word, count))

    variants = []
    for word, (count, line_number) in low_freq.items():
        if len(word) <= 1:
            continue
        tail = word[1:]
        if tail in high_freq_by_tail:
            for high_word, high_count in high_freq_by_tail[tail]:
                if word[0] != high_word[0]:
                    # Get .yet line number if available
                    yet_line = None
                    if yet_word_line is not None:
                        yet_line = yet_word_line.get(word.lower(), "")
                    variants.append((
                        word,  # low-frequency word
                        count,  # its count
                        line_number,  # line number in vocab_counts.txt
                        yet_line,  # line number in .yet file
                        high_word,  # matching high-frequency word
                        high_count,  # its count
                        word[0],  # low-freq first letter
                        high_word[0]  # high-freq first letter
                    ))
    # Sort by low-frequency word count, then by high-frequency word count descending
    variants.sort(key=lambda x: (x[1], -x[5]))
    return variants


def write_results(variants, outpath: Path):
    """Write results to output file, including .yet line number."""
    with outpath.open('w', encoding='utf-8') as f:
        f.write('word\tcount\tvocab_line\tyet_line\tsuggestion\tsugg_count\tfirst_letter\tsugg_letter\n')
        for v in variants:
            f.write(f"{v[0]}\t{v[1]}\t{v[2]}\t{v[3]}\t{v[4]}\t{v[5]}\t{v[6]}\t{v[7]}\n")
    return len(variants)


def main(argv=None):
    p = argparse.ArgumentParser(
        description='Find first-letter spelling variants in vocabulary')
    p.add_argument('vocab', help='vocab_counts.txt input file')
    p.add_argument('output', nargs='?', default='first_letter_variants.txt',
                  help='output file (default: first_letter_variants.txt)')
    p.add_argument('--yet', default='../Bible_thk_v6.yet', help='Path to .yet file for line lookup')
    args = p.parse_args(argv)

    inpath = Path(args.vocab)
    if not inpath.exists():
        print(f"Error: input file not found: {inpath}", file=sys.stderr)
        return 2

    # Build .yet word->line map
    yet_path = Path(args.yet)
    yet_word_line = None
    if yet_path.exists():
        print(f"Indexing .yet file: {yet_path}")
        yet_word_line = build_yet_word_line_map(yet_path)
    else:
        print(f"Warning: .yet file not found at {yet_path}, skipping .yet line lookup")

    low_freq, high_freq = read_vocab(inpath)
    variants = find_first_letter_variants(low_freq, high_freq, yet_word_line)
    
    outpath = Path(args.output)
    count = write_results(variants, outpath)
    print(f"Found {count} potential first-letter variants")
    print(f"Wrote results to {outpath}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())