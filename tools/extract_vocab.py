#!/usr/bin/env python3
"""Extract vocabulary and counts from a text file.

Usage:
  python extract_vocab.py input_file [output_file]

Writes a tab-separated file with header: Vocabulary\tCount
"""
from pathlib import Path
import sys
from collections import Counter
import argparse
import re


def get_word_finder():
    # Prefer the third-party 'regex' module for full Unicode letter support if available
    try:
        import regex as _regex
        return lambda text: _regex.findall(r"\p{L}+", text)
    except Exception:
        # Fallback: basic Unicode letter ranges and apostrophes/hyphens
        return lambda text: re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ'-]+", text)


def extract_counts(path: Path) -> Counter:
    text = path.read_text(encoding="utf-8", errors="ignore")
    finder = get_word_finder()
    tokens = [t.lower() for t in finder(text)]
    return Counter(tokens)


def write_tsv(counter: Counter, out: Path):
    with out.open("w", encoding="utf-8") as f:
        f.write("Vocabulary\tCount\n")
        for word, cnt in counter.most_common():
            f.write(f"{word}\t{cnt}\n")


def main(argv=None):
    p = argparse.ArgumentParser(description="Extract vocabulary and counts from a text file")
    p.add_argument("input", help="Input file path")
    p.add_argument("output", nargs="?", default="vocab_counts.txt", help="Output TSV file (default: vocab_counts.txt)")
    args = p.parse_args(argv)

    inp = Path(args.input)
    if not inp.exists():
        print(f"Error: input file not found: {inp}", file=sys.stderr)
        return 2

    counter = extract_counts(inp)
    outp = Path(args.output)
    write_tsv(counter, outp)
    print(f"Wrote {len(counter)} tokens to {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
