# Multi-File Paper Structure (SH26 Pattern)

## When to Use

- **Multi-file** (`doc/chapters/*.tex` + `\input{}`): Long papers, parallel editing, individual section review, many authors
- **Monolithic** (`main.tex` only): Short papers, rapid iteration, single author

## Structure

```
project/
├── Makefile              ← build system
├── README.md
├── img/                  ← generated figures (project root)
├── src/                  ← Python analysis scripts
└── doc/
    ├── main.tex          ← entry point
    ├── chapters/         ← one .tex per section
    │   ├── abstract.tex
    │   ├── introduction.tex
    │   ├── data_pipeline.tex
    │   ├── results.tex
    │   ├── discussion.tex
    │   └── conclusion.tex
    └── references.bib
```

## Key Rules

1. **Figure directory**: `img/` at project root, NOT `doc/figures/`. LaTeX reference: `../../img/fig.png`
2. **Chapter directory**: `doc/chapters/` (not `sections/`)
3. **Entry point**: `main.tex` uses `\input{chapters/...}` for each section
4. **Makefile**: Tracks `$(BUILDDOC)/main.tex` and `$(BUILDDOC)/chapters/*.tex` as dependencies

## Adding a Chapter

1. Create `doc/chapters/new_section.tex`
2. Add `\input{chapters/new_section}` to `main.tex` at desired position
3. Add `make pdf` target dependency if needed

## Removing a Chapter

1. Remove `\input{chapters/old_section}` from `main.tex`
2. Delete `doc/chapters/old_section.tex`
3. Run `make clean` to remove stale build artifacts

## Pitfalls

- **Stale files**: Always clean up `.tex` files in `chapters/` that are no longer `\input{}`-ed
- **Relative paths**: Figures referenced in `doc/chapters/*.tex` need `../../img/` not `../img/`
- **Makefile dependencies**: If you add a new chapter, the Makefile wildcard `$(wildcard $(BUILDDOC)/chapters/*.tex)` will pick it up automatically — no need to add explicit dependencies
- **Cross-references**: When splitting a monolithic paper, make sure `\label{}` and `\ref{}` references still resolve correctly

## Scaffold Script

Use `scripts/scaffold-paper.py` (bundled with this skill) to create a new multi-file project:

```bash
python3 scripts/scaffold-paper.py <project-name> --authors "Author Name" --description "Short description"
```

Creates all files above with TODO placeholders ready for filling.
