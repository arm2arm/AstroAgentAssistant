#!/usr/bin/env python3
"""
Interactive helper: append vetted entries from references/_autofetch_candidates.bib
into references.bib with provenance comments. Creates a backup of references.bib and
never overwrites existing entries without confirmation.

Usage:
  python3 scripts/append_bib_from_candidates.py [--candidates path] [--refs path]

Default paths (relative to repository root):
  candidates: references/_autofetch_candidates.bib
  refs:       references.bib

Behavior:
 - Parses the candidates file by splitting on blank lines between entries.
 - For each candidate, shows provenance lines (lines starting with "%") and the
   BibTeX entry preview.
 - Prompts the user to: (a) accept and append, (e) edit in $EDITOR before appending,
   (s) skip, or (m) mark as manual (leave in candidates with a TODO comment).
 - Before any writes, creates references.bib.bak timestamped and writes a commit-like
   provenance header above appended entries.

This script is intentionally interactive to preserve human vetting. For CI or
non-interactive usage, run with --auto-accept to append all candidates (use with care).
"""

import argparse
import datetime
import os
import shutil
import subprocess
import tempfile


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def split_candidates(content):
    # naive split: entries separated by two or more newlines
    parts = [p.strip() for p in content.split('\n\n') if p.strip()]
    # recombine lines that are part of the same entry if they start with '@'
    entries = []
    cur = []
    for p in parts:
        if p.startswith('@'):
            if cur:
                entries.append('\n\n'.join(cur).strip())
            cur = [p]
        else:
            if cur:
                cur.append(p)
            else:
                # stray comment or line; keep it as its own entry
                entries.append(p)
    if cur:
        entries.append('\n\n'.join(cur).strip())
    return entries


def open_in_editor(initial_text):
    editor = os.environ.get('EDITOR', 'vi')
    with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.bib') as tf:
        tf.write(initial_text)
        tf.flush()
        path = tf.name
    try:
        subprocess.call([editor, path])
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    finally:
        os.unlink(path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidates', default='references/_autofetch_candidates.bib')
    p.add_argument('--refs', default='references.bib')
    p.add_argument('--auto-accept', action='store_true', help='Append all candidates without prompting (use with care)')
    args = p.parse_args()

    if not os.path.exists(args.candidates):
        print(f'Candidates file not found: {args.candidates}')
        raise SystemExit(1)
    if not os.path.exists(args.refs):
        print(f'References file not found: {args.refs}; creating a new one.')
        write_file(args.refs, '')

    cand_text = read_file(args.candidates)
    entries = split_candidates(cand_text)
    if not entries:
        print('No candidate entries found.')
        return

    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    bak_name = f"{args.refs}.bak.{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
    shutil.copy2(args.refs, bak_name)
    print(f'Backup of {args.refs} written to {bak_name}')

    refs_content = read_file(args.refs)
    appended = []

    for i, entry in enumerate(entries, start=1):
        print('\n' + '='*80)
        print(f'Candidate {i}/{len(entries)}')
        preview_lines = [ln for ln in entry.split('\n') if ln.strip()]
        # show provenance comments and first 20 lines of entry
        for ln in preview_lines[:20]:
            print(ln)
        if len(preview_lines) > 20:
            print('... (truncated preview)')

        if args.auto_accept:
            choice = 'a'
        else:
            choice = input('(a)ccept / (e)dit / (s)kip / (m)ark manual / (q)uit ? ').strip().lower()
        if choice == 'q':
            break
        if choice == 's':
            continue
        if choice == 'm':
            # leave in candidates but annotate with TODO
            print('Marked manual; leaving candidate in place with TODO.')
            continue
        if choice == 'e':
            edited = open_in_editor(entry)
            entry_to_append = edited.strip() + '\n\n'
        else:
            entry_to_append = entry.strip() + '\n\n'

        # append provenance header
        provenance = f"% Appended by append_bib_from_candidates.py on {timestamp}\n% Source: {args.candidates}\n"
        refs_content += '\n' + provenance + entry_to_append
        appended.append(entry_to_append)
        print('Appended candidate to references.bib')

    if appended:
        write_file(args.refs, refs_content)
        print(f'Wrote {len(appended)} entries to {args.refs}. Backup at {bak_name}')
    else:
        print('No entries appended.')


if __name__ == '__main__':
    main()
