#!/usr/bin/env python3
"""Find word pairs in vocabulary that differ by exactly one character.

This helps identify likely typos by focusing on single-character insertions, deletions,
or substitutions between words in the vocabulary. Words are compared only to other words
of similar length for efficiency.

Usage:
  python extract_one_letter_diff.py vocab_counts.txt [output_file]
"""
from pathlib import Path
import sys
import argparse
from collections import defaultdict


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate edit distance between strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if not s2:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def describe_difference(w1: str, w2: str) -> str:
    """Return a human-readable description of the single-character difference."""
    if len(w1) == len(w2):
        # Substitution
        for i, (c1, c2) in enumerate(zip(w1, w2)):
            if c1 != c2:
                return f"Changed '{c1}' to '{c2}' at position {i+1}"
    elif len(w1) < len(w2):
        # Insertion
        for i in range(len(w1) + 1):
            if i == len(w1) or w1[i] != w2[i]:
                return f"Added '{w2[i]}' at position {i+1}"
    else:
        # Deletion
        for i in range(len(w2) + 1):
            if i == len(w2) or w1[i] != w2[i]:
                return f"Removed '{w1[i]}' at position {i+1}"
    return "Unknown difference"


def read_vocab(path: Path):
    """Read vocabulary and counts from TSV file."""
    vocab = {}
    with path.open(encoding='utf-8') as f:
        header = f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
            word, count = parts[0], int(parts[1])
            vocab[word] = count
    return vocab


def chars_diff_by_one(w1: str, w2: str) -> bool:
    """Fast check if strings differ by exactly one character."""
    if abs(len(w1) - len(w2)) > 1:
        return False
    
    # For strings of same length
    if len(w1) == len(w2):
        diffs = 0
        for c1, c2 in zip(w1, w2):
            if c1 != c2:
                diffs += 1
                if diffs > 1:
                    return False
        return diffs == 1
    
    # For strings differing by 1 char
    if len(w1) > len(w2):
        w1, w2 = w2, w1  # Make w1 the shorter one
    
    i = j = diffs = 0
    while i < len(w1) and j < len(w2):
        if w1[i] != w2[j]:
            diffs += 1
            if diffs > 1:
                return False
            j += 1
        else:
            i += 1
            j += 1
    return diffs + (len(w2) - j) == 1


def find_one_letter_diffs(vocab: dict, min_freq=2):
    """Find pairs of words that differ by exactly one character.
    
    Uses length and prefix bucketing plus fast character comparison
    to efficiently find one-character differences.
    """
    # Group words by length and first character for efficient comparison
    by_length = defaultdict(list)
    by_prefix = defaultdict(list)
    
    for word, count in vocab.items():
        if count >= min_freq:  # Only process words meeting minimum frequency
            by_length[len(word)].append((word, count))
            if word:
                by_prefix[word[0]].append((word, count))
    
    pairs = []
    seen = set()
    
    # Compare words of similar lengths that share a prefix or differ by one char
    for length in sorted(by_length.keys()):
        words = by_length[length]
        
        # Group words by first character for faster filtering
        length_by_prefix = defaultdict(list)
        for w, c in words:
            if w:
                length_by_prefix[w[0]].append((w, c))
        
        # Check words of same length with same or adjacent prefixes
        for prefix, prefix_words in length_by_prefix.items():
            # Compare within same prefix group
            for i, (w1, c1) in enumerate(prefix_words):
                for w2, c2 in prefix_words[i+1:]:
                    if chars_diff_by_one(w1, w2):
                        key = tuple(sorted([w1, w2]))
                        if key not in seen:
                            seen.add(key)
                            diff = describe_difference(w1, w2)
                            pairs.append((w1, str(c1), w2, str(c2), "1.0", diff))
        
        # Check words of length+1 that share first character
        if length + 1 in by_length:
            longer_words = by_length[length + 1]
            for w1, c1 in words:
                if not w1:
                    continue
                # Only compare with longer words starting with same character
                for w2, c2 in longer_words:
                    if w2 and w1[0] == w2[0] and chars_diff_by_one(w1, w2):
                        key = tuple(sorted([w1, w2]))
                        if key not in seen:
                            seen.add(key)
                            diff = describe_difference(w1, w2)
                            pairs.append((w1, str(c1), w2, str(c2), "1.0", diff))
    
    # Sort by frequency ascending (less frequent words first)
    pairs.sort(key=lambda x: (int(x[1]), -int(x[3])))
    return pairs


def write_results(pairs, outpath: Path):
    """Write results to output file."""
    with outpath.open('w', encoding='utf-8') as f:
        f.write('word\tcount\tcandidate\tcount\tscore\tdifference\n')
        for p in pairs:
            f.write('\t'.join(p) + '\n')
    return len(pairs)


def main(argv=None):
    p = argparse.ArgumentParser(description='Find words differing by one character')
    p.add_argument('input', help='vocab_counts.txt input file')
    p.add_argument('output', nargs='?', default='one_letter_diff.txt',
                  help='output file (default: one_letter_diff.txt)')
    p.add_argument('--min-freq', type=int, default=2,
                  help='minimum frequency to consider (default: 2)')
    args = p.parse_args(argv)

    inpath = Path(args.input)
    if not inpath.exists():
        print(f"Error: input file not found: {inpath}", file=sys.stderr)
        return 2

    vocab = read_vocab(inpath)
    pairs = find_one_letter_diffs(vocab, min_freq=args.min_freq)
    
    outpath = Path(args.output)
    count = write_results(pairs, outpath)
    print(f"Found {count} word pairs with exactly one character difference")
    print(f"Wrote results to {outpath}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())