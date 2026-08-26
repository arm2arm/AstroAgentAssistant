# Journal Class Troubleshooting

## aa.cls (Astronomy & Astrophysics)

**Source**: A&A journal class v7.0. Often not pre-installed on fresh Debian/Ubuntu systems.

**Install**:
```bash
kpsewhich aa.cls              # verify missing
mkdir -p /home/hermes/texmf/tex/latex/
curl -sL https://fits.gsfc.nasa.gov/standard30/aa.cls -o /home/hermes/texmf/tex/latex/aa.cls
kpsewhich aa.cls              # verify found → /home/hermes/texmf/tex/latex/aa.cls
```

**⚠ NASA mirror only**: `https://www.aanda.org/for-authors/aa.cls` returns 504 Gateway Time-out. NASA (`fits.gsfc.nasa.gov`) is the reliable source.

**⚠ BibTeX, NOT biblatex**: The aa v7.0 class is designed for traditional BibTeX. Using `\\usepackage[style=aa]{biblatex}` fails with "Style 'aa' not found." Correct preamble:
```latex
\bibliographystyle{aa}
\bibliography{references}
```
Makefile must use `bibtex` (not `biber`).

**texmf home**: `/home/hermes/texmf` — not `~/.texlive/`.

## Mnras.cls

Similar issue — may not be installed. Install via:
```bash
sudo apt install texlive-publishers   # includes mnras.cls on many systems
# or CTAN: https://www.ctan.org/pkg/mnras
```

## General Pattern

1. Compile → if "File `X.cls' not found", identify the class
2. Check if a TeX Live package provides it: `apt-cache search texlive | grep <keyword>`
3. If not packaged, download from author/CTAN/NASA mirror to `/home/hermes/texmf/tex/latex/`
4. Verify with `kpsewhich X.cls` before recompiling