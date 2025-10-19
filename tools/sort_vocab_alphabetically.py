#!/usr/bin/env python3
"""Sort vocabulary entries alphabetically.

Reads vocab_counts.txt and creates a new file with entries sorted A-Z.
Preserves the count for each word and the header row.

Usage:
    python sort_vocab_alphabetically.py vocab_counts.txt [output_file]
"""
from pathlib import Path
import sys
import argparse


def sort_vocab_file(inpath: Path, outpath: Path):
    """Read vocab file, sort entries alphabetically, and write to new file."""
    # Read and parse input file
    entries = []
    header = None
    
    with inpath.open(encoding='utf-8') as f:
        header = f.readline().strip()  # Preserve header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                word = parts[0]
                try:
                    count = int(parts[1])
                    entries.append((word, count))
                except ValueError:
                    continue  # Skip invalid count values
    
    # Sort alphabetically
    entries.sort(key=lambda x: x[0].lower())  # Case-insensitive sort
    
    # Write sorted entries
    with outpath.open('w', encoding='utf-8') as f:
        f.write(header + '\n')  # Write original header
        for word, count in entries:
            f.write(f"{word}\t{count}\n")
    
    return len(entries)


def main(argv=None):
    p = argparse.ArgumentParser(description='Sort vocabulary entries alphabetically')
    p.add_argument('vocab', help='vocab_counts.txt input file')
    p.add_argument('output', nargs='?', default='vocab_counts_alpha.txt',
                  help='output file (default: vocab_counts_alpha.txt)')
    args = p.parse_args(argv)

    inpath = Path(args.vocab)
    if not inpath.exists():
        print(f"Error: input file not found: {inpath}", file=sys.stderr)
        return 2

    outpath = Path(args.output)
    count = sort_vocab_file(inpath, outpath)
    print(f"Sorted {count} vocabulary entries")
    print(f"Wrote alphabetized results to {outpath}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())