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
    """Read vocabulary and counts from TSV file."""
    low_freq = {}  # words with count 1-2
    high_freq = {}  # words with count > 2
    
    with path.open(encoding='utf-8') as f:
        header = f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
            word, count = parts[0], int(parts[1])
            if count <= 2:
                low_freq[word] = count
            else:
                high_freq[word] = count
    return low_freq, high_freq


def find_first_letter_variants(low_freq: dict, high_freq: dict):
    """Find low-frequency words that match high-frequency words except for first letter."""
    # Group high-frequency words by their tail (everything after first letter)
    high_freq_by_tail = defaultdict(list)
    for word, count in high_freq.items():
        if len(word) > 1:  # Skip single-letter words
            tail = word[1:]
            high_freq_by_tail[tail].append((word, count))
    
    variants = []
    # Look for low-frequency words that match tails
    for word, count in low_freq.items():
        if len(word) <= 1:  # Skip single-letter words
            continue
            
        tail = word[1:]
        if tail in high_freq_by_tail:
            # Found matching tail in high-frequency words
            for high_word, high_count in high_freq_by_tail[tail]:
                if word[0] != high_word[0]:  # Different first letter
                    variants.append((
                        word,  # low-frequency word
                        count,  # its count
                        high_word,  # matching high-frequency word
                        high_count,  # its count
                        word[0],  # low-freq first letter
                        high_word[0]  # high-freq first letter
                    ))
    
    # Sort by low-frequency word count, then by high-frequency word count descending
    variants.sort(key=lambda x: (x[1], -x[3]))
    return variants


def write_results(variants, outpath: Path):
    """Write results to output file."""
    with outpath.open('w', encoding='utf-8') as f:
        f.write('word\tcount\tsuggestion\tsugg_count\tfirst_letter\tsugg_letter\n')
        for v in variants:
            f.write(f"{v[0]}\t{v[1]}\t{v[2]}\t{v[3]}\t{v[4]}\t{v[5]}\n")
    return len(variants)


def main(argv=None):
    p = argparse.ArgumentParser(
        description='Find first-letter spelling variants in vocabulary')
    p.add_argument('vocab', help='vocab_counts.txt input file')
    p.add_argument('output', nargs='?', default='first_letter_variants.txt',
                  help='output file (default: first_letter_variants.txt)')
    args = p.parse_args(argv)

    inpath = Path(args.vocab)
    if not inpath.exists():
        print(f"Error: input file not found: {inpath}", file=sys.stderr)
        return 2

    low_freq, high_freq = read_vocab(inpath)
    variants = find_first_letter_variants(low_freq, high_freq)
    
    outpath = Path(args.output)
    count = write_results(variants, outpath)
    print(f"Found {count} potential first-letter variants")
    print(f"Wrote results to {outpath}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())