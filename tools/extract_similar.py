#!/usr/bin/env python3
"""Find likely misspellings by comparing low-frequency tokens to high-frequency tokens.

Reads a tab-separated file with header 'Vocabulary\tCount' (like `vocab_counts.txt`).
Writes `similar_words.txt` with columns: word\tcount\tcandidate\tcandidate_count\tscore

Usage:
  python extract_similar.py vocab_counts.txt [output_file]
"""
from pathlib import Path
import sys
import argparse
from collections import OrderedDict
import difflib


def read_vocab(path: Path):
    vocab = OrderedDict()
    with path.open(encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            word = parts[0]
            try:
                count = int(parts[1])
            except Exception:
                count = 0
            vocab[word] = count
    return vocab


def find_similars(vocab, low_thresh=5, high_thresh=50, top_n=3, cutoff=0.75):
    """Find similar high-frequency candidate words for low-frequency words.

    Optimization: bucket high-frequency words by prefix (1-2 chars) and by length so
    difflib runs only on a small subset per low word. This avoids O(|lows|*|highs|)
    comparisons which can be very slow when vocab is large.
    """
    lows = [w for w,c in vocab.items() if c <= low_thresh]
    highs = [(w, c) for w,c in vocab.items() if c >= high_thresh]

    # Build buckets
    highs_by_prefix = {}
    highs_by_len = {}
    for w,c in highs:
        if w:
            p1 = w[0]
            p2 = w[:2] if len(w) >= 2 else p1
            highs_by_prefix.setdefault(p1, []).append(w)
            highs_by_prefix.setdefault(p2, []).append(w)
        highs_by_len.setdefault(len(w), []).append(w)

    results = []
    for w in lows:
        cand_set = set()
        if not w:
            continue
        p1 = w[0]
        p2 = w[:2] if len(w) >= 2 else p1
        cand_set.update(highs_by_prefix.get(p1, []))
        cand_set.update(highs_by_prefix.get(p2, []))
        cand_set.update(highs_by_len.get(len(w), []))
        cand_set.update(highs_by_len.get(len(w)-1, []))
        cand_set.update(highs_by_len.get(len(w)+1, []))

        # If candidate set is empty (rare), fall back to a small global sample of highs
        if not cand_set:
            # choose top 500 highs by frequency
            cand_set.update([w for w,_ in highs[:500]])

        # Convert to list and limit size to keep matching fast
        cand_list = list(cand_set)
        if len(cand_list) > 2000:
            cand_list = cand_list[:2000]

        matches = difflib.get_close_matches(w, cand_list, n=top_n, cutoff=cutoff)
        for m in matches:
            score = difflib.SequenceMatcher(None, w, m).ratio()
            results.append((w, vocab[w], m, vocab.get(m, 0), score))

    results.sort(key=lambda x: (x[1], -x[4]))
    return results


def write_results(results, outpath: Path):
    with outpath.open('w', encoding='utf-8') as f:
        f.write('word\tcount\tcandidate\tcandidate_count\tscore\n')
        for w,c,m,mc,score in results:
            f.write(f"{w}\t{c}\t{m}\t{mc}\t{score:.3f}\n")


def main(argv=None):
    p = argparse.ArgumentParser(description='Find likely misspellings')
    p.add_argument('vocab', help='vocab TSV input file (Vocabulary\tCount)')
    p.add_argument('out', nargs='?', default='similar_words.txt', help='output file')
    p.add_argument('--low', type=int, default=5, help='max count to consider a word low-frequency')
    p.add_argument('--high', type=int, default=50, help='min count to consider a candidate high-frequency')
    p.add_argument('--cutoff', type=float, default=0.75, help='similarity cutoff for matches (0..1)')
    p.add_argument('--top', type=int, default=3, help='top N matches to consider per low word')
    args = p.parse_args(argv)

    vocab = read_vocab(Path(args.vocab))
    results = find_similars(vocab, low_thresh=args.low, high_thresh=args.high, top_n=args.top, cutoff=args.cutoff)
    write_results(results, Path(args.out))
    print(f'Wrote {len(results)} potential matches to {args.out}')


if __name__ == '__main__':
    raise SystemExit(main())
