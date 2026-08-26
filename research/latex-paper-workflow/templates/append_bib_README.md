# append_bib_README.md

This short template explains the safe interactive usage of `scripts/append_bib_from_candidates.py` and the preferred repository backup policy when accepting automated bibliographic candidates.

Usage summary
- Always create a backup git branch before merging candidates: `git checkout -b backup/bib-sweep-YYYYMMDD`
- Commit `_autofetch_candidates.bib` first so the provenance of candidates is preserved.
- Run `python3 scripts/append_bib_from_candidates.py` and vet each candidate entry.
- Commit `references.bib` after appending with a clear message describing which entries were added.

Do NOT use `--auto-accept` in unattended or CI environments unless you understand the provenance of each candidate.
